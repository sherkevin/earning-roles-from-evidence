# Task report — v22/v24 figure promotion and PDF refresh

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`

The previous figure report records the v19/v20/v21 candidate set and remains a
historical receipt. A later visual pass produced v22 for Figure 2 and v24 for
Figure 3; this follow-up records their promotion without rewriting that history.

## Selected assets

- Figure 1: the existing overview asset;
- Figure 2: `v22_method_open_lanes_20261006/method_state_v22.pdf`, which removes
  decorative panels and makes the episode, public evidence and local decision lanes
  read as one temporal spine;
- Figure 3: `v24_evaluation_no_method_cards_20261006/experiment_map_v24.pdf`,
  which uses open three-column grouping for tracks, policies and endpoints.

Prompts, PNG candidates and the intermediate v23 experiment map remain versioned.
The selected PDFs are byte-identical to the v22 and v24 source files.

## Build evidence

```text
python3 scripts/build_aamas2027.py --main-only \
  --build-dir build_paper_v25 --require-content-pages 8
```

The new artifact is
[paper_figure_refresh_v2_20261006/main.pdf](../../artifacts/aamas2027/paper_figure_refresh_v2_20261006/main.pdf).
It has 10 total pages, references beginning on page 9, exactly 8 body pages,
resolved citations and zero overfull boxes. Pages 7 and 8 were rendered and
visually inspected after the new figures were installed; no clipping or overlap
was found.

## Boundary

This is a presentation improvement only. It does not alter the active story,
method, benchmark, baseline or Goal, and it does not fill any result cell or open
the scientific submission gate.
