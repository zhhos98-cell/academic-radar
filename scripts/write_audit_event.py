from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a minimal processing audit event.")
    parser.add_argument("--output", required=True, help="JSONL output path.")
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--event", required=True)
    parser.add_argument("--source-type", default="")
    parser.add_argument("--source-id", default="")
    parser.add_argument("--storage-mode", default="ephemeral")
    parser.add_argument("--content-persisted", default="false")
    parser.add_argument("--category", action="append", default=[])
    args = parser.parse_args()

    event = {
        "schema_version": 1,
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "workflow": args.workflow,
        "event": args.event,
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
        "commit_sha": os.environ.get("GITHUB_SHA", ""),
        "source": {
            "type": args.source_type,
            "id": args.source_id,
        },
        "data_categories_processed": args.category,
        "storage_mode": args.storage_mode,
        "content_persisted": as_bool(args.content_persisted),
        "audit_contains_content": False,
        "retention_recommendation_days": 30,
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"Wrote audit event: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
