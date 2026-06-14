# Changelog

## v0.2.0 - 2026-06-14

- Added a Windows desktop GUI for form-based setup, local file generation, no-network summary, diagnostics, dry-run previews, and opening generated HTML results without PowerShell.
- Added a GitHub Actions workflow that builds `AcademicRadar.exe` with PyInstaller and uploads `AcademicRadar-Windows.zip` as a workflow artifact.
- Added `academic-radar-gui` and `academic_radar_gui.py` entry points for launching or packaging the desktop GUI.
- Added GUI packaging smoke tests that compile the desktop GUI sources without opening a display window.
- Added `docs/WINDOWS_APP.md` with download, first-run, workspace, button, privacy, and build instructions for the desktop app.
- Improved the Pages web builder with beginner-facing instructions, a privacy note, a three-step workflow, clearer generated-file labels, and links to the repository, local first-run guide, and releases.
- Reduced the Pages web builder module structure by replacing card-heavy workflow panels with a single editorial process line, compressing the responsible-use notice into a text strip, and renaming sections to `Build Profile`, `Review Files`, and `Run Locally`.
- Shifted the Pages web builder visual design toward a Rubin-inspired UI language with deep vermilion, saffron, marigold, plum-black, warm paper tones, darker text hierarchy, and fewer boxed modules.
- Added a responsible-use notice reminding users to check source terms, platform rules, institutional policies, data-protection duties, and private runtime file handling before automation.
- Added bilingual English/Chinese interface text and a non-persistent language switcher for the Pages web builder.
- Refined the Pages web builder typography with IM Fell English, EB Garamond, and Chinese serif fallbacks.
- Adjusted the Pages web builder layout toward lighter Apple-style spacing with an early-modern book-page tone, subtler shadows, balanced heading sizes, and softer compliance styling.
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
