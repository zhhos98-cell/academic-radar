# CFP Parser

`scripts/cfp_parse_text.py` turns a pasted CFP or CFP URL into a Markdown issue draft whose headings match the `Add CFP` issue form.

It is intentionally conservative:

- it does not update `cfp/` records directly;
- it does not open a GitHub issue by itself;
- it produces fields for review before ingestion.

## Local Usage

Parse a local text file:

```bash
python scripts/cfp_parse_text.py --file path/to/cfp.txt --output cfp_issue_draft.md
```

Parse text from an environment variable:

```bash
CFP_RAW_TEXT="Call for papers..." python scripts/cfp_parse_text.py
```

Parse a URL:

```bash
python scripts/cfp_parse_text.py --url https://example.org/cfp --output cfp_issue_draft.md
```

Output JSON instead of Markdown:

```bash
python scripts/cfp_parse_text.py --file path/to/cfp.txt --format json
```

## Extracted Fields

The parser tries to infer:

- CFP title;
- opportunity type;
- source URL;
- organiser and host institution;
- location and online/hybrid status;
- event dates;
- abstract, full paper, registration, and notification deadlines;
- abstract and paper word limits;
- submission email and portal;
- theme keywords from the active profile;
- starter next action and tracking options.

## GitHub Actions Usage

Run `CFP Parse Draft` manually from the Actions tab. Provide either a URL, pasted raw text, or both.

By default, the workflow does not upload the parsed draft because the draft may contain pasted CFP text or personal material. Select `upload_artifact` only when storing the draft in GitHub Actions artifacts is intentional. Audit artifacts remain content-free.

Review the draft before opening an issue. The draft is meant to reduce typing, not to be treated as authoritative metadata.
