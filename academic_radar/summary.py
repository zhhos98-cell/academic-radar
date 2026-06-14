def _sample(values, limit=5):
    values = [str(value) for value in values if str(value).strip()]
    if not values:
        return "none"
    shown = values[:limit]
    suffix = "" if len(values) <= limit else f"; +{len(values) - limit} more"
    return "; ".join(shown) + suffix


def summarize_config(config):
    """Return a no-network, human-readable summary of a loaded radar profile."""
    lines = [
        "Academic Radar profile summary:",
        f"Name: {config.name}",
        "",
        "Files:",
        f"  OPML: {config.opml_file}",
        f"  Bluesky watchlist: {config.bsky_watchlist_file}",
        f"  Seen-link state: {config.state_file}",
        "",
        "Settings:",
        f"  RSS max age: {config.rss_max_age_days} day(s)",
        f"  Bluesky max age: {config.bsky_max_age_days} day(s)",
        f"  Max digest items: {config.max_email_items}",
        f"  Max RSS items per feed: {config.max_rss_per_feed}",
        f"  Max Bluesky items per query: {config.max_bsky_per_query}",
        f"  Max Bluesky items per watched account: {config.max_bsky_per_account}",
        "",
        "Scoring:",
        f"  Event terms: {len(config.event_terms)} ({_sample(config.event_terms)})",
        f"  Field terms: {len(config.core_field_terms)} ({_sample(config.core_field_terms)})",
        f"  Source terms: {len(config.prestige_or_core_sources)} ({_sample(config.prestige_or_core_sources)})",
        f"  Negative terms: {len(config.negative_terms)} ({_sample(config.negative_terms)})",
        "",
        "Bluesky:",
        f"  Public search queries: {len(config.bluesky_queries)} ({_sample(config.bluesky_queries, limit=3)})",
    ]
    return "\n".join(lines)
