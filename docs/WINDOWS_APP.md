# Windows desktop app

Academic Radar can be built as a small Windows desktop app for users who do not want to use PowerShell or a terminal.

The app provides a form-based interface for creating local radar files and running a dry preview. It writes files into a local workspace folder selected by the user.

## Download

For released builds, download the Windows zip from the GitHub Release assets when available:

- `AcademicRadar-Windows.zip`

For development builds, go to GitHub Actions, open the latest successful `Build Windows App` run, and download the `AcademicRadar-Windows` artifact.

## First run

1. Unzip `AcademicRadar-Windows.zip`.
2. Double-click `AcademicRadar.exe`.
3. Choose a workspace folder, or keep the default folder under Documents.
4. Fill the form, or keep the defaults for a quick test.
5. Click `Save files`, then `Summary`, then `Doctor`.
6. Click `Dry run` to fetch matching RSS and Bluesky items.
7. The app writes an HTML preview under the workspace `tmp` folder and opens it in your browser.

## What the app creates

Inside the chosen workspace, the app creates this structure:

```text
Academic Radar Run/
  .radar/
    profiles/
      local.json
    feedly_active.opml
    bsky_watchlist_core.txt
    sent_items.json
  tmp/
    radar_digest.html
    radar_items.json
```

The files mean:

- `local.json`: the radar profile and settings.
- `feedly_active.opml`: RSS feed list.
- `bsky_watchlist_core.txt`: Bluesky account watchlist.
- `sent_items.json`: seen-link state file. It may not exist until state writing is enabled elsewhere.
- `radar_digest.html`: dry-run preview.
- `radar_items.json`: dry-run selected item data.

## Button guide

- `Save files`: writes the local profile, OPML file, and Bluesky watchlist.
- `Summary`: prints a no-network summary of the current configuration.
- `Doctor`: checks local paths, settings, source files, terms, and query configuration.
- `Dry run`: fetches matching RSS and Bluesky items, renders a preview, and does not send email or write seen-link state.
- `Open folder`: opens the workspace folder.
- `Open latest HTML preview`: opens the latest dry-run preview if it exists.

## Privacy and responsible use

The desktop app writes runtime files locally under the workspace selected by the user. Do not copy private watchlists, OPML exports, state files, delivery settings, or private research records into a public repository unless you intentionally want them public.

Before running collection, check source terms, platform rules, institutional policies, and any data-protection duties that apply to your use case. The app is a local research utility and does not determine whether a particular collection or reuse is permitted.

## Building locally, for developers

```bash
python -m pip install . pyinstaller
python -m PyInstaller --onefile --windowed --name AcademicRadar academic_radar_gui.py
```

The executable will be created under `dist/`.
