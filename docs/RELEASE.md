# Release Notes Draft

## v0.1.0

Academic Radar is a reusable starter for monitoring CFPs, academic events, journal calls, new books, and field-specific scholarly updates from RSS feeds and Bluesky.

Highlights:

- Static Pages config builder in `site/`.
- Modular Python package with a compatibility `radar.py` CLI entry point.
- Generic radar CLI and workflow driven by a JSON profile.
- CFP issue templates, parsers, archive workflows, and deadline digest generation.
- Example OPML and Bluesky watchlist files in `examples/`.
- Release hygiene validation for privacy-sensitive files and personal archive remnants.
- No-network unit tests for scoring, rendering, and state behavior.

Privacy note:

- Do not publish real state files, private watchlists, exported feed lists, email credentials, or personal CFP archive records.
- Use repository secrets for SMTP credentials.
- Forks that run the workflow in public may expose generated state unless they keep the fork private or choose not to commit state files.

GDPR-oriented note:

- The hosted Pages builder is static and client-side only: it has no analytics, cookies, uploads, accounts, or server-side storage.
- A fork owner who configures workflows, email delivery, watchlists, or state commits is responsible for the personal data they process.
- Bluesky handles, RSS selections, seen-link history, recipient email addresses, issue bodies, abstracts, and bios may be personal data depending on context.
- Public forks should avoid committing runtime state or personal CFP records unless the owner intentionally wants them public.
