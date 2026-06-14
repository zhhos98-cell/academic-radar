# Privacy And Accountability

This project is a reusable template, not a hosted data-processing service. It is designed to be privacy-preserving by default and auditable when automation runs.

This document is an engineering privacy note, not legal advice.

## Hosted Pages Builder

The GitHub Pages config builder in `site/` is static and client-side only.

- No analytics.
- No cookies.
- No account system.
- No uploads.
- No server-side storage.
- No backend API calls from the builder.

Inputs typed into the builder stay in the visitor's browser. Generated files are downloaded locally by the visitor.

## Repository And Workflow Data

When someone forks or configures this repository, they control what data their workflows process. Depending on context, these items may be personal data:

- Bluesky handles and watchlists.
- RSS source selections that reveal research interests.
- Seen-link state files.
- Email recipient addresses.
- Issue bodies, notes, abstracts, bios, CV exports, and ORCID exports.

Do not publish real state files, private watchlists, exported feed lists, email credentials, or personal CFP archive records unless you intentionally want them public.

## Default Storage Policy

The public template defaults are conservative:

- The Pages builder stores nothing server-side.
- Radar digest artifacts are not uploaded unless `UPLOAD_RADAR_DIGEST=true`.
- Seen-link state is not committed unless `COMMIT_RADAR_STATE=true`.
- CFP and backfill records are not committed unless `PERSIST_CFP_LEDGER=true`.
- CFP issue comments are not posted unless both `PERSIST_CFP_LEDGER=true` and `COMMENT_CFP_ISSUES=true`.
- Backfill issues are not automatically closed unless `CLOSE_CFP_ISSUES=true`.
- CFP parser drafts are not uploaded unless the manual workflow input `upload_artifact` is selected.

The workflows may still process issue fields, RSS items, Bluesky posts, or pasted CFP text transiently inside the GitHub Actions runner. By default, that content should disappear when the run environment is discarded.

## Accountability Trace

"Do not store personal data" does not mean "leave no accountability trail." Workflows write a minimal JSONL audit artifact through `scripts/write_audit_event.py`.

The audit artifact records:

- workflow name;
- event type;
- repository and GitHub run identifiers;
- commit SHA;
- source type and minimal source id, such as an issue number or profile path;
- broad categories of data processed;
- whether content persistence was enabled;
- storage mode;
- retention recommendation.

The audit artifact does not include issue body text, raw CFP text, abstracts, bios, email addresses, Bluesky handle lists, digest item text, or generated archive files. Audit artifacts use a 30-day retention setting in the workflows.

## GDPR-Oriented Responsibilities

This project is a template. A fork owner who runs the workflows is responsible for their own data-processing choices, including lawful basis, retention, access, deletion, and disclosure decisions.

For a privacy-preserving setup:

- Keep forks private when monitoring reveals personal research interests.
- Store SMTP credentials only as GitHub repository secrets.
- Leave `UPLOAD_RADAR_DIGEST`, `COMMIT_RADAR_STATE`, and `PERSIST_CFP_LEDGER` unset unless repository storage is intentional.
- Avoid putting personal data into public issues.
- Delete or redact issue bodies that include personal data when they are no longer needed.
- Review generated exports manually before publishing them elsewhere.

If repository persistence is intentionally enabled, document:

- the purpose of processing;
- the categories of data stored;
- the retention period;
- who can access the repository, Actions logs, artifacts, and issues;
- how correction and deletion requests are handled;
- how old Git history will be purged if personal data is accidentally committed.
