# Local First Run

This guide is for running Academic Radar locally before connecting email delivery or repository automation. It keeps runtime files under `.radar/`, which is ignored by git.

## 1. Install the package locally

From the repository root:

```bash
pip install .
```

For an isolated environment, create and activate a virtual environment first:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

On Windows PowerShell, activate the environment with:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install .
```

## 2. Inspect available presets

```bash
academic-radar --list-presets
```

Presets are reusable bundles of field terms and public Bluesky queries. You can repeat `--preset` or pass comma-separated names.

## 3. Create private first-run files

This command creates a local profile, OPML file, Bluesky watchlist, and seen-link state path under `.radar/`:

```bash
academic-radar --init \
  --profile-name "My Academic Radar" \
  --preset hps \
  --preset photography-history \
  --field-term "household experiment" \
  --bsky-handle "@example.bsky.social" \
  --rss-feed "Example=https://example.org/feed.xml"
```

Generated files:

- `.radar/profiles/local.json`: local JSON profile.
- `.radar/feeds.opml`: local RSS feed list.
- `.radar/bsky_watchlist.txt`: local Bluesky account watchlist.
- `.radar/seen.json`: state file path used after a non-dry run.

The `.radar/` directory is ignored by git. Do not remove that ignore rule if the repository is public.

## 4. Inspect the generated profile

Before fetching anything, print a no-network profile summary:

```bash
academic-radar --config .radar/profiles/local.json --summary
```

The summary reports the profile name, local file paths, source limits, scoring term counts, and public Bluesky query counts. It does not fetch RSS feeds or Bluesky data.

## 5. Run diagnostics

```bash
academic-radar --config .radar/profiles/local.json --doctor
```

Diagnostics check local file paths, OPML parseability, watchlist readability, positive integer settings, scoring term availability, negative-term overlap, and Bluesky query presence. This also avoids network fetching.

Warnings are not necessarily fatal. For example, an empty watchlist is acceptable if you only want RSS and public Bluesky search queries.

## 6. Run a dry preview

```bash
academic-radar --config .radar/profiles/local.json \
  --dry-run \
  --output-html tmp/radar_digest.html \
  --output-json tmp/radar_items.json
```

A dry run may fetch RSS and Bluesky data, render local preview files, skip email delivery, and skip seen-link state updates.

Open `tmp/radar_digest.html` in a browser to review the digest.

## 7. Optional source overrides

You can override file paths without editing the profile:

```bash
academic-radar --config .radar/profiles/local.json \
  --opml .radar/feeds.opml \
  --watchlist .radar/bsky_watchlist.txt \
  --state .radar/seen.json \
  --summary
```

You can also reduce output size during testing:

```bash
academic-radar --config .radar/profiles/local.json --dry-run --max-items 5
```

## 8. Email delivery

Email delivery requires environment variables:

```bash
export SMTP_USER="you@example.com"
export SMTP_PASS="app-password-or-smtp-password"
export TO_EMAIL="recipient@example.com"
```

Then run without `--dry-run`:

```bash
academic-radar --config .radar/profiles/local.json
```

This sends email and writes the seen-link state file unless you pass `--no-email` or `--no-state`.

## 9. Privacy checklist

For a public repository:

1. Keep `.radar/` ignored.
2. Do not commit real OPML exports, private Bluesky watchlists, seen-link state files, email addresses, or private CFP records.
3. Use repository secrets for email credentials if you later enable GitHub Actions.
4. Run `python scripts/validate_release.py` before public release.
5. Review `PRIVACY.md` and `docs/ACCOUNTABILITY.md` before enabling persistence variables.

## 10. Troubleshooting

If `academic-radar` is not found, confirm that `pip install .` ran in the active environment.

If `--doctor` says the OPML file has no feeds, add at least one `--rss-feed` during `--init` or edit `.radar/feeds.opml`.

If the watchlist is empty, add handles to `.radar/bsky_watchlist.txt`, one handle per line. The leading `@` is optional.

If a dry run returns no items, try broader field terms or fewer negative terms, then inspect the profile again with `--summary`.
