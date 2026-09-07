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

## General prose architecture rules (2026-09-07)

These rules govern finished scholarly prose across projects. They take precedence over older stylistic or architectural heuristics when those conflict, but they do not override repository-specific source locks, evidence levels, canonical-file rules, frozen areas, or factual constraints.

- **Sentence falsification:** delete or compress a sentence when its removal loses no factual or inferential step and it merely repeats a premise, explains the preceding sentence, or proves continued contact without changing the historical action.
- Secure or interesting evidence is not automatically entitled to body space. A source belongs in the body only when it changes the event, inference, or governing claim; otherwise move it to a note/control or omit it.
- **Correspondence is evidence, not the default narrative engine.** Keep a letter in the body when the message itself performs the historical action under analysis. Relationship continuity, density, reciprocity, or chronology alone should not organize the prose.
- **Prevent module hardening.** Historiography, background, method, institutions, counterevidence, and source practice should not each be discharged in separate self-contained blocks. Place material where it changes the meaning of an event already under way.
- Prefer a chronology of developing problems and actions to a sequence of thematic research packets when thematic organization causes backtracking or additive mini-essays.
- **Paragraph proportionality:** formulate a one-sentence summary proportional to the paragraph's length. The opening sentence should govern most of that informational burden without an A/B/C/D list, repeated `and`, semicolon chains, or extra subordinate clauses. If it cannot, redistribute the material instead of making the topic sentence heavier.
- **Paragraph-boundary counterfactual:** the next paragraph should arise as a continuation, complication, consequence, or contrast of the unresolved problem before it. If chronology or a transition word is doing all the work, revise the boundary or reorder the material.
- **First-sentence-only test:** read only the paragraph openings. They should form a coherent compressed argument, not an outline, case list, historiography inventory, or set of memo headings.
- Treat conjunction proliferation and clause stacking as structural evidence. If heterogeneous material requires extra `and`, `while`, semicolons, or nested subordinate clauses to cohere, restructure before polishing.
- Avoid ABCD constructions, repeated triads, parallel noun strings, and symmetrical `X / Y / Z` summaries unless the historical evidence itself genuinely has that form.
- Keep defensive temperature low. Replace repeated `not X`, `nor Y`, `this does not mean`, `cannot be treated as`, and pre-emptive rebuttal with positive historical statements. Preserve genuine counterevidence and reader-relevant source limits.
- Keep internal workflow out of finished prose and notes: no `HOLD`, `control`, `audit`, `bounded`, acquisition status, `currently cannot confirm`, internal QA paths, or repo-workbench locators. Store those states in controls rather than narrating them to the reader.
- Do not tell the reader that a point is important, central, key, striking, or significant when the historical action can establish its weight.
- Do not let a paragraph ending introduce a new research task that its opening cannot govern. Move, cut, or reassign that material.
- Historiography belongs where it changes the reading of a live event or claim, not in a dedicated literature-review block by default.
- A section or paragraph should not exist mainly to discharge a research obligation. Prefer **unresolved-problem propagation**: one historical action creates a question it cannot settle, and the next passage arises because of that question.

Working maxim: **if the prose needs more connective syntax to make the structure look coherent, fix the structure rather than the syntax.**

## Compression and recovery rules (2026-09-07)

Use these rules for late-stage shortening and density passes in scholarly prose and research writing. They are meant to prevent both bloated accretion and over-compression.

- **Compression is not deletion-first.** Prefer, in order: merge repeated qualifications; put names or comparable cases into rapid parallel form; interleave evidence that performs the same historical action; move provenance or non-argumentative background to notes; delete only what still adds no event, inference, historiographical intervention, or necessary source limit.
- **Do not narrate one item to completion when several items are doing the same work.** When A, B, and C jointly establish one historical point, weave them together instead of giving each a miniature beginning-middle-end. Preserve chronology when chronology itself carries the argument.
- **Sentence-function test:** every body sentence should do at least one of the following: establish an event/fact; show what a source actually does; advance an inference; alter the historiographical reading; preserve a necessary qualification or counterexample. If it does none of these, compress, move, or delete it.
- **Repeated explanation is expendable; argument-bearing friction is not.** Do not delete a short sentence merely because the preceding evidence implies it if that sentence supplies the hinge needed for the next paragraph or makes a non-obvious relation explicit. Conversely, delete verdicts that simply restate an immediately preceding quotation or contrast.
- **Public prose should use source or actor language before workbench language.** Prefer the sources' own vocabulary or ordinary established disciplinary/historiographical language. Do not publish repo-invented labels, workflow nouns, or bridge/framework vocabulary unless an external historiography or the source material independently establishes the term and the prose needs it.
- **An organizing thread is not automatically a causal mechanism.** A recurring term may organize later material without proving genealogy, influence, transmission, or causation. State the stronger relation only when the evidence establishes it.
- **Compression requires a recovery pass.** After any substantial shortening, compare against the immediately prior controlled state and classify deletions as: (a) successful removal of repetition/background; (b) acceptable loss of nonessential detail; or (c) accidental removal of an argument-bearing pin. Restore only category (c), and restore it in the shortest source-controlled form.
- Typical argument-bearing pins include: a sentence that changes a historiographical date; a short inference without which two sources merely sit beside each other; a return to an earlier textual witness that blocks a teleological story; or a sentence that tells the reader why a concrete distinction matters for the next historical action.
- **Do not restore density by restoring scaffolding.** When a compression pass cuts too deeply, add back evidence, historical consequence, or source-language formulation—not the old roadmap, abstract framework, repeated closure, or workbench term.
- **Notes are part of the compression system.** Remove orphan notes; compress repeated provenance; keep exact locators and evidence ceilings; do not let notes re-explain an inference already made in the body.

Compact rule: **cut repetition aggressively, recover argument-bearing pins conservatively, and let the sources carry as much of the conceptual work as possible.**

## Information packaging, attribution, and public-language QA (2026-09-07)

- **Architecture stays backstage.** Architecture and control tests may change order, paragraph boundaries, and sentence function, but their vocabulary must not migrate into finished prose. Translate terms such as `scale`, `carrier`, `control`, `reaggregation`, `organizing field`, or `proof burden` into the actual historical or textual action.
- **Paragraphs package actions, not dossiers.** A core scholarly paragraph should normally let one historical or intellectual action finish. As a diagnostic, roughly **6–9 interrelated information points** can indicate healthy density when the evidence supports it; this is not a quota. Several 1–3-point paragraphs serving the same action usually signal dossier-card fragmentation.
- **Density is relational, not additive.** Raise density by combining facts, relations, quotations, and textual moves that change the same event or problem. Do not add names or examples merely to increase count.
- **Opening delivery.** The opening two or three paragraphs should normally give the reader an event or scene, the problem generated by it, and the article's stakes. Bibliographic metadata and literature review should not precede the event unless they are themselves the historical scene.
- **Attribution before interpretation.** In notebooks, course notes, lecture records, marginalia, compilations, and working files, distinguish lecturer/source propositions, copied examples or bibliography, and the writer's own questions or reclassifications. Handwriting, possession, or copying does not by itself establish proposition authorship.
- **Defensive prose becomes source-state prose.** Where possible, replace reviewer-management formulas such as `this does not show`, `not X but Y`, or `supports X not Y` with positive descriptions of the available witness, action, missing item, or unresolved mechanism. Keep real uncertainty and counterevidence.
- **Repack QA is mandatory.** After substantial paragraph reorganization, rerun the first-sentence-only test, paragraph-boundary test, public-language leakage check, attribution/ownership check, and transport-diff check before reporting completion.
- **Whole-file write audit.** After any whole-file replacement, inspect the diff for unrelated changes to titles, quotations, citations, links, endnotes, punctuation, status lines, typography, or metadata and undo them immediately.

Compact rule: **make architecture change what the prose does, not what the prose calls itself; make paragraphs carry events, not research packets.**