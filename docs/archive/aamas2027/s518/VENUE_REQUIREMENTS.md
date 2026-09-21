# AAMAS 2027: verified requirements and calendar

Verified: 2026-09-16. Target: Main Technical Track. These are 2027 rules, not a rollover from 2026. Official HTML, extracted text, template ZIP, and source hashes are saved in `references/aamas/`; `sources.json` records retrieval URLs and timestamps.

## Calendar

The [official main-track call](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/) specifies end-of-day Anywhere on Earth (UTC-12). Beijing/Shanghai is 20 hours ahead of AoE.

| Milestone | Official AoE date | Asia/Shanghai deadline |
|---|---|---|
| Every author has an OpenReview account | 2026-09-17 | 2026-09-18 19:59:59 |
| Mandatory abstract registration | 2026-10-01 | 2026-10-02 19:59:59 |
| Full paper | 2026-10-08 | 2026-10-09 19:59:59 |
| Rebuttal window | 2026-11-20 to 2026-11-24 | Ends 2026-11-25 19:59:59 |
| Notification | 2026-12-21 | Published date, not an author action deadline |
| Camera ready | 2027-01-25 | 2027-01-26 19:59:59 |
| Conference | 2027-05-03 to 2027-05-07 | Hanoi, Vietnam; conference dates are local event dates |

Registration is urgent: the stated date is tomorrow relative to this audit. Existing accounts still need current author profiles. No accounts, submissions, or reviewer commitments were created by this task.

## Format and submission

The [official instructions](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/) require English, anonymous review, LaTeX, a PDF, at most eight content pages, and unlimited reference-only pages. Treat limitations and any in-paper appendix as content; the ACL exemption for limitations does not carry over. Abstract registration needs approximately 100--300 words. A single anonymous supplement ZIP must be at most 25 MB. Essential argument and evidence must be in the paper because reviewers need not read the supplement.

The [official 2027 template ZIP](https://warwick.ac.uk/fac/sci/dcs/aamas2027/aamas_2027_template.zip) contains `aamas.cls`, `ACM-Reference-Format.bst`, `by.pdf`, and the sample source/PDF. Use `\documentclass[sigconf,anonymous]{aamas}`. Retain the supplied conference/copyright block, Libertine typography, and layout. Supply the actual OpenReview ID after abstract registration. Do not retain the old EMNLP submission number 11746. The separate AAMAS directory uses the unmodified official files; the build script checks their hashes.

Submission portal: [AAMAS 2027 on OpenReview](https://openreview.net/group?id=ifaamas.org/AAMAS/2027/Conference). The instructions prohibit changing the author list/order after acceptance. Archival simultaneous submission is prohibited. An EMNLP rejection does not make the paper eligible for the AAAI fast track, which is specifically for qualifying AAAI-27 submissions.

## Area and evaluation criteria

The main-track call evaluates originality, significance, soundness, reproducibility, clarity, relevance, presentation, and engagement with prior work. Its explicit area descriptions are more useful than guessing reviewer preferences:

- **Recommended current fit: GAAI (Generative and Agentic AI).** The work centers on delegation, state, interaction, and evaluation in generative-model-based teams. The call explicitly excludes generic prompting/tool use without an agent contribution.
- **Conditional alternative: COINE.** Appropriate if the final contribution becomes a general theory or mechanism of organization, reputation, or coordination, with LLMs an application. Adding organizational vocabulary to a generative-agent architecture does not meet this distinction.
- **Not the current primary fit: LEARN.** Reconsider only if the contribution becomes a genuinely new learning method with relevant analysis; EMA reputation and a heuristic router alone do not justify this positioning.

These are reasoned placement recommendations, not statements about which area is easier to enter.

## New policies that matter

The [2027 Findings policy](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/findings/) introduces Findings as an archival publication category within the same submission process. Papers not chosen for the main proceedings are considered automatically unless authors opt out. Findings has the same paper length. The policy explicitly allows strong negative, theoretical, replication, and exploratory contributions in the main proceedings; it does not reserve them for Findings. A clean negative result about reputation is therefore scientifically viable, provided its contribution and validation are substantial.

The [reciprocal reviewer policy](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/reciprocal-reviewer-policy/) requires a qualified coauthor reviewer or an eligible exemption during abstract submission. All qualified authors serving in official organizing roles, or no qualified authors, are listed exemption cases. The exact qualification test must be checked against the Reviewer Guidelines/form; this audit does not infer an author's eligibility.

The author AI policy in the instructions requires disclosure of tool/version and prompts when AI assists hypotheses, methodology, or experiment design. This revision uses assistance in those areas. The old statement that AI was used only for grammar/code completion would be inaccurate. The conference also restricts generated images to qualitative research evidence; the new process diagram is deterministic TikZ, with no image-generation service used.

## Files and remaining author-owned actions

- Download manifest: `references/aamas/sources.json`.
- Source archive: `references/aamas/official/`.
- Original template: `references/aamas/template/aamas_2027_template.zip`.
- Working manuscript: `article/aamas2027/`.
- Submission readiness: `docs/paper/aamas2027/submission_gate.json`.

Authors still need to ensure OpenReview accounts by the registration date, decide reviewer/exemption and Findings settings, supply the author list and actual submission ID, verify AI disclosure, and complete the scientific evidence gates. These are recorded actions, not an instruction to submit the current draft.
