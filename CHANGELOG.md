# Changelog

## Unreleased

- Added a local first-run CLI setup flow that creates a private `.radar/` profile, OPML file, Bluesky watchlist, and seen-link state path.
- Added a `docs/LOCAL_FIRST_RUN.md` walkthrough for local installation, private profile generation, no-network inspection, diagnostics, dry previews, email setup, and privacy checks.
- Added reusable first-run presets for HPS, history of knowledge, scientific instruments, photography history, Romantic science, and book history.
- Added `academic-radar --list-presets` and `academic-radar --init --preset ...` support.
- Added `academic-radar --summary` for no-network inspection of profile names, local paths, source limits, scoring term counts, and Bluesky query counts.
- Added `academic-radar --doctor` no-network diagnostics for local paths, source-list parseability, settings, scoring terms, and query configuration.
- Added setup tests for first-run file generation, RSS argument parsing, Bluesky handle normalization, OPML escaping, and preset merging.
- Added CLI smoke tests for preset listing, profile summaries, and first-run setup output.
- Added profile summary tests for profile name preservation and no-network summary output.
- Added diagnostics tests for valid local source files, missing input warnings, and invalid setting errors.
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
