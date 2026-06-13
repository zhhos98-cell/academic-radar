from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

from cfp_ingest_archive import build_dashboard as build_combined_dashboard


ROOT = Path.cwd()

CFP_DIR = ROOT / "cfp"
BACKFILL_DIR = CFP_DIR / "backfill"

EXPORT_DIR = CFP_DIR / "exports"
ORCID_EXPORT_DIR = EXPORT_DIR / "orcid"
CV_EXPORT_DIR = EXPORT_DIR / "cv"

COMMENT_PATH = Path(
    os.environ.get(
        "CFP_BACKFILL_COMMENT_PATH",
        Path(tempfile.gettempdir()) / "cfp_backfill_comment.md",
    )
)


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

    no_response_values = {
        "No response",
        "_No response_",
        "No Response",
        "no response",
    }
    if value.strip() in no_response_values:
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
        raw_value = "\n".join(current_lines).strip()
        fields[current_heading] = clean_response(raw_value)
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
    normalized: list[tuple[str, str]] = [
        (heading.strip().lower(), value) for heading, value in parsed.items()
    ]

    for prefix in prefixes:
        prefix_lower = prefix.strip().lower()
        for heading_lower, value in normalized:
            if heading_lower.startswith(prefix_lower):
                return value.strip()

    return ""


def parse_exports(text: str) -> dict[str, bool]:
    text = clean_response(text)
    lower = text.lower()

    if not lower:
        return {
            "cv": False,
            "orcid_ready": False,
            "abstract_archive": False,
        }

    def selected(label: str) -> bool:
        label_lower = label.lower()
        if label_lower not in lower:
            return False

        checkbox_patterns = [
            f"- [x] {label_lower}",
            f"- [X] {label_lower}",
            f"* [x] {label_lower}",
            f"* [X] {label_lower}",
        ]
        if any(pattern.lower() in lower for pattern in checkbox_patterns):
            return True

        return True

    return {
        "cv": selected("Include in CV conference list"),
        "orcid_ready": selected("Include in ORCID-ready export"),
        "abstract_archive": selected("Include abstract in local archive"),
    }


def slugify(text: str, fallback: str = "untitled") -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:90] or fallback


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text or ""))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = text or ""
    path.write_text(text.strip() + ("\n" if text.strip() else ""), encoding="utf-8")


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
    return value


def escape_table(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def rel_to_cfp(path: Path) -> str:
    return path.relative_to(CFP_DIR).as_posix()


def markdown_link(label: str, path: Path) -> str:
    return f"[{label}]({rel_to_cfp(path)})"


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


def build_orcid_export() -> None:
    records = load_backfill_records()
    export_records: list[dict[str, Any]] = []

    for record in records:
        if not record.get("exports", {}).get("orcid_ready"):
            continue

        presentation = record.get("presentation", {})
        conference = record.get("conference", {})

        external_url = (
            conference.get("proceedings_url")
            or conference.get("programme_url")
            or conference.get("website_url")
            or ""
        )

        export_records.append(
            {
                "record_type": "conference-presentation",
                "title": presentation.get("title", ""),
                "role": presentation.get("role", ""),
                "presentation_date": presentation.get("presentation_date", ""),
                "conference_title": conference.get("title", ""),
                "panel_title": conference.get("panel_title", ""),
                "host_institution": conference.get("host_institution", ""),
                "location": conference.get("location", ""),
                "event_start": conference.get("event_start", ""),
                "event_end": conference.get("event_end", ""),
                "event_dates_raw": conference.get("event_dates_raw", ""),
                "url": external_url,
                "source_issue": record.get("source_issue", ""),
                "source_issue_url": record.get("source_issue_url", ""),
                "local_id": record.get("id", ""),
                "sync_status": "ready_for_manual_entry",
            }
        )

    ORCID_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": utc_now_iso(),
        "note": "ORCID-ready export. Review manually before entering into ORCID.",
        "records": export_records,
    }

    (ORCID_EXPORT_DIR / "orcid_ready.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md_lines: list[str] = [
        "# ORCID-ready conference records",
        "",
        "Generated from `cfp/backfill/*/metadata.json`.",
        "",
    ]

    if not export_records:
        md_lines.append("No ORCID-ready records yet.")
        md_lines.append("")
    else:
        for item in export_records:
            md_lines.extend(
                [
                    f"## {item.get('title', '')}",
                    "",
                    f"- Type: `{item.get('record_type', '')}`",
                    f"- Role: {item.get('role', '')}",
                    f"- Conference: {item.get('conference_title', '')}",
                    f"- Panel: {item.get('panel_title', '')}",
                    f"- Host: {item.get('host_institution', '')}",
                    f"- Location: {item.get('location', '')}",
                    f"- Presentation date: {item.get('presentation_date', '')}",
                    f"- Event start: {item.get('event_start', '')}",
                    f"- Event end: {item.get('event_end', '')}",
                    f"- Event dates raw: {item.get('event_dates_raw', '')}",
                    f"- URL: {item.get('url', '')}",
                    f"- Source issue: {item.get('source_issue_url', '')}",
                    "",
                ]
            )

    (ORCID_EXPORT_DIR / "orcid_ready.md").write_text(
        "\n".join(md_lines),
        encoding="utf-8",
    )


def build_cv_export() -> None:
    records = load_backfill_records()
    cv_records = [record for record in records if record.get("exports", {}).get("cv")]

    CV_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        "# Conference presentations / 会议报告",
        "",
        "Generated from CFP Ledger backfill records.",
        "",
    ]

    if not cv_records:
        lines.append("No CV-ready records yet.")
        lines.append("")
    else:
        for record in cv_records:
            presentation = record.get("presentation", {})
            conference = record.get("conference", {})

            citation_note = presentation.get("citation_note", "").strip()

            if citation_note:
                lines.append(f"- {citation_note}")
                continue

            title = presentation.get("title", "")
            conference_title = conference.get("title", "")
            panel_title = conference.get("panel_title", "")
            location = conference.get("location", "")
            date = (
                presentation.get("presentation_date")
                or conference.get("event_start")
                or conference.get("event_dates_raw")
                or ""
            )
            programme_url = conference.get("programme_url") or conference.get("website_url") or ""

            line = f"- “{title},” {conference_title}"
            if panel_title:
                line += f", panel “{panel_title}”"
            if location:
                line += f", {location}"
            if date:
                line += f", {date}"
            if programme_url:
                line += f". {programme_url}"
            else:
                line += "."
            lines.append(line)

        lines.append("")

    (CV_EXPORT_DIR / "conference_presentations.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    event = read_event()
    issue = event["issue"]

    issue_number = issue["number"]
    issue_url = issue["html_url"]
    issue_body = issue.get("body") or ""

    parsed = parse_issue_form(issue_body)

    presentation_title = pick(parsed, "Presentation title")
    conference_title = pick(parsed, "Conference title")

    if not presentation_title:
        raise RuntimeError("Missing required field: Presentation title / 论文题目")

    if not conference_title:
        raise RuntimeError("Missing required field: Conference title / 会议名称")

    panel_title = pick(parsed, "Panel title")
    conference_website = pick(parsed, "Conference website")
    programme_url = pick(parsed, "Programme URL")
    proceedings_url = pick(parsed, "Proceedings")
    location = pick(parsed, "Location")
    host_institution = pick(parsed, "Host institution")
    event_dates_raw = pick(parsed, "Event dates")
    presentation_date = pick(parsed, "Presentation date")
    role = pick(parsed, "Role")
    project_link = pick(parsed, "Project link")
    abstract = pick(parsed, "Abstract text")
    bio = pick(parsed, "Bio text")
    citation_note = pick(parsed, "Citation note")
    notes = pick(parsed, "Notes")
    exports_raw = pick(parsed, "Export options")
    exports = parse_exports(exports_raw)

    event_start, event_end = parse_event_dates(event_dates_raw)

    slug = f"issue-{issue_number}-{slugify(presentation_title, fallback='backfilled-conference')}"
    record_dir = BACKFILL_DIR / slug
    record_dir.mkdir(parents=True, exist_ok=True)

    title_path = record_dir / "title.txt"
    abstract_path = record_dir / "abstract.txt"
    bio_path = record_dir / "bio.txt"
    citation_note_path = record_dir / "citation_note.txt"
    notes_path = record_dir / "notes.txt"

    write_text(title_path, presentation_title)
    write_text(abstract_path, abstract)
    write_text(bio_path, bio)
    write_text(citation_note_path, citation_note)
    write_text(notes_path, notes)

    file_hashes = {
        "title.txt": sha256_file(title_path),
        "abstract.txt": sha256_file(abstract_path),
        "bio.txt": sha256_file(bio_path),
        "citation_note.txt": sha256_file(citation_note_path),
        "notes.txt": sha256_file(notes_path),
    }

    bundle_source = "\n".join(
        f"{filename}:{digest}" for filename, digest in sorted(file_hashes.items())
    )
    bundle_sha256 = sha256_text(bundle_source)

    metadata: dict[str, Any] = {
        "id": slug,
        "record_type": "conference-presentation",
        "status": "completed",
        "created_at": utc_now_iso(),
        "source_issue": issue_number,
        "source_issue_url": issue_url,
        "presentation": {
            "title": presentation_title,
            "role": role,
            "presentation_date": presentation_date,
            "project_link": project_link,
            "citation_note": citation_note,
            "abstract_words": word_count(abstract),
            "bio_words": word_count(bio),
        },
        "conference": {
            "title": conference_title,
            "panel_title": panel_title,
            "host_institution": host_institution,
            "location": location,
            "event_dates_raw": event_dates_raw,
            "event_start": event_start,
            "event_end": event_end,
            "website_url": conference_website,
            "programme_url": programme_url,
            "proceedings_url": proceedings_url,
        },
        "texts": {
            "title_file": "title.txt",
            "abstract_file": "abstract.txt",
            "bio_file": "bio.txt",
            "citation_note_file": "citation_note.txt",
            "notes_file": "notes.txt",
        },
        "hashes": {
            "files": file_hashes,
            "bundle_sha256": bundle_sha256,
        },
        "exports": exports,
        "orcid": {
            "include": exports.get("orcid_ready", False),
            "work_type": "conference-presentation",
            "sync_status": "ready_for_manual_entry"
            if exports.get("orcid_ready")
            else "",
        },
    }

    (record_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_yaml(record_dir / "metadata.yml", metadata)

    sha_lines = [
        f"{digest}  {filename}" for filename, digest in sorted(file_hashes.items())
    ]
    sha_lines.append(f"{bundle_sha256}  BUNDLE")
    (record_dir / "SHA256SUMS.txt").write_text(
        "\n".join(sha_lines) + "\n",
        encoding="utf-8",
    )

    build_combined_dashboard()
    build_orcid_export()
    build_cv_export()

    COMMENT_PATH.write_text(
        "\n".join(
            [
                "Archived this backfilled conference record.",
                "",
                f"- Folder: `cfp/backfill/{slug}/`",
                f"- Abstract words: `{word_count(abstract)}`",
                f"- Bio words: `{word_count(bio)}`",
                f"- Bundle SHA-256: `{bundle_sha256}`",
                "- Dashboard updated: `cfp/README.md`",
                "- ORCID-ready export updated: `cfp/exports/orcid/orcid_ready.json`",
                "- CV export updated: `cfp/exports/cv/conference_presentations.md`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
