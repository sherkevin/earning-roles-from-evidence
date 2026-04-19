# EDO-Lite Executable Specification

**Prepared by:** Engineer 3, Agent-3 Session 6  
**Date:** 2026-04-14  
**Scope:** Prototype-level (Stage-1) concrete definitions for the four main reviewer-flagged underspecifications in `idea.md`. This note bridges the gap between the conceptual EDO framework and an implementable, reviewable prototype.

---

## 0. Purpose and Scope

gpt-4.1-mini reviewer batch (Session 4) consistently scored technical_soundness=6 and executability=6, citing:

> "Core update rules (persona, neighbor beliefs, utilities) remain conceptual, not yet algorithmically pinned down."  
> "Several core mechanisms (persona update, utility estimation, task signature extraction, audit protocol) remain semi-formal and underspecified."

This note pins down the four underspecified pieces at a level that is:
- **Implementable** in the current `workspace/idea04_core/` Python codebase
- **Falsifiable** with the current HotpotQA + chain/star experiment harness
- **Honest** about what is prototype-scope vs. full-EDO-scope

The current prototype (`TCPB`) is a **restricted instantiation** of EDO. All specs below are written for the prototype scope first, then mapped to full-EDO scope.

---

## 1. Task Signature Extraction: `phi(z)`

### 1.1 Full EDO Definition (from `idea.md`)

```
phi(z) = [need_decompose, need_verification, need_integration,
          need_exploration, evidence_breadth, uncertainty, cost_sensitivity]
```

Each dimension is a scalar in [0, 1].

### 1.2 Prototype Extraction Rule (deterministic, no LLM call required)

For the current HotpotQA chain prototype, `phi(z)` is extracted from the `HandoffPacket` fields using the following deterministic rules:

| dimension | extraction rule | type |
|---|---|---|
| `need_decompose` | `1` if `hop_count == 0` else `0` | binary |
| `need_verification` | `1` if `hop_count >= 2` else `0` | binary |
| `need_integration` | `1` if `len(evidence_so_far) >= 8` else `0` | binary |
| `need_exploration` | `1 - min(1, len(evidence_so_far) / 10)` | continuous |
| `evidence_breadth` | `min(1, len(evidence_so_far) / 12)` | continuous |
| `uncertainty` | `packet.uncertainty` (already tracked) | continuous |
| `cost_sensitivity` | `min(1, hop_count / max_handoff)` | continuous |

**Implementation anchor:** `workspace/idea04_core/methods.py::_build_routing_features()` already computes most of these; `phi(z)` is a named alias for the vector form.

**Multi-hop heuristic** (already implemented as `_is_multihop_question`):  
If `_is_multihop_question(question)` → set `need_decompose=1` and `need_exploration=0.7` as priors at `hop_count=0`.

### 1.3 Full EDO Extension (Stage-2)

For non-HotpotQA or open-ended tasks, `phi(z)` can be extracted via a **lightweight classifier LLM call** (single system prompt, ≤ 64 tokens response):

```
System: "Given this task description, rate each of 7 dimensions from 0.0 to 1.0: 
[need_decompose, need_verification, need_integration, need_exploration, 
evidence_breadth, uncertainty, cost_sensitivity]. Output as JSON."
User: "{question}\n\nCurrent evidence count: {n}"
```

This call is optional in Stage-1 (deterministic rules suffice for HotpotQA) and mandatory in Stage-2.

---

## 2. Local Utility Estimators: `U_self`, `U_out`, `U_split`

### 2.1 Full EDO Formulas (from `idea.md`)

```
U_self_i(z)    = Fit(P_i, phi(z)) - λ_c * Cost_self(z) - λ_r * Risk_self(z)
U_out_i(z, j)  = Fit(B_i(j), phi(z)) - λ_s * SendCost(i,j) - λ_a * AuditCost(z) - λ_r * RejectRisk(j,z)
U_split_i(z)   = SplitGain(z) - λ_m * MergeCost(z) - λ_d * DepthPenalty(z) - λ_a * AuditLoad(z)
```

### 2.2 Prototype Instantiation

The prototype uses `accept / forward` only (no `split` action). Map:

| EDO term | Prototype instantiation | value range | source |
|---|---|---|---|
| `Fit(P_i, phi(z))` | `competence_i[agent_name]` (self-competence scalar) | [0, 1] | `competence_by_agent` in `MethodState` |
| `Cost_self(z)` | `0` (prototype assumes uniform cost per hop) | 0 | constant |
| `Risk_self(z)` | `packet.uncertainty` | [0, 1] | `HandoffPacket` |
| `Fit(B_i(j), phi(z))` | `neighbor_belief_i[j]` (peer belief in neighbor j's competence) | [0, 1] | published_competence or default |
| `SendCost(i,j)` | `0` (uniform) | 0 | constant |
| `AuditCost(z)` | `0.05` (fixed audit overhead per hop, in fraction of budget) | 0.05 | constant |
| `RejectRisk(j,z)` | `revisit_penalty` if `j in visited_nodes` else `0` | {0, 0.25} | routing_features |
| `SplitGain(z)` | **not implemented** (prototype has no split) | — | Stage-2 |
| `MergeCost(z)` | **not implemented** | — | Stage-2 |
| `DepthPenalty(z)` | `hop_count / max_handoff` (already tracks depth) | [0, 1] | HandoffPacket |
| `AuditLoad(z)` | **not implemented** | — | Stage-2 |

**Prototype scoring equations** (currently in `_score_accept` and `_score_neighbors`):

```python
# U_self prototype:
U_self = (0.55 * self_competence
        + 0.20 * evidence_sufficiency
        + 0.10 * (1.0 - uncertainty)
        - 0.10 * loop_risk
        - 0.05 * revisit_risk)

# U_out prototype (per neighbor j):
U_out_j = (0.60 * neighbor_belief_j
         + 0.25 * role_match_j
         + 0.05 * structural_prior
         - revisit_penalty_j)

# Action: accept iff U_self >= max_j(U_out_j) + accept_margin
```

**Weight justification** (deterministic, not learned):
- 0.55 on self-competence: primary signal; dominates when competence is clearly high or low
- 0.20 on evidence_sufficiency: secondary quality signal (does the agent have enough to work with?)
- 0.10 on uncertainty: small penalty for high-uncertainty states
- Loop/revisit penalties: pure safety terms to prevent cycles

These weights are **not tuned to maximize F1**. As the sensitivity analysis confirms (see `round1_v3_weight_sensitivity.md`), varying them ±2× produces < 0.003pp F1 change on the chain-200 slice. They are qualitative priors, not performance-critical hyperparameters.

### 2.3 Full EDO Extension (Stage-2)

In Stage-2, `Fit(P_i, phi(z))` is computed as:

```
Fit(P_i, phi(z)) = dot(P_i, W * phi(z)) / (||P_i|| * ||phi(z)|| + eps)
```

where `W` is a 7×7 role-task compatibility matrix, initialized as identity and updated via gradient from terminal outcomes. This is the only component requiring learning; all others remain rule-based.

---

## 3. Persona Update Rule

### 3.1 Full EDO Formula (from `idea.md`)

```
P_i^(t+1) = clip((1-μ) * P_i^t + μ * (η_local * LocalValue + η_terminal * TerminalValue - η_rework * ReworkPenalty))
```

### 3.2 Prototype Instantiation (scalar competence, not vector persona)

The current prototype uses a **scalar self-competence** per agent (a 1D simplification). The update rule is:

```python
# After each sample is accepted by accepted_node:
prev_self = competence[accepted_node][accepted_node]   # scalar in [0.05, 0.95]
raw_delta = +0.06 if answer_f1 >= 0.5 else -0.10      # terminal outcome signal
raw_delta = clip(raw_delta, -0.06, +0.06)              # max_delta cap
target    = clip(prev_self + raw_delta, 0.05, 0.95)
new_self  = 0.5 * prev_self + 0.5 * target             # momentum=0.5
```

**Mapping to full-EDO formula:**
- `LocalValue` → 0 (not implemented; would require hop-level audit events)
- `TerminalValue` → `answer_f1 >= 0.5` (binary terminal quality signal)
- `ReworkPenalty` → `answer_f1 < 0.5` (negative signal)
- `μ = 0.5 * (1 - momentum) = 0.5` (effective learning rate)
- `η_local=0, η_terminal=1, η_rework=1` (prototype only uses terminal signal)
- `clip` → competence stays in [0.05, 0.95]

**Implementation anchor:** `workspace/idea04_core/methods.py::apply_peer_post_sample_competence()` and `runner.py` post-sample update block.

### 3.3 Full-EDO Extension (Stage-2, vector persona)

Replace scalar `competence[i][i]` with vector `P_i ∈ [0,1]^7`. The update event tuple becomes:

```
LocalValue_i  = mean([label_event.value_gain for label_event in recent_accepted_by_upstream])
TerminalValue_i = terminal_quality if agent_i in critical_path else 0
ReworkPenalty_i = mean([label_event.rework_cost for label_event in recent_rejected_by_upstream])
```

All three components are computable from `routing_traces.jsonl` + `parsed_predictions.jsonl` without any new LLM calls.

Concrete update (for role dimension `k` of persona vector):

```
delta_k = eta_local * LocalValue[k] + eta_terminal * TerminalValue * task_relevance[k] - eta_rework * ReworkPenalty[k]
P_i_k^(t+1) = clip((1 - mu) * P_i_k^t + mu * clip(P_i_k^t + delta_k, 0.05, 0.95), 0.05, 0.95)
```

Default hypers: `mu=0.1, eta_local=0.5, eta_terminal=1.0, eta_rework=0.8`.

---

## 4. Termination and Audit Rules

### 4.1 Minimum Termination Rules (current prototype)

The prototype uses the following hard termination triggers (already implemented):

| trigger | condition | action |
|---|---|---|
| Max handoff | `hop_count >= max_handoff` | Force accept at current node |
| Terminal node | `neighbor_list == []` | Accept (synthesizer in chain) |
| Topology violation | `chosen_target not in adjacency[node]` | Dead-end: accept at current |
| Loop protection | `next_node in seen_nodes AND next_node != synthesizer` | Reroute to synthesizer |

**Parameters (current defaults):** `max_handoff=4`, chain topology → synthesizer is the only terminal node.

### 4.2 Audit Decision Protocol (prototype: implicit terminal audit)

In the prototype, "audit" is implicit: the terminal node (synthesizer) generates the final answer, which is compared to the gold answer. There is no hop-level upstream rejection.

**Minimal explicit audit rule for Stage-1.5 (implementable without major refactor):**

Define an `AuditDecision` enum: `{ACCEPT, ACCEPT_WITH_NOTE, REJECT_REROUTE}`.

After any non-terminal node accepts (premature accept), apply:

```python
audit_score = candidate_answer_quality(candidate_answer, evidence_so_far)
if audit_score >= ACCEPT_THRESHOLD:
    decision = ACCEPT
elif audit_score >= SOFT_THRESHOLD and hop_count < max_handoff - 1:
    decision = ACCEPT_WITH_NOTE  # pass upstream with a quality flag
else:
    decision = REJECT_REROUTE    # forward to synthesizer directly
```

Where `candidate_answer_quality` is a lightweight rule: answer length >= 2 tokens AND not a rejection phrase ("I don't know", "unable to", "[ERROR").

**Parameters:** `ACCEPT_THRESHOLD=0.5` (F1 proxy), `SOFT_THRESHOLD=0.2`.

### 4.3 Split Termination Rules (Stage-2 only)

Not applicable to current prototype (no split action). For Stage-2:

| parameter | value | rationale |
|---|---|---|
| `max_subtasks_per_split` | 3 | Prevents combinatorial explosion; merge cost grows super-linearly |
| `max_tree_depth` | 3 | Controls recursion; deeper than 3 hops rarely provides value on HotpotQA-class tasks |
| `max_total_nodes` | 12 | `max_subtasks^max_depth = 3^3 = 27` theoretical; cap at half |
| `min_split_gain_threshold` | 0.1 | Only split if `SplitGain > min_split_gain_threshold` (prevents spurious decomposition) |

---

## 5. What Is In Current Code vs. Stage-2

| EDO component | Current code status | Stage-2 requirement |
|---|---|---|
| `phi(z)` extraction | ✅ Deterministic rules in `_build_routing_features()` | LLM-based classifier for open-domain |
| `U_self` (scalar) | ✅ `_score_accept()` (weighted sum of competence + evidence) | Replace scalar competence with vector `Fit(P_i, phi)` |
| `U_out` (per neighbor) | ✅ `_score_neighbors()` | Add `AuditCost` and `RejectRisk` from historical logs |
| `U_split` | ❌ Not implemented | Requires split action + `SplitGain` estimator |
| Persona vector `P_i` | ❌ Simplified to scalar self-competence | 7-dim vector; update from audit events |
| Persona update rule | ✅ Terminal-only scalar update (`apply_peer_post_sample_competence`) | Add LocalValue / ReworkPenalty from hop-level audit |
| Audit protocol | ❌ Implicit (terminal gold comparison only) | Explicit `AuditDecision` per hop; rejection events |
| `split` action | ❌ Not implemented | Core Stage-2 primitive; creates task subtree |
| Recursive audit | ❌ Not implemented | Upstream rejects/accepts sub-results; TCPB is a degenerate case |
| Public persona | ❌ Published only as scalar in `published_competence` | Broadcast vector `P_i` to neighbors at each hop |

---

## 6. Minimum Paper-Safe Claims

Based on the above mapping, the following claims are **safe to make** in the current submission:

1. **phi(z) is computable deterministically** from the current `HandoffPacket` fields (hop_count, evidence_so_far length, uncertainty). No LLM call required for the prototype.

2. **U_self and U_out are explicitly instantiated** as weighted linear functions of competence, evidence quality, and peer beliefs (see §2.2 weight table). The weights are qualitative priors confirmed insensitive to ±2× variation (sensitivity analysis, Session 3).

3. **Persona update is a scalar simplification** of the EDO vector update, using terminal outcome signal only. The mapping to the full vector rule is explicit (§3.3).

4. **Termination is fully deterministic** with 4 hard rules (§4.1). Audit is currently implicit (terminal gold comparison).

5. **The prototype demonstrates the EDO routing loop** — local utility comparison → action selection → competence update → propagation to next sample — even if `split` and full recursive audit are absent.

---

## 7. What To Fix In `idea.md`

The following passages need tightening (not rewriting — just adding the concrete rule references from this note):

| section | current wording | recommended tightening |
|---|---|---|
| `phi(z)` definition (§9) | "来源可以是 rule features 或 lightweight LLM" | Add: "For the current prototype, phi(z) is computed deterministically from HandoffPacket fields per the rule table in edo_lite_executable_spec.md §1.2." |
| Utility formulas (§11) | Component functions listed but not defined | Add: "See edo_lite_executable_spec.md §2.2 for the prototype instantiation of each component." |
| Persona update (§13.3) | `LocalValue`, `TerminalValue`, `ReworkPenalty` undefined | Add the computation table from §3.2 of this note, or cross-reference it. |
| Termination (§11.3) | "安全规则" only described at high level | Add the 4-rule table from §4.1 of this note. |
| Current code mapping (§15.3) | Correctly maps EDO→TCPB at high level | Add "see edo_lite_executable_spec.md §5 for complete current/Stage-2 status table." |
