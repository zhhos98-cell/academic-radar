# Privacy Attack/Defense Model

This project is designed for public reuse without storing personal data by default. It still keeps a minimal accountability trace for automated processing.

This is an engineering model, not legal advice.

## Design Baseline

- Data protection by default: public workflows should not commit generated personal records unless a repository owner explicitly opts in.
- Data minimization: audit records contain operational metadata, not content.
- Purpose limitation: each workflow has a narrow processing purpose.
- Storage limitation: audit artifacts are configured with short retention.
- Accountability: every automated processing run can leave a minimal audit event showing what category of processing occurred and whether persistence was enabled.

## Default-Off Persistence Controls

Repository variables control persistence:

- `UPLOAD_RADAR_DIGEST=true`: uploads radar HTML/JSON digest artifacts. Default: off.
- `COMMIT_RADAR_STATE=true`: commits seen-link state. Default: off.
- `PERSIST_CFP_LEDGER=true`: commits generated CFP, backfill, deadline, ORCID, and CV files. Default: off.
- `COMMENT_CFP_ISSUES=true`: posts workflow comments on CFP/backfill issues. Default: off.
- `CLOSE_CFP_ISSUES=true`: closes processed backfill issues. Default: off.

Manual CFP draft parsing also has an `upload_artifact` input. It defaults to false because the parsed draft may contain pasted CFP text or personal material.

## Accountability Record

`scripts/write_audit_event.py` writes a JSONL audit event containing:

- workflow name and event type;
- repository, run id, run attempt, and commit SHA;
- minimal source reference, such as an issue number or profile path;
- broad data categories processed;
- storage mode;
- whether content persistence was enabled;
- a retention recommendation.

It intentionally does not store:

- issue body text;
- raw CFP text;
- abstracts or bios;
- notes;
- email addresses;
- Bluesky watchlists;
- digest item text;
- generated CFP records or exports.

## Threats And Defenses

| Threat | Defense |
| --- | --- |
| A public issue contains personal data | Issue templates warn users before entry; automation does not commit generated records by default. |
| A workflow commits CFP abstracts, bios, notes, or raw text | CFP commit steps require `PERSIST_CFP_LEDGER=true`; release validation checks this guard. |
| A radar run stores Bluesky posts or research-interest signals in Actions artifacts | Digest artifacts require `UPLOAD_RADAR_DIGEST=true`; audit artifacts contain metadata only. |
| Seen-link state exposes reading or monitoring history | State commits require `COMMIT_RADAR_STATE=true`; state files are ignored by git. |
| A manual CFP parser stores pasted text | Draft artifact upload requires explicit `upload_artifact=true`; audit artifact remains content-free. |
| Project history accidentally contains personal data | Current release checks prevent reintroduction, but true removal from Git history requires history rewrite or a clean repository. |

## Operational Checklist

For a public fork:

1. Keep persistence variables unset.
2. Keep private watchlists, feed exports, state files, and CFP archives out of git.
3. Treat GitHub issues as public unless the repository is private.
4. Review Actions artifacts and logs before sharing access.
5. If personal data is accidentally committed, remove it from current files immediately and then purge Git history or move to a clean repository.

For a private fork where persistence is intentionally enabled:

1. Document the purpose and lawful basis for processing.
2. Define retention periods for issues, artifacts, generated records, and state files.
3. Limit repository and Actions access.
4. Provide a process for correction, export, and deletion.
5. Periodically run `python scripts/validate_release.py`.
