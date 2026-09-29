# Round 0 — devil's-advocate review

- **Run:** `run_e313af962946`
- **Source:** independent read-only review from `/root/round0_devils_advocate`
- **Status:** one Round 0 report received; not a synthesis or decision
- **Date:** 2026-09-29

## POSITION

`ArtifactRole/PeerRoleBench-TB` may still carry the primary claim, but current
evidence cannot call it a qualified benchmark/baseline or start a formal effect,
API, or A800 stream. The causal chain

```text
situated recipient judgment → attributable producer evidence
→ pre-execution assignment → unseen quality/full cost
```

has not yet been identified. Existing smoke runs demonstrate protocol safety in a
limited case, not role-learning efficacy.

## Objections and decision tests

### 1. Responsibility labels are not yet identifiable

**Evidence:** The active Goal requires producer contract checks, recipient action,
later outcome, and `UNKNOWN` to remain separate. The v6 real smoke report
(`docs/coordination/task_reports/20260929_pipe3_real_smoke_v6.md`) records
`PENDING_ATTRIBUTION`, `producer_feedback_eligible=false`, and
`policy_update_allowed=false`; the judged target was recipient-owned integration.

**Test:** Pre-register a 2×2 factorial (producer-contract defect × recipient-owned
integration defect), hold delivery and recipient capability fixed, and score producer
correctness, recipient correctness, adoption, and attribution independently. Report
false-producer penalties and `UNKNOWN`; only responsibility-complete producer-defect
cells may update.

### 2. Benchmark authority and independent roots are open

**Evidence:** `benchmark_baseline_v1.2_20260929_eval.md` marks PeerRoleBench-TB as a
TeamBench-derived candidate, not a frozen public benchmark. DIST1 has a history/leakage
issue; PIPE3 lacks qualified scientific text, later assignment, independent live
streams, and clean reconstruction.

**Test:** Freeze primary/secondary, qualify at least two structurally independent roots
(preferably three), and publish dependency/root taxonomy, contamination audit, clean
reconstruction, and an unseen-root split. Payoff results from PeerSelect/IPD cannot
substitute for situated judgment evidence.

### 3. Baseline parity is not executable yet

**Evidence:** Six comparator adapters have zero-call qualification, but raw acceptance
has no independent public projection, RARE has no selection adapter, the closest
published adapter is missing, and there is no unified PIPE3 runner/parity.

**Test:** On one frozen root, run uniform/no-update/raw/terminal/contextual/pooled/
closest/RARE with identical menu, visible events, `UNKNOWN`, arrival/watermark,
propensity, model/API/token/scorer/retry/state/wall-clock budgets. Verify policy-read
traces; a non-constructible arm blocks effect experiments.

### 4. Persistent role learning is not identified

**Evidence:** Earlier review found same model/configuration, fresh calls, and no
individual memory/skills. N02 feedback left probabilities at `[.5,.5]`; v6 has no
later assignment.

**Test:** Start persistent agents identically with auditable IDs and experience
snapshots; accumulate valid producer-defect feedback across two orthogonal tasks; seal
the next assignment before execution; compare no-update, same-information contextual
trust, and RARE on an unseen root. Exchangeable agents cannot support the role claim.

### 5. Online update, stability, and timeliness are unmeasured

**Evidence:** Updater equations, capacity/eviction, late correction, idempotency,
drift windows, and update/selection latency are not fixed; N02 had no effective signal.

**Test:** After signal qualification, use eligible positive/negative/`UNKNOWN` feedback,
delay/reordering, peer/task drift, and an old holdout. Pre-register update/selection
p50/p95, state cap, response window, peak/average forgetting, and recovery. Only a
passing updater may justify A800.

### 6. Scorer coverage and temporal validity are incomplete

**Evidence:** The priority audit found producer import/constructor failure missed by
the consumer 4/4 score; v6 explicitly says `scientific_claim_allowed=false`. v6 has
no later assignment, and N02 feedback did not change selection.

**Test:** Build a mutation matrix for producer syntax/import/constructor/semantic
contract, recipient-only error, mixed edit, digest/timeout/resource and `UNKNOWN`.
Seal assignment before execution and vary only eligible evidence arrival/order in paired
episodes; report FAIL, `UNKNOWN`, and unstarted denominators.

### 7. Complete cost and contribution novelty remain unproven

**Evidence:** v6 has API calls and wall-clock, but no policy comparison or complete
judgment/scorer/communication/repair cost. RARE components map to responsibility
filtering, trust/reputation, contextual selection, and delayed updates.

**Test:** Log all producer/recipient/judge/scorer/retry/tool/communication/token/
wall-clock/human/repair costs under matched budgets. Build a prior-art overlap matrix,
matched-composition control, leave-one-module ablations, and interaction tests. A
strong same-information trust/bandit matching RARE would defeat an unqualified
mechanism novelty claim.

## Ranked blockers

1. Freeze primary track and authority/root split.
2. Qualify producer-defect versus recipient-defect labels and scorer coverage.
3. Complete executable baseline parity, including raw projection, RARE, and closest published adapter.
4. Give peers persistent auditable state and enforce pre-execution assignment.
5. Qualify one updater with latency, drift, and forgetting evidence.
6. Add complete cost and independent confirmation streams.

This is an objection ledger. It does not change the active benchmark plan or Goal and
does not authorize API/A800 execution.
