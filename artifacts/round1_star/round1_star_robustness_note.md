# Star Topology Robustness Note

**Run**: `artifacts/round1_star/run_20260413_055929`  
**Config**: `configs/round1_hotpotqa_star.yaml`  
**Sample set**: `artifacts/seed/hotpotqa_validation_200.jsonl` (n=200)  
**Model**: glm-4-flash, temperature=0.0  
**Date**: 2026-04-13

---

## Validation

All three method directories pass `validate_logs.py`:

```
[OK]  fixed_peer_calibrated  (200 samples, 100% coverage)
[OK]  fixed_static_roles     (200 samples, 100% coverage)
[OK]  fixed_self_claim       (200 samples, 100% coverage)
```

---

## Metrics Table

| method | F1 | EM | PAR | dead_end_rate | FAC | MHC | api_tokens/sample |
|---|---|---|---|---|---|---|---|
| fixed_peer_calibrated | **0.5808** | 0.46 | 0.0 | 0.0 | 0.0 | 1 | 3336 |
| fixed_static_roles    | 0.5783 | 0.46 | 0.0 | 0.0 | 0.0 | 1 | 3336 |
| fixed_self_claim      | 0.5783 | 0.46 | 0.0 | 0.0 | 0.0 | 1 | 3336 |

*(PAR = premature_accept_rate; FAC = forward_after_correction_rate; MHC = mean_handoff_count)*

---

## Key Finding: Star Topology Collapses Method Differentiation

All three methods produce **identical routing decisions** in the star topology:

| accepted_node | fixed_peer_calibrated | fixed_static_roles | fixed_self_claim |
|---|---|---|---|
| evidence_seeker | 104 | 104 | 104 |
| synthesizer | 79 | 79 | 79 |
| verifier | 17 | 17 | 17 |

- Every sample completes in exactly **2 hops** (hub dispatch → leaf accept) for all methods.
- `mean_handoff_count = 1` (one forward from hub to leaf).
- `premature_accept_rate = 0.0` for all, including `fixed_self_claim` (which had PAR=1.0 in chain). This is because in star the hub dispatches to a leaf agent designed to accept — the leaf's accept is structurally appropriate, not premature.

**Root cause**: In the star topology, the hub (decomposer) selects the `preferred_role` leaf based on a shared dispatch heuristic. This dispatch rule does not consume the TCPB competence signal at the hub level — competence calibration only affects the leaf's `accept vs. forward` decision, but in a forced single-hop star structure, the leaf has no neighbors to forward to (it can only return to hub or accept). Since all leaf agents have sufficient competence to accept (self_competence ≥ accept_threshold for the assigned preferred_role), they all accept on the first leaf visit.

---

## Comparison With Chain Topology (run_20260411_102202, n=200)

| topology | method | F1 | PAR | MHC |
|---|---|---|---|---|
| chain | fixed_peer_calibrated | 0.5955 | 0.00 | 1.0 |
| chain | fixed_static_roles    | 0.5802 | 0.00 | 1.677 |
| chain | fixed_self_claim      | 0.5619 | 1.00 | 0.0 |
| **star** | fixed_peer_calibrated | **0.5808** | **0.0** | **1** |
| **star** | fixed_static_roles    | 0.5783 | 0.0 | 1 |
| **star** | fixed_self_claim      | 0.5783 | 0.0 | 1 |

**Observations**:
1. In chain, `fixed_peer_calibrated` achieves F1=0.5955 vs static=0.5802 (+1.53pp). In star, the margin collapses to 0.0025 pp — not a signal.
2. Chain's hallmark `fixed_self_claim` PAR=1.0 disappears in star (PAR=0) because the star structure eliminates the multi-hop delegation path that creates premature-accept dynamics.
3. Token costs converge in star (all 3336 api_tokens/sample vs chain range 300–3360).

---

## Assessment

**No obviously broken code behavior** is observed. Logs are complete, metrics compute correctly, and validation passes for all three methods. The star topology itself functions as implemented.

However, **the star topology is not an appropriate robustness probe for TCPB**: because the hub-dispatch→leaf-accept path is architecturally forced (1 handoff, 2 hops, PAR always 0), the mechanism differences between `fixed_peer_calibrated`, `fixed_static_roles`, and `fixed_self_claim` cannot manifest. The dynamic that TCPB targets — iterative peer belief update guiding multi-hop delegation — requires a chain or mesh topology where agents both receive and forward tasks.

**Paper recommendation**: Report star results in an appendix robustness note as confirming that "when the topology is constrained to single-hop dispatch, all three methods converge to equivalent routing behavior, suggesting that peer calibration signals require multi-hop paths to express their advantage."

---

## API Token Usage

| method | api_prompt_tokens/sample | api_completion_tokens/sample | api_total_tokens/sample |
|---|---|---|---|
| fixed_peer_calibrated | 3306.16 | 29.86 | 3336.02 |
| fixed_static_roles    | 3306.18 | 29.87 | 3336.05 |
| fixed_self_claim      | 3306.17 | 29.87 | 3336.04 |

Token usage is near-identical across methods, consistent with all samples traversing the same 2-step path.
