# 2026-10-03 Same-information baseline repair proposal

## Finding

The active baseline contract correctly keeps `contextual_trust` open, but its current
implementation is not yet a strong same-information comparator. `ContextualTrustPolicy` keys a
Beta update by `context_key × candidate`, while RARE consumes fixed candidate feature vectors,
responsibility-gated rows and event-time corrections. Comparing them now would confound the
closed-loop mechanism with the input representation and correction channel.

## Required contract before live parity

Freeze one public feature schema, `artifactrole-public-v1`, built only from fields available at
the policy read cut: candidate registry/version, task context representation, role/state scope,
public evidence aggregates, arrival watermark and UNKNOWN/correction metadata. It must exclude
Qp hidden checks, terminal future outcomes, raw artifacts, recipient private text and another arm's
state. The schema version, dimension, encoder digest and state capacity are part of every selection
receipt.

RARE and the contextual comparator must receive the same `φ` vectors, candidate menu, selected-only
eligible rows, arrival order, correction lineage, exploration floor, model/API/tool budget and
complete cost ledger. The comparator may use a simpler update (for example context×candidate
ridge/logistic or Beta projection), but it must explicitly consume or explicitly no-op on the same
correction rows; that behavior is a predeclared ablation, not an accidental information mismatch.

## Zero-call acceptance checks

Before any live arm is run, a parity receipt must show for every policy:

1. identical candidate registry/menu/order and `φ` digest at the same read cut;
2. identical legal feedback rows, `UNKNOWN` denominator and selected-only binding;
3. identical propensity/exploration and state-capacity/cost fields;
4. distinct update semantics recorded by versioned policy state, with no shared live memory;
5. correction, duplicate, late and resource-failure rows replayed under the declared arm rule.

If any arm receives a different public feature or cost budget, it is not a same-information
baseline and must be reported as a separate ablation. This proposal does not select the final
updater, change the active benchmark, or authorize API/GPU work.

`goal_change_requested=false`。
