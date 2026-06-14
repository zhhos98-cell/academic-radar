from pathlib import Path

from .sources import load_bsky_watchlist, load_opml_feeds


ERROR = "error"
WARN = "warn"
OK = "ok"


def _result(status, check, message):
    return {
        "status": status,
        "check": check,
        "message": message,
    }


def _check_positive_int(results, config, attr):
    value = getattr(config, attr)
    if isinstance(value, int) and value > 0:
        results.append(_result(OK, attr, f"{attr}={value}"))
    else:
        results.append(_result(ERROR, attr, f"{attr} must be a positive integer; got {value!r}"))


def diagnose_config(config):
    """Run no-network diagnostics for a loaded RadarConfig."""
    results = []

    opml_path = Path(config.opml_file)
    if opml_path.exists():
        try:
            feeds = load_opml_feeds(str(opml_path))
        except Exception as exc:
            results.append(_result(ERROR, "opml", f"Could not parse OPML file {opml_path}: {exc}"))
        else:
            if feeds:
                results.append(_result(OK, "opml", f"Found {len(feeds)} unique RSS feed(s) in {opml_path}."))
            else:
                results.append(_result(WARN, "opml", f"OPML file exists but has no xmlUrl entries: {opml_path}"))
    else:
        results.append(_result(WARN, "opml", f"OPML file not found: {opml_path}"))

    watchlist_path = Path(config.bsky_watchlist_file)
    if watchlist_path.exists():
        try:
            handles = load_bsky_watchlist(str(watchlist_path))
        except Exception as exc:
            results.append(_result(ERROR, "watchlist", f"Could not read Bluesky watchlist {watchlist_path}: {exc}"))
        else:
            if handles:
                results.append(_result(OK, "watchlist", f"Found {len(handles)} Bluesky handle(s) in {watchlist_path}."))
            else:
                results.append(_result(WARN, "watchlist", f"Watchlist file exists but has no handles: {watchlist_path}"))
    else:
        results.append(_result(WARN, "watchlist", f"Bluesky watchlist not found: {watchlist_path}"))

    state_path = Path(config.state_file)
    if state_path.exists():
        results.append(_result(OK, "state", f"Seen-link state file exists: {state_path}"))
    elif state_path.parent.exists():
        results.append(_result(OK, "state", f"State file will be created on first non-dry run: {state_path}"))
    else:
        results.append(_result(WARN, "state", f"State parent directory does not exist yet: {state_path.parent}"))

    for attr in [
        "rss_max_age_days",
        "bsky_max_age_days",
        "max_email_items",
        "max_rss_per_feed",
        "max_bsky_per_query",
        "max_bsky_per_account",
    ]:
        _check_positive_int(results, config, attr)

    if config.event_terms:
        results.append(_result(OK, "event_terms", f"Loaded {len(config.event_terms)} event term(s)."))
    else:
        results.append(_result(ERROR, "event_terms", "At least one event term is required."))

    if config.core_field_terms or config.prestige_or_core_sources:
        results.append(
            _result(
                OK,
                "relevance_terms",
                f"Loaded {len(config.core_field_terms)} field term(s) and {len(config.prestige_or_core_sources)} source term(s).",
            )
        )
    else:
        results.append(_result(ERROR, "relevance_terms", "At least one field or source term is required."))

    negative_overlap = sorted({term.lower() for term in config.negative_terms} & {term.lower() for term in config.core_field_terms})
    if negative_overlap:
        results.append(_result(WARN, "negative_terms", f"Negative terms overlap with field terms: {', '.join(negative_overlap)}"))
    else:
        results.append(_result(OK, "negative_terms", f"Loaded {len(config.negative_terms)} negative term(s)."))

    if config.bluesky_queries:
        results.append(_result(OK, "bluesky_queries", f"Loaded {len(config.bluesky_queries)} public Bluesky search query/queries."))
    else:
        results.append(_result(WARN, "bluesky_queries", "No public Bluesky search queries configured."))

    return results


def diagnostics_exit_code(results):
    return 1 if any(result["status"] == ERROR for result in results) else 0


def format_diagnostics(results):
    labels = {
        OK: "OK",
        WARN: "WARN",
        ERROR: "ERROR",
    }
    lines = ["Academic Radar diagnostics:"]
    for result in results:
        lines.append(f"[{labels.get(result['status'], result['status'].upper())}] {result['check']}: {result['message']}")
    return "\n".join(lines)
