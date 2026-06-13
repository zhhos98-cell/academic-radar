import os, re, html, json, smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

import feedparser
import requests

STATE_FILE = "black_studies_sent.json"
MAX_ITEMS = 10
RSS_MAX_AGE_DAYS = 60
BSKY_MAX_AGE_DAYS = 21

RSS_FEEDS = [
    "https://networks.h-net.org/node/73374/announcements/feed",
    "https://www.aaihs.org/feed/",
    "https://asalh.org/feed/",
]

BSKY_QUERIES = [
    '"call for papers" "Black Studies"',
    '"cfp" "Black Studies"',
    '"special issue" "Black Studies"',
    '"call for papers" "African American history"',
    '"special issue" "African American history"',
    '"call for papers" "Black feminism"',
    '"special issue" "Black feminism"',
    '"call for papers" "Black women"',
    '"special issue" "Black women"',
    '"call for papers" "Black Power"',
    '"special issue" "Black Power"',
    '"call for papers" "Black Panther Party"',
    '"special issue" "Black Panther Party"',
    '"call for papers" "civil rights movement"',
    '"special issue" "civil rights movement"',
    '"fellowship" "Black Studies"',
    '"grant" "African American history"',
]

EVENT_TERMS = [
    "call for papers", "cfp", "call for chapters",
    "special issue", "edited collection", "conference proposal",
    "grant", "fellowship",
]

CORE_TERMS = [
    "black studies", "african american history", "african american",
    "black feminism", "black women", "black power",
    "black panther party", "civil rights movement",
    "black radicalism", "african diaspora", "race and resistance",
    "black freedom struggle", "black liberation",
]

NEGATIVE_TERMS = [
    "breaking news", "election", "campaign", "op-ed", "opinion",
    "podcast", "book review", "music", "celebrity", "sports",
    "police shooting", "live update",
]


def load_config():
    path = os.environ.get("BLACK_STUDIES_RADAR_CONFIG", "config/profiles/black_studies.json")
    if not path or not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_config(config):
    global STATE_FILE, MAX_ITEMS, RSS_MAX_AGE_DAYS, BSKY_MAX_AGE_DAYS
    global RSS_FEEDS, BSKY_QUERIES, EVENT_TERMS, CORE_TERMS, NEGATIVE_TERMS

    files = config.get("files", {})
    settings = config.get("settings", {})
    rss = config.get("rss", {})
    bluesky = config.get("bluesky", {})
    scoring = config.get("scoring", {})

    STATE_FILE = files.get("state", STATE_FILE)
    MAX_ITEMS = int(settings.get("max_items", MAX_ITEMS))
    RSS_MAX_AGE_DAYS = int(settings.get("rss_max_age_days", RSS_MAX_AGE_DAYS))
    BSKY_MAX_AGE_DAYS = int(settings.get("bsky_max_age_days", BSKY_MAX_AGE_DAYS))

    RSS_FEEDS = rss.get("feeds", RSS_FEEDS)
    BSKY_QUERIES = bluesky.get("queries", BSKY_QUERIES)
    EVENT_TERMS = scoring.get("event_terms", EVENT_TERMS)
    CORE_TERMS = scoring.get("core_terms", CORE_TERMS)
    NEGATIVE_TERMS = scoring.get("negative_terms", NEGATIVE_TERMS)


apply_config(load_config())


def clean(s):
    if not s:
        return ""
    s = html.unescape(str(s))
    s = re.sub(r"<.*?>", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def score(text):
    t = text.lower()
    if any(x in t for x in NEGATIVE_TERMS):
        return 0
    event = sum(4 for x in EVENT_TERMS if x in t)
    core = sum(3 for x in CORE_TERMS if x in t)
    if event == 0 or core == 0:
        return 0
    return event + core


def classify(text):
    t = text.lower()
    if "special issue" in t:
        return "Special Issues", "专刊"
    if any(x in t for x in ["grant", "fellowship"]):
        return "Grants / Fellowships", "资助"
    return "CFP / Calls", "征稿"


def parse_rss_date(entry):
    for key in ["published_parsed", "updated_parsed"]:
        value = entry.get(key)
        if value:
            return datetime(*value[:6], tzinfo=timezone.utc)
    return None


def too_old(dt, days):
    if not dt:
        return False
    return dt < datetime.now(timezone.utc) - timedelta(days=days)


def bsky_link(post):
    uri = post.get("uri", "")
    author = post.get("author", {}).get("handle", "")
    if not uri or not author:
        return ""
    return f"https://bsky.app/profile/{author}/post/{uri.split('/')[-1]}"


def bsky_date(post):
    created = post.get("record", {}).get("createdAt")
    if not created:
        return None
    try:
        return datetime.fromisoformat(created.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def make_item(title, link, summary, source):
    title, summary = clean(title), clean(summary)
    text = f"{title} {summary}"
    s = score(text)
    if s <= 0:
        return None
    cat, zh = classify(text)
    return {
        "score": s,
        "title": title[:220],
        "summary": summary[:520],
        "link": link,
        "source": source,
        "category": cat,
        "zh": zh,
    }


def fetch_rss():
    items = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:20]:
                dt = parse_rss_date(e)
                if too_old(dt, RSS_MAX_AGE_DAYS):
                    continue
                item = make_item(
                    e.get("title", ""),
                    e.get("link", ""),
                    e.get("summary", "") or e.get("description", ""),
                    f"RSS · {feed.feed.get('title', url)}",
                )
                if item:
                    items.append(item)
        except Exception as ex:
            print(f"[RSS ERROR] {url}: {ex}")
    return items


def fetch_bsky():
    items = []
    for q in BSKY_QUERIES:
        try:
            r = requests.get(
                "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
                params={"q": q, "limit": 15},
                timeout=20,
            )
            if not r.ok:
                print(f"[BSKY ERROR] {q}: {r.status_code}")
                continue
            for p in r.json().get("posts", []):
                dt = bsky_date(p)
                if too_old(dt, BSKY_MAX_AGE_DAYS):
                    continue
                text = p.get("record", {}).get("text", "")
                item = make_item(text[:180], bsky_link(p), text, "Bluesky search")
                if item:
                    items.append(item)
        except Exception as ex:
            print(f"[BSKY ERROR] {q}: {ex}")
    return items


def load_seen():
    if not os.path.exists(STATE_FILE):
        return set()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f).get("seen_links", []))
    except Exception:
        return set()


def save_seen(items):
    seen = load_seen()
    for item in items:
        if item.get("link"):
            seen.add(item["link"])
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"updated_at": datetime.now(timezone.utc).isoformat(), "seen_links": list(seen)[-3000:]},
            f,
            indent=2,
            ensure_ascii=False,
        )


def dedupe(items):
    seen, out = set(), []
    for item in sorted(items, key=lambda x: x["score"], reverse=True):
        key = item["link"] or item["title"]
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def render(items):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not items:
        return "No new Black Studies CFP / special issue items found today ({}).".format(today)

    cats = ["CFP / Calls", "Special Issues", "Grants / Fellowships"]
    parts = [
        "<h2>Black Studies CFP Digest — {}</h2>".format(html.escape(today)),
        "<p>仅抓 CFP、special issue；grant/fellowship 作为次级信号。</p >",
    ]

    count = 0
    for cat in cats:
        cat_items = [x for x in items if x["category"] == cat]
        if not cat_items:
            continue

        parts.append("<h2>{}</h2>".format(html.escape(cat)))

        for item in cat_items:
            if count >= MAX_ITEMS:
                break

            count += 1

            title = html.escape(item.get("title", ""))
            zh = html.escape(item.get("zh", ""))
            source = html.escape(item.get("source", ""))
            score = item.get("score", "")
            summary = html.escape(item.get("summary", ""))
            link = html.escape(item.get("link", ""))

            parts.append(
                "<div style='margin-bottom:18px;'>"
                "<h3>[{}] {}</h3>"
                "<p><b>Source:</b> {} · <b>Score:</b> {}</p >"
                "<p>{}</p >"
                "<p><a href='{}'>{}</a ></p >"
                "</div>".format(zh, title, source, score, summary, link, link)
            )

        if count >= MAX_ITEMS:
            break

    return "\n".join(parts)


def send_email(items):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    body = render(items)
    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = f"Black Studies CFP Digest — {today}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["TO_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(msg)


if __name__ == "__main__":
    items = dedupe(fetch_rss() + fetch_bsky())
    seen = load_seen()
    new_items = [x for x in items if x.get("link") not in seen]

    print(f"Matched items: {len(items)}")
    print(f"New items: {len(new_items)}")

    send_email(new_items[:MAX_ITEMS])
    save_seen(items)
