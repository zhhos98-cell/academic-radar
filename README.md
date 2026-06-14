# Academic Radar

Academic Radar is a reusable starter for monitoring CFPs, academic events, journal calls, new books, and field-specific scholarly updates from RSS feeds and Bluesky.

The first public prototype is a static config builder:

https://zhhos98-cell.github.io/academic-radar/

## What It Does

- Builds a JSON radar profile from field terms, negative filters, Bluesky queries, and source limits.
- Generates a Bluesky watchlist file.
- Generates an OPML feed list.
- Provides GitHub Actions workflows for running the radar and maintaining a CFP ledger.
- Includes CFP issue templates, parsers, archive automation, and a deadline digest.
- Provides a local first-run CLI setup flow for private, ignored runtime files.

## Privacy Posture

The Pages builder is static and client-side only. It has no analytics, cookies, uploads, accounts, backend API calls, or server-side storage.

If you fork this repository and run the workflows, you control the data processing in your fork. Bluesky handles, RSS selections, seen-link state files, recipient email addresses, issue bodies, abstracts, bios, CV exports, and ORCID exports may be personal data depending on context. See [PRIVACY.md](PRIVACY.md) and [docs/ACCOUNTABILITY.md](docs/ACCOUNTABILITY.md).

By default, workflows avoid repository persistence for content-bearing outputs. Radar digest uploads, seen-link state commits, CFP ledger commits, issue comments, and parsed CFP draft uploads must be explicitly enabled.

## Quick Start

For a local private setup, generate ignored first-run files under `.radar/`:

```bash
pip install .
academic-radar --init \
  --field-term "photographic history" \
  --bsky-handle "@example.bsky.social" \
  --rss-feed "Example=https://example.org/feed.xml"
academic-radar --config .radar/profiles/local.json --dry-run --output-html tmp/radar_digest.html --output-json tmp/radar_items.json
```

For the static Pages builder:

1. Open the Pages builder and generate your files.
2. Put the JSON profile under `config/profiles/`.
3. Put the generated watchlist and OPML files where the profile points.
4. Add GitHub repository secrets:
   - `SMTP_USER`
   - `SMTP_PASS`
   - `TO_EMAIL`
5. Run the `Daily Academic Radar` workflow manually.

For public forks, avoid committing real runtime state, private watchlists, exported feed lists, or personal CFP archive records unless you intentionally want them public.

Installable CLI:

```bash
pip install .
academic-radar --config config/profiles/hps.json --dry-run --output-html tmp/radar_digest.html --output-json tmp/radar_items.json
```

Local preview:

```bash
python radar.py --config config/profiles/hps.json --dry-run --output-html tmp/radar_digest.html --output-json tmp/radar_items.json
```

Release hygiene check:

```bash
python scripts/validate_release.py
python -m unittest discover -s tests
```

## Repository Map

- `site/`: static Pages config builder.
- `academic_radar/`: reusable Python package for config, sources, scoring, rendering, state, email, CLI setup, and CLI code.
- `pyproject.toml`: Python package metadata and `academic-radar` console command.
- `LICENSE`: MIT license for reuse.
- `config/profiles/`: radar profile examples.
- `examples/`: starter watchlist and OPML files.
- `radar.py`: compatibility entry point for the package CLI.
- `audit_feeds.py`: OPML audit helper.
- `cfp/`: generated CFP ledger surface.
- `scripts/`: CFP parsing, ingestion, backfill, and deadline digest scripts.
- `.github/workflows/`: GitHub Actions automation.
- `tests/`: no-network unit tests for core scoring, rendering, setup, and state behavior.
- `docs/`: project notes, accountability model, release notes, and parser documentation.

## Release Notes

See [docs/RELEASE.md](docs/RELEASE.md) and [CHANGELOG.md](CHANGELOG.md).
