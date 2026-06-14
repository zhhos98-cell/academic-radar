from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
DEFAULT_PROFILE = ROOT / "config" / "profiles" / "hps.json"

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

MONTH_RE = (
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
)
DATE_TOKEN_RE = (
    r"\d{4}-\d{2}-\d{2}|"
    r"\d{1,2}(?:st|nd|rd|th)?\s+(?:" + MONTH_RE + r")\s+\d{4}|"
    r"(?:" + MONTH_RE + r")\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|"
    r"(?:" + MONTH_RE + r")\s+\d{4}"
)

ISSUE_FIELDS = [
    "CFP title",
    "Type",
    "Source URL",
    "Organiser",
    "Host institution",
    "Location",
    "Online option",
    "Event dates",
    "Abstract deadline",
    "Full paper deadline",
    "Registration deadline",
    "Notification date",
    "Abstract word limit",
    "Paper word limit",
    "Submission method",
    "Submission email",
    "Submission portal",
    "Theme keywords",
    "Project link",
    "Priority",
    "Status",
    "Next action",
    "Next action due",
    "Raw CFP text",
    "Notes",
    "Tracking options",
]


def clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_url(url: str) -> str:
    import requests

    response = requests.get(
        url,
        headers={"User-Agent": "academic-radar-cfp-parser/1.0"},
        timeout=(10, 30),
    )
    response.raise_for_status()
    return clean_text(response.text)


def read_inputs(args: argparse.Namespace) -> tuple[str, str]:
    parts: list[str] = []
    source_url = args.url or ""

    if args.url:
        parts.append(fetch_url(args.url))

    if args.file:
        parts.append(Path(args.file).read_text(encoding="utf-8"))

    if args.text:
        parts.append(args.text)

    env_text = os.environ.get("CFP_RAW_TEXT", "")
    if env_text:
        parts.append(env_text)

    return clean_text("\n\n".join(part for part in parts if part)), source_url


def month_number(value: str) -> int:
    key = value.lower().rstrip(".")
    return MONTHS[key]


def normalize_date_token(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value

    match = re.fullmatch(
        rf"(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_RE})\s+(\d{{4}})",
        value,
        flags=re.IGNORECASE,
    )
    if match:
        day = int(match.group(1))
        month = month_number(match.group(2))
        year = int(match.group(3))
        return f"{year:04d}-{month:02d}-{day:02d}"

    match = re.fullmatch(
        rf"({MONTH_RE})\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})",
        value,
        flags=re.IGNORECASE,
    )
    if match:
        month = month_number(match.group(1))
        day = int(match.group(2))
        year = int(match.group(3))
        return f"{year:04d}-{month:02d}-{day:02d}"

    match = re.fullmatch(rf"({MONTH_RE})\s+(\d{{4}})", value, flags=re.IGNORECASE)
    if match:
        month = month_number(match.group(1))
        year = int(match.group(2))
        return f"{year:04d}-{month:02d}"

    return value


def first_match(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            for group in match.groups():
                if group:
                    return clean_text(group)
    return ""


def extract_date_after(text: str, prefixes: list[str]) -> str:
    for prefix in prefixes:
        pattern = rf"{prefix}[^\n.;:]{{0,80}}?[:\s]+({DATE_TOKEN_RE})"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return normalize_date_token(match.group(1))
    return ""


def normalize_event_range(text: str) -> str:
    iso_range = re.search(
        r"(\d{4}-\d{2}-\d{2})\s*(?:to|through|until|[-–])\s*(\d{4}-\d{2}-\d{2})",
        text,
        flags=re.IGNORECASE,
    )
    if iso_range:
        return f"{iso_range.group(1)} to {iso_range.group(2)}"

    day_month_range = re.search(
        rf"(\d{{1,2}})(?:st|nd|rd|th)?\s*[-–]\s*(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_RE})\s+(\d{{4}})",
        text,
        flags=re.IGNORECASE,
    )
    if day_month_range:
        start_day = int(day_month_range.group(1))
        end_day = int(day_month_range.group(2))
        month = month_number(day_month_range.group(3))
        year = int(day_month_range.group(4))
        return f"{year:04d}-{month:02d}-{start_day:02d} to {year:04d}-{month:02d}-{end_day:02d}"

    month_day_range = re.search(
        rf"({MONTH_RE})\s+(\d{{1,2}})(?:st|nd|rd|th)?\s*[-–]\s*(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})",
        text,
        flags=re.IGNORECASE,
    )
    if month_day_range:
        month = month_number(month_day_range.group(1))
        start_day = int(month_day_range.group(2))
        end_day = int(month_day_range.group(3))
        year = int(month_day_range.group(4))
        return f"{year:04d}-{month:02d}-{start_day:02d} to {year:04d}-{month:02d}-{end_day:02d}"

    single = first_match(
        text,
        [
            rf"(?:conference|workshop|symposium|event|seminar)[^\n.]{{0,80}}(?:on|from|takes place|will be held)[^\n.]{{0,80}}({DATE_TOKEN_RE})",
            rf"(?:date|dates)[:\s]+({DATE_TOKEN_RE})",
        ],
    )
    return normalize_date_token(single) if single else ""


def infer_type(text: str) -> str:
    lower = text.lower()
    checks = [
        ("special issue", "special issue"),
        ("edited volume", "edited volume"),
        ("edited collection", "edited volume"),
        ("fellowship", "fellowship"),
        ("grant", "grant"),
        ("prize", "prize"),
        ("workshop", "workshop"),
        ("symposium", "symposium"),
        ("seminar", "seminar"),
        ("job", "job"),
        ("conference", "conference"),
    ]
    for needle, cfp_type in checks:
        if needle in lower:
            return cfp_type
    return "other"


def infer_online_option(text: str) -> str:
    lower = text.lower()
    if "hybrid" in lower:
        return "hybrid"
    if any(term in lower for term in ["online", "virtual", "zoom"]):
        return "yes"
    if any(term in lower for term in ["in person", "in-person", "on site", "onsite"]):
        return "no"
    return "unknown"


def infer_title(text: str, title_hint: str = "") -> str:
    if title_hint:
        return title_hint.strip()

    call_title = first_match(
        text,
        [
            r"^\s*(?:call for papers|cfp|call for chapters)[:\-–]\s*(.+)$",
            r"^\s*(?:special issue|conference|workshop|symposium)[:\-–]\s*(.+)$",
        ],
    )
    if call_title:
        return call_title[:220]

    for line in text.splitlines():
        line = line.strip(" -*#\t")
        if not line:
            continue
        if len(line) < 8:
            continue
        if line.lower() in {"call for papers", "cfp", "call for chapters"}:
            continue
        return line[:220]

    return "Untitled CFP"


def extract_word_limit(text: str, subject: str) -> str:
    if subject == "abstract":
        patterns = [
            r"abstracts? (?:of|should be|must be|up to|no more than|not exceeding)?\s*(\d{2,4})\s+words?",
            r"(\d{2,4})[- ]word abstracts?",
            r"proposal[s]? (?:of|should be|must be|up to|no more than|not exceeding)?\s*(\d{2,4})\s+words?",
        ]
    else:
        patterns = [
            r"(?:full papers?|articles?|chapters?) (?:of|should be|must be|up to|no more than|not exceeding)?\s*(\d{3,6})\s+words?",
            r"(\d{3,6})[- ]word (?:paper|article|chapter)",
        ]

    value = first_match(text, patterns)
    return f"{value} words" if value else ""


def extract_keywords(text: str, profile_path: Path) -> list[str]:
    if not profile_path.exists():
        return []

    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    scoring = profile.get("scoring", {})
    candidates: list[str] = []
    for key in ["core_field_terms", "core_terms", "event_terms"]:
        candidates.extend(scoring.get(key, []))

    lower = text.lower()
    seen: set[str] = set()
    found: list[str] = []
    for term in candidates:
        term_lower = str(term).lower()
        if term_lower in lower and term_lower not in seen:
            seen.add(term_lower)
            found.append(str(term))

    return found[:12]


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s<>)\]]+", text)
    cleaned: list[str] = []
    for url in urls:
        url = url.rstrip(".,;:")
        if url not in cleaned:
            cleaned.append(url)
    return cleaned


def extract_fields(text: str, source_url: str, title_hint: str, profile_path: Path) -> dict[str, str]:
    urls = extract_urls(text)
    emails = re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    submission_portal = first_match(
        "\n".join(urls),
        [
            r"(https?://[^\s]*(?:easychair|oxfordabstracts|submittable|forms\.gle|docs\.google|google\.com/forms)[^\s]*)",
            r"(https?://[^\s]*(?:submit|submission|proposal)[^\s]*)",
        ],
    )

    abstract_deadline = extract_date_after(
        text,
        [
            r"abstracts?(?:\s+are)?(?:\s+due|\s+deadline|\s+by)",
            r"proposal[s]?(?:\s+are)?(?:\s+due|\s+deadline|\s+by)",
            r"deadline(?:\s+for\s+(?:abstracts?|proposals?))?",
            r"submission deadline",
        ],
    )
    full_paper_deadline = extract_date_after(
        text,
        [
            r"full papers?(?:\s+are)?(?:\s+due|\s+deadline|\s+by)",
            r"articles?(?:\s+are)?(?:\s+due|\s+deadline|\s+by)",
            r"chapters?(?:\s+are)?(?:\s+due|\s+deadline|\s+by)",
        ],
    )
    registration_deadline = extract_date_after(text, [r"registration(?:\s+deadline|\s+by)?"])
    notification_date = extract_date_after(text, [r"notification(?:\s+date|\s+by)?", r"decisions?(?:\s+by)?"])

    fields = {
        "CFP title": infer_title(text, title_hint),
        "Type": infer_type(text),
        "Source URL": source_url or (urls[0] if urls else ""),
        "Organiser": first_match(text, [r"(?:organised|organized) by[:\s]+([^\n.]{3,120})", r"organiser[:\s]+([^\n.]{3,120})"]),
        "Host institution": first_match(text, [r"hosted by[:\s]+([^\n.]{3,120})", r"host institution[:\s]+([^\n.]{3,120})"]),
        "Location": first_match(text, [r"location[:\s]+([^\n.]{3,120})", r"venue[:\s]+([^\n.]{3,120})"]),
        "Online option": infer_online_option(text),
        "Event dates": normalize_event_range(text),
        "Abstract deadline": abstract_deadline,
        "Full paper deadline": full_paper_deadline,
        "Registration deadline": registration_deadline,
        "Notification date": notification_date,
        "Abstract word limit": extract_word_limit(text, "abstract"),
        "Paper word limit": extract_word_limit(text, "paper"),
        "Submission method": "email" if emails else ("portal" if submission_portal else ""),
        "Submission email": emails[0] if emails else "",
        "Submission portal": submission_portal,
        "Theme keywords": "\n".join(extract_keywords(text, profile_path)),
        "Project link": "unknown",
        "Priority": "unknown",
        "Status": "inbox",
        "Next action": "Review fit and decide go/no-go",
        "Next action due": abstract_deadline,
        "Raw CFP text": text,
        "Notes": "Parsed automatically from CFP text. Review all fields before opening the issue.",
        "Tracking options": "- [x] Add to active CFP dashboard\n- [x] Send deadline reminders later",
    }

    return fields


def render_issue_markdown(fields: dict[str, str]) -> str:
    lines: list[str] = []
    for field in ISSUE_FIELDS:
        value = fields.get(field, "")
        if field == "Raw CFP text" and value:
            value = "\n".join(f"    {line}" if line else "" for line in value.splitlines()).rstrip()
        else:
            value = value.strip()
        lines.extend([f"## {field}", value, ""])
    return "\n".join(lines).rstrip() + "\n"


def write_output(fields: dict[str, str], output_format: str, output: str) -> None:
    if output_format == "json":
        text = json.dumps(fields, ensure_ascii=False, indent=2) + "\n"
    else:
        text = render_issue_markdown(fields)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Parse pasted CFP text into an Add CFP issue draft.")
    parser.add_argument("--url", help="Fetch and parse a CFP page URL.")
    parser.add_argument("--file", help="Read CFP text from a local UTF-8 file.")
    parser.add_argument("--text", help="Parse CFP text passed directly on the command line.")
    parser.add_argument("--title-hint", default="", help="Optional title to use instead of inferring one.")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE), help="Profile JSON used for keyword extraction.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    parser.add_argument("--output", default="", help="Optional output file path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    text, source_url = read_inputs(args)
    if not text:
        raise SystemExit("No CFP text found. Provide --url, --file, --text, or CFP_RAW_TEXT.")

    fields = extract_fields(text, source_url, args.title_hint, Path(args.profile))
    write_output(fields, args.format, args.output)


if __name__ == "__main__":
    main()
