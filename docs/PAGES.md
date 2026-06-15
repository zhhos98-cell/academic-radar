# GitHub Pages Web Builder

The static web builder lives in `site/` and is published at:

https://zhhos98-cell.github.io/academic-radar/

A root `index.html` is also kept in the repository so branch-based Pages setups can still show the builder. The GitHub Actions Pages workflow publishes the `site/` directory.

## Privacy posture

The builder is client-side only:

- no analytics;
- no cookies;
- no account system;
- no uploads;
- no backend API calls;
- no server-side storage.

Visitors can generate and download:

- `academic-radar-profile.json`;
- `bsky_watchlist_core.txt`;
- `feedly_active.opml`.

Generated files are created in the browser. They are not sent to this repository or to a backend service.

## Deployment

The deployment workflow is `.github/workflows/pages.yml`.

It runs on:

- pushes to `main` that touch `site/**`, `index.html`, or the workflow file;
- manual `workflow_dispatch` runs.

The workflow uses official GitHub Pages actions:

- `actions/configure-pages`;
- `actions/upload-pages-artifact`;
- `actions/deploy-pages`.

## If the Pages URL returns 404

Check these in order:

1. Repository `Settings -> Pages` should use `GitHub Actions` as the source.
2. `Actions -> Deploy Pages` should have a recent successful run.
3. The `github-pages` environment should show a deployment URL.
4. `site/index.html` should exist on `main`.
5. `site/.nojekyll` should exist on `main`.
6. Wait a minute after a successful deployment, then refresh the Pages URL.

If the repository is instead configured as `Deploy from a branch`, set the branch to `main` and folder to `/root`. The root `index.html` loads the same web builder assets from `site/`.

For a public release, keep real watchlists, RSS exports, state files, and CFP archive records out of the repository. Use the files in `examples/` as starters, or generate fresh files from the Pages tool.
