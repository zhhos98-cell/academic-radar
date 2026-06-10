import os, re, smtplib, html
from email.mime.text import MIMEText
from datetime import datetime, timezone
import feedparser
import requests

RSS_FEEDS = [
    "https://networks.h-net.org/node/73374/announcements/feed",
]

BLUESKY_QUERIES = [
    '"call for papers" "history of science"',
    'cfp "history of knowledge"',
    '"new book" "book history"',
    '"special issue" "material culture"',
    '"fellowship" "history of science"',
]

KEYWORDS = [
    "call for papers", "cfp", "call for chapters", "special issue",
    "new book", "forthcoming", "review copy", "book launch",
    "history of science", "history of knowledge", "book history",
    "material culture", "eighteenth century", "romanticism",
    "archive", "fellowship", "workshop", "conference",
]

def score(text):
    t = text.lower()
    return sum(1 for k in KEYWORDS if k in t)

def fetch_rss():
    items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries[:30]:
            title = e.get("title", "")
            link = e.get("link", "")
            summary = re.sub("<.*?>", "", e.get("summary", ""))[:700]
            s = score(title + " " + summary)
            if s:
                items.append((s, title, link, summary, "RSS"))
    return items

def fetch_bluesky():
    items = []
    for q in BLUESKY_QUERIES:
        r = requests.get(
            "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
            params={"q": q, "limit": 25},
            timeout=20,
        )
        if r.ok:
            for p in r.json().get("posts", []):
                text = p.get("record", {}).get("text", "")
                uri = p.get("uri", "")
                author = p.get("author", {}).get("handle", "")
                link = f"https://bsky.app/profile/{author}/post/{uri.split('/')[-1]}"
                s = score(text)
                if s:
                    items.append((s, text[:140], link, text[:700], "Bluesky"))
    return items

def send_email(items):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows, seen = [], set()

    for s, title, link, summary, source in sorted(items, reverse=True):
        key = link or title
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            f"<h3>[{html.escape(source)}] {html.escape(title)}</h3>"
            f"<p>{html.escape(summary)}</p>"
            f"<p><a href='{html.escape(link)}'>{html.escape(link)}</a></p>"
        )

    body = "<br>".join(rows[:25]) if rows else f"No relevant items found today ({today})."

    msg = MIMEText(body, "html", "utf-8")
    msg["Subject"] = f"Daily Academic Radar — {today}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["TO_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        s.send_message(msg)

if __name__ == "__main__":
    send_email(fetch_rss() + fetch_bluesky())
