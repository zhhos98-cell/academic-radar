# Release Notes

## v0.2.0 - 2026-06-14

Academic Radar v0.2.0 turns the prototype into a more usable local-first starter. The release focuses on first-run setup, reusable field presets, no-network inspection, diagnostics, and clearer privacy-preserving defaults.

Highlights:

- Added `academic-radar --init` to generate private runtime files under `.radar/`.
- Added reusable presets for HPS, history of knowledge, scientific instruments, photography history, Romantic science, and book history.
- Added `academic-radar --list-presets` for preset discovery.
- Added `academic-radar --summary` for no-network inspection of profile names, paths, source limits, scoring term counts, and Bluesky query counts.
- Added `academic-radar --doctor` for no-network diagnostics of local paths, source-list parseability, positive integer settings, scoring terms, negative-term overlap, and Bluesky queries.
- Added `docs/LOCAL_FIRST_RUN.md` with local setup, virtualenv, private profile generation, dry preview, email setup, privacy checklist, and troubleshooting notes.
- Added setup, CLI smoke, summary, and diagnostics tests for the local-first path.
- Ignored `.radar/` runtime files by default.

Recommended first-run flow:

```bash
pip install .
academic-radar --init --preset hps
academic-radar --config .radar/profiles/local.json --summary
academic-radar --config .radar/profiles/local.json --doctor
academic-radar --config .radar/profiles/local.json --dry-run
```

Privacy note:

- `.radar/` is ignored by default for local private profiles, OPML exports, Bluesky watchlists, and seen-link state files.
- Public forks should still avoid committing real runtime state, private watchlists, exported feed lists, email credentials, or personal CFP archive records.
- Repository persistence remains default-off through workflow variables.
- Review `PRIVACY.md`, `docs/ACCOUNTABILITY.md`, and `docs/LOCAL_FIRST_RUN.md` before enabling persistence or email automation.

Release checklist:

```bash
python scripts/validate_release.py
python -m unittest discover -s tests
```

## v0.1.0 - Prototype

Academic Radar is a reusable starter for monitoring CFPs, academic events, journal calls, new books, and field-specific scholarly updates from RSS feeds and Bluesky.

Highlights:

- Static Pages config builder in `site/`.
- Modular Python package with a compatibility `radar.py` CLI entry point.
- Installable `academic-radar` console command via `pyproject.toml`.
- Generic radar CLI and workflow driven by a JSON profile.
- CFP issue templates, parsers, archive workflows, and deadline digest generation.
- Example OPML and Bluesky watchlist files in `examples/`.
- Release hygiene validation for privacy-sensitive files and personal archive remnants.
- No-network unit tests for scoring, rendering, and state behavior.
- Default-off persistence for radar artifacts, state files, CFP ledger records, CFP comments, and parsed CFP draft artifacts.
- Minimal JSONL processing audit artifacts for workflow accountability without storing content-bearing fields.

Privacy note:

- Do not publish real state files, private watchlists, exported feed lists, email credentials, or personal CFP archive records.
- Use repository secrets for SMTP credentials.
- Public forks should leave persistence variables unset unless repository storage is intentional.
- Review `PRIVACY.md` and `docs/ACCOUNTABILITY.md` before enabling persistence.

GDPR-oriented note:

- The hosted Pages builder is static and client-side only: it has no analytics, cookies, uploads, accounts, or server-side storage.
- A fork owner who configures workflows, email delivery, watchlists, or state commits is responsible for the personal data they process.
- Bluesky handles, RSS selections, seen-link history, recipient email addresses, issue bodies, abstracts, and bios may be personal data depending on context.
- Public forks should avoid committing runtime state or personal CFP records unless the owner intentionally wants them public.
