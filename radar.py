import argparse
import html
import json
import os
import re
import smtplib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime

DEFAULT_CONFIG = "config/profiles/hps.json"

OPML_FILE = "feedly_active.opml"
BSKY_WATCHLIST_FILE = "bsky_watchlist_core.txt"
STATE_FILE = "sent_items.json"

RSS_MAX_AGE_DAYS = 35
BSKY_MAX_AGE_DAYS = 10
MAX_EMAIL_ITEMS = 20
MAX_RSS_PER_FEED = 12
MAX_BSKY_PER_QUERY = 15
MAX_BSKY_PER_ACCOUNT = 8

EVENT_TERMS = [
    "call for papers",
    "cfp",
    "call for chapters",
    "special issue",
    "conference",
    "workshop",
    "symposium",
    "seminar",
    "new book",
    "forthcoming",
    "book launch",
    "review copy",
    "fellowship",
    "grant",
    "bursary",
    "studentship",
    "research assistant",
    "ra position",
    "library assistant",
    "assistant librarian",
    "archivist",
    "curator",
    "deadline",
    "open access",
    "new issue",
]

CORE_FIELD_TERMS = [
    "history of science",
    "histstm",
    "hstm",
    "history of knowledge",
    "history of humanities",
    "book history",
    "material culture",
    "intellectual history",
    "history of medicine",
    "history of technology",
    "philosophy of science",
    "hps",
    "sts",
    "early modern",
    "eighteenth century",
    "18th century",
    "manuscript",
    "bibliography",
    "rare books",
    "scientific instrument",
    "natural history",
]

PRESTIGE_OR_CORE_SOURCES = [
    "bshs",
    "hstm",
    "hopos",
    "isis",
    "history of science",
    "jhi",
    "journal of the history of ideas",
    "isih",
    "history of humanities",
    "mpi",
    "mpiwg",
    "royal historical society",
    "royal society",
    "royal astronomical society",
    "society for renaissance studies",
    "bsecs",
    "bars",
    "warburg",
    "whipple",
    "cambridge",
    "oxford",
    "bodleian",
    "british library",
    "wellcome",
    "ihr",
    "crassh",
]

NEGATIVE_TERMS = [
    "contemporary",
    "postdoc",
    "postdoctoral",
    "lecturer",
    "assistant professor",
    "associate professor",
    "professor",
    "tenure",
    "tenure-track",
    "faculty position",
    "undergraduate",
    "high school",
    "marketing",
    "seo",
]

BLUESKY_QUERIES = [
    '"call for papers" "history of science"',
    'cfp "history of science"',
    '"special issue" "history of science"',
    '"new book" "history of science"',
    '"call for papers" "history of knowledge"',
    '"special issue" "history of knowledge"',
    '"new book" "history of knowledge"',
    '"call for papers" "book history"',
    '"special issue" "book history"',
    '"new book" "book history"',
    '"call for papers" "history of humanities"',
    '"special issue" "history of humanities"',
    '"fellowship" "history of science"',
    '"bursary" "history of science"',
    '"scientific instruments" "call for papers"',
    '"premodern mediterranean" "history of medicine"',
    '"research assistant" "history of science"',
    '"archivist" "history of science"',
    '"curator" "history of science"',
]


def load_config(path=None):
    path = path or os.environ.get("RADAR_CONFIG", DEFAULT_CONFIG)
    if not path or not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_config(config):
    global OPML_FILE, BSKY_WATCHLIST_FILE, STATE_FILE
    global RSS_MAX_AGE_DAYS, BSKY_MAX_AGE_DAYS
    global MAX_EMAIL_ITEMS, MAX_RSS_PER_FEED, MAX_BSKY_PER_QUERY, MAX_BSKY_PER_ACCOUNT
    global EVENT_TERMS, CORE_FIELD_TERMS, PRESTIGE_OR_CORE_SOURCES, NEGATIVE_TERMS, BLUESKY_QUERIES

    files = config.get("files", {})
    settings = config.get("settings", {})
    scoring = config.get("scoring", {})
    bluesky = config.get("bluesky", {})

    OPML_FILE = files.get("opml", OPML_FILE)
    BSKY_WATCHLIST_FILE = files.get("bsky_watchlist", BSKY_WATCHLIST_FILE)
    STATE_FILE = files.get("state", STATE_FILE)

    RSS_MAX_AGE_DAYS = int(settings.get("rss_max_age_days", RSS_MAX_AGE_DAYS))
    BSKY_MAX_AGE_DAYS = int(settings.get("bsky_max_age_days", BSKY_MAX_AGE_DAYS))
    MAX_EMAIL_ITEMS = int(settings.get("max_email_items", MAX_EMAIL_ITEMS))
    MAX_RSS_PER_FEED = int(settings.get("max_rss_per_feed", MAX_RSS_PER_FEED))
    MAX_BSKY_PER_QUERY = int(settings.get("max_bsky_per_query", MAX_BSKY_PER_QUERY))
    MAX_BSKY_PER_ACCOUNT = int(settings.get("max_bsky_per_account", MAX_BSKY_PER_ACCOUNT))

    EVENT_TERMS = scoring.get("event_terms", EVENT_TERMS)
    CORE_FIELD_TERMS = scoring.get("core_field_terms", CORE_FIELD_TERMS)
    PRESTIGE_OR_CORE_SOURCES = scoring.get("prestige_or_core_sources", PRESTIGE_OR_CORE_SOURCES)
    NEGATIVE_TERMS = scoring.get("negative_terms", NEGATIVE_TERMS)
    BLUESKY_QUERIES = bluesky.get("queries", BLUESKY_QUERIES)


def apply_cli_overrides(args):
    global OPML_FILE, BSKY_WATCHLIST_FILE, STATE_FILE, MAX_EMAIL_ITEMS

    if args.opml:
        OPML_FILE = args.opml
    if args.watchlist:
        BSKY_WATCHLIST_FILE = args.watchlist
    if args.state:
        STATE_FILE = args.state
    if args.max_items is not None:
        MAX_EMAIL_ITEMS = args.max_items


def clean_text(value):
    if not value:
        return ""
    value = html.unescape(str(value))
    value = re.sub(r"<.*?>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_feed_date(entry):
    for key in ["published", "updated", "created"]:
        value = entry.get(key)
        if not value:
            continue
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            pass
    return None


def too_old(dt, max_age_days):
    if not dt:
        return False
    return dt < datetime.now(timezone.utc) - timedelta(days=max_age_days)


def load_opml_feeds(path=None):
    path = path or OPML_FILE
    if not os.path.exists(path):
        print(f"[CONFIG] OPML file not found: {path}")
        return []

    root = ET.parse(path).getroot()
    feeds = []
    for outline in root.iter("outline"):
        url = outline.attrib.get("xmlUrl") or outline.attrib.get("xmlurl")
        title = outline.attrib.get("title") or outline.attrib.get("text") or url
        if url:
            feeds.append((title, url))

    seen = set()
    deduped = []
    for title, url in feeds:
        if url not in seen:
            seen.add(url)
            deduped.append((title, url))
    return deduped


def load_bsky_watchlist(path=None):
    path = path or BSKY_WATCHLIST_FILE
    if not os.path.exists(path):
        print(f"[CONFIG] Bluesky watchlist not found: {path}")
        return []

    handles = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            handle = line.split("\t")[0].strip()
            if handle and "." in handle:
                handles.append(handle)
    return sorted(set(handles))


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


def score(text):
    text = text.lower()

    if any(term in text for term in NEGATIVE_TERMS):
        return 0

    event_score = sum(3 for term in EVENT_TERMS if term in text)
    field_score = sum(2 for term in CORE_FIELD_TERMS if term in text)
    core_source_bonus = 4 if any(term in text for term in PRESTIGE_OR_CORE_SOURCES) else 0
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


def make_item(title, link, summary, source, source_name="", dt=None):
    full_text = f"{title} {summary} {source_name}"
    item_score = score(full_text)
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


def fetch_rss():
    import feedparser

    items = []
    for feed_title, url in load_opml_feeds():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:MAX_RSS_PER_FEED]:
                entry_dt = parse_feed_date(entry)
                if too_old(entry_dt, RSS_MAX_AGE_DAYS):
                    continue

                item = make_item(
                    entry.get("title", ""),
                    entry.get("link", ""),
                    entry.get("summary", "") or entry.get("description", ""),
                    "RSS",
                    feed_title,
                    entry_dt,
                )
                if item:
                    items.append(item)
        except Exception as exc:
            print(f"[RSS ERROR] {url}: {exc}")
    return items


def bsky_post_link(post):
    uri = post.get("uri", "")
    author = post.get("author", {}).get("handle", "")
    if not uri or not author:
        return ""
    return f"https://bsky.app/profile/{author}/post/{uri.split('/')[-1]}"


def bsky_created_at(post):
    created_at = post.get("record", {}).get("createdAt")
    if not created_at:
        return None
    try:
        return datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def fetch_bluesky_search():
    import requests

    items = []
    for query in BLUESKY_QUERIES:
        try:
            response = requests.get(
                "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
                params={"q": query, "limit": MAX_BSKY_PER_QUERY},
                timeout=20,
            )
            if not response.ok:
                print(f"[BSKY SEARCH ERROR] {query}: {response.status_code}")
                continue

            for post in response.json().get("posts", []):
                dt = bsky_created_at(post)
                if too_old(dt, BSKY_MAX_AGE_DAYS):
                    continue

                text = post.get("record", {}).get("text", "")
                item = make_item(
                    text[:180],
                    bsky_post_link(post),
                    text,
                    "Bluesky search",
                    post.get("author", {}).get("handle", ""),
                    dt,
                )
                if item:
                    items.append(item)
        except Exception as exc:
            print(f"[BSKY SEARCH ERROR] {query}: {exc}")
    return items


def fetch_bluesky_watchlist():
    import requests

    items = []
    for handle in load_bsky_watchlist():
        try:
            response = requests.get(
                "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed",
                params={"actor": handle, "limit": MAX_BSKY_PER_ACCOUNT},
                timeout=20,
            )
            if not response.ok:
                print(f"[BSKY WATCH ERROR] {handle}: {response.status_code}")
                continue

            for row in response.json().get("feed", []):
                post = row.get("post", {})
                dt = bsky_created_at(post)
                if too_old(dt, BSKY_MAX_AGE_DAYS):
                    continue

                text = post.get("record", {}).get("text", "")
                item = make_item(text[:180], bsky_post_link(post), text, "Bluesky watchlist", handle, dt)
                if item:
                    items.append(item)
        except Exception as exc:
            print(f"[BSKY WATCH ERROR] {handle}: {exc}")
    return items


def dedupe(items):
    seen = set()
    output = []
    for item in sorted(items, key=lambda row: row["score"], reverse=True):
        key = item["link"] or item["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def load_seen_links():
    if not os.path.exists(STATE_FILE):
        return set()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen_links", []))
    except Exception:
        return set()


def filter_new_items(items):
    seen = load_seen_links()
    return [item for item in items if item.get("link") not in seen]


def save_seen_links(items):
    seen = load_seen_links()
    for item in items:
        link = item.get("link")
        if link:
            seen.add(link)

    state_dir = os.path.dirname(STATE_FILE)
    if state_dir:
        os.makedirs(state_dir, exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "seen_links": list(seen)[-5000:],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def render_details(details):
    rows = []
    if details.get("deadline"):
        rows.append(f"<b>Deadline:</b> {html.escape(details['deadline'])}")
    if details.get("event_date"):
        rows.append(f"<b>Date:</b> {html.escape(details['event_date'])}")
    if details.get("location"):
        rows.append(f"<b>Place:</b> {html.escape(details['location'])}")
    if details.get("format"):
        rows.append(f"<b>Format:</b> {html.escape(details['format'])}")
    if details.get("funding"):
        rows.append(f"<b>Funding:</b> {html.escape(details['funding'])}")

    if not rows:
        return ""
    return "<p>" + " | ".join(rows) + "</p>"


def render_email(items):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not items:
        return f"No new relevant items found today ({today})."

    categories = [
        "CFP / Calls",
        "Special Issues / Journals",
        "New Books",
        "Fellowships / Grants",
        "RA / Library / Archive Jobs",
        "Events / Seminars",
        "Other Signals",
    ]

    parts = [
        f"<h2>Daily Academic Radar - {html.escape(today)}</h2>",
        "<p>Only new links are shown. Scoring and categories are rule-based.</p>",
    ]
    count = 0

    for category in categories:
        category_items = [item for item in items if item["category"] == category]
        if not category_items:
            continue

        parts.append(f"<h2>{html.escape(category)}</h2>")
        for item in category_items:
            if count >= MAX_EMAIL_ITEMS:
                break

            count += 1
            source_line = item["source"]
            if item["source_name"]:
                source_line += f" | {item['source_name']}"

            parts.append(
                f"<div style='margin-bottom:18px;'>"
                f"<h3>[{html.escape(item['tag'])}] {html.escape(item['title'])}</h3>"
                f"{render_details(item['details'])}"
                f"<p><b>Source:</b> {html.escape(source_line)} | "
                f"<b>Score:</b> {item['score']}</p>"
                f"<p>{html.escape(item['summary'])}</p>"
                f"<p><a href='{html.escape(item['link'])}'>{html.escape(item['link'])}</a></p>"
                f"</div>"
            )

        if count >= MAX_EMAIL_ITEMS:
            break

    return "\n".join(parts)


def send_email(items):
    missing = [key for key in ["SMTP_USER", "SMTP_PASS", "TO_EMAIL"] if not os.environ.get(key)]
    if missing:
        raise RuntimeError(f"Missing email environment variables: {', '.join(missing)}")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg = MIMEText(render_email(items), "html", "utf-8")
    msg["Subject"] = f"Daily Academic Radar - {today}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["TO_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        smtp.send_message(msg)


def write_output(path, body):
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


def serializable_items(items):
    output = []
    for item in items:
        row = dict(item)
        if row.get("dt"):
            row["dt"] = row["dt"].isoformat()
        output.append(row)
    return output


def collect_items(skip_rss=False, skip_bsky=False):
    rss_items = [] if skip_rss else fetch_rss()
    bsky_search_items = [] if skip_bsky else fetch_bluesky_search()
    bsky_watch_items = [] if skip_bsky else fetch_bluesky_watchlist()

    print(f"RSS items: {len(rss_items)}")
    print(f"Bluesky search items: {len(bsky_search_items)}")
    print(f"Bluesky watchlist items: {len(bsky_watch_items)}")

    items = dedupe(rss_items + bsky_search_items + bsky_watch_items)
    print(f"Deduped items: {len(items)}")
    return items


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Run the Academic Radar digest.")
    parser.add_argument("--config", default=os.environ.get("RADAR_CONFIG", DEFAULT_CONFIG))
    parser.add_argument("--opml", help="Override the OPML path from the profile.")
    parser.add_argument("--watchlist", help="Override the Bluesky watchlist path from the profile.")
    parser.add_argument("--state", help="Override the seen-link state file path from the profile.")
    parser.add_argument("--max-items", type=int, help="Override max email/output items.")
    parser.add_argument("--output-html", help="Write rendered digest HTML to this path.")
    parser.add_argument("--output-json", help="Write selected items as JSON to this path.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and render without sending email or writing state.")
    parser.add_argument("--no-email", action="store_true", help="Do not send email.")
    parser.add_argument("--no-state", action="store_true", help="Do not write seen-link state.")
    parser.add_argument("--include-seen", action="store_true", help="Render all matching items, including seen links.")
    parser.add_argument("--skip-rss", action="store_true", help="Skip RSS fetching.")
    parser.add_argument("--skip-bsky", action="store_true", help="Skip Bluesky fetching.")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    apply_config(load_config(args.config))
    apply_cli_overrides(args)

    items = collect_items(skip_rss=args.skip_rss, skip_bsky=args.skip_bsky)
    selected_items = items if args.include_seen else filter_new_items(items)
    digest_items = selected_items[:MAX_EMAIL_ITEMS]
    print(f"Rendered items: {len(digest_items)}")

    body = render_email(digest_items)

    if args.output_html:
        write_output(args.output_html, body)
        print(f"Wrote digest HTML: {args.output_html}")
    if args.output_json:
        write_output(args.output_json, json.dumps(serializable_items(digest_items), ensure_ascii=False, indent=2))
        print(f"Wrote digest JSON: {args.output_json}")

    if args.dry_run or args.no_email:
        print("Email skipped.")
    else:
        send_email(digest_items)
        print("Email sent.")

    if args.dry_run or args.no_state:
        print("State update skipped.")
    else:
        save_seen_links(items)
        print(f"State updated: {STATE_FILE}")


if __name__ == "__main__":
    main()
