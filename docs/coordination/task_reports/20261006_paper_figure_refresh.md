# Task report — AI figure refresh and eight-page PDF rebuild

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`

## Deliverable

The latest AI-generated figure iterations were selected after visual inspection and
installed as the paper assets:

- Figure 1 `overview.pdf`: open responsibility spine from peer context through
  delayed selected-only feedback;
- Figure 2 `method_state.pdf`: episode, public-evidence gate and local-decision
  lanes with the before-selection/after-seal timing;
- Figure 3 `experiment_map.pdf`: ArtifactRole and PeerSelect tracks, matched policy
  arms and the four pre-specified research endpoints.

The source prompts and candidate PNG/PDF files remain versioned under
`article/aamas2027/figures/ai_versions/v18*` through `v21*`. The three selected
PDFs are byte-identical to v19, v20 and v21 respectively.

## Build and visual checks

Command:

```text
python3 scripts/build_aamas2027.py --main-only \
  --build-dir build_paper_v22 --require-content-pages 8
```

The isolated build produced [main.pdf](../../artifacts/aamas2027/paper_figure_refresh_20261006/main.pdf)
with 10 total pages, references beginning on page 9, and exactly 8 body pages.
Citation resolution passed and the LaTeX log reports zero overfull boxes. Pages 1,
7, 8, 9 and 10 were rendered and visually inspected; the figures are legible at
paper scale and contain no clipping or overlap.

The verification and source hashes are recorded in
[`paper_figure_refresh_20261006`](../../artifacts/aamas2027/paper_figure_refresh_20261006/).
This is an internal revision: the title/metadata still contain the submission
placeholder and the scientific submission gate remains closed.

## Scientific boundary

The figure refresh improves the paper's communication and does not create empirical
evidence. Result cells remain blank until the benchmark, same-information baselines,
independent histories, costs and real confirmation manifests pass their gates.
