# Task report — watermarked prospective experiment guide

Date: 2026-10-08  
Status: independent guide completed, compiled and visually verified.  
Goal change requested: false.

**Subsequent confidence audit (2026-10-08): superseded as an expectation guide.**
The v1 GO covered labelled targets and local arithmetic, not a fitted joint
population, variance or realistic method ranking. The subsequent independent
review found those predictions unidentifiable. Values and artifacts remain
archived; the [v2 report](20261008_guide_confidence_and_joint_distribution.md)
records the correction without rewriting historical evidence.

## Purpose and criterion

Produce the user-authorized independent Guide PDF containing reasonable target
matrices, visibly distinguished from real results. It must map one-to-one to
the three body tables, expose assumptions, use real data as scoped anchors,
derive internally related quantities consistently, retain previous drafts, and
leave the canonical main PDF and empirical results out of its write paths.

## Delivered design

The four-page source covers: measured PIPE3 anchors and ArtifactRole targets;
PeerSelect service/adaptation budgets; mechanism and responsibility targets;
sensitivity, conditional precision and execution-scale calculations. Specification
and arithmetic artifacts are in the versioned Guide directory. Every page has a
diagonal `GUIDE --- NOT OBSERVED` watermark and prospective status header/footer.

S1 targets a 5 percentage-point future-quality improvement against a strong
control, while allowing extra cost. It does not assume RARE wins every metric.
The sensitivity panel includes a strong-control win and a null. Utility derives
from one cost coefficient, Brier/ECE from one risk/forecast model, and the four-cell
interaction and safety average exactly match their inputs. Service/backlog uses
an explicit maximum-time assumption; memory has a byte-level allowance.

The guide does not invent result intervals, significance, completed stream
counts, backbone training measurements, or results for an unqualified published
adapter. One undefined selected-only ablation is marked N/A. Conditional adapter
rows are labelled proxies. Guide-only metric definitions and thresholds do not
activate or replace the existing endpoint cards.

## Independent review and iteration

Two Codex gpt-6-sol read-only audits were used: one located the active metric
contracts; one checked the guide calculations and method implications. The first
confirmed that numerical thresholds and several precise measurement functions
remain NOT_FROZEN. The second requested five fixes: legal credit-only semantics,
within-root precision scope, backlog/max-service dependence, a strong-control-win
scenario, and exact-zero floating-point cleanup. All were incorporated; the
reviewer issued GO for the revised guide text/calculations, conditional on the
rebuilt PDF and visible watermark checks. Initial PDF, TeX, spec, calculations
and build receipts remain under `pre_independent_review/`.

## Goal comparison

This supplies a quantitative development target and budget reality check. It
does not close ER-G3/ER-G4, any scientific submission gate, benchmark/root or
baseline qualification, or final backbone/update selection. Future observations
must be compared to these targets with their actual denominators and costs; they
must not be edited to match S1. No new API, GPU or empirical benchmark run occurred.

## Files and verification

- Source: `article/aamas2027/guides/v1_20261008/guide_experiment_matrix.tex`.
- Input definitions: `docs/paper/aamas2027/guides/v1_20261008/target_spec.json`.
- Explanation: `docs/paper/aamas2027/guides/v1_20261008/README.md`.
- Versioned PDF/math: `artifacts/aamas2027/guide_experiment_matrix_v1_20261008/`.
- Build provenance: `experiments/logs/experiment_target_guide_20261008_v1/`.
- Independent guide master: `artifacts/aamas2027/guide_experiment_matrix.pdf`.

Final PDF: 4 A4 pages; 0 overfull boxes; 0 undefined references. All four page
renders were inspected: the complete diagonal watermark is visible inside the
page, the prospective header/footer are present, and tables/text are unclipped.
The first visual check caught an oversized clipped watermark and one paragraph
overflow; those were corrected, and the pre-fix PDF/source and failed receipt
were preserved under `pre_visual_refinement/`. The final PDF SHA-256 is
`2dd32352bc260a96d7b2060584e3de3e079fb7a5233bc93dd5a13c70621ced35`.
Source, specification and output hashes are recorded in verification and guide
master receipts. The initial source compiled successfully with the desktop
editor's compiler; local latexmk exported the final PDF. No canonical paper
file or empirical result was written by this task.
