import json
import py_compile
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_PATHS = [
    "sent_items.json",
    "black_studies_sent.json",
    "feedly_active.opml",
    "bsky_watchlist_core.txt",
    "black_studies_radar.py",
    "config/profiles/black_studies.json",
]

FORBIDDEN_PARTS = [
    "cfp/backfill/",
    "cfp/exports/",
]

FORBIDDEN_TEXT = [
    "Koh-i-Noor",
    "Story-Maskelyne",
    "weighing-the-koh-i-noor",
    "black_studies",
    "black-studies",
    "Black Studies CFP",
    "Personal research link hub",
    "British Library Main Catalogue",
]

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".opml",
    ".py",
    ".txt",
    ".yml",
    ".yaml",
}


def repo_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if ".git/" in rel or "__pycache__/" in rel:
            continue
        yield path, rel


def check_forbidden_paths():
    errors = []
    existing = {rel for _, rel in repo_files()}

    for rel in FORBIDDEN_PATHS:
        if rel in existing:
            errors.append(f"forbidden release file exists: {rel}")

    for rel in existing:
        if any(part in rel for part in FORBIDDEN_PARTS):
            errors.append(f"forbidden generated archive/export path exists: {rel}")

    return errors


def check_forbidden_text():
    errors = []
    for path, rel in repo_files():
        if rel == "scripts/validate_release.py":
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for needle in FORBIDDEN_TEXT:
            if needle in text:
                errors.append(f"forbidden text {needle!r} found in {rel}")
    return errors


def check_structured_files():
    errors = []
    try:
        json.loads((ROOT / "config/profiles/hps.json").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"config/profiles/hps.json is invalid JSON: {exc}")

    try:
        ET.parse(ROOT / "examples/feedly.example.opml")
    except Exception as exc:
        errors.append(f"examples/feedly.example.opml is invalid XML: {exc}")

    return errors


def check_python_compile():
    errors = []
    for path, rel in repo_files():
        if path.suffix != ".py":
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            errors.append(f"{rel} does not compile: {exc}")
    return errors


def check_privacy_workflow_defaults():
    errors = []

    expectations = {
        ".github/workflows/radar.yml": [
            "vars.UPLOAD_RADAR_DIGEST == 'true'",
            "vars.COMMIT_RADAR_STATE == 'true'",
            "scripts/write_audit_event.py",
            "retention-days: 30",
        ],
        ".github/workflows/cfp_ingest_archive.yml": [
            "vars.PERSIST_CFP_LEDGER == 'true'",
            "vars.COMMENT_CFP_ISSUES == 'true'",
            "scripts/write_audit_event.py",
            "retention-days: 30",
        ],
        ".github/workflows/cfp_backfill_archive.yml": [
            "vars.PERSIST_CFP_LEDGER == 'true'",
            "vars.COMMENT_CFP_ISSUES == 'true'",
            "vars.CLOSE_CFP_ISSUES == 'true'",
            "scripts/write_audit_event.py",
            "retention-days: 30",
        ],
        ".github/workflows/cfp_deadline_digest.yml": [
            "vars.PERSIST_CFP_LEDGER == 'true'",
            "scripts/write_audit_event.py",
            "retention-days: 30",
        ],
        ".github/workflows/cfp_parse_draft.yml": [
            "upload_artifact",
            "inputs.upload_artifact == true",
            "scripts/write_audit_event.py",
            "retention-days: 30",
        ],
    }

    for rel, needles in expectations.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"privacy workflow check missing file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"privacy workflow guard {needle!r} missing from {rel}")

    return errors


def main():
    errors = []
    errors.extend(check_forbidden_paths())
    errors.extend(check_forbidden_text())
    errors.extend(check_structured_files())
    errors.extend(check_python_compile())
    errors.extend(check_privacy_workflow_defaults())

    if errors:
        print("Release validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Release validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
