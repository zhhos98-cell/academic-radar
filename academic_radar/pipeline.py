from .sources import fetch_bluesky_search, fetch_bluesky_watchlist, fetch_rss


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


def collect_items(config, skip_rss=False, skip_bsky=False):
    rss_items = [] if skip_rss else fetch_rss(config)
    bsky_search_items = [] if skip_bsky else fetch_bluesky_search(config)
    bsky_watch_items = [] if skip_bsky else fetch_bluesky_watchlist(config)

    print(f"RSS items: {len(rss_items)}")
    print(f"Bluesky search items: {len(bsky_search_items)}")
    print(f"Bluesky watchlist items: {len(bsky_watch_items)}")

    items = dedupe(rss_items + bsky_search_items + bsky_watch_items)
    print(f"Deduped items: {len(items)}")
    return items
