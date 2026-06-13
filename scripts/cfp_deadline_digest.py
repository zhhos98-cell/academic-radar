from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
CFP_DIR = ROOT / "cfp"
RECORDS_DIR = CFP_DIR / "records"
DIGEST_PATH = CFP_DIR / "deadlines.md"

DEFAULT_WINDOW_DAYS = 45
TERMINAL_STATUSES = {"accepted", "rejected", "declined", "archived"}

DATE_FIELDS = [
    ("Next action", ("next_action", "due")),
    ("Abstract deadline", ("deadlines", "abstract_deadline")),
    ("Full paper deadline", ("deadlines", "full_paper_deadline")),
    ("Registration deadline", ("deadlines", "registration_deadline")),
    ("Notification date", ("deadlines", "notification_date")),
]


def clean_cell(value: Any) -> str:
    text = str(value or "").replace("\n", " ").strip()
    return text.replace("|", "\\|")


def get_nested(data: dict[str, Any], path: tuple[str, ...]) -> str:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return ""
        value = value.get(key)
    return str(value or "").strip()


def parse_date_token(value: str) -> tuple[dt.date | None, bool]:
    value = (value or "").strip()
    if not value:
        return None, False

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return dt.date.fromisoformat(value), True

    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, month = [int(part) for part in value.split("-")]
        return dt.date(year, month, 1), False

    if re.fullmatch(r"\d{4}", value):
        return dt.date(int(value), 1, 1), False

    return None, False


def load_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not RECORDS_DIR.exists():
        return records

    for path in RECORDS_DIR.glob("*/*/metadata.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            records.append(
                {
                    "id": path.parent.name,
                    "title": path.parent.name,
                    "status": "unreadable",
                    "metadata_error": f"{type(exc).__name__}: {exc}",
                    "metadata_path": path.as_posix(),
                }
            )
            continue

        data["metadata_path"] = path.as_posix()
        records.append(data)

    return sorted(records, key=lambda item: (item.get("status", ""), item.get("title", "")))


def issue_or_source(record: dict[str, Any]) -> str:
    issue = record.get("source_issue")
    issue_url = record.get("source_issue_url")
    source_url = record.get("source", {}).get("url", "")

    if issue and issue_url:
        return f"[#{issue}]({issue_url})"
    if source_url:
        return f"[source]({source_url})"
    return ""


def collect_deadlines(
    records: list[dict[str, Any]],
    today: dt.date,
    window_days: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    exact: list[dict[str, Any]] = []
    approximate: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []

    for record in records:
        status = str(record.get("status", "")).strip().lower()
        if status in TERMINAL_STATUSES:
            continue

        found_any = False
        for label, path in DATE_FIELDS:
            raw = get_nested(record, path)
            parsed, is_exact = parse_date_token(raw)
            if not raw:
                continue

            found_any = True
            if parsed is None:
                approximate.append(
                    {
                        "sort_date": dt.date.max,
                        "date": raw,
                        "kind": label,
                        "record": record,
                        "note": "unparsed date",
                    }
                )
                continue

            days = (parsed - today).days
            item = {
                "sort_date": parsed,
                "date": raw,
                "days": days,
                "kind": label,
                "record": record,
                "note": "" if is_exact else "approximate date",
            }

            if is_exact and days <= window_days:
                exact.append(item)
            elif not is_exact:
                approximate.append(item)

        if not found_any:
            missing.append(record)

    exact.sort(key=lambda item: (item["sort_date"], item["record"].get("priority", ""), item["record"].get("title", "")))
    approximate.sort(key=lambda item: (item["sort_date"], item["record"].get("title", "")))
    missing.sort(key=lambda item: (item.get("status", ""), item.get("priority", ""), item.get("title", "")))
    return exact, approximate, missing


def render_days(days: int) -> str:
    if days < 0:
        return f"{abs(days)} days overdue"
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    return f"in {days} days"


def render_deadline_table(items: list[dict[str, Any]], include_days: bool) -> list[str]:
    if not items:
        return ["No records.", ""]

    if include_days:
        lines = [
            "| Date | When | Kind | Title | Status | Priority | Issue / Source | Note |",
            "|---|---:|---|---|---|---|---|---|",
        ]
    else:
        lines = [
            "| Date | Kind | Title | Status | Priority | Issue / Source | Note |",
            "|---|---|---|---|---|---|---|",
        ]

    for item in items:
        record = item["record"]
        row = [
            clean_cell(item["date"]),
            clean_cell(item["kind"]),
            clean_cell(record.get("title", "")),
            clean_cell(record.get("status", "")),
            clean_cell(record.get("priority", "")),
            issue_or_source(record),
            clean_cell(item.get("note", "")),
        ]
        if include_days:
            row.insert(1, clean_cell(render_days(item["days"])))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    return lines


def render_missing_table(records: list[dict[str, Any]]) -> list[str]:
    if not records:
        return ["No records.", ""]

    lines = [
        "| Title | Status | Priority | Issue / Source |",
        "|---|---|---|---|",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    clean_cell(record.get("title", "")),
                    clean_cell(record.get("status", "")),
                    clean_cell(record.get("priority", "")),
                    issue_or_source(record),
                ]
            )
            + " |"
        )

    lines.append("")
    return lines


def build_digest(window_days: int = DEFAULT_WINDOW_DAYS) -> None:
    today = dt.datetime.now(dt.timezone.utc).date()
    records = load_records()
    exact, approximate, missing = collect_deadlines(records, today, window_days)

    lines = [
        "# CFP Deadline Digest",
        "",
        f"Generated: {today.isoformat()} UTC",
        f"Reminder window: {window_days} days",
        "",
        "## Needs Attention",
        "",
    ]
    lines.extend(render_deadline_table(exact, include_days=True))
    lines.extend(["## Approximate Or Unparsed Dates", ""])
    lines.extend(render_deadline_table(approximate, include_days=False))
    lines.extend(["## Missing Deadline Data", ""])
    lines.extend(render_missing_table(missing))

    DIGEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    DIGEST_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    window_days = int(os.environ.get("CFP_DEADLINE_WINDOW_DAYS", DEFAULT_WINDOW_DAYS))
    build_digest(window_days)


if __name__ == "__main__":
    main()
