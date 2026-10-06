# Task report — native projection mutation qualification

Date: 2026-10-07
Status: `PARTIAL` (engineering prerequisite only)
Goal change requested: `false`
Scientific result: `none`

## Purpose

The previous task only inventoried the completed C1 episode. This task exercised
the existing typed projections that are allowed to cross the policy boundary:
raw recipient acceptance and canonical terminal outcome. The purpose was to
make the next live card fail before a policy runner starts when selection,
delivery, candidate, mapping, UNKNOWN, late, duplicate, or public-boundary
evidence is invalid. No new updater or benchmark arm was introduced.

## Frozen runs and evidence

Both runs wrote configuration before execution and used the current commit
`528c8b6`. They made zero real API calls and launched zero GPU jobs.

- [`n03_terminal_projection_mutation_20261007_v1`](../../../experiments/logs/n03_terminal_projection_mutation_20261007_v1/summary.json)
  ran the canonical terminal-only adapter over all seven registered arms. The
  positive cell passed: `terminal_only` consumed one eligible terminal signal
  and updated once; the other six arms ignored it; public-input digests and
  snapshot replay matched. Nine negative cells (wrong outcome/delivery/
  selection/candidate/mapping, UNKNOWN, late, duplicate) were rejected before
  runner start and produced zero policy updates.
- [`n03_raw_acceptance_projection_mutation_20261007_v1`](../../../experiments/logs/n03_raw_acceptance_projection_mutation_20261007_v1/summary.json)
  passed six cells: accept and reject map through the existing
  `raw-acceptance-v1` projection, while canonical-label mutation, rework,
  unchosen-candidate, selection-binding, and public-boundary mutations fail
  closed. The two positive cells update only the raw-acceptance comparator.

The raw JSONL, console output, component hashes, and summary are retained under
each directory. These are protocol/runner qualifications, not model results.

## Interpretation and limits

The tests establish that the existing native sidecars can enforce their own
lineage and label contracts before policy updates. They do not validate the
new read-only inventory as a gate, and they do not show that a recipient
judgment predicts producer quality or downstream value.

The current C1 runner still defines `Y_current` from downstream adoption plus
recipient scorer completeness. It is therefore a derived diagnostic, not an
independent terminal outcome. This run does not qualify an independent `Y`,
does not make `terminal_only` scientifically comparable to the live arms, and
does not repair the missing `A`/`D`/independent-`Y` receipts. Historical
UNKNOWN values remain UNKNOWN.

## Goal reconciliation and next step

ER-G1: `PARTIAL`; native projection lineage is stronger, but the complete
judgment→role→future-assignment→quality chain remains unmeasured.

ER-G2: `OPEN`; no online training, latency, drift, or forgetting result was run.

ER-G3: `PARTIAL`; raw and terminal adapters are qualified offline, but all
seven arms do not yet have live same-information parity and the terminal arm has
no independent Y in the current runner.

ER-G4: `PARTIAL`; mutation evidence is reproducible and fail-closed, but no real
LLM comparison was performed.

ER-G5: the native projection prerequisite advances; scientific submission gate
remains closed. No A800 job is justified.

ER-G6: no Goal change requested (`false`).

The next smallest repair is to add first-class recipient action `A`, downstream
adoption `D`, and an actually independent later/terminal `Y` record to the
runner and bind each to the existing sidecars/assignment offers. Only then can
the second root and seven-arm live parity card be frozen.
