# Branch closure ledger — 2026-08-19

This note records the disposition of two long-lived `codex/*` branches before their refs are reset to current `main`.

## `codex/academic-radar-improvements`

Pre-closure Git state:

- 31 commits ahead of its merge base;
- 207 commits behind current `main`;
- divergent from `main`.

The branch represented an early integrated CFP/radar improvement line: corrected issue-template placement, CFP ingest/backfill/deadline/parser workflows, profile configuration, parser/deadline scripts, documentation, and related exports.

Its functionality was subsequently incorporated and continued on the mainline. In particular, mainline commit `b21899d75444d722581ac04254a3bb1ee81a17da` (`Improve academic radar and CFP ledger automation`) is an ancestor of current `main`; current `main` is 202 commits ahead of that checkpoint. The current tree retains and further develops the CFP issue templates, ingest/backfill/deadline/parser workflows, HPS profile, CFP parser/deadline tooling, and project documentation.

Later mainline changes intentionally removed or replaced some old-branch material, including personal CFP exports/backfill data and the separate Black Studies radar script/workflow. Those removals are part of the later privacy/public-release and application refactor and must not be reversed merely because the old branch still contains earlier copies.

Disposition: **obsolete implementation branch; do not merge or salvage wholesale. Reset ref to current `main`.**

## `codex/cfp-ingest-cross-platform`

Pre-closure Git state:

- 1 commit ahead of its merge base;
- 203 commits behind current `main`;
- divergent from `main`.

The unique commit `4f5843dfe6ee63d81f9b08a07e452d90748caa6a` (`Make CFP ingest cross-platform and deadline-aware`) added four behaviors to `scripts/cfp_ingest_archive.py`:

1. use `tempfile.gettempdir()` / `CFP_INGEST_COMMENT_PATH` instead of hard-coded `/tmp`;
2. add timezone-aware `utc_now_iso()`;
3. link the generated dashboard to `cfp/deadlines.md`;
4. use the UTC helper for `created_at`.

All four behaviors are already present in current `main`, which has since added further privacy/persistence safeguards around CFP workflows.

Disposition: **semantically absorbed; no unique functionality remains to recover. Reset ref to current `main`.**

## Closure rule

After both refs are reset, `main` is the only canonical development line. Historical branch names may remain as aliases, but they must carry no commits or content distinct from `main`. Future CFP/radar work belongs on new branches cut from current `main`, not by reviving either obsolete branch.
