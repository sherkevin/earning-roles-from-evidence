# Task report — typed signal-contract qualification

Date: 2026-10-06
Status: `PARTIAL` (engineering prerequisite only)
Goal change requested: `false`
Scientific result: `none`

## Purpose and Goal alignment

The preceding parent-source smoke showed `J` (recipient judgment) equal to
`accept` while the independent producer and adoption checks failed. This task
qualified the smallest reusable, read-only inventory needed before another
root: preserve `Qp`, `J`, `A`, `D`, `Y`, and `L` as separate observations and
make their dependence visible. It addresses ER-G1 responsibility semantics,
ER-G2 update-boundary clarity, ER-G3 arm information parity, and ER-G4
reproducible UNKNOWN handling. It does not alter the active method, benchmark,
baseline set, or Goal.

## Frozen input and evidence

Before execution the zero-call configuration was written to
[`n03_signal_contract_qualification_20261007_v1/config.json`](../../../experiments/logs/n03_signal_contract_qualification_20261007_v1/config.json).
The implementation is [`peerrolebench_signal_contract.py`](../../../scripts/peerrolebench_signal_contract.py)
and the mutation tests are [`test_peerrolebench_signal_contract.py`](../../../tests/test_peerrolebench_signal_contract.py).
The command ran against the recorded repository commit and used Python's local
pytest only: 6 tests passed, 0 real API calls, 0 GPU jobs. Raw test output and
the digest are retained in the dated log directory; the receipt is
[`summary.json`](../../../experiments/logs/n03_signal_contract_qualification_20261007_v1/summary.json).

The adapter reuses `BASELINE_ARM_SPECS` and existing mapping constants. It reads
only a completed episode mapping, performs no API/network calls, and always
sets `policy_eligible=false`. It does not validate native lineage, read cuts,
assignment offers, duplicate/late/correction order, or policy updates; the
existing sidecar/offer/peer-history bridge remains the only eligibility gate.
Historical `Y_current` is recorded as `derived_from=(D, recipient)` because the
runner's outcome field is downstream adoption quality subject to recipient
completeness. It is not an independent terminal signal.

## What passed and what remains open

Passed at the engineering boundary:

- all seven registered arm names are reused without a second baseline registry;
- `Qp/J/A/D/Y/L` are emitted as separate rows, with categorical labels mapped
  only when the existing public mapping recognizes the raw value;
- unknown values fail closed and every row is explicitly non-eligible;
- `Y_current` records its dependence on `D` and recipient completeness rather
  than being presented as independent terminal evidence;
- the `contextual_trust_linear` name is retained only as an explicit alias of
  the registered `contextual_trust` arm.

Still open:

- the current live runner does not yet emit independent `A`, `D`, and `Y`
  receipts. Its historical `Y_current` is a diagnostic derived from `D` and
  recipient completeness and cannot qualify `terminal_only`; historical
  UNKNOWN is never relabelled;
- the adapter is not yet connected to `FeedbackSidecar`,
  `AssignmentEvidenceOffer`, peer-history, or the event-time replay path. The
  existing native bridge remains the only place allowed to update a policy;
- native selection/delivery/ledger lineage, read-cut, duplicate/late/correction
  and assignment-credit validation remain open and must be qualified by the
  existing typed adapters, not by this inventory helper;
- no second root, independent history, seven-arm live parity, assignment
  effect, real-time/forgetting measurement, or efficacy estimate exists.

## Failure classification and next repair

The initial draft was too permissive: it reimplemented stream/update logic,
accepted arbitrary mapping versions, returned early for forged UNKNOWN rows, and
used a new `contextual_trust_linear` arm name. Independent review rejected that
shape. The final bounded adapter removes those paths and reuses the registered
contracts, while making no native-provenance claim. This is a measurement
inventory repair, not a model improvement.

The next smallest task is to add a zero-call projection mutation matrix using
real `RawAcceptanceSidecar`, `TerminalOutcomeSidecar`, `FeedbackSidecar`, and
`AssignmentEvidenceOffer` objects, then update the live runner to persist
independent `A`, `D`, and an actually independent `Y` receipt. Only after that
passes can a second root be considered. No A800 job or baseline freeze is
authorized by this report.

## Goal reconciliation

ER-G1: `PARTIAL`; signal disagreement is now representable, but future
assignment and downstream effect remain unmeasured.
ER-G2: `PARTIAL`; the inventory leaves the update boundary untouched and the
native bridge remains the gate; no real-time training result exists.
ER-G3: `OPEN`; the seven-arm registry is explicit, but live same-information
parity is absent.
ER-G4: `OPEN`; this was a zero-call protocol test, not a real experiment.
ER-G5: G1/G2 prerequisite improved, scientific gate remains closed.
ER-G6: no Goal change requested (`false`).
