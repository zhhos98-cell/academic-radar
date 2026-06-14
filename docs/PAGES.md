# GitHub Pages Prototype

The static prototype lives in `site/`.

It is a client-side config builder. It does not read private repository data, call a backend, or store user input. Visitors can generate:

- `academic-radar-profile.json`
- `bsky_watchlist_core.txt`
- `feedly_active.opml`

The Pages workflow deploys the `site/` directory from `main`.

For a public release, keep real watchlists, RSS exports, state files, and CFP archive records out of the repository. Use the files in `examples/` as starters, or generate fresh files from the Pages tool.
