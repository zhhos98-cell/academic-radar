# Privacy

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

## GDPR-Oriented Responsibilities

This project is a template. A fork owner who runs the workflows is responsible for their own data-processing choices, including lawful basis, retention, access, deletion, and disclosure decisions.

For a privacy-preserving setup:

- Keep forks private when monitoring reveals personal research interests.
- Store SMTP credentials only as GitHub repository secrets.
- Avoid committing generated state files in public repositories.
- Delete issue bodies or generated CFP records that include personal data when they are no longer needed.
- Review generated exports manually before publishing them elsewhere.
