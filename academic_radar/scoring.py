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


def score(text, config):
    text = text.lower()

    if any(term in text for term in config.negative_terms):
        return 0

    event_score = sum(3 for term in config.event_terms if term in text)
    field_score = sum(2 for term in config.core_field_terms if term in text)
    core_source_bonus = 4 if any(term in text for term in config.prestige_or_core_sources) else 0
    raw = event_score + field_score + core_source_bonus

    has_event = event_score > 0
    has_core_field = field_score > 0
    has_core_source = core_source_bonus > 0

    if has_event and not has_core_field and not has_core_source:
        return 0
    if any(term in text for term in ["call for papers", "cfp", "call for chapters"]) and raw < 9:
        return 0
    if any(term in text for term in ["fellowship", "grant", "bursary", "studentship"]) and raw < 10:
        return 0
    if any(
        term in text
        for term in ["research assistant", "library assistant", "assistant librarian", "archivist", "curator"]
    ) and raw < 10:
        return 0

    return raw


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
    item_score = score(full_text, config)
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
        "dt": dt,
    }
