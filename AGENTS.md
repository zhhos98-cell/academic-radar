# AGENTS.md — Research, Writing, and Editing Protocol

This file is a persistent instruction set for ChatGPT, Codex, and other agents working in this repository. Read it before editing. Repository-specific instructions, if present elsewhere, override only the relevant parts of this general protocol. Do not rewrite or shorten this file unless the user explicitly asks.

## 0. First-order fact and syntactic packing — highest priority

These rules are applied before all later prose heuristics.

- **Keep a first-order factual layer.** Historical prose should remain recoverable to controlled actors, actions, institutions, texts, objects, dates, places, or source wording. An interpretive term may compress those facts after they have appeared; it must not replace them.
- **After every drafting or editing pass, treat every word as questionable.** For each abstract or general noun, adjective, or verb ask whether it can be replaced by the actor/source's own wording, a first-order action, a named institution/person/book/document/object, an established theory or method name, or a date/place when that specificity matters. Prefer the concrete replacement when it is source-locked and analytically equivalent.
- **Do not narrate item A from beginning to end and only then narrate B when A and B perform the same historical or argumentative work.** Interleave and pack them. One item may become a noun phrase, concrete modifier, apposition, subordinate or relative clause, participial phrase, parenthesis, quick flashback, or short embedded source fragment.
- **Sentence-boundary test.** If sentence B is substantively a modifier, premise, qualification, example, source attribution, or brief flashback for sentence A, test merging B into A. If compression hides a distinct actor, action, chronology, or evidence ownership, split instead.
- **Several fast fragments may share one sentence.** When juxtaposition itself carries the point, chain short actor/source phrases or quotations without granting each a full miniature narrative.
- **Vary syntax with the historical action.** Avoid repetitive `A did X. B did Y. Therefore ...` patterns. Use apposition, subordination, parataxis, relative clauses, embedded quotations, brief returns, and sentence-length variation when they make the relation more exact.
- **Historiography obeys the same compression rule.** Do not summarize scholar A at length, then scholar B, then add a synthetic `therefore`. Extract only the proposition live in the present sentence or scene; weave A as a phrase or clause, B as a narrowing/correction/redirect, and the present evidence as the next move. A scholar's whole argument need not be rehearsed when one proposition does the work.
- **Compression is not abstraction.** Preserve first-order facts, chronology, source ownership, uncertainty, counterevidence, and argument-bearing friction. Density comes from tighter packaging of related facts, not from replacing them with higher-order labels.
- After every substantive round run two passes: **(1) first-order / every-word audit; (2) syntactic packing audit.** Then check that no actor, sequence, provenance, or inferential hinge disappeared.

Working maxim: **every word has a problem until the first-order fact or source language earns it.**

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

## Reader-background factual-premise audit (2026-09-08)

- **Do not make the reader supply a missing factual premise.** If an argument-bearing sentence depends on background knowledge that has not been established nearby, add the minimum source-controlled fact needed for the sentence to work.
- Run this especially at first appearances of people, texts, institutions, disputes, dates, technical terms, acronyms, and retrospective labels. A surname or title should not function as unexplained shorthand for a proposition the reader must already know.
- The factual layer is local and minimal: usually one identifying clause or one sentence stating who/what the item is, when/where it belongs, or the exact proposition under dispute. Add only the fact that changes the reader’s ability to follow the inference.
- Background remains source-locked. Never repair an assumed-knowledge gap from model memory or plausible general knowledge; verify it under the same evidence rules as any other historical addition.
- Do not turn this rule into encyclopedia biography, textbook exposition, standalone background sections, or name accumulation. If the extra fact does not alter the live event, relation, or inference, omit it or move it to a note.
- **Adjacent-field reader test:** read the draft as an intelligent historian outside the immediate subfield. Mark any sentence whose force collapses unless that reader already knows an unstated fact, then repair the gap at the smallest possible locus.

Compact rule: **state the factual premise the argument needs; never require the reader to reconstruct it from specialist background knowledge.**

## Evidence packaging and quotation granularity (2026-09-08)

- **Let the material happen before naming it.** Establish the concrete action, comparison, classification, sequence, or source problem before introducing an abstract noun that summarizes it. A noun handle may compress facts already shown; it must never substitute for facts the reader has not yet seen.
- **Use nouns to carry established fact packages; use verbs to carry history and argument.** Prefer actors comparing, revising, classifying, borrowing, rejecting, returning to, or reusing material over prose in which abstractions appear to act on their own.
- **Cut quotations by argumentative unit, not by the source sentence boundary.** Use three levels: **WORD/PHRASE** when only an actor’s label or concept matters; **RELATION/CLAUSE** when contrast, causation, sequence, logical relation, modality, or qualification matters; **SPEECH-ACT/SENTENCE** when the utterance itself is the historical action, or when the intact syntax is itself the evidence.
- **Do not make quotation perform the article’s interpretation.** The quotation should establish the lexical, relational, or speech-act fact; attribution, historical consequence, and inference belong in the author’s own syntax.
- **Several facts may share one explanation.** When two to four adjacent pieces of evidence perform the same historical action, let them accumulate before giving the interpretive sentence. Avoid a mechanical `fact → verdict → fact → verdict` rhythm.
- Preserve complete wording where completeness carries evidence: a dual relation, explicit negation, qualification, refusal, instruction, or other speech act may require the whole clause or sentence. Compression is functional, not a preference for shorter quotation.
- Any clipping, ellipsis, paraphrase, or nominal compression remains source-locked. Never remove a qualifier, negation, modality, referent, or contextual condition in a way that changes the source’s force.
- During QA, mark each quotation as **word / relation / speech act** and each abstract noun as **earned / premature**. Shorten or unpack only where that classification reveals a mismatch.

Compact rule: **facts first, noun after; quote only the unit that carries the evidence; let the author’s verbs do the arguing.**

## Paragraph-argument compression and chain test (2026-09-08)

- For every body paragraph, state its **argumentative advance** in one sentence, excluding source inventory, examples, dates, names, and materials as such. If no single sentence can state what the paragraph changes in the argument without an A/B/C list or several independent claims, the paragraph is structurally heterogeneous: split, redistribute, compress, or cut it.
- The paragraph opening should normally govern that one argumentative advance. Do not turn every opening into abstract thesis prose; historical action may lead, but the first sentence must make clear what work the evidence is doing or set up the problem the paragraph resolves.
- Run a **first-sentence / one-sentence-skeleton audit** after editing: read only the paragraph openings, then separately read the one-sentence argumentative summaries. Both sequences should form a coherent chain in which each paragraph advances, complicates, limits, supplies counterevidence to, or converts the unresolved problem from the previous paragraph into the next question.
- A sequence of parallel cases, thematic packets, chronology-only steps, repeated conclusions, or detached “balance” paragraphs fails this test even if each paragraph is individually sound. Reorder or rewrite until the paragraphs produce cumulative argument.
- Counterevidence belongs where it exerts pressure on a live claim and changes the next inferential step; do not quarantine it in a decorative counterargument paragraph.
- When a paragraph contains more material than its one-sentence argument can govern, remove or move the excess material rather than making the opening sentence heavier.
- Final compression test: strip each paragraph mentally to its one-sentence argument. The resulting skeleton should preserve the article's progression and its internal counterpressure. Then restore only evidence that earns a step in that chain.

Compact rule: **one paragraph, one compressible argumentative advance; first sentences and paragraph summaries must read as a cumulative argument with counterevidence, not as a list of materials.**

## Thematic callbacks, scholarly depth, and descriptive breathing (2026-09-08)

- **Sentence and clause burden:** a sentence may contain useful information and still be redundant if another sentence already performs the same argumentative function. Ask what exact step breaks if the sentence or clause disappears. Remove functional duplication before cutting first-order evidence.
- **Two-layer callback:** when an article has both a concrete historical object and a methodological or historiographical problem, keep both visible at low frequency. Return to the object through texts, practices, disputes, or later reuse; return to the methodological problem through source relations, contemporary disagreement, historiography, or counterevidence. Do not use slogans as callbacks.
- **Parallel strands need a hinge.** If two strands run beside each other, do not wait until the conclusion to join them. Locate the historical or conceptual point at which one begins to change the interpretation of the other.
- **Seed early, recover later.** A title, schedule, citation, object, or parallel inquiry may establish contemporaneity without establishing conceptual connection. State that ceiling, then let a later surviving source recover the strand only when the relation becomes readable. Never write the later formulation backward into the earlier archive.
- **Scholarly callbacks must perform work.** A contemporary, adjacent-field, later-generation, or current scholar belongs in the body only to support, oppose, offer another reconstruction, provide a field control, show later development, establish specialist afterlife, or recalibrate the historiographical claim. Aim for **random feel, non-random function**; one strong comparison is better than a name cluster.
- A near-contemporary parallel is not evidence of influence without transmission evidence. Later reuse is not a causal genealogy. Current scholarship may establish afterlife or continuing technical relevance without validating an intellectual-development story.
- **Descriptive breathing:** after dense argumentative stretches, occasional source-grounded sentences may show a person reading, writing, travelling, meeting, teaching, corresponding, handling an object, or encountering an institutional constraint. These sentences should give the prose air without opening a new research branch or inventing atmosphere.
- **Counterevidence changes geometry.** Contrary passages, omissions, later compression, disciplinary narrowing, failed transmission, or changed scale should narrow, redirect, or otherwise reshape the claim. Do not add a decorative counterargument that leaves the argument unchanged.
- **Introduction discipline:** seed the main object, governing problem, and any secondary strand needed for a later hinge, but only at the evidence level currently available.
- **Conclusion discipline:** do not introduce a new scholar, archive object, comparison, or evidentiary branch merely to broaden the ending. State the first-order claim, use historiography for calibration, and let counterevidence define the ceiling.
- **Note-burden corollary:** submission notes should support claims still alive in the body. Abandoned comparators, unused page ranges, and superseded research inventory belong in research controls, not indefinitely in public notes.

Compact rule: **every paragraph advances one compressible claim; every callback is source-bearing; every outside scholar changes the pressure on that claim; every counterexample changes its shape; descriptive prose gives air without opening a new argument.**

## Concrete-information substitution rule (2026-09-09)

- Before keeping an abstract or general word in historical prose, ask whether source-controlled specificity can replace it without distorting the claim. Test for a named actor, a specific historiographical position, the exact proposition or short primary wording, an institution, a date, a place, a text or object, a concrete action, or provenance—who or where the material came from.
- Ask explicitly: **Who? Which historiography? What exactly was said or done? What is the relevant original wording? Which institution? When? Where? Which text or object? From whom or where did it come?**
- Prefer the concrete replacement when it materially improves the reader’s ability to follow the event, relation, or inference. For example, replace `training` with a teacher/course/text/date when those facts matter, or `institutional participation` with the specific paper, meeting, election, publication, appointment, or record that constitutes it.
- Do not force specificity when the evidence is uncertain, when naming a source would imply a stronger relation than the sources support, or when the extra detail does not change the live argument. A precise-looking false relation is worse than a bounded general formulation.

Compact rule: **interrogate abstractions; if a source-locked answer to who/when/where/what/from whom materially strengthens the sentence, use it.**