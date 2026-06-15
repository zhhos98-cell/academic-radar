# Release Notes

## v0.2.0 - 2026-06-14

Academic Radar v0.2.0 turns the prototype into a more usable local-first starter. The release focuses on the public web builder, a Windows desktop app, first-run setup, reusable field presets, no-network inspection, diagnostics, and clearer privacy-preserving defaults.

Web builder:

https://zhhos98-cell.github.io/academic-radar/

Windows desktop app:

Download `AcademicRadar-Windows.zip` from release assets when available, unzip it, and double-click `AcademicRadar.exe`. The app provides a form-based interface for creating local files, running summary and diagnostics, running dry previews, and opening generated HTML results without PowerShell.

Highlights:

- Added a Windows desktop GUI for form-based setup, local file generation, no-network summary, diagnostics, dry-run previews, and opening generated HTML results without PowerShell.
- Added a GitHub Actions workflow that builds `AcademicRadar.exe` with PyInstaller and uploads `AcademicRadar-Windows.zip` as a workflow artifact.
- Added a `Build Release` workflow that publishes Python package artifacts and `AcademicRadar-Windows.zip` to GitHub Releases.
- Added `academic-radar-gui` and `academic_radar_gui.py` entry points for launching or packaging the desktop GUI.
- Added `docs/WINDOWS_APP.md` with download, first-run, workspace, button, privacy, and build instructions for the desktop app.
- Added `docs/RELEASE_PROCESS.md` with tag-based and manual release publishing instructions.
- Improved the Pages web builder with beginner-facing instructions, a privacy note, a three-step workflow, clearer generated-file labels, and links to the repository, local first-run guide, and releases.
- Added a responsible-use notice reminding users to check source terms, platform rules, institutional policies, data-protection duties, and private runtime file handling before automation.
- Added bilingual English/Chinese interface text and a non-persistent language switcher for the Pages web builder.
- Refined the Pages web builder typography with IM Fell English, EB Garamond, and Chinese serif fallbacks.
- Added `academic-radar --init` to generate private runtime files under `.radar/`.
- Added reusable presets for HPS, history of knowledge, scientific instruments, photography history, Romantic science, and book history.
- Added `academic-radar --list-presets` for preset discovery.
- Added `academic-radar --summary` for no-network inspection of profile names, paths, source limits, scoring term counts, and Bluesky query counts.
- Added `academic-radar --doctor` for no-network diagnostics of local paths, source-list parseability, positive integer settings, scoring terms, negative-term overlap, and Bluesky queries.
- Added setup, CLI smoke, summary, and diagnostics tests for the local-first path.
- Ignored `.radar/` runtime files by default.

Recommended GUI flow:

1. Download `AcademicRadar-Windows.zip`.
2. Unzip it.
3. Double-click `AcademicRadar.exe`.
4. Choose a workspace folder.
5. Fill the form, then click `Save files`, `Summary`, `Doctor`, or `Dry run`.

Recommended CLI first-run flow:

```bash
pip install .
academic-radar --init --preset hps
academic-radar --config .radar/profiles/local.json --summary
academic-radar --config .radar/profiles/local.json --doctor
academic-radar --config .radar/profiles/local.json --dry-run
```

Privacy note:

- `.radar/` is ignored by default for local private profiles, OPML exports, Bluesky watchlists, and seen-link state files.
- The desktop app writes runtime files locally under the workspace selected by the user.
- Public forks should still avoid committing real runtime state, private watchlists, exported feed lists, email credentials, or personal CFP archive records.
- Repository persistence remains default-off through workflow variables.
- Review `PRIVACY.md`, `docs/ACCOUNTABILITY.md`, `docs/LOCAL_FIRST_RUN.md`, and `docs/WINDOWS_APP.md` before enabling persistence or email automation.

Release checklist:

```bash
python scripts/validate_release.py
python -m unittest discover -s tests
```

Publishing:

- See `docs/RELEASE_PROCESS.md` for tag-based and manual release publishing.
- The `Build Release` workflow builds Python package files and `AcademicRadar-Windows.zip`, then creates or updates the GitHub Release for the requested tag.
