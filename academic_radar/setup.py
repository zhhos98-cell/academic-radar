import json
from pathlib import Path
from xml.sax.saxutils import escape

from .config import (
    DEFAULT_BLUESKY_QUERIES,
    DEFAULT_CORE_FIELD_TERMS,
    DEFAULT_EVENT_TERMS,
    DEFAULT_NEGATIVE_TERMS,
    DEFAULT_PRESTIGE_OR_CORE_SOURCES,
)


DEFAULT_LOCAL_PROFILE = ".radar/profiles/local.json"


def _unique(values):
    seen = set()
    output = []
    for value in values:
        normalized = " ".join(str(value).strip().split())
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append(normalized)
    return output


def _unique_feeds(feeds):
    seen = set()
    output = []
    for title, url in feeds:
        title = " ".join(str(title).strip().split())
        url = str(url).strip()
        if not url:
            continue
        key = url.lower()
        if key in seen:
            continue
        seen.add(key)
        output.append((title or url, url))
    return output


def parse_feed_arg(value):
    """Parse TITLE=URL or URL syntax for --rss-feed."""
    raw = str(value).strip()
    if "=" in raw:
        title, url = raw.split("=", 1)
        title = title.strip()
        url = url.strip()
    else:
        title = raw
        url = raw
    if not url:
        raise ValueError("RSS feed URL cannot be empty")
    return title or url, url


def normalize_bsky_handle(value):
    handle = str(value).strip()
    if handle.startswith("@"):
        handle = handle[1:]
    return handle


def _write_text(path, content, overwrite):
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"{path} already exists; pass --overwrite to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def build_opml(feeds):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="2.0">',
        "  <head>",
        "    <title>Academic Radar feeds</title>",
        "  </head>",
        "  <body>",
    ]
    for title, url in feeds:
        title = escape(title, {'"': "&quot;"})
        url = escape(url, {'"': "&quot;"})
        lines.append(f'    <outline text="{title}" title="{title}" type="rss" xmlUrl="{url}" />')
    lines.extend(["  </body>", "</opml>", ""])
    return "\n".join(lines)


def build_watchlist(handles):
    lines = ["# Bluesky handles watched by Academic Radar."]
    lines.extend(normalize_bsky_handle(handle) for handle in handles if normalize_bsky_handle(handle))
    return "\n".join(_unique(lines)) + "\n"


def build_profile(profile_name, opml_path, watchlist_path, state_path, field_terms=None, negative_terms=None, bsky_queries=None):
    extra_field_terms = _unique(field_terms or [])
    field_term_list = _unique([*DEFAULT_CORE_FIELD_TERMS, *extra_field_terms])
    query_list = _unique([*DEFAULT_BLUESKY_QUERIES, *(bsky_queries or [])])
    for term in extra_field_terms:
        query_list.extend(
            [
                f'"call for papers" "{term}"',
                f'"special issue" "{term}"',
                f'"new book" "{term}"',
            ]
        )
    profile = {
        "name": profile_name,
        "files": {
            "opml": str(opml_path),
            "bsky_watchlist": str(watchlist_path),
            "state": str(state_path),
        },
        "settings": {
            "rss_max_age_days": 35,
            "bsky_max_age_days": 10,
            "max_email_items": 20,
            "max_rss_per_feed": 12,
            "max_bsky_per_query": 15,
            "max_bsky_per_account": 8,
        },
        "scoring": {
            "event_terms": list(DEFAULT_EVENT_TERMS),
            "core_field_terms": field_term_list,
            "prestige_or_core_sources": list(DEFAULT_PRESTIGE_OR_CORE_SOURCES),
            "negative_terms": _unique([*DEFAULT_NEGATIVE_TERMS, *(negative_terms or [])]),
        },
        "bluesky": {
            "queries": _unique(query_list),
        },
    }
    return json.dumps(profile, ensure_ascii=False, indent=2) + "\n"


def write_first_run_files(
    profile_path=DEFAULT_LOCAL_PROFILE,
    profile_name="Local Academic Radar",
    field_terms=None,
    negative_terms=None,
    bsky_queries=None,
    bsky_handles=None,
    rss_feeds=None,
    overwrite=False,
):
    profile_path = Path(profile_path)
    root = profile_path.parents[1] if len(profile_path.parents) > 1 else profile_path.parent
    opml_path = root / "feeds.opml"
    watchlist_path = root / "bsky_watchlist.txt"
    state_path = root / "seen.json"

    parsed_feeds = _unique_feeds(parse_feed_arg(feed) for feed in (rss_feeds or []))

    _write_text(opml_path, build_opml(parsed_feeds), overwrite)
    _write_text(watchlist_path, build_watchlist(bsky_handles or []), overwrite)
    _write_text(
        profile_path,
        build_profile(
            profile_name=profile_name,
            opml_path=opml_path,
            watchlist_path=watchlist_path,
            state_path=state_path,
            field_terms=field_terms,
            negative_terms=negative_terms,
            bsky_queries=bsky_queries,
        ),
        overwrite,
    )

    return {
        "profile": str(profile_path),
        "opml": str(opml_path),
        "watchlist": str(watchlist_path),
        "state": str(state_path),
    }
