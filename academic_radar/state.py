import json
import os
from datetime import datetime, timezone


def load_seen_links(state_file):
    if not os.path.exists(state_file):
        return set()

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("seen_links", []))
    except Exception:
        return set()


def filter_new_items(items, state_file):
    seen = load_seen_links(state_file)
    return [item for item in items if item.get("link") not in seen]


def save_seen_links(items, state_file):
    seen = load_seen_links(state_file)
    for item in items:
        link = item.get("link")
        if link:
            seen.add(link)

    state_dir = os.path.dirname(state_file)
    if state_dir:
        os.makedirs(state_dir, exist_ok=True)

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "seen_links": list(seen)[-5000:],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
