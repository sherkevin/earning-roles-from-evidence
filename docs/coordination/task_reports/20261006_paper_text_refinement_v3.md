# Task report — v3 paper text refinement and rebuild

Date: 2026-10-06
Status: `PARTIAL`
Goal change requested: `false`
Scientific result: `none`

## Changes

- The baseline table now states that a closest published adapter enters the
  matrix only after faithful qualification; otherwise the card records an
  explicit `NO-GO` instead of substituting a self-authored weak control.
- RQ1 now declares a field-level feature manifest (judgment-only,
  producer-check/terminal-only, and declared fusion) and fixes artifact, owner,
  Qp/Y, read cut, arrival schedule and cost for legal judgment mutations.
- H1--H4 endpoint cards now require an exploration floor/positivity condition
  in addition to the control, precision target, interval and stopping rule.

These are design and identifiability clarifications. No result cell, claim level,
active method version or Goal requirement was changed.

## Build and visual check

Command:

```text
python3 scripts/build_aamas2027.py --main-only \
  --build-dir build_paper_v26b --require-content-pages 8
```

Promoted artifact:
`artifacts/aamas2027/paper_figure_refresh_v3_20261006/main.pdf`

- 10 total pages;
- exactly 8 body pages;
- references start on page 9;
- unresolved citations: false;
- overfull boxes: 0;
- PDF SHA-256:
  `3624e8917e77d738c4cd5d8281def32dc944c4ce353d9cc217fea54c841b8f37`.

Pages 2, 3, 7 and 8 were rendered at 110 dpi and visually inspected. The new
baseline paragraph and feature-manifest sentence fit without clipping; all three
vector figures remain legible.

## Gate reconciliation

The draft remains an internal pre-results revision. The field-level manifest and
NO-GO rule make the future comparison more identifiable, but live same-information
parity, a second structural root, independent histories, later assignment/use,
complete cost and measured online/stability results remain open. The scientific
submission gate stays closed.
