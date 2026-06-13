from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path.cwd()

CFP_DIR = ROOT / "cfp"
RECORDS_DIR = CFP_DIR / "records"
BACKFILL_DIR = CFP_DIR / "backfill"
EXPORT_DIR = CFP_DIR / "exports"

DASHBOARD = CFP_DIR / "README.md"
COMMENT_PATH = Path(
    os.environ.get(
        "CFP_INGEST_COMMENT_PATH",
        Path(tempfile.gettempdir()) / "cfp_ingest_comment.md",
    )
)

CFP_STATUSES = {
    "inbox",
    "reviewing",
    "active",
    "drafting",
    "submitted",
    "accepted",
    "rejected",
    "declined",
    "archived",
}


def utc_now_iso() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def read_event() -> dict[str, Any]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise RuntimeError("GITHUB_EVENT_PATH is not set.")
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def clean_response(value: str) -> str:
    value = (value or "").strip()

    if not value:
        return ""

    if value.strip() in {"No response", "_No response_", "No Response", "no response"}:
        return ""

    lines = value.splitlines()
    if len(lines) >= 2 and lines[0].strip().startswith("```") and lines[-1].strip() == "```":
        value = "\n".join(lines[1:-1]).strip()

    return value


def parse_issue_form(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}

    current_heading: str | None = None
    current_lines: list[str] = []
    heading_re = re.compile(r"^#{2,6}\s+(.*?)\s*$")

    def flush() -> None:
        nonlocal current_heading, current_lines
        if current_heading is None:
            return
        fields[current_heading] = clean_response("\n".join(current_lines).strip())
        current_heading = None
        current_lines = []

    for line in body.splitlines():
        match = heading_re.match(line)
        if match:
            flush()
            current_heading = match.group(1).strip()
            current_lines = []
        else:
            if current_heading is not None:
                current_lines.append(line)

    flush()
    return fields


def pick(parsed: dict[str, str], *prefixes: str) -> str:
    normalized = [(heading.strip().lower(), value) for heading, value in parsed.items()]

    for prefix in prefixes:
        prefix_lower = prefix.strip().lower()
        for heading_lower, value in normalized:
            if heading_lower.startswith(prefix_lower):
                return value.strip()

    return ""


def parse_selected_options(text: str, known_labels: list[str]) -> dict[str, bool]:
    text = clean_response(text)
    lower = text.lower()

    results: dict[str, bool] = {}
    for label in known_labels:
        label_lower = label.lower()
        key = (
            label_lower
            .replace(" / ", " ")
            .replace("/", " ")
            .replace("-", "_")
            .replace(" ", "_")
        )
        key = re.sub(r"[^a-z0-9_]+", "", key).strip("_")

        if not lower:
            results[key] = False
            continue

        if label_lower not in lower:
            results[key] = False
            continue

        checkbox_patterns = [
            f"- [x] {label_lower}",
            f"- [X] {label_lower}",
            f"* [x] {label_lower}",
            f"* [X] {label_lower}",
        ]
        if any(pattern.lower() in lower for pattern in checkbox_patterns):
            results[key] = True
        else:
            # GitHub issue-form output often includes only selected checkbox labels.
            results[key] = True

    return results


def parse_tracking_options(text: str) -> dict[str, bool]:
    raw = parse_selected_options(
        text,
        [
            "Add to active CFP dashboard",
            "Send deadline reminders later",
            "Needs funding or travel check",
            "Keep only as archive lead",
        ],
    )

    return {
        "dashboard": raw.get("add_to_active_cfp_dashboard", False),
        "reminders": raw.get("send_deadline_reminders_later", False),
        "funding_or_travel_check": raw.get("needs_funding_or_travel_check", False),
        "archive_only": raw.get("keep_only_as_archive_lead", False),
    }


def slugify(text: str, fallback: str = "untitled") -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:90] or fallback


def normalize_status(value: str, tracking: dict[str, bool]) -> str:
    status = (value or "").strip().lower()
    if status not in CFP_STATUSES:
        status = "inbox"

    if tracking.get("archive_only"):
        return "archived"

    return status


def normalize_priority(value: str) -> str:
    value = (value or "").strip().lower()
    if value in {"high", "medium", "low", "archive only", "unknown"}:
        return value
    return "unknown"


def normalize_date_token(token: str) -> str:
    token = (token or "").strip()

    match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", token)
    if match:
        return match.group(0)

    match = re.search(r"\b\d{4}-\d{2}\b", token)
    if match:
        return match.group(0)

    match = re.search(r"\b\d{4}\b", token)
    if match:
        return match.group(0)

    return token


def parse_event_dates(raw: str) -> tuple[str, str]:
    raw = (raw or "").strip()
    if not raw:
        return "", ""

    separators = [" to ", " – ", " — ", " - ", "–", "—"]
    for sep in separators:
        if sep in raw:
            left, right = raw.split(sep, 1)
            return normalize_date_token(left), normalize_date_token(right)

    return normalize_date_token(raw), ""


def split_keywords(raw: str) -> list[str]:
    raw = clean_response(raw)
    if not raw:
        return []

    pieces: list[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if "," in line:
            pieces.extend(part.strip() for part in line.split(",") if part.strip())
        else:
            pieces.append(line)

    # stable de-duplication
    seen: set[str] = set()
    out: list[str] = []
    for item in pieces:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def yaml_scalar(value: Any) -> str:
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []

    def emit(key: str, value: Any, indent: int = 0) -> None:
        pad = " " * indent

        if isinstance(value, dict):
            lines.append(f"{pad}{key}:")
            for child_key, child_value in value.items():
                emit(child_key, child_value, indent + 2)
            return

        if isinstance(value, list):
            lines.append(f"{pad}{key}:")
            if not value:
                lines.append(f"{pad}  []")
            else:
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{pad}  -")
                        for child_key, child_value in item.items():
                            emit(child_key, child_value, indent + 4)
                    else:
                        lines.append(f"{pad}  - {yaml_scalar(item)}")
            return

        if isinstance(value, str) and "\n" in value:
            lines.append(f"{pad}{key}: |")
            for line in value.splitlines():
                lines.append(f"{pad}  {line}")
            return

        lines.append(f"{pad}{key}: {yaml_scalar(value)}")

    for top_key, top_value in data.items():
        emit(top_key, top_value, 0)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_sort_date(value: str) -> str:
    value = value or ""
    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    if match:
        return match.group(0)
    match = re.search(r"\d{4}-\d{2}", value)
    if match:
        return match.group(0)
    match = re.search(r"\d{4}", value)
    if match:
        return match.group(0)
    return "9999-99-99" if not value else value


def escape_table(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def rel_to_cfp(path: Path) -> str:
    return path.relative_to(CFP_DIR).as_posix()


def markdown_link(label: str, path: Path) -> str:
    return f"[{label}]({rel_to_cfp(path)})"


def load_cfp_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for meta_path in sorted(RECORDS_DIR.glob("*/*/metadata.json")):
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        data["_record_dir"] = meta_path.parent
        records.append(data)

    records.sort(
        key=lambda record: parse_sort_date(
            record.get("deadlines", {}).get("abstract_deadline")
            or record.get("deadlines", {}).get("full_paper_deadline")
            or record.get("deadlines", {}).get("registration_deadline")
            or record.get("next_action", {}).get("due")
            or ""
        )
    )

    return records


def load_backfill_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for meta_path in sorted(BACKFILL_DIR.glob("*/metadata.json")):
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        data["_record_dir"] = meta_path.parent
        records.append(data)

    records.sort(
        key=lambda record: parse_sort_date(
            record.get("presentation", {}).get("presentation_date")
            or record.get("conference", {}).get("event_start")
            or record.get("conference", {}).get("event_dates_raw")
            or ""
        ),
        reverse=True,
    )

    return records


def issue_link(record: dict[str, Any]) -> str:
    number = record.get("source_issue", "")
    url = record.get("source_issue_url", "")
    if number and url:
        return f"[#{number}]({url})"
    return ""


def deadline_for(record: dict[str, Any]) -> str:
    deadlines = record.get("deadlines", {})
    return (
        deadlines.get("abstract_deadline")
        or deadlines.get("full_paper_deadline")
        or deadlines.get("registration_deadline")
        or ""
    )


def build_cfp_table(records: list[dict[str, Any]]) -> list[str]:
    if not records:
        return ["No records.", ""]

    lines = [
        "| Deadline | Title | Type | Priority | Project | Next action | Issue |",
        "|---|---|---|---|---|---|---|",
    ]

    for record in records:
        title = record.get("title", "")
        cfp_type = record.get("type", "")
        priority = record.get("priority", "")
        project = record.get("project_link", "")
        next_action = record.get("next_action", {}).get("text", "")
        next_due = record.get("next_action", {}).get("due", "")

        if next_due:
            next_action_display = f"{next_action} ({next_due})" if next_action else next_due
        else:
            next_action_display = next_action

        lines.append(
            "| "
            + " | ".join(
                [
                    escape_table(deadline_for(record)),
                    escape_table(title),
                    escape_table(cfp_type),
                    escape_table(priority),
                    escape_table(project),
                    escape_table(next_action_display),
                    issue_link(record),
                ]
            )
            + " |"
        )

    lines.append("")
    return lines


def build_dashboard() -> None:
    cfp_records = load_cfp_records()
    backfill_records = load_backfill_records()

    inbox = [r for r in cfp_records if r.get("status") in {"inbox", "reviewing"}]
    active = [r for r in cfp_records if r.get("status") in {"active", "drafting"}]
    submitted = [r for r in cfp_records if r.get("status") == "submitted"]
    archived = [r for r in cfp_records if r.get("status") in {"accepted", "rejected", "declined", "archived"}]

    lines: list[str] = [
        "# CFP Ledger / 投稿与会议台账",
        "",
        "自动生成。不要手动编辑本页；修改 issue 或 metadata 后重新运行 workflow。",
        "",
        "Deadline summary: [cfp/deadlines.md](deadlines.md).",
        "",
        "## Inbox / 待判断",
        "",
    ]

    lines.extend(build_cfp_table(inbox))

    lines.extend(
        [
            "## Active / 进行中",
            "",
        ]
    )
    lines.extend(build_cfp_table(active))

    lines.extend(
        [
            "## Submitted / 已提交",
            "",
        ]
    )
    lines.extend(build_cfp_table(submitted))

    lines.extend(
        [
            "<details>",
            f"<summary>Archived CFP leads / 已归档 CFP 线索 {len(archived)}</summary>",
            "",
        ]
    )
    lines.extend(build_cfp_table(archived))
    lines.extend(["</details>", ""])

    lines.extend(
        [
            "<details>",
            f"<summary>Backfilled / 补档 {len(backfill_records)}</summary>",
            "",
        ]
    )

    if not backfill_records:
        lines.extend(["No backfilled records yet.", ""])
    else:
        lines.extend(
            [
                "| Date | Presentation | Conference | Panel | Location | Abstract | Bio | Programme | Proceedings | Hash | Issue | ORCID |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|",
            ]
        )
        for record in backfill_records:
            record_dir: Path = record["_record_dir"]
            presentation = record.get("presentation", {})
            conference = record.get("conference", {})
            exports = record.get("exports", {})

            date = (
                presentation.get("presentation_date")
                or conference.get("event_start")
                or conference.get("event_dates_raw")
                or ""
            )
            title = presentation.get("title", "")
            conference_title = conference.get("title", "")
            panel_title = conference.get("panel_title", "")
            location = conference.get("location", "")

            programme_url = conference.get("programme_url") or ""
            proceedings_url = conference.get("proceedings_url") or ""

            programme = f"[programme]({programme_url})" if programme_url else ""
            proceedings = f"[proceedings]({proceedings_url})" if proceedings_url else ""
            orcid = "ready" if exports.get("orcid_ready") else ""

            lines.append(
                "| "
                + " | ".join(
                    [
                        escape_table(date),
                        escape_table(title),
                        escape_table(conference_title),
                        escape_table(panel_title),
                        escape_table(location),
                        markdown_link("abstract", record_dir / "abstract.txt"),
                        markdown_link("bio", record_dir / "bio.txt"),
                        programme,
                        proceedings,
                        markdown_link("hash", record_dir / "SHA256SUMS.txt"),
                        issue_link(record),
                        escape_table(orcid),
                    ]
                )
                + " |"
            )
        lines.append("")

    lines.extend(["</details>", ""])

    DASHBOARD.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD.write_text("\n".join(lines), encoding="utf-8")


def remove_existing_record_dirs(issue_number: int) -> None:
    pattern = f"issue-{issue_number}-*"
    for status_dir in RECORDS_DIR.glob("*"):
        if not status_dir.is_dir():
            continue
        for record_dir in status_dir.glob(pattern):
            if record_dir.is_dir():
                shutil.rmtree(record_dir)


def main() -> None:
    event = read_event()
    issue = event["issue"]

    issue_number = issue["number"]
    issue_url = issue["html_url"]
    issue_body = issue.get("body") or ""

    parsed = parse_issue_form(issue_body)

    title = pick(parsed, "CFP title")
    if not title:
        # fallback to issue title after removing the prefix
        title = re.sub(r"^\[CFP\]\s*", "", issue.get("title") or "").strip()

    if not title:
        raise RuntimeError("Missing required field: CFP title / CFP 标题")

    cfp_type = pick(parsed, "Type")
    source_url = pick(parsed, "Source URL")
    organiser = pick(parsed, "Organiser")
    host_institution = pick(parsed, "Host institution")
    location = pick(parsed, "Location")
    online_option = pick(parsed, "Online option")
    event_dates_raw = pick(parsed, "Event dates")
    abstract_deadline = pick(parsed, "Abstract deadline")
    full_paper_deadline = pick(parsed, "Full paper deadline")
    registration_deadline = pick(parsed, "Registration deadline")
    notification_date = pick(parsed, "Notification date")
    word_limit_abstract = pick(parsed, "Abstract word limit")
    word_limit_paper = pick(parsed, "Paper word limit")
    submission_method = pick(parsed, "Submission method")
    submission_email = pick(parsed, "Submission email")
    submission_portal = pick(parsed, "Submission portal")
    theme_keywords_raw = pick(parsed, "Theme keywords")
    project_link = pick(parsed, "Project link")
    priority_raw = pick(parsed, "Priority")
    status_raw = pick(parsed, "Status")
    next_action_text = pick(parsed, "Next action")
    next_action_due = pick(parsed, "Next action due")
    raw_text = pick(parsed, "Raw CFP text")
    notes = pick(parsed, "Notes")
    tracking_raw = pick(parsed, "Tracking options")

    tracking = parse_tracking_options(tracking_raw)
    priority = normalize_priority(priority_raw)
    status = normalize_status(status_raw, tracking)
    event_start, event_end = parse_event_dates(event_dates_raw)

    slug = f"issue-{issue_number}-{slugify(title, fallback='cfp')}"
    remove_existing_record_dirs(issue_number)

    record_dir = RECORDS_DIR / status / slug
    record_dir.mkdir(parents=True, exist_ok=True)

    metadata: dict[str, Any] = {
        "id": slug,
        "record_type": "cfp",
        "status": status,
        "created_at": utc_now_iso(),
        "source_issue": issue_number,
        "source_issue_url": issue_url,
        "title": title,
        "type": cfp_type,
        "priority": priority,
        "project_link": project_link,
        "source": {
            "url": source_url,
            "raw_text": raw_text,
        },
        "organiser": organiser,
        "host_institution": host_institution,
        "location": location,
        "online_option": online_option,
        "event": {
            "dates_raw": event_dates_raw,
            "start": event_start,
            "end": event_end,
        },
        "deadlines": {
            "abstract_deadline": normalize_date_token(abstract_deadline),
            "full_paper_deadline": normalize_date_token(full_paper_deadline),
            "registration_deadline": normalize_date_token(registration_deadline),
            "notification_date": normalize_date_token(notification_date),
        },
        "requirements": {
            "word_limit_abstract": word_limit_abstract,
            "word_limit_paper": word_limit_paper,
            "submission_method": submission_method,
            "submission_email": submission_email,
            "submission_portal": submission_portal,
        },
        "theme_keywords": split_keywords(theme_keywords_raw),
        "next_action": {
            "text": next_action_text,
            "due": normalize_date_token(next_action_due),
        },
        "tracking": tracking,
        "notes": notes,
    }

    (record_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_yaml(record_dir / "metadata.yml", metadata)

    if raw_text:
        (record_dir / "raw_cfp.txt").write_text(raw_text.strip() + "\n", encoding="utf-8")
    if notes:
        (record_dir / "notes.txt").write_text(notes.strip() + "\n", encoding="utf-8")

    build_dashboard()

    COMMENT_PATH.write_text(
        "\n".join(
            [
                "Added this CFP issue to the CFP Ledger.",
                "",
                f"- Folder: `cfp/records/{status}/{slug}/`",
                f"- Status: `{status}`",
                f"- Priority: `{priority}`",
                f"- Deadline: `{deadline_for(metadata) or 'not recorded'}`",
                "- Dashboard updated: `cfp/README.md`",
                "",
                "Edit this issue and save again to update the ledger record.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
