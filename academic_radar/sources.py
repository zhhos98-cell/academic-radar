import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from .scoring import make_item
from .text import parse_feed_date, too_old


def load_opml_feeds(path):
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


def load_bsky_watchlist(path):
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


def fetch_rss(config):
    import feedparser

    items = []
    for feed_title, url in load_opml_feeds(config.opml_file):
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[: config.max_rss_per_feed]:
                entry_dt = parse_feed_date(entry)
                if too_old(entry_dt, config.rss_max_age_days):
                    continue

                item = make_item(
                    entry.get("title", ""),
                    entry.get("link", ""),
                    entry.get("summary", "") or entry.get("description", ""),
                    "RSS",
                    config,
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


def fetch_bluesky_search(config):
    import requests

    items = []
    for query in config.bluesky_queries:
        try:
            response = requests.get(
                "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts",
                params={"q": query, "limit": config.max_bsky_per_query},
                timeout=20,
            )
            if not response.ok:
                print(f"[BSKY SEARCH ERROR] {query}: {response.status_code}")
                continue

            for post in response.json().get("posts", []):
                dt = bsky_created_at(post)
                if too_old(dt, config.bsky_max_age_days):
                    continue

                text = post.get("record", {}).get("text", "")
                item = make_item(
                    text[:180],
                    bsky_post_link(post),
                    text,
                    "Bluesky search",
                    config,
                    post.get("author", {}).get("handle", ""),
                    dt,
                )
                if item:
                    items.append(item)
        except Exception as exc:
            print(f"[BSKY SEARCH ERROR] {query}: {exc}")
    return items


def fetch_bluesky_watchlist(config):
    import requests

    items = []
    for handle in load_bsky_watchlist(config.bsky_watchlist_file):
        try:
            response = requests.get(
                "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed",
                params={"actor": handle, "limit": config.max_bsky_per_account},
                timeout=20,
            )
            if not response.ok:
                print(f"[BSKY WATCH ERROR] {handle}: {response.status_code}")
                continue

            for row in response.json().get("feed", []):
                post = row.get("post", {})
                dt = bsky_created_at(post)
                if too_old(dt, config.bsky_max_age_days):
                    continue

                text = post.get("record", {}).get("text", "")
                item = make_item(text[:180], bsky_post_link(post), text, "Bluesky watchlist", config, handle, dt)
                if item:
                    items.append(item)
        except Exception as exc:
            print(f"[BSKY WATCH ERROR] {handle}: {exc}")
    return items
