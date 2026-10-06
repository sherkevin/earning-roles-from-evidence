# Task report — freeze the next C1 structural-owner live card

**Date:** 2026-10-06
**Status:** `PARTIAL`
**Goal change requested:** `false`
**Scientific API calls:** `0`

## Purpose

The previous C1 v3 live trace stopped the contextual arm because model wording was treated as a
hard ownership gate. After ADR 0047 and method v1.2, the next bounded card must carry the structural
owner contract explicitly before any new API request.

## Frozen card changes

[`n03_c1_pipe3_bounded_live_dev_v2.json`](../../../configs/aamas2027/n03_c1_pipe3_bounded_live_dev_v2.json)
keeps the same one-root development scope, three arms, candidate menu, model route, exploration,
request cap, and UNKNOWN policy as the historical C1 card. It adds:

- `two-stage-role-evidence-v3-structural-owner` as the gate version;
- contract/registry/scorer as the owner source;
- model judged role as calibration-only with `judged_role_agrees` retained;
- an explicit registered producer-defect candidate (`peer-b@v1`);
- complete cost fields including action wall time and repair-cost semantics.

The runner now reads the registration from the card rather than hardcoding it and refuses mutated
v2 responsibility contracts before dispatch. Historical v1 cards remain readable for audit but are
not promoted.

## Qualification

The first card-contract regression intentionally failed: the validator checked whether the manifest
name ended in `-v2`, while the frozen name correctly ends in `-v2-structural-owner`; four mutation
cases were not rejected. The failure was fixed before any API call. The corrected targeted suite
passes **16 tests**, including all four fail-closed mutations and the existing zero-API three-arm
contract qualification.

## Boundary and next step

This card is design/contract evidence only; it does not prove benchmark validity, baseline parity,
future assignment quality, real-time training, or self-evolution. After the card and source commit
are frozen, one bounded real-API rerun may test whether judged-role disagreement is logged without
censoring structurally eligible producer evidence. Its result remains development-only and will
not fill the paper's scientific result cells.
