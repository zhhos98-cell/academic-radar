from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


ROOT = Path.cwd()
CFP_DIR = ROOT / "cfp"
BACKFILL_DIR = CFP_DIR / "backfill"
EXPORT_DIR = CFP_DIR / "exports" / "orcid"
DASHBOARD = CFP_DIR / "README.md"
COMMENT_PATH = Path("/tmp/cfp_backfill_comment.md")


FIELD_MAP = {
    "presentation_title": "Presentation title",
    "conference_title": "Conference title",
    "conference_website": "Conference website",
    "programme_url": "Programme URL",
    "proceedings_url": "Proceedings",
    "location": "Location",
    "host_institution": "Host institution",
    "event_dates": "Event dates",
    "presentation_date": "Presentation date",
    "role": "Role",
    "project_link": "Project link",
    "abstract": "Abstract text",
    "bio": "Bio text",
    "notes": "Notes",
    "exports": "Export options",
}


def read_event() -> dict[str, Any]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise RuntimeError("GITHUB_EVENT_PATH is not set.")
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def parse_issue_form(body: str) -> dict[str, str]:
    """
    GitHub Issue Forms render as markdown sections:

    ### Field label
    value

    This parser collects each heading and its following body.
    """
    fields: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_heading, current_lines
        if current_heading is None:
            return
        value = "\n".join(current_lines).strip()
        if value == "_No response_":
            value = ""
        fields[current_heading] = value
        current_heading = None
        current_lines = []

    for line in body.splitlines():
        if line.startswith("### "):
            flush()
            current_heading = line[4:].strip()
            current_lines = []
        else:
            if current_heading is not None:
                current_lines.append(line)

    flush()
    return fields


def pick(parsed: dict[str, str], starts_with: str) -> str:
    for heading, value in parsed.items():
        if heading.strip().lower().startswith(starts_with.lower()):
            return value.strip()
    return ""


def parse_exports(text: str) -> dict[str, bool]:
    lower = text.lower()
    return {
        "cv": "include in cv conference list" in lower and "- [x]" in lower,
        "orcid_ready": "include in orcid-ready export" in lower and "- [x]" in lower,
        "abstract_archive": "include abstract in local archive" in lower and "- [x]" in lower,
    }


def slugify(text: str, fallback: str = "untitled") -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80] or fallback


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w’'-]+\b", text))


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
    path.write_text(text.strip() + ("\n" if text.strip() else ""), encoding="utf-8")


def yaml_quote(value: Any) -> str:
    if value is None:
        return '""'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    value = str(value)
    if "\n" in value:
        return "|\n" + "\n".join(f"  {line}" for line in value.splitlines())
    return json.dumps(value, ensure_ascii=False)


def write_metadata_yml(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []

    def emit_dict(d: dict[str, Any], indent: int = 0) -> None:
        pad = " " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{pad}{key}:")
                emit_dict(value, indent + 2)
            elif isinstance(value, list):
                lines.append(f"{pad}{key}:")
                if value:
                    for item in value:
                        lines.append(f"{pad}  - {yaml_quote(item)}")
                else:
                    lines.append(f"{pad}  []")
            else:
                rendered = yaml_quote(value)
                if rendered.startswith("|\n"):
                    lines.append(f"{pad}{key}: {rendered}")
                else:
                    lines.append(f"{pad}{key}: {rendered}")

    emit_dict(data)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_date_for_sort(value: str) -> str:
    if not value:
        return ""
    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    if match:
        return match.group(0)
    match = re.search(r"\d{4}", value)
    if match:
        return match.group(0)
    return value


def markdown_link(label: str, path: Path | None) -> str:
    if not path:
        return ""
    rel = path.as_posix()
    return f"[{label}]({rel})"


def escape_table(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def build_dashboard() -> None:
    records: list[dict[str, Any]] = []
    for meta_path in sorted(BACKFILL_DIR.glob("*/metadata.json")):
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        data["_record_dir"] = meta_path.parent.relative_to(CFP_DIR).as_posix()
        records.append(data)

    records.sort(
        key=lambda r: parse_date_for_sort(
            r.get("presentation", {}).get("presentation_date")
            or r.get("conference", {}).get("event_start")
            or ""
        ),
        reverse=True,
    )

    lines: list[str] = [
        "# CFP Ledger / 投稿与会议台账",
        "",
        "自动生成。手动改 metadata 时，重新跑 workflow 或下次补档会刷新本页。",
        "",
        "## Active / 进行中",
        "",
        "下一步再接入未来 CFP tracker。",
        "",
        "<details>",
        f"<summary>Backfilled / 补档 {len(records)}</summary>",
        "",
    ]

    if not records:
        lines.append("No backfilled records yet.")
        lines.append("")
    else:
        lines.extend(
            [
                "| Date | Presentation | Conference | Location | Abstract | Bio | Programme | Proceedings | ORCID |",
                "|---|---|---|---|---|---|---|---|---|",
            ]
        )
        for r in records:
            record_dir = Path(r["_record_dir"])
            p = r.get("presentation", {})
            c = r.get("conference", {})
            exports = r.get("exports", {})

            date = p.get("presentation_date") or c.get("event_start") or ""
            title = p.get("title") or ""
            conf = c.get("title") or ""
            location = c.get("location") or ""
            programme_url = c.get("programme_url") or ""
            proceedings_url = c.get("proceedings_url") or ""

            abstract_link = markdown_link("abstract", record_dir / "abstract.txt")
            bio_link = markdown_link("bio", record_dir / "bio.txt")
            programme = f"[programme]({programme_url})" if programme_url else ""
            proceedings = f"[proceedings]({proceedings_url})" if proceedings_url else ""
            orcid = "ready" if exports.get("orcid_ready") else ""

            lines.append(
                "| "
                + " | ".join(
                    [
                        escape_table(date),
                        escape_table(title),
                        escape_table(conf),
                        escape_table(location),
                        abstract_link,
                        bio_link,
                        programme,
                        proceedings,
                        escape_table(orcid),
                    ]
                )
                + " |"
            )
        lines.append("")

    lines.extend(["</details>", ""])
    DASHBOARD.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD.write_text("\n".join(lines), encoding="utf-8")


def build_orcid_export() -> None:
    records: list[dict[str, Any]] = []

    for meta_path in sorted(BACKFILL_DIR.glob("*/metadata.json")):
        data = json.loads(meta_path.read_text(encoding="utf-8"))
        if not data.get("exports", {}).get("orcid_ready"):
            continue

        presentation = data.get("presentation", {})
        conference = data.get("conference", {})

        url = (
            conference.get("proceedings_url")
            or conference.get("programme_url")
            or conference.get("website_url")
            or ""
        )

        records.append(
            {
                "record_type": "conference-presentation",
                "title": presentation.get("title", ""),
                "role": presentation.get("role", ""),
                "presentation_date": presentation.get("presentation_date", ""),
                "conference_title": conference.get("title", ""),
                "host_institution": conference.get("host_institution", ""),
                "location": conference.get("location", ""),
                "event_start": conference.get("event_start", ""),
                "event_end": conference.get("event_end", ""),
                "url": url,
                "source_issue": data.get("source_issue", ""),
                "local_id": data.get("id", ""),
            }
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "note": "ORCID-ready export. Manual review recommended before entering into ORCID.",
        "records": records,
    }
    (EXPORT_DIR / "orcid_ready.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
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

    if not presentation_title or not conference_title:
        raise RuntimeError("Missing required fields: presentation title or conference title.")

    conference_website = pick(parsed, "Conference website")
    programme_url = pick(parsed, "Programme URL")
    proceedings_url = pick(parsed, "Proceedings")
    location = pick(parsed, "Location")
    host_institution = pick(parsed, "Host institution")
    event_dates = pick(parsed, "Event dates")
    presentation_date = pick(parsed, "Presentation date")
    role = pick(parsed, "Role")
    project_link = pick(parsed, "Project link")
    abstract = pick(parsed, "Abstract text")
    bio = pick(parsed, "Bio text")
    notes = pick(parsed, "Notes")
    exports_raw = pick(parsed, "Export options")
    exports = parse_exports(exports_raw)

    slug = f"issue-{issue_number}-{slugify(presentation_title)}"
    record_dir = BACKFILL_DIR / slug
    record_dir.mkdir(parents=True, exist_ok=True)

    write_text(record_dir / "title.txt", presentation_title)
    write_text(record_dir / "abstract.txt", abstract)
    write_text(record_dir / "bio.txt", bio)
    write_text(record_dir / "notes.txt", notes)

    file_hashes = {}
    for name in ["title.txt", "abstract.txt", "bio.txt", "notes.txt"]:
        path = record_dir / name
        file_hashes[name] = sha256_file(path)

    bundle_source = "\n".join(f"{name}:{digest}" for name, digest in sorted(file_hashes.items()))
    bundle_sha = sha256_text(bundle_source)

    metadata = {
        "id": slug,
        "record_type": "conference-presentation",
        "status": "completed",
        "created_at": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "source_issue": issue_number,
        "source_issue_url": issue_url,
        "presentation": {
            "title": presentation_title,
            "role": role,
            "presentation_date": presentation_date,
            "project_link": project_link,
            "abstract_words": word_count(abstract),
            "bio_words": word_count(bio),
        },
        "conference": {
            "title": conference_title,
            "host_institution": host_institution,
            "location": location,
            "event_dates_raw": event_dates,
            "event_start": "",
            "event_end": "",
            "website_url": conference_website,
            "programme_url": programme_url,
            "proceedings_url": proceedings_url,
        },
        "texts": {
            "title_file": "title.txt",
            "abstract_file": "abstract.txt",
            "bio_file": "bio.txt",
            "notes_file": "notes.txt",
        },
        "hashes": {
            "files": file_hashes,
            "bundle_sha256": bundle_sha,
        },
        "exports": exports,
        "orcid": {
            "include": exports.get("orcid_ready", False),
            "work_type": "conference-presentation",
            "sync_status": "ready_for_manual_entry" if exports.get("orcid_ready") else "",
        },
    }

    (record_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_metadata_yml(record_dir / "metadata.yml", metadata)

    sha_lines = [f"{digest}  {name}" for name, digest in sorted(file_hashes.items())]
    sha_lines.append(f"{bundle_sha}  BUNDLE")
    (record_dir / "SHA256SUMS.txt").write_text("\n".join(sha_lines) + "\n", encoding="utf-8")

    build_dashboard()
    build_orcid_export()

    COMMENT_PATH.write_text(
        "\n".join(
            [
                "Archived this backfilled conference record.",
                "",
                f"- Folder: `cfp/backfill/{slug}/`",
                f"- Abstract words: `{word_count(abstract)}`",
                f"- Bio words: `{word_count(bio)}`",
                f"- Bundle SHA-256: `{bundle_sha}`",
                "- Dashboard updated: `cfp/README.md`",
                "- ORCID-ready export updated: `cfp/exports/orcid/orcid_ready.json`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
