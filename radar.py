import os
import re
import html
import smtplib
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from datetime import datetime, timezone

import feedparser
import requests


OPML_FILE = "feedly_active.opml"
BSKY_WATCHLIST_FILE = "bsky_watchlist_core.txt"

MAX_EMAIL_ITEMS = 35
MAX_RSS_PER_FEED = 15
MAX_BSKY_PER_QUERY = 20
MAX_BSKY_PER_ACCOUNT = 10


EVENT_TERMS = [
    "call for papers", "cfp", "call for chapters", "special issue",
    "conference", "workshop", "symposium", "seminar",
    "new book", "forthcoming", "book launch", "review copy",
    "fellowship", "grant", "bursary", "studentship", "postdoc",
    "archive", "archives", "digitisation", "digitization", "collection",
    "deadline", "open access", "new issue",
]

FIELD_TERMS = [
    "history of science", "histstm", "hstm", "history of knowledge",
    "book history", "material culture", "history of humanities",
    "early modern", "eighteenth century", "18th century", "c18",
    "romanticism", "manuscript", "archives", "intellectual history",
    "history of medicine", "history of technology", "philosophy of science",
    "hps", "sts", "bibliography", "rare books",
]

NEGATIVE_TERMS = [
    "crypto", "nft", "marketing", "seo", "undergraduate open day",
    "high school", "junior einsteins", "garden planner",
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
    '"call for papers" "early modern"',
    '"special issue" "early modern"',
    '"new book" "early modern"',
    '"call for papers" "eighteenth century"',
    '"special issue" "eighteenth century"',
    '"new book" "romanticism"',
    '"fellowship" "history of science"',
    '"archive" "history of science"',
]


def clean_text(s):
    if not s:
        return ""
    s = re.sub(r"<.*?>", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


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

    # 去重
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
    if any(x in t for x in ["fellowship", "grant", "bursary", "studentship", "postdoc"]):
        return "Fellowships / Grants / Jobs", "机会"
    if any(x in t for x in ["archive", "archives", "digitisation", "digitization", "collection", "library"]):
        return "Archives / Collections", "档案/馆藏"
    if any(x in t for x in ["conference", "workshop", "symposium", "seminar"]):
        return "Events / Seminars", "活动"
    return "Other Signals", "线索"


def score(text):
    t = text.lower()

    if any(x in t for x in NEGATIVE_TERMS):
        return 0

    event_score = sum(3 for k in EVENT_TERMS if k in t)
    field_score = sum(2 for k in FIELD_TERMS if k in t)

    # RSS 学会/期刊本身可能已很准，所以只要有事件词也保留
    return event_score + field_score


def make_item(title, link, summary, source, source_name=""):
    text = f"{title} {summary}"
    s = score(text)
    if s <= 0:
        return None

    category, zh_tag = classify(text)
    return {
        "score": s,
        "title": clean_text(title)[:220],
        "link": link,
        "summary": clean_text(summary)[:600],
        "source": source,
        "source_name": source_name,
        "category": category,
        "zh_tag": zh_tag,
    }


def fetch_rss():
    items = []
    feeds = load_opml_feeds()

    for feed_title, url in feeds:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:MAX_RSS_PER_FEED]:
                title = e.get("title", "")
                link = e.get("link", "")
                summary = e.get("summary", "") or e.get("description", "")
                item = make_item(title, link, summary, "RSS", feed_title)
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
                text = p.get("record", {}).get("text", "")
                author = p.get("author", {}).get("handle", "")
                link = bsky_post_link(p)
                item = make_item(text[:180], link, text, "Bluesky search", author)
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
                text = p.get("record", {}).get("text", "")
                link = bsky_post_link(p)
                item = make_item(text[:180], link, text, "Bluesky watchlist", handle)
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


def render_email(items):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not items:
        return f"No relevant items found today ({today})."

    categories = [
        "CFP / Calls",
        "Special Issues / Journals",
        "New Books",
        "Fellowships / Grants / Jobs",
        "Archives / Collections",
        "Events / Seminars",
        "Other Signals",
    ]

    parts = [
        f"<h2>Daily Academic Radar — {html.escape(today)}</h2>",
        "<p>中文标签是规则生成的快速提示，不是机器翻译。</p>",
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

    send_email(items)
