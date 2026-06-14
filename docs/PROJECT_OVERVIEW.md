# Academic Radar Project Overview

This repository is a reusable academic monitoring starter. It currently has four working parts:

1. `site/`
   - A static GitHub Pages config builder.
   - Generates a JSON radar profile, a Bluesky watchlist, and an OPML feed list in the browser.
   - Does not call a backend or store visitor input.

2. `academic_radar/` and `radar.py`
   - Reusable package plus a compatibility CLI entry point.
   - Loads its profile from `config/profiles/hps.json` by default.
   - Override the profile with the `RADAR_CONFIG` environment variable.
   - Reads RSS sources and Bluesky handles from the files named in the profile.
   - Searches public Bluesky posts with topic queries in the profile.
   - Sends an email digest and records seen links in the configured state file.

3. `audit_feeds.py`
   - Audits OPML feeds and separates active feeds from stale or unknown feeds.
   - Defaults to `feedly.opml` when present.
   - Falls back to `feedly_active.opml` when available.

4. CFP Ledger
   - Issue forms live in `.github/ISSUE_TEMPLATE/`.
   - Workflows live in `.github/workflows/cfp_ingest_archive.yml` and `.github/workflows/cfp_backfill_archive.yml`.
   - Scripts live in `scripts/cfp_ingest_archive.py` and `scripts/cfp_backfill_archive.py`.
   - Generated records live under `cfp/`.
   - Deadline reminders are summarized in `cfp/deadlines.md`.
   - CFP text and URLs can be pre-parsed with `scripts/cfp_parse_text.py`; see `docs/CFP_PARSER.md`.

## Config Profiles

Radar profiles live in `config/profiles/`.

- `hps.json`: an example profile for history of science / HPS.
- `examples/feedly.example.opml`: starter RSS feed list.
- `examples/bsky_watchlist.example.txt`: starter Bluesky watchlist.

Profiles control:

- input files, such as OPML, Bluesky watchlist, and seen-link state files;
- age limits and per-source item limits;
- scoring terms;
- negative filters;
- Bluesky queries.

The script still includes safe defaults. If a profile file is missing, the script falls back to its built-in configuration.

## Required GitHub Secrets

The email digest workflow needs these repository secrets:

- `SMTP_USER`: Gmail address or SMTP username.
- `SMTP_PASS`: SMTP app password.
- `TO_EMAIL`: destination email address.

The CFP workflows use `GITHUB_TOKEN`, which GitHub Actions provides automatically.

## Workflows

- `Daily Academic Radar`: runs manually by default. Fork users can add a schedule after setting their own profile and secrets.
- `Audit Feedly OPML`: runs manually and uploads OPML audit artifacts.
- `CFP Ingest Archive`: runs when a CFP issue is opened or edited.
- `CFP Backfill Archive`: runs when a backfill issue is opened or edited.
- `CFP Deadline Digest`: runs daily and updates `cfp/deadlines.md`.
- `CFP Parse Draft`: runs manually and uploads a draft issue body from a CFP URL or pasted text.
- `Deploy Pages`: publishes the config builder from `site/`.
- `Release Hygiene Check`: blocks accidental reintroduction of runtime state, generated personal archives, or known personal example strings.
  It also runs the no-network unit tests in `tests/`.

## Public Release Hygiene

Keep personal runtime data out of the public repository:

- real feed exports;
- real Bluesky watchlists;
- seen-link state files;
- private notes, abstracts, bios, CV exports, and ORCID exports;
- SMTP credentials or email addresses.

Use repository secrets for credentials, and use the files in `examples/` only as starters.

## CFP Ledger Flow

Use `Add CFP` for future opportunities:

1. Open a new issue with the `Add CFP` form.
2. Fill in title, type, source URL, deadlines, status, priority, notes, and tracking options.
3. The workflow creates a structured record under `cfp/records/<status>/`.
4. `cfp/README.md` is regenerated as the dashboard.
5. `cfp/deadlines.md` can be regenerated to show upcoming, overdue, approximate, and missing deadlines.

Use `Backfill conference` for past presentations:

1. Open a new issue with the `Backfill conference` form.
2. Fill in presentation title, conference title, event details, abstract, bio, and export options.
3. The workflow creates a record under `cfp/backfill/`.
4. ORCID-ready and CV-ready exports are regenerated under `cfp/exports/`.

## Next Generalization Step

- Add packaging metadata so the CLI can be installed with `pipx` or bundled as a small desktop executable.
- Add a local "first run" setup flow that writes a profile, OPML file, and Bluesky watchlist without exposing private data.
- Promote the CFP parser from draft generation to optional issue creation once the rules feel reliable.
- Later, wrap the CLI with a packaged desktop or web interface.
