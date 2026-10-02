# Figure visual review v1 — AAMAS role-evidence paper

- Date: 2026-10-02
- Reviewer: independent Codex visual audit
- Scope: `article/aamas2027/figures/{overview,timeline,experiment_map}.pdf`, `scripts/build_aamas_figures.py`, and rendered pages 3 and 5 of `article/aamas2027/build/main.pdf`.
- Reference standards: local `paper-figure-design` skill, the local `/topconf-figure-gallery` audit already recorded in the project, and the official AAMAS template constraints.
- Status: review only; this report does not overwrite the v1 figures.

The preserved snapshots are retained at `article/aamas2027/figures/versions/v0_baseline_20261002/`, `v1_feedback_target_and_fonts_20261002/`, and `v2_outer_feedback_route_20261002/`; the current candidate is additionally preserved at `v3_outer_right_grey_feedback_20261002/`. Each directory keeps the PDFs and the generator used for that version.

## Current asset inventory

| Figure | Intended role | PDF size | Paper placement | One-sentence test |
|---|---|---:|---|---|
| `overview.pdf` | Main mechanism / closed loop | 501.84 x 193.82 pt | Full width | A situated delivery is judged by its recipient, admitted as responsibility-safe evidence, and affects only a later assignment and delayed credit. |
| `timeline.pdf` | Event-time and legal boundary | 242.97 x 129.92 pt | Single column | A future outcome is unavailable when the next assignment is sealed, so feedback is delayed and cannot rewrite that assignment. |
| `experiment_map.pdf` | Benchmark/baseline/RQ map | 501.84 x 164.34 pt | Full width | Two tracks feed the same matched policy menu and are scored on information, assignment, cost, and safety endpoints. |

## What passes

- The three figures have a coherent visual grammar: green for evidence/safety, blue for decision and outcome, orange for situated observation, and gray for neutral text/boundaries.
- They use few colors, avoid red/green contrast, have no decorative gradients, no 3-D effects, and no empirical numbers invented inside diagrams.
- The full-width figures fit the available two-column width without clipping. The single-column timeline remains legible at the rendered paper scale and has a short independent caption.
- The captions state the figure takeaway and explicitly mark the planned ledger fields as planned rather than observed results. All three figures have `\\Description{}` entries.
- The experiment map is especially clean: its left-to-right grammar (tracks → matched policies → endpoints) agrees with the paper's benchmark/baseline argument.
- Page-level inspection at 100% showed no text collision in the panel bodies, captions, or table/figure boundaries.

## Required v2 fixes

### 1. Correct the delayed-feedback target (high priority)

In both `overview.pdf` and `timeline.pdf`, the orange dashed path starts near `Delayed credit` but travels above the diagram and ends at the top of `Public role evidence` / `evidence / UNKNOWN`. The caption says that delayed feedback changes a later read cut only. The visible endpoint therefore contradicts the legal timing claim: a reader can infer that delayed credit rewrites evidence publication.

The dashed path should terminate at `Future assignment` / `seal assignment`, because that is the only stage whose later read cut can change. Route the path around the outer perimeter or under the lower row so it does not cross Stage 1 text or any box interior. Keep the arrowhead visibly entering the assignment/read-cut box. Update the description if the route changes.

Use a neutral gray dashed stroke for this temporal dependency (or retain a
clearly labeled temporal color), because orange already denotes situated
observation and green denotes admitted evidence. A gray dashed stroke makes the
edge's timing semantics independent of the endpoint colors.

### 2. Embed TrueType fonts (high priority)

`pdffonts` reports Type 3 DejaVu fonts for all three current PDFs. The local figure standard requests `pdf.fonttype=42` / embedded TrueType fonts for publication vector assets. Set these parameters before importing `pyplot` or before saving:

```python
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
```

Regenerate all three PDFs and verify with `pdffonts`; the output should report a TrueType/OpenType font type rather than Type 3. Preserve the current PDFs as version v1 before replacing the paper-facing assets.

### 3. Keep the single-column timeline conservative

The timeline is readable in the current paper render, but its small labels are near the lower comfortable limit. Do not add more fields. If the feedback route is changed, preserve the current six-stage text and increase label size only if the resulting PDF still fits the single-column height.

## Scores against the figure gate

| Criterion | Score | Reason |
|---|---:|---|
| Figure 1 / overview 30-second takeaway | 8/10 | Closed loop is immediately visible; feedback endpoint currently makes the timing story ambiguous. |
| Semantic color consistency | 9/10 | Four stable semantic groups and redundant labels; no unsafe red/green encoding. |
| Layout and spacing | 8/10 | Strong box grid and whitespace; dashed route crosses a box in the current version. |
| Single-column readability | 8/10 | Timeline remains readable at paper scale, though text should not shrink further. |
| Caption and accessibility | 9/10 | Captions are self-contained and descriptions are present. |
| Reproducibility/vector quality | 7/10 | Script is deterministic and PDFs are vector, but Type 3 fonts need correction. |
| Experiment map clarity | 9/10 | Tracks, policy arms, and endpoints are clearly separated. |

**Current visual gate: conditional pass.** The figures are suitable for layout prototyping and reviewer discussion. The v2 paper-facing set should not be frozen until the dashed feedback endpoint and font embedding are fixed. The later v3 candidate addresses both items and remains subject to final story/visual review.

## Version policy for the next iteration

1. Copy the current three PDFs to a versioned review directory before regeneration.
2. Generate v2 from the same script with only the route and font changes.
3. Run `pdffonts`, `pdfinfo`, and a 100% page render for v2.
4. Ask an independent reviewer to inspect v2 against this report. Keep v1 and v2 side by side; do not delete v1.
5. Only then update the paper's `figures/` assets and rebuild the main PDF.
