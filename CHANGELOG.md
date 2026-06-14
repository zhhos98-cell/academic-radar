# Changelog

## Unreleased

- Added a local first-run CLI setup flow that creates a private `.radar/` profile, OPML file, Bluesky watchlist, and seen-link state path.
- Added reusable first-run presets for HPS, history of knowledge, scientific instruments, photography history, Romantic science, and book history.
- Added `academic-radar --list-presets` and `academic-radar --init --preset ...` support.
- Added setup tests for first-run file generation, RSS argument parsing, Bluesky handle normalization, OPML escaping, and preset merging.
- Ignored `.radar/` runtime files by default.

## v0.1.0 - Prototype

- Added a GitHub Pages config builder for generating radar profiles, Bluesky watchlists, and OPML feed lists.
- Added a reusable radar CLI with dry-run, no-email, no-state, HTML output, and JSON output modes.
- Split the radar runner into a reusable `academic_radar` package with a thin `radar.py` compatibility entry point.
- Added Python package metadata and an `academic-radar` console command.
- Added reusable CFP parsing, archive, and deadline digest workflows.
- Added example input files for public use.
- Added release hygiene validation for privacy-sensitive files and known personal archive strings.
- Added no-network unit tests for core scoring, rendering, and state behavior.
- Added default-off persistence controls and minimal workflow audit artifacts for privacy accountability.
- Removed personal runtime state, feed exports, watchlists, topic-specific automation, and backfilled CFP records from the public release surface.
