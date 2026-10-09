# Experiment-matrix audit — 2026-10-08

## Scope and evidence

This audit asks whether the current experiment tables communicate a credible
AAMAS evaluation at a glance. It separates three questions that are easy to
confuse:

1. Is the scientific design complete enough to test the four research questions?
2. Is the table a good **pre-results design scaffold**?
3. Does its visual role match the numeric result tables used by strong recent
   papers?

The audit is based on the current source
`article/aamas2027/main.tex` (SHA-256
`cbd920abb12e40c3c7b0c3b79ce6bff3f49c9cf2a7b58e879fd768a165a38772`) and the
canonical PDF `artifacts/aamas2027/main.pdf` (SHA-256
`9092c81938e12a9bcf8b234bc28c7fe758c6f3fa3e55b70bfc9ac224da671edc`). The
page review used rendered pages 5–7. The comparison set is the locally archived
CollabLLM (ICML 2025 oral/best-gallery sample), MultiAgentBench (ACL 2025), and
Cross-environment Cooperation (ICML 2025) PDFs. Their hashes and the exact
inspection configuration are in
`experiments/logs/experiment_matrix_audit_20261008/config.json`.

No experiment, API call, or benchmark result was run for this audit.

## Current matrix inventory

The paper currently has five table environments:

| Table | Role | Size / density | Empirical payload |
|---|---|---:|---:|
| Novelty boundary | comparison-family boundary | full-width, `\scriptsize` | none; design contract |
| State contract | legal state-update fields | single column, `\scriptsize` | none; method contract |
| Baselines | information and cost boundary | full-width, `\small`, 8 arms | none; comparison contract |
| Complete experiment matrix | RQ/cell execution skeleton | full-width, `\scriptsize`, 9 cells × 6 columns | 0 numeric results; one empty result column |
| Headline endpoints | future headline result placeholder | single column, `\small`, 8 rows | 0 numeric results; three empty value columns |

The complete matrix contains nine planned cells (RQ1-I through RQ4-II), four
research questions, two tracks, seven named alternatives plus RARE, and eight
headline endpoints. In the PDF, Table 4 is rendered in approximately 6.5–7pt
text. Long prose wraps inside `Policy/intervention`, `Primary comparison`, and
`Measures`; the rightmost `Result` column is only a dash in every row. Table 5
then repeats the same “future values” idea as a mostly empty table directly
below it.

## What the comparison papers do

The strong-paper examples use tables as **result instruments**, not as a list of
all planned execution metadata.

* CollabLLM's main table groups columns by task and metric, places methods in
  rows, and reports a compact numeric payload with arrows, bold best values, and
  an improvement row. A second table isolates generalization rather than adding
  setup prose to the main result table.
* MultiAgentBench uses grouped task/domain headers and two fixed metrics per
  group. The visual hierarchy is immediately legible: method rows, task groups,
  numeric cells, and the best values.
* Cross-environment Cooperation puts architecture and hyperparameter tables in
  the appendix, where a table can carry implementation detail without competing
  with the main claim. Its main pages use plots and compact result comparisons.

The common pattern is not a fixed row count. It is a separation of duties:

1. a small setup/protocol description;
2. a hero result table with a stable set of numeric endpoints;
3. a separate ablation, stress, or resource table/plot;
4. detailed execution parameters in the appendix or artifact.

## Diagnosis

### Scientific coverage: substantially present, but not yet executable evidence

The current matrix does cover the right families of questions: situated signal,
assignment causality, online service behavior, and safety/stability. The baseline
table also exposes the most important same-information alternative. The problem
is not that the matrix has too few rows.

The unresolved scientific gap is that each high-level row still expands to a
confirmation card with a root, stream count, seed plan, budget, scorer,
estimand, stopping rule, and independent label contract. Until those cards and
the two roots are qualified, the matrix is a design promise rather than
evidence. A cleaner table cannot close that gate.

### Presentation: the current table is doing too many jobs

Table 4 combines RQ routing, benchmark/root identity, policy definition,
fairness controls, metric lists, and an empty result slot. This makes a planning
schema look like a result table. It forces `\scriptsize` and still produces
wrapped prose. Table 5 then provides a second empty result table, so the page
has the visual footprint of a quantitative section without any quantitative
payload.

The important distinction is:

> The matrix has roughly the same rectangular cell count as a real result table,
> but none of the cells contain measurements. It therefore feels simultaneously
> too large (too much prose and wrapping) and too small (no scale of evidence).

This is why simply increasing the font or adding more rows would not make it
look like a best paper.

### Scale check

The apparent scale mismatch can be made concrete. CollabLLM's inspected main
result table has roughly 6 method rows × 3 task groups × 3 metrics (about 54
numeric cells); MultiAgentBench has 5 model rows × 6 task groups × 2 metrics
(about 60 numeric cells). The current Table 4 has 9 planned rows × 6 prose
columns (about 54 text cells), but **zero** observed values, intervals, or
per-root variation. It occupies a comparable rectangle while carrying an
entirely different kind of information. The correct repair is therefore to
reduce the design overview and later fill a separate numeric result table; it is
not to manufacture a larger empty matrix.

### Page-level problem

On page 7, the full-width matrix occupies the top of the page at a very small
size. The mostly empty headline table occupies the lower left column while the
right column continues prose. The visual rhythm is therefore “dense plan → empty
placeholder → prose,” rather than “question → numeric answer → interpretation.”
The baseline table on page 6 is materially better: three columns, short cells,
`\small` text, and one clear comparison contract. It should be retained as the
style anchor.

## Gap against the best-paper standard

| Criterion | Current state | Assessment |
|---|---|---|
| Clear RQ-to-measure mapping | Present across RQ1–RQ4 | Pass as design |
| Fair baseline boundary | Strong, explicit in Table 3 | Pass pending executable adapters |
| Main result table | Not yet present; empty placeholders only | Fails result-stage standard |
| Visual legibility | Table 4 too dense for main text | Needs redesign |
| Numeric scale | No observed values, intervals, or per-root variation | Correctly absent pre-results, but cannot be sold as result evidence |
| Ablation/mechanism isolation | Described in prose and rows RQ4-II | Present in design; needs compact presentation |
| Setup detail vs main claim | Mixed in Table 4 | Needs separation |
| Page economy | Page 7 spends space on empty cells | Needs reduction |

The current score is therefore **6.0/10 for a pre-results design table** and
**3.5/10 for a submission-stage results presentation**. The lower score is not a
judgment that the scientific questions are wrong; it records that a reviewer
cannot yet see a result-bearing hero table.

## Recommended correction

The next paper-layout candidate should preserve the nine-cell execution skeleton
in the experiment-card/manifest documentation, but use a compact four-row
overview in the main paper:

| RQ | Track / unit | Contrast | Primary endpoint | Stress or split |
|---|---|---|---|---|
| RQ1 information | ArtifactRole / independent root | RARE vs raw acceptance, terminal-only, same-information contextual control | held-out Brier/log loss and calibration | development → confirmation root |
| RQ2 assignment | ArtifactRole / target assignment | public evidence + delayed credit vs no evidence, delayed-only, pooled | future quality–cost utility and assignment change | assignment sealed before execution |
| RQ3 service | PeerSelect / independent stream | updater vs uniform, no-history, history-only | payoff/regret, update p95, backlog, state bytes | selected-only delay and fixed budget |
| RQ4 safety & stability | both / mutation and drift streams | ownership mutations, drift, leave-one-mechanism-out | false attribution, UNKNOWN precision, forgetting/recovery | producer/recipient/mixed and delayed order |

This table is an overview, not a result table. It can remain readable at
`\small` and make the paper's four claims visible in four rows. The detailed
nine-cell execution cards should retain the exact roots, seeds, budgets, scorers,
and manifests. Once real confirmation data exist, the overview can be replaced
by a grouped numeric hero table in the style of the comparison papers, with
method rows, fixed metrics, intervals, and bold best values.

The empty Table 5 should not remain a pseudo-result table. Until results exist,
replace it with a short endpoint contract (`H1`–`H4`, metric, direction, unit),
or move it to the internal experiment-card document. After results exist, bring
back a numeric headline table with only the primary endpoints; do not fill the
current dashes with predicted numbers.

## Gate and next action

This audit does **not** change the benchmark, baseline, RQ, or scientific goal.
It identifies a presentation repair: separate the main-paper overview from the
execution manifest, and reserve result-table space for measured values. The
candidate passed the canonical-PDF checks and page review and is now the current
`artifacts/aamas2027/main.pdf`; the promotion receipt and final hash are recorded
in `artifacts/aamas2027/experiment_matrix_20261008_v3/`.

The next scientific action is unchanged: freeze and qualify the execution cards,
then replace the endpoint contract with a numeric hero table only after real
confirmation evidence exists.
