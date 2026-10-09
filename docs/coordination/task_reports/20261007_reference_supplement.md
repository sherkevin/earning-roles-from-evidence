# Task report — reference survey and supplement (2026-10-07)

## Purpose

Audit the reference-list scale and source mix of strong, directly relevant papers, then
repair the current AAMAS draft's claim-to-citation coverage without padding the bibliography.
No LLM API, GPU, benchmark execution, or scientific result was used.

## Work completed

- Read the compiled bibliographies of five primary-source samples: two ICML 2025 papers
  tagged oral in the local Top-Conf Figure Gallery, two official AAMAS partner/reputation
  papers, and ACL 2025 MultiAgentBench.
- Recorded exact count methods and official URLs in
  `experiments/logs/reference_supplement_round_20261007/config.json`.
- Found a compiled-reference range of 38–65 (median 57). The papers do not cite only
  top-conference work: they combine the nearest problem literature, canonical bandit/MARL/
  reputation/game-theory foundations, benchmark and evaluator specifications, adjacent
  social or human-AI evidence, and implementation/preprint sources whose status is labelled.
- Audited the active draft: 22 cited keys out of 28 BibTeX entries, with six stale uncited
  entries from an abandoned benchmark direction.
- Added and cited eight verified sources: AAMAS 2024 partner selection; ICLR 2024
  MetaGPT and AgentVerse; ACL 2024 AppWorld; NeurIPS 2024 LLM cooperation; Nature Human
  Behaviour 2025 repeated LLM games; JAIR 2022 continual RL; and the 2017 multi-agent
  non-stationarity survey.
- Removed the six uncited stale entries from the active `.bib`; historical files are
  untouched. The active bibliography now has 30 entries and all 30 are cited.
- Updated the Chinese reading copy so its selected list and its “full list is authoritative
  in the English source” statement are no longer stale.

## Validation

Candidate build:

```text
python3 scripts/build_aamas2027.py \
  --build-dir build/reference_supplement_20261007_v2 \
  --main-only --require-content-pages 8
```

Receipt: `article/aamas2027/build/reference_supplement_20261007_v3/verification.json`.

- body pages: 8;
- total pages: 9;
- references begin on page 9;
- unresolved citations/references: 0;
- overfull boxes: 0;
- official template files unchanged;
- submission/scientific gate: still closed.

The verified candidate was promoted to the single canonical internal PDF
`artifacts/aamas2027/main.pdf`; the immutable version snapshot and promotion receipt are
under `artifacts/aamas2027/reference_supplement_20261007_v3/`. The canonical and workspace
`article/aamas2027/build/main.pdf` hashes are both
`b316464801f9e02c65fa61d9f704c21945679ced1492e897df1749b72425f3be`.

## Interpretation and next check

The result is a citation-coverage repair, not evidence that the proposed role protocol works.
The reference count is intentionally below the 38–65 sample range because the current paper
has a narrower claim surface and an eight-page body. The next bibliography pass should be a
claim-to-citation audit after benchmark, baseline, and method details are frozen. It should
add a source only when a concrete claim, baseline, benchmark, or measurement needs it.
