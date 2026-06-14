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

## Privacy Posture

The Pages builder is static and client-side only. It has no analytics, cookies, uploads, accounts, backend API calls, or server-side storage.

If you fork this repository and run the workflows, you control the data processing in your fork. Bluesky handles, RSS selections, seen-link state files, recipient email addresses, issue bodies, abstracts, bios, CV exports, and ORCID exports may be personal data depending on context. See [PRIVACY.md](PRIVACY.md).

## Quick Start

1. Open the Pages builder and generate your files.
2. Put the JSON profile under `config/profiles/`.
3. Put the generated watchlist and OPML files where the profile points.
4. Add GitHub repository secrets:
   - `SMTP_USER`
   - `SMTP_PASS`
   - `TO_EMAIL`
5. Run the `Daily Academic Radar` workflow manually.

For public forks, avoid committing real runtime state, private watchlists, exported feed lists, or personal CFP archive records unless you intentionally want them public.

Local preview:

```bash
python radar.py --config config/profiles/hps.json --dry-run --output-html radar_digest.html --output-json radar_items.json
```

Release hygiene check:

```bash
python scripts/validate_release.py
```

## Repository Map

- `site/`: static Pages config builder.
- `config/profiles/`: radar profile examples.
- `examples/`: starter watchlist and OPML files.
- `radar.py`: main academic radar runner.
- `audit_feeds.py`: OPML audit helper.
- `cfp/`: generated CFP ledger surface.
- `scripts/`: CFP parsing, ingestion, backfill, and deadline digest scripts.
- `.github/workflows/`: GitHub Actions automation.
- `docs/`: project notes, release notes, and parser documentation.

## Release Notes

See [docs/RELEASE.md](docs/RELEASE.md) and [CHANGELOG.md](CHANGELOG.md).
