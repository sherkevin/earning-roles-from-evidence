# Task report — experiment-matrix design boundary

- **Date:** 2026-10-06
- **Status:** `PARTIAL`
- **Goal change requested:** `false`

## Purpose

The paper's matrix was detailed enough to look like a completed registration even though root,
seed, budget, scorer, stopping, and manifest fields are not all frozen for confirmation. This
pass makes the distinction explicit in the main text and caption.

## Change

The Experimental Questions and Matrix section now states that the matrix is a pre-specified
design scaffold. A cell is eligible for confirmation analysis only after its root, stream, seed,
budget, scorer, complete-cost contract, stopping rule, and manifest digest are frozen before the
corresponding calls. Unfrozen cells remain planned or `UNKNOWN`.

## Verification

The source was rebuilt with the official page gate:

```text
python3 scripts/build_aamas2027.py \
  --build-dir build/paper_ai_refs_v4_20261006 \
  --main-only --require-content-pages 8
```

Receipt: total pages `9`, body pages `8`, references start on page `9`, citations resolved, and
zero overfull boxes. The artifact and source hashes are preserved under
[`artifacts/aamas2027/paper_ai_refs_v4_20261006/`](../../../artifacts/aamas2027/paper_ai_refs_v4_20261006/).

## Goal reconciliation

This improves claim hygiene but does not freeze the confirmation manifest or produce a result.
The experimental-design item remains `PARTIAL`; `goal_change_requested=false`.

## Next action

When the ownership gate and baseline parity are resolved, generate the immutable confirmation
manifest and replace only the corresponding planned/TBD cells with audited results.
