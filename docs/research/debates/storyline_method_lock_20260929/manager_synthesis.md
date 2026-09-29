# Manager synthesis — storyline and method debate

- **Date**：2026-09-29
- **Evidence basis**：three independent Round 0 reports, active six-document registry, prior N02/N03 reports, and Orca process record
- **Scientific status**：`STORYLINE_CANDIDATE_FRAMING / NOVELTY_OPEN / METHOD_NOT_READY / BENCHMARK_NOT_READY`
- **Active documents changed**：none
- **Goal changed**：none

## 1. What the debate established

The project has a coherent candidate story:

```text
real delivery
→ recipient use/modify/reject
→ attributable situated judgment
→ public role evidence
→ future owner assignment before execution
→ unseen quality and complete cost
```

This is sharper than a generic “agents evaluate one another” framing because recipient use, ownership and future assignment are necessary parts of the proposed problem. The event-time distinction between decision index and feedback-arrival index, and the public/private evidence boundary, are useful foundations. Round 1 correctly warns that these foundations are not yet novelty evidence.

The debate did **not** establish that the story is novel or that the method works. Existing role/reputation/delegation ideas may cover the broad pattern “third-party assessment influences future partner choice.” The defensible novelty candidate is narrower: responsibility-safe evidence must separate recipient integration error from producer defect, remain correctable when delayed evidence arrives, and be consumed by a different future owner before execution. Round 1 shows that even this candidate can be a delayed contextual trust or pooled reputation system unless a same-information counterfactual proves otherwise.

## 2. Evaluation against the three active standards

| Gate | Current judgment | Why | Required closure |
|---|---|---|---|
| Storyline A sharp problem | `CANDIDATE_FRAMING` | One MAS-specific question and explicit causal chain, but minimum counterexample is not yet audited | Write minimal counterexample and closest-neighbor novelty table |
| Storyline B identifiable innovation | `OPEN` | responsibility/propagation/delay candidate is plausible but same-info trust/bandit may explain it | fixed treatment + same-info counterfactual + prior-art audit |
| Storyline C causal chain | `NOT_READY` | no independent later assignment/unseen-root evidence | root-level event chain with separate denominators |
| Storyline D claim/evidence | `PASS_FOR_BOUNDARY` | active text correctly avoids claiming efficacy | keep claim levels synchronized |
| Storyline E–H paper logic | `PASS_FOR_SCAFFOLD` | paragraph duties and H1/H2/H3 are specified | write only after evidence levels close |
| Method A formal completeness | `NOT_READY` | `U` and RARE remain interfaces/candidates | method-lock card with replayable algorithm |
| Method B novelty | `NOT_READY` | closest updater/trust/bandit not yet parity-tested | same-info baseline and component counterfactuals |
| Method C online properties | `NOT_READY` | no live latency, backlog, drift, forgetting, cost evidence | bounded workload matrix |
| Method E–G objective/selection bias | `OPEN` | target and selected-only correction not fixed | estimand, propensity and judge reliability card |
| Benchmark/baseline | `NOT_READY` | candidate roots, runner, later assignment, closest adapter and cell manifest open | keep tracks separate and complete qualification |

## 3. What to absorb into the main line

1. **Keep the main question, sharpen the obstruction.** Do not replace the original role-learning line with a generic workflow or co-evolution question. State the obstruction as contaminated and delayed recipient evidence.
2. **Treat realtime/timeliness/stability as three falsifiable properties.** This decomposition is useful and should remain, but it is an evaluation framework until one concrete updater is frozen.
3. **Make public evidence consumption explicit.** The future owner must be a separate event actor; `assignment` must be recorded before delivery and must cite the public evidence snapshot it saw.
4. **Separate four labels and three estimands.** `situated_judgment`, independent `producer_contract`, recipient integration/adoption, and later outcome must not be collapsed. The primary estimand must be selected before tuning.
5. **Measure peer persistence rather than assume specialization.** Define how each `H_u` is carried across episodes and run identity permutation; otherwise the role claim is not identifiable.
6. **Use composition tests as supporting evidence only.** Leave-one-out and interactions can show necessity after the complete mechanism beats the strongest same-information control; interaction alone cannot prove innovation.

## 4. Required next work (without changing active docs)

### Gate A — prior-art and sharp counterexample

Produce a five-neighbor table covering observation, responsibility/credit, public propagation, delay correction, update state and future decision. Construct one event stream where raw acceptance and contextual trust make the wrong producer assignment, while the proposed responsibility/late mechanism makes the correct one. If no such stream exists, record the novelty claim as failed.

### Gate B — method-lock card

Freeze one candidate instance with:

- objective/estimand and quality–complete-cost accounting;
- context encoding, state dimensions/capacity/eviction;
- responsibility fields and eligibility/no-op rules;
- exact incremental update and exploration/propensity;
- future-owner assignment operator and evidence snapshot;
- duplicate, late correction, tombstone, version replacement, snapshot/restore;
- time/space complexity and state digest replay invariant.

RARE, RLS, online SGD and periodic refit remain candidates/comparators until this card is reviewed. The historical RARE-Anchor algebra concern is candidate-only and must first receive a zero-call unit test.

That zero-call audit has now been run: consolidation can erase the just-learned preference (`θ: 0.5 → 0.0` in the one-dimensional case), and 300 late corrections create a queue of length 300 despite the declared bounded-state form. The candidate is blocked pending design repair; this does not change active method v1.0 or the Goal.

### Gate C — causal measurement card

Publish a field-arrival table and independent denominators for `gate-only`, `judgment-only`, `gate+judgment`, `contract-only`, recipient integration and later outcome. Add judge reliability/shared-model sensitivity and selected-only propensity handling. No gate may read the target it is later used to predict without an independent holdout target.

### Gate D — benchmark/baseline qualification

Keep `ArtifactRole` and `PeerSelect` as separate tracks until the benchmark evaluation v1.2 gates pass. Finish authority/root scorecard, later assignment, independent streams, raw/RARE/closest published adapters, runner parity and full cell manifest before any formal effect stream or A800.

## 5. Kill criteria carried forward

- same-information contextual trust/bandit reproduces all gain;
- situated judgment has no out-of-sample increment over raw/terminal/contract-only signals;
- future owner assignment does not change before execution or does not improve unseen quality/full cost;
- recipient-owned edits are charged to producer, UNKNOWN is treated as negative, or posterior outcomes leak into decisions;
- peer performance is exchangeable after identity permutation;
- replay, late correction, state cap, latency, drift recovery, forgetting or complete cost misses the pre-registered gate.

These are stop conditions for the relevant claim, not permission to silently lower `GOAL.md`.

## 6. Goal comparison

| Goal requirement | Current evidence | Gap |
|---|---|---|
| G1 situated recipient judgment and attribution | real v6 chain shows responsibility gate can block an ineligible update | no eligible producer-defect learning signal or later assignment effect |
| G2 real-time online update | protocol contracts and zero-call replay seams exist | no locked updater or live realtime/timeliness/stability result |
| G3 future assignment and unseen quality/cost | assignment attestation seam exists | no independent live histories, unseen root outcome or complete-cost result |
| G4 publishable integrated method | storyline framing and strict standards exist | novelty, algorithm, benchmark and baseline remain open |

The distance is therefore methodological and identification-related rather than cosmetic: the story is ready for a disciplined method-lock stage, while the paper-level scientific claims are not yet supported. The next round must close the nearest-method counterfactual, algorithm and causal measurement gates before expanding experiments.
