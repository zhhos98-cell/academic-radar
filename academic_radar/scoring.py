import re

from .text import clean_text


def classify(text):
    text = text.lower()

    if any(term in text for term in ["call for papers", "cfp", "call for chapters"]):
        return "CFP / Calls", "CFP"
    if any(term in text for term in ["special issue", "new issue"]):
        return "Special Issues / Journals", "Journal"
    if any(term in text for term in ["new book", "forthcoming", "book launch", "review copy"]):
        return "New Books", "Book"
    if any(
        term in text
        for term in [
            "research assistant",
            "ra position",
            "library assistant",
            "assistant librarian",
            "archivist",
            "curator",
        ]
    ):
        return "RA / Library / Archive Jobs", "Job"
    if any(term in text for term in ["fellowship", "grant", "bursary", "studentship"]):
        return "Fellowships / Grants", "Funding"
    if any(term in text for term in ["conference", "workshop", "symposium", "seminar"]):
        return "Events / Seminars", "Event"
    return "Other Signals", "Signal"


def matching_terms(text, terms):
    lower_text = text.lower()
    matches = []
    for term in terms:
        normalized = str(term).strip().lower()
        if normalized and normalized in lower_text and normalized not in matches:
            matches.append(normalized)
    return matches


def _reason(label, matches, points=None):
    if not matches:
        return ""
    suffix = f" (+{points})" if points is not None else ""
    return f"{label}: {', '.join(matches[:8])}{suffix}"


def explain_score(text, config):
    lower_text = text.lower()
    negative_matches = matching_terms(lower_text, config.negative_terms)
    event_matches = matching_terms(lower_text, config.event_terms)
    field_matches = matching_terms(lower_text, config.core_field_terms)
    source_matches = matching_terms(lower_text, config.prestige_or_core_sources)

    event_score = len(event_matches) * 3
    field_score = len(field_matches) * 2
    source_bonus = 4 if source_matches else 0
    raw = event_score + field_score + source_bonus

    explanation = {
        "score": raw,
        "raw_score": raw,
        "filtered": False,
        "filtered_by": "",
        "event_terms": event_matches,
        "core_field_terms": field_matches,
        "source_terms": source_matches,
        "negative_terms": negative_matches,
        "reasons": [],
    }

    if negative_matches:
        explanation.update(score=0, filtered=True, filtered_by="negative_terms")
        explanation["reasons"].append(_reason("Filtered by negative terms", negative_matches))
        return explanation

    if event_score:
        explanation["reasons"].append(_reason("Event terms", event_matches, event_score))
    if field_score:
        explanation["reasons"].append(_reason("Field terms", field_matches, field_score))
    if source_bonus:
        explanation["reasons"].append(_reason("Core source terms", source_matches, source_bonus))

    has_event = event_score > 0
    has_core_field = field_score > 0
    has_core_source = source_bonus > 0

    if has_event and not has_core_field and not has_core_source:
        explanation.update(score=0, filtered=True, filtered_by="event_without_relevance")
        explanation["reasons"].append("Filtered: event signal without configured field/source relevance.")
        return explanation
    if any(term in lower_text for term in ["call for papers", "cfp", "call for chapters"]) and raw < 9:
        explanation.update(score=0, filtered=True, filtered_by="cfp_threshold")
        explanation["reasons"].append("Filtered: CFP/call signals require score >= 9.")
        return explanation
    if any(term in lower_text for term in ["fellowship", "grant", "bursary", "studentship"]) and raw < 10:
        explanation.update(score=0, filtered=True, filtered_by="funding_threshold")
        explanation["reasons"].append("Filtered: funding signals require score >= 10.")
        return explanation
    if any(
        term in lower_text
        for term in ["research assistant", "library assistant", "assistant librarian", "archivist", "curator"]
    ) and raw < 10:
        explanation.update(score=0, filtered=True, filtered_by="job_threshold")
        explanation["reasons"].append("Filtered: job/archive signals require score >= 10.")
        return explanation

    if not explanation["reasons"]:
        explanation["reasons"].append("Matched baseline relevance rules.")

    return explanation


def score(text, config):
    return explain_score(text, config)["score"]


def extract_dates_and_details(text):
    text = clean_text(text)
    lower = text.lower()

    details = {
        "deadline": "",
        "event_date": "",
        "location": "",
        "format": "",
        "funding": "",
    }

    deadline_patterns = [
        r"deadline(?: for submissions)?[:\s]+([^.;\n]{3,80})",
        r"submission deadline[:\s]+([^.;\n]{3,80})",
        r"abstracts? (?:due|by)[:\s]+([^.;\n]{3,80})",
        r"deadline is[:\s]+([^.;\n]{3,80})",
        r"deadline to submit [^:]{0,40}[:\s]+([^.;\n]{3,80})",
        r"by ([0-9]{1,2}(?:st|nd|rd|th)? [A-Z][a-z]+ 20[0-9]{2})",
        r"by ([A-Z][a-z]+ [0-9]{1,2}, 20[0-9]{2})",
    ]
    for pattern in deadline_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            details["deadline"] = match.group(1).strip()[:100]
            break

    event_patterns = [
        r"([0-9]{1,2}[-/][0-9]{1,2} [A-Z][a-z]+ 20[0-9]{2})",
        r"([0-9]{1,2} [A-Z][a-z]+ 20[0-9]{2})",
        r"([A-Z][a-z]+ [0-9]{1,2}[-/][0-9]{1,2}, 20[0-9]{2})",
        r"([A-Z][a-z]+ [0-9]{1,2}, 20[0-9]{2})",
    ]
    for pattern in event_patterns:
        match = re.search(pattern, text)
        if match:
            details["event_date"] = match.group(1).strip()[:100]
            break

    location_patterns = [
        r"(?:venue:|hosted by|held at)\s+([^.;\n]{3,90})",
        r"([A-Z][A-Za-z .'-]+ University(?:, [A-Z][A-Za-z .'-]+)?)",
        r"(University of [A-Z][A-Za-z .'-]+)",
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            candidate = match.group(1).strip()
            if len(candidate.split()) <= 14:
                details["location"] = candidate[:120]
                break

    if "hybrid" in lower:
        details["format"] = "hybrid"
    elif "online" in lower or "zoom" in lower or "virtual" in lower:
        details["format"] = "online"
    elif "in person" in lower or "in-person" in lower:
        details["format"] = "in-person"

    funding_terms = [
        "bursary",
        "travel support",
        "travel grant",
        "stipend",
        "scholarship",
        "fee waiver",
        "funding available",
    ]
    for term in funding_terms:
        index = lower.find(term)
        if index != -1:
            start = max(0, index - 70)
            end = min(len(text), index + 160)
            details["funding"] = text[start:end].strip()[:240]
            break

    return details


def make_item(title, link, summary, source, config, source_name="", dt=None):
    full_text = f"{title} {summary} {source_name}"
    score_details = explain_score(full_text, config)
    item_score = score_details["score"]
    if item_score <= 0:
        return None

    category, tag = classify(full_text)
    return {
        "score": item_score,
        "title": clean_text(title)[:220],
        "link": link,
        "summary": clean_text(summary)[:520],
        "source": source,
        "source_name": source_name,
        "category": category,
        "tag": tag,
        "details": extract_dates_and_details(full_text),
        "score_reasons": score_details["reasons"],
        "score_matches": {
            "event_terms": score_details["event_terms"],
            "core_field_terms": score_details["core_field_terms"],
            "source_terms": score_details["source_terms"],
        },
        "dt": dt,
    }
