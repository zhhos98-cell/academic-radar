# AGENTS.md — Research, Writing, and Editing Protocol

This file is a persistent instruction set for ChatGPT, Codex, and other agents working in this repository. Read it before editing. Repository-specific instructions, if present elsewhere, override only the relevant parts of this general protocol. Do not rewrite or shorten this file unless the user explicitly asks.

## 1. Source discipline

- Factual expansion is source-locked. Dates, places, people, actions, quotations, correspondence sequences, causal links, and bibliographic claims must come from material already controlled in the repository or from newly verified external research that has first been recorded in a repo research/control note.
- Never fill historical gaps from model memory, general knowledge, plausibility, or stylistic completion.
- Distinguish evidence levels explicitly: **secure/body**, **partial/note**, and **uncontrolled/quarantine**. Do not promote a lower-level item merely because it would improve the story.
- Absence from one catalogue, inventory, OCR layer, or index does not by itself invalidate material independently controlled by another archive or source. Record the discrepancy first; do not silently delete or downgrade the source.
- When sources conflict, preserve the conflict and identify which claim each source can support. Do not normalize anomalies silently.
- External research should be bounded by a concrete sentence-level or source-level gap. Do not reopen generic web discovery once a corpus has been calibrated.

## 2. Editing method

- **Surgical patch, not regeneration.** Preserve surrounding prose verbatim unless the requested change truly requires local restructuring.
- Do not rewrite paragraphs or sections merely for flow, completeness, tone, balance, elegance, or symmetry.
- Do not let model completion raise the draft's explanatory or defensive temperature.
- Work from one canonical draft when a canonical draft exists. Do not create `draft_05`, `draft_06`, parallel prose versions, or substitute rewrites unless the user explicitly requests them.
- If a bilingual or reading companion exists, it mirrors the canonical text; it is not an independent draft and should be synchronized only after the canonical passage is stable.
- User annotations are local instructions. Patch the annotated place rather than using the annotation as permission to regenerate the surrounding section.
- Before any write, fetch the current file/blob SHA. Sequential updates to the same file must use the latest returned SHA.

## 3. Historical reconstruction and chronology

- Prefer historical growth through completed event chains: **date/place/action → document/request → reply → consequence**.
- Restore antecedents and consequences when a reader would otherwise lack background or temporal orientation.
- The governing principle is: **the event must finish happening; it does not have to be explained to exhaustion.**
- Add time anchors when they change the reader's sense of sequence, duration, or density: flashbacks, long gaps, or rapid exchanges. Do not mechanically calculate intervals everywhere.
- Keep actors visible. If a paragraph contains several letters, institutions, manuscripts, or scholars, make clear who is acting at each step.
- Scarce direct traces—sending, reading, speaking, lending, correcting, carrying a letter, using a book—can be historically important. Do not delete them merely because they look mundane.

## 4. Intellectual and conceptual history

- Keep one conceptual center at a time. Supporting concepts should explain the central problem rather than become parallel themes.
- Do not establish conceptual history by word frequency alone. Ask what a term allowed an actor to classify, infer, compare, authorize, or withhold in a particular setting.
- Shared vocabulary does not imply shared definition, evidence, method, or disciplinary authority.
- Correspondence is not an endpoint. When relevant, open a letter outward to the books, lectures, notes, manuscripts, objects, and institutional documents that give its language intellectual work.
- A high-value sequence is often: **exchange/correspondence → specific text or object → reuse in another text, lecture, note, or argument**.
- Avoid clean conversion stories, forced analogies, and teleologies in which one concept simply replaces another. Persistence plus changed use is often historically more accurate.

## 5. Historiography

- Every secondary source in the body should have a function: **inherit, correct, refute, converge, narrow, redirect, or expose a gap**.
- Do not make citation dumps. Prefer a sentence that states exactly what an earlier historian made visible and what the present evidence changes.
- Put historiography into the body only when it changes the reading of the case. Otherwise keep it in notes or references.
- Do not let secondary literature substitute for primary reconstruction when primary material is available.

## 6. Prose and paragraph style

- Avoid agent-internal labels and invented technical vocabulary in finished prose unless the discipline genuinely needs the term.
- Minimize slogans, conceptual branding, and repeated formulas invented during drafting.
- Avoid over-defensive scaffolding such as repeated `this does not mean`, `rather`, `not X but Y`, pre-emptive qualifications, symmetrical counterarguments, roadmap sentences, and paragraph-end verdicts.
- Genuine counterevidence stays. Removing over-defensiveness must never remove a real contradiction, ugly fact, evidentiary limit, or source uncertainty.
- Prefer ordinary historical prose over meta-commentary about method.
- Avoid excessive one-sentence paragraphs when adjacent sentences perform the same historical or analytical action. Conversely, do not merge distinct events merely to make paragraphs longer.
- Keep name-density under control. Add a proper name only when the name itself does argumentative work.
- Do not grow word count with filler. Grow through source scenes, event chains, conceptual uses, material practices, and historiographical consequences.

## 7. Layer changes

- Keep four layers distinguishable when they occur: **fact/event**, **material/source**, **historiography**, and **the article's inference**.
- Do not label every paragraph. Use only minimal anchors where a reader would otherwise mistake one layer for another.
- A reader should be able to disagree with the source reading, the historiographical placement, or the inference separately.

## 8. Notes and source limits

- Notes are useful for concise background, chronology, translation choices, provenance, archive locators, source uncertainty, and controlled side-material.
- Do not bury the article's central argumentative step in a note.
- Preserve source language when wording matters. Translate only to the degree justified by the source control.
- Unpublished or partially controlled material can remain useful if its evidentiary level is stated precisely.

## 9. QA before writing back

Check each proposed change for:

1. source control;
2. chronology and actor clarity;
3. whether it strengthens the central conceptual problem;
4. whether it accidentally creates a new parallel thesis;
5. whether counterevidence remains visible;
6. unnecessary defensive language or invented jargon;
7. paragraph rhythm and excessive single-sentence paragraphs;
8. whether growth comes from historical/intellectual substance rather than explanation for its own sake.

After editing, report the exact repository path and commit SHA, and describe the conceptual or historical effect of the local diff.