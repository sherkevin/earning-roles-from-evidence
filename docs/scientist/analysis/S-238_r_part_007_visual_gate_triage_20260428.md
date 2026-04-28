# S-238 R-PART-007 Visual Gate Triage

Date: 2026-04-28
Author role: scientist
Review artifact: `artifacts/idea_reviews/reviewer_20260428_1015_partial_v1gate/review.md`

## 1. Judgment

I accept `R-PART-007` as a useful candidate-visual gate. Its findings match direct inspection:

- `figure1_v1.png` is a cleaner direction than the old Figure 1 and is safe to wire into the main paper.
- `figure2_v1.png` and `figure3_v1.png` should not replace the current paper figures yet because they are too dense at the current placement and still contain draft/scaffold labels.
- The current cautious captions in `edo_paper.tex` should remain because the figures are mechanism sketches, not empirical evidence.

## 2. Accepted Fixes

Actions taken:

1. Replaced the main-paper Figure 1 include with `figure1_v1.png`.
2. Softened the Figure 1 generation prompt language from the more absolute "one context, no organization" to "single shared context".
3. Updated the Figure 2 prompt for v2:
   - use "(c) Logged evidence trail" rather than "Reproducible evidence trail";
   - use "evidence bundle" rather than "accepted evidence";
   - prohibit design-scaffold text and duplicate panel titles;
   - state that the rail logs artifacts without implying positive empirical validation.
4. Updated the Figure 3 prompt for v2:
   - remove visible layout-zone scaffolding;
   - use paper-facing labels "call tool" and "update memory";
   - use "evidence bundle" in the memory loop;
   - keep the single-hop diagram compact and semantic.
5. Updated `USER_TODO.md` `C-026` so the user can render v2 from the revised prompts.

## 3. Rejected Or Deferred Points

- I did not replace Figure 2 or Figure 3 with the v1 images.
- I did not trigger a full-paper review from candidate images that are not yet wired into LaTeX.
- I did not request a new visual gate until the user renders v2 and the scientist wires the assets into the paper.

## 4. Verification

Build command:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/build_paper.ps1" -Clean
```

Build result after wiring Figure 1 v1:

```text
[OK] build succeeded
PDF pages including Limitations and References: 10
Main body ends on page 8: COMPLIANT
Overfull hboxes: 0
Underfull hboxes: 32
```

## 5. Status

`S-238` is complete. `C-026` remains open only for Figure 2 / Figure 3 v2 rendering.
