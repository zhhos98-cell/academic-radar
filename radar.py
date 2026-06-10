import os
import re
import html
import json
import smtplib
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

import feedparser
import requests


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
    "call for papers", "cfp", "call for chapters", "special issue",
    "conference", "workshop", "symposium", "seminar",
    "new book", "forthcoming", "book launch", "review copy",
    "fellowship", "grant", "bursary", "studentship",
    "research assistant", "ra position", "library assistant",
    "assistant librarian", "archivist", "curator",
    "archive", "archives", "digitisation", "digitization", "collection",
    "deadline", "open access", "new issue",
]

CORE_FIELD_TERMS = [
    "history of science", "histstm", "hstm", "history of knowledge",
    "history of humanities", "book history", "material culture",
    "intellectual history", "history of medicine", "history of technology",
    "philosophy of science", "hps", "sts",
    "early modern", "eighteenth century", "18th century", "c18",
    "romanticism", "manuscript", "archives", "archive", "bibliography",
    "rare books", "scientific instrument", "scientific instruments",
    "natural history", "premodern", "mediterranean",
]

PRESTIGE_OR_CORE_SOURCES = [
    "bshs", "hstm", "hopos", "isis", "history of science",
    "jhi", "journal of the history of ideas", "isih",
    "history of humanities", "mpi", "mpiwg",
    "royal historical society", "royal society", "royal astronomical society",
    "society for renaissance studies", "bsecs", "bars",
    "warburg", "whipple", "cambridge", "oxford", "bodleian",
    "british library", "wellcome", "ihr", "crassh",
]

NEGATIVE_TERMS = [
    "contemporary", "twentieth century", "21st century", "twenty-first century",
    "media studies", "global media", "digital governance", "algorithmic media",
    "artificial intelligence", "platform", "social media", "public discourse",
    "digital sovereignty", "policy", "governance", "sociology", "social scientists",
    "social science", "anthropological linguistics",

    "china", "chinese", "sinology", "sinological", "sino-",
    "east asia", "east asian", "asian studies", "asian humanities",
    "south asia", "south asian", "southeast asia", "southeast asian",
    "korea", "korean", "japan", "japanese", "confucian", "dao ",
    "pre-qin",

    "classics", "classical studies", "homer", "odyssey", "greco-roman",

    "american literature", "emerson", "thoreau", "joseph conrad",
    "popular fiction", "neo-victorian", "victorian publics",
    "postcolonial", "film and television", "popular culture",
    "modernist studies", "creative-critical",

    "postdoc", "postdoctoral", "lecturer", "assistant professor",
    "associate professor", "professor", "tenure", "tenure-track",
    "faculty position", "jobs for medievalists",

    "errant journal", "online conference", "samla",
    "undergraduate", "high school",

    "crypto", "nft", "marketing", "seo", "garden planner",
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
    '"archive" "history of science"',
    '"scientific instruments" "call for papers"',
    '"premodern mediterranean" "history of medicine"',
    '"research assistant" "history of science"',
    '"archivist" "history of science"',
    '"curator" "history of science"',
]


def clean_text(s):
    if not s:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r"<.*?>", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def parse_feed_date(entry):
    for key in ["published", "updated", "created"]:
        value = entry.get(key)
        if value:
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


def load_opml_feeds(path=OPML_FILE):
    if not os.path.exists(path):
        return []
    root = ET.parse(path).getroot()
    feeds = []
    for outline in root.iter("outline"):
        url = outline.attrib.get("xmlUrl") or outline.attrib.get("xmlurl")
        title = outline.attrib.get("title") or outline.attrib.get("text") or url
        if url:
            feeds.append((title, url))

    seen, out = set(), []
    for title, url in feeds:
        if url not in seen:
            seen.add(url)
            out.append((title, url))
    return out


def load_bsky_watchlist(path=BSKY_WATCHLIST_FILE):
    if not os.path.exists(path):
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
    t = text.lower()

    if any(x in t for x in ["call for papers", "cfp", "call for chapters"]):
        return "CFP / Calls", "征稿"

    if any(x in t for x in ["special issue", "new issue"]):
        return "Special Issues / Journals", "专刊/期刊"

    if any(x in t for x in ["new book", "forthcoming", "book launch", "review copy"]):
        return "New Books", "新书"

    if any(x in t for x in [
        "research assistant", "ra position", "library assistant",
        "assistant librarian", "archivist", "curator"
    ]):
        return "RA / Library / Archive Jobs", "职位"

    if any(x in t for x in ["fellowship", "grant", "bursary", "studentship"]):
        return "Fellowships / Grants", "资助"

    if any(x in t for x in [
        "archive", "archives", "digitisation", "digitization",
        "collection", "library"
    ]):
        return "Archives / Collections", "档案/馆藏"

    if any(x in t for x in ["conference", "workshop", "symposium", "seminar"]):
        return "Events / Seminars", "活动"

    return "Other Signals", "线索"


def score(text):
    t = text.lower()

    if any(x in t for x in NEGATIVE_TERMS):
        return 0

    event_score = sum(3 for k in EVENT_TERMS if k in t)
    field_score = sum(2 for k in CORE_FIELD_TERMS if k in t)
    core_source_bonus = 4 if any(k in t for k in PRESTIGE_OR_CORE_SOURCES) else 0
    raw = event_score + field_score + core_source_bonus

    has_event = event_score > 0
    has_core_field = field_score > 0
    has_core_source = core_source_bonus > 0

    if has_event and not has_core_field and not has_core_source:
        return 0

    if any(x in t for x in ["call for papers", "cfp", "call for chapters"]) and raw < 9:
        return 0

    if any(x in t for x in ["fellowship", "grant", "bursary", "studentship"]) and raw < 10:
        return 0

    if any(x in t for x in [
        "research assistant", "library assistant",
        "assistant librarian", "archivist", "curator"
    ]) and raw < 10:
        return 0

    return raw


def extract_dates_and_details(text):
    t = clean_text(text)
    lower = t.lower()

    deadline = ""
    event_date = ""
    location = ""
    format_hint = ""
    funding = ""

    deadline_patterns = [
        r"deadline(?: for submissions)?[:\s]+([^.;\n]{3,80})",
        r"submission deadline[:\s]+([^.;\n]{3,80})",
        r"abstracts? (?:due|by)[:\s]+([^.;\n]{3,80})",
        r"deadline is[:\s]+([^.;\n]{3,80})",
        r"deadline to submit [^:]{0,40}[:\s]+([^.;\n]{3,80})",
        r"by ([0-9]{1,2}(?:st|nd|rd|th)? [A-Z][a-z]+ 20[0-9]{2})",
        r"by ([A-Z][a-z]+ [0-9]{1,2}, 20[0-9]{2})",
    ]
    for pat in deadline_patterns:
        m = re.search(pat, t, flags=re.IGNORECASE)
        if m:
            deadline = m.group(1).strip()
            break

    event_patterns = [
        r"([0-9]{1,2}[–-][0-9]{1,2} [A-Z][a-z]+ 20[0-9]{2})",
        r"([0-9]{1,2} [A-Z][a-z]+ 20[0-9]{2})",
        r"([A-Z][a-z]+ [0-9]{1,2}[–-][0-9]{1,2}, 20[0-9]{2})",
        r"([A-Z][a-z]+ [0-9]{1,2}, 20[0-9]{2})",
    ]
    for pat in event_patterns:
        m = re.search(pat, t)
        if m:
            event_date = m.group(1).strip()
            break

    location_patterns = [
        r"(?:venue:|hosted by|held at)\s+([^.;\n]{3,90})",
        r"([A-Z][A-Za-z .'-]+ University(?:, [A-Z][A-Za-z .'-]+)?)",
        r"(University of [A-Z][A-Za-z .'-]+)",
    ]
    for pat in location_patterns:
        m = re.search(pat, t, flags=re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if len(candidate.split()) <= 14:
                location = candidate
                break

    if "hybrid" in lower:
        format_hint = "hybrid"
    elif "online" in lower or "zoom" in lower or "virtual" in lower:
        format_hint = "online"
    elif "in person" in lower or "in-person" in lower:
        format_hint = "in-person"

    funding_terms = [
        "bursary", "travel support", "travel grant",
        "stipend", "scholarship", "fee waiver", "funding available"
    ]
    if any(x in lower for x in funding_terms):
        for term in funding_terms:
            idx = lower.find(term)
            if idx != -1:
                start = max(0, idx - 70)
                end = min(len(t), idx + 160)
                funding = t[start:end].strip()
                break

    return {
        "deadline": deadline[:100],
        "event_date": event_date[:100],
        "location": location[:120],
        "format": format_hint,
        "funding": funding[:240],
    }


def make_item(title, link, summary, source, source_name="", dt=None):
    full_text = f"{title} {summary} {source_name}"
    s = score(full_text)
    if s <= 0:
        return None

    category, zh_tag = classify(full_text)
    details = extract_dates_and_details(full_text)

    return {
        "score": s,
        "title": clean_text(title)[:220],
        "link": link,
        "summary": clean_text(summary)[:520],
        "source": source,
        "source_name": source_name,
        "category": category,
        "zh_tag": zh_tag,
        "details": details,
        "dt": dt,
    }


def fetch_rss():
    items = []
    feeds = load_opml_feeds()

    for feed_title, url in feeds:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:MAX_RSS_PER_FEED]:
                entry_dt = parse_feed_date(e)
                if too_old(entry_dt, RSS_MAX_AGE_DAYS):
                    continue

                title = e.get("title", "")
                link = e.get("link", "")
                summary = e.get("summary", "") or e.get("description", "")
                item = make_item(title, link, summary, "RSS", feed_title, entry_dt)
                if item:
                    items.append(item)
        except Exception as ex:
            print(f"[RSS ERROR] {url}: {ex}")

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
    items = []

    for q in BLUESKY_QUERIES:
        try:
            r = requests.get(
                "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
                params={"q": q, "limit": MAX_BSKY_PER_QUERY},
                timeout=20,
            )
            if not r.ok:
                print(f"[BSKY SEARCH ERROR] {q}: {r.status_code}")
                continue

            for p in r.json().get("posts", []):
                dt = bsky_created_at(p)
                if too_old(dt, BSKY_MAX_AGE_DAYS):
                    continue

                text = p.get("record", {}).get("text", "")
                author = p.get("author", {}).get("handle", "")
                link = bsky_post_link(p)
                item = make_item(text[:180], link, text, "Bluesky search", author, dt)
                if item:
                    items.append(item)
        except Exception as ex:
            print(f"[BSKY SEARCH ERROR] {q}: {ex}")

    return items


def fetch_bluesky_watchlist():
    items = []
    handles = load_bsky_watchlist()

    for handle in handles:
        try:
            r = requests.get(
                "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed",
                params={"actor": handle, "limit": MAX_BSKY_PER_ACCOUNT},
                timeout=20,
            )
            if not r.ok:
                print(f"[BSKY WATCH ERROR] {handle}: {r.status_code}")
                continue

            for row in r.json().get("feed", []):
                p = row.get("post", {})
                dt = bsky_created_at(p)
                if too_old(dt, BSKY_MAX_AGE_DAYS):
                    continue

                text = p.get("record", {}).get("text", "")
                link = bsky_post_link(p)
                item = make_item(text[:180], link, text, "Bluesky watchlist", handle, dt)
                if item:
                    items.append(item)
        except Exception as ex:
            print(f"[BSKY WATCH ERROR] {handle}: {ex}")

    return items


def dedupe(items):
    seen = set()
    out = []

    for item in sorted(items, key=lambda x: x["score"], reverse=True):
        key = item["link"] or item["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)

    return out


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

    seen_list = list(seen)[-5000:]

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "seen_links": seen_list,
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

    return "<p>" + " · ".join(rows) + "</p>"


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
        "Archives / Collections",
        "Events / Seminars",
        "Other Signals",
    ]

    parts = [
        f"<h2>Daily Academic Radar — {html.escape(today)}</h2>",
        "<p>仅显示新链接；过滤较严格；中文标签为规则提示，不是机器翻译。</p>",
    ]

    count = 0

    for cat in categories:
        cat_items = [x for x in items if x["category"] == cat]
        if not cat_items:
            continue

        parts.append(f"<h2>{html.escape(cat)}</h2>")

        for item in cat_items:
            if count >= MAX_EMAIL_ITEMS:
                break

            count += 1

            source_line = item["source"]
            if item["source_name"]:
                source_line += f" · {item['source_name']}"

            parts.append(
                f"<div style='margin-bottom:18px;'>"
                f"<h3>[{html.escape(item['zh_tag'])}] {html.escape(item['title'])}</h3>"
                f"{render_details(item['details'])}"
                f"<p><b>Source:</b> {html.escape(source_line)} · "
                f"<b>Score:</b> {item['score']}</p>"
                f"<p>{html.escape(item['summary'])}</p>"
                f"<p><a href='{html.escape(item['link'])}'>{html.escape(item['link'])}</a></p>"
                f"</div>"
            )

        if count >= MAX_EMAIL_ITEMS:
            break

    return "\n".join(parts)


def send_email(items):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = render_email(items)

    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = f"Daily Academic Radar — {today}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["TO_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(msg)


if __name__ == "__main__":
    rss_items = fetch_rss()
    bsky_search_items = fetch_bluesky_search()
    bsky_watch_items = fetch_bluesky_watchlist()

    print(f"RSS items: {len(rss_items)}")
    print(f"Bluesky search items: {len(bsky_search_items)}")
    print(f"Bluesky watchlist items: {len(bsky_watch_items)}")

    items = dedupe(rss_items + bsky_search_items + bsky_watch_items)
    print(f"Deduped items: {len(items)}")

    new_items = filter_new_items(items)
    print(f"New items: {len(new_items)}")

    send_email(new_items[:MAX_EMAIL_ITEMS])
    save_seen_links(items)
