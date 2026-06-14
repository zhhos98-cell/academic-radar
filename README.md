# Academic Radar

Academic Radar is a reusable starter for monitoring CFPs, academic events, journal calls, new books, and field-specific scholarly updates from RSS feeds and Bluesky.

Public web builder:

https://zhhos98-cell.github.io/academic-radar/

Use the web builder to generate a JSON radar profile, Bluesky watchlist, and OPML feed list in the browser. GitHub Releases provide version notes and source snapshots.

## What It Does

- Builds a JSON radar profile from field terms, negative filters, Bluesky queries, and source limits.
- Generates a Bluesky watchlist file.
- Generates an OPML feed list.
- Provides GitHub Actions workflows for running the radar and maintaining a CFP ledger.
- Includes CFP issue templates, parsers, archive automation, and a deadline digest.
- Provides a local first-run CLI setup flow for ignored runtime files.
- Includes built-in academic presets for reusable field-specific profiles.
- Provides no-network profile summaries and diagnostics before fetching RSS or Bluesky data.

## Privacy Posture

The Pages builder is static and client-side only. It has no analytics, cookies, uploads, accounts, backend API calls, or server-side storage.

If you fork this repository and run the workflows, you control the data processing in your fork. Bluesky handles, RSS selections, seen-link state files, recipient email addresses, issue bodies, abstracts, bios, CV exports, and ORCID exports may be personal data depending on context. See [PRIVACY.md](PRIVACY.md) and [docs/ACCOUNTABILITY.md](docs/ACCOUNTABILITY.md).

By default, workflows avoid repository persistence for content-bearing outputs. Radar digest uploads, seen-link state commits, CFP ledger commits, issue comments, and parsed CFP draft uploads must be explicitly enabled.

## Quick Start

For a local setup, generate ignored first-run files under `.radar/`:

```bash
pip install .
academic-radar --init \
  --preset hps \
  --preset photography-history \
  --preset scientific-instruments \
  --field-term "household experiment" \
  --bsky-handle "@example.bsky.social" \
  --rss-feed "Example=https://example.org/feed.xml"
academic-radar --config .radar/profiles/local.json --summary
academic-radar --config .radar/profiles/local.json --doctor
academic-radar --config .radar/profiles/local.json --dry-run --output-html tmp/radar_digest.html --output-json tmp/radar_items.json
```

For a fuller walkthrough, see [Local First Run](docs/LOCAL_FIRST_RUN.md).

List available presets:

```bash
academic-radar --list-presets
```

Current presets are `hps`, `history-of-knowledge`, `scientific-instruments`, `photography-history`, `romantic-science`, and `book-history`. Presets can be repeated or passed as a comma-separated list.

Inspect a profile before running live collection:

```bash
academic-radar --config config/profiles/hps.json --summary
```

The summary command reports the profile name, configured local paths, source limits, scoring term counts, and Bluesky query counts. It does not fetch network data.

Run diagnostics before fetching live data:

```bash
academic-radar --config config/profiles/hps.json --doctor
```

The diagnostics command checks configured local paths, source-list parseability, positive integer settings, scoring term availability, negative-term overlap, and Bluesky query presence. It does not fetch network data.

For the static Pages builder:

1. Open the web builder and generate your files.
2. Download the JSON profile, Bluesky watchlist, and OPML file.
3. Keep runtime files under `.radar/` for local use, or put generated files where your profile points.
4. Add delivery settings only if you later enable email automation.
5. Run locally with `--summary`, `--doctor`, and `--dry-run` before sending email or writing state.

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

- `site/`: static Pages web builder.
- `academic_radar/`: reusable Python package for config, sources, scoring, rendering, state, email, presets, profile summaries, diagnostics, CLI setup, and CLI code.
- `pyproject.toml`: Python package metadata and `academic-radar` console command.
- `LICENSE`: MIT license for reuse.
- `config/profiles/`: radar profile examples.
- `examples/`: starter watchlist and OPML files.
- `radar.py`: compatibility entry point for the package CLI.
- `audit_feeds.py`: OPML audit helper.
- `cfp/`: generated CFP ledger surface.
- `scripts/`: CFP parsing, ingestion, backfill, and deadline digest scripts.
- `.github/workflows/`: GitHub Actions automation.
- `tests/`: no-network unit tests for core scoring, rendering, setup, presets, profile summaries, diagnostics, and state behavior.
- `docs/`: project notes, first-run setup guide, accountability model, release notes, and parser documentation.

## Release Notes

See [docs/RELEASE.md](docs/RELEASE.md) and [CHANGELOG.md](CHANGELOG.md).
