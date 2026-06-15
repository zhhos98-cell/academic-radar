import os
from pathlib import Path


INFO = "info"
OK = "ok"
WARN = "warn"

EMAIL_ENV_KEYS = ("SMTP_USER", "SMTP_PASS", "TO_EMAIL")
PRIVATE_PATH_MARKERS = {".radar", "tmp"}
IGNORED_RUNTIME_FILES = {
    "feedly_active.opml",
    "bsky_watchlist_core.txt",
    "sent_items.json",
}
REPOSITORY_DATA_DIRS = {"config", "docs", "examples", "site", "cfp"}


def _env_has_value(env, key):
    value = env.get(key)
    return bool(str(value).strip()) if value is not None else False


def _path_parts(path):
    normalized = str(path).replace("\\", "/")
    return {part.lower() for part in normalized.split("/") if part}


def _is_private_runtime_path(path):
    lowered = str(path).replace("\\", "/").lower()
    name = Path(path).name.lower()
    return (
        bool(_path_parts(path) & PRIVATE_PATH_MARKERS)
        or name in IGNORED_RUNTIME_FILES
        or name.endswith(".local.json")
        or name.endswith("_sent.json")
        or lowered.startswith("tmp/")
    )


def _assess_path(path):
    path_text = str(path or "").strip()
    if not path_text:
        return {
            "status": WARN,
            "path": "(not configured)",
            "exists": False,
            "note": "No path is configured.",
        }

    candidate = Path(path_text)
    try:
        exists = candidate.exists()
    except OSError:
        exists = False

    if _is_private_runtime_path(path_text):
        status = OK
        note = "Looks like an ignored/local runtime path."
    elif _path_parts(path_text) & REPOSITORY_DATA_DIRS:
        status = WARN
        note = "Looks like a repository path; avoid committing personal runtime data here in a public fork."
    else:
        status = INFO
        note = "Review whether this path is private and ignored before using real data."

    return {
        "status": status,
        "path": path_text,
        "exists": exists,
        "note": note,
    }


def _file_item(label, path, data, retention):
    assessed = _assess_path(path)
    return {
        "label": label,
        "path": assessed["path"],
        "status": assessed["status"],
        "exists": assessed["exists"],
        "data": data,
        "retention": retention,
        "note": assessed["note"],
    }


def _email_item(env):
    configured_count = sum(1 for key in EMAIL_ENV_KEYS if _env_has_value(env, key))
    if configured_count == len(EMAIL_ENV_KEYS):
        return {
            "status": WARN,
            "label": "Email delivery",
            "message": "SMTP delivery is configured; a live run may send digest content through smtp.gmail.com.",
            "note": "Environment variable values are intentionally not displayed.",
        }
    if configured_count:
        return {
            "status": WARN,
            "label": "Email delivery",
            "message": f"Partial SMTP delivery configuration detected ({configured_count}/{len(EMAIL_ENV_KEYS)} required variables set).",
            "note": "A live send will fail until SMTP_USER, SMTP_PASS, and TO_EMAIL are all configured.",
        }
    return {
        "status": OK,
        "label": "Email delivery",
        "message": "No SMTP delivery environment variables are configured in this process.",
        "note": "Use --dry-run or --no-email while testing; values are never printed by this report.",
    }


def build_privacy_report(config, env=None):
    env = env if env is not None else os.environ
    profile_name = getattr(config, "name", "Academic Radar")

    local_files = [
        _file_item(
            "OPML feed list",
            config.opml_file,
            "RSS feed URLs selected by the user; this can reveal research interests.",
            "Read during live collection and kept until the user edits or deletes the file.",
        ),
        _file_item(
            "Bluesky watchlist",
            config.bsky_watchlist_file,
            "Public Bluesky handles selected by the user; handles can be personal data.",
            "Read during live collection and kept until the user edits or deletes the file.",
        ),
        _file_item(
            "Seen-link state",
            config.state_file,
            "Previously seen item URLs plus an update timestamp.",
            "Updated only on non-dry runs unless --no-state is used; capped by the state writer.",
        ),
    ]

    network = [
        {
            "status": INFO,
            "label": "RSS fetching",
            "message": "Live runs request the feed URLs listed in the OPML file.",
            "note": "The privacy report itself makes no network requests.",
        },
        {
            "status": INFO,
            "label": "Bluesky collection",
            "message": f"Configured public search queries: {len(config.bluesky_queries)}.",
            "note": "Watchlist handles are read from the local watchlist file during live runs.",
        },
        _email_item(env),
    ]

    controls = [
        "Keep profiles, OPML files, watchlists, state files, and exported digests under .radar/ or another ignored private folder.",
        "Run --summary, --doctor, and --privacy-report before live collection; use --dry-run --no-state while tuning.",
        "Do not commit SMTP secrets, recipient addresses, watchlists, seen-link state, exported digests, or CFP records containing personal data unless intentionally public.",
        "If you operate a public fork, document controller/contact, purpose, lawful basis, retention, and erasure workflow in PRIVACY.md or your own privacy notice.",
    ]

    return {
        "profile": profile_name,
        "local_files": local_files,
        "network": network,
        "controls": controls,
    }


def _format_status(status):
    return {
        INFO: "INFO",
        OK: "OK",
        WARN: "WARN",
    }.get(status, status.upper())


def format_privacy_report(report):
    lines = [
        "Academic Radar privacy/accountability report",
        f"Profile: {report['profile']}",
        "No network calls are made while producing this report.",
        "",
        "Local files:",
    ]

    for item in report["local_files"]:
        exists = "exists" if item["exists"] else "not found yet"
        lines.append(f"[{_format_status(item['status'])}] {item['label']}: {item['path']} ({exists})")
        lines.append(f"    Data: {item['data']}")
        lines.append(f"    Retention: {item['retention']}")
        lines.append(f"    Note: {item['note']}")

    lines.extend(["", "Network and disclosure:"])
    for item in report["network"]:
        lines.append(f"[{_format_status(item['status'])}] {item['label']}: {item['message']}")
        lines.append(f"    Note: {item['note']}")

    lines.extend(["", "Accountability controls:"])
    for control in report["controls"]:
        lines.append(f"- {control}")

    return "\n".join(lines)
