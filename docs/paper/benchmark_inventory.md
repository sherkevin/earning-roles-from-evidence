# Benchmark Inventory — Datasets + Baselines + Topologies + Backbones

> **Single authoritative source** for "what benchmarks are we using". Compiled per user instruction (R34 commit, 2026-04-20).
> Owner: scientist (writing lead); engineer keeps `methods.py` + `external_baselines/*` actually runnable.
> Cross-references: [`external_baseline_plan.md`](external_baseline_plan.md) (module-swap design + external baseline survey), [`page_budget_audit.md`](page_budget_audit.md) (page count), [`PROJECT_STRUCTURE.md`](../../PROJECT_STRUCTURE.md) §0 (sprint state), [`docs/coordination/implementation_log.md`](../coordination/implementation_log.md) (engineer execution log).

---

## 0. Headline summary (read this first)

| Question | Answer (current state, 2026-04-20) |
|---|---|
| **What benchmark do we evaluate on?** | HotpotQA (multi-hop QA, English, Wikipedia-sourced) — the canonical benchmark for ALL Stage-1 results in Tables 1, 2, Figure 2, Appendix D. MuSiQue + 2WikiMultiHop are scope-locked for Stage-2 (`U-013` ✅, engineer pipeline). |
| **What model (backbone) do we evaluate?** | `gpt-4.1-mini` via OpenAI-compatible API (`newapi` channel = `xh.v1api.cc`, set as PRIMARY in R7). Historical Stage-1 runs used `glm-4-flash` (still cited in Table 2 ablation). No GPU / no on-prem model in main results. |
| **Which methods/baselines do we compare?** | (a) 8 author-internal methods registered in `workspace/idea04_core/methods.py::METHOD_NAMES` + 1 Stage-2 prototype (`edo_stage2_chain`); (b) 3 external 2024-SOTA multi-agent systems for module-swap comparison (AutoGen + ChatEval + MAD; engineer pipeline E-010..E-016). |
| **Which topology do we use?** | Chain (canonical for all Stage-1 + Stage-2 prototype results). Star is supported by code but NOT in any Table 1 result. Sparse-graph topologies (random / small-world / community-bridge) are Stage-2 agenda E4. |
| **What sample sizes have we run?** | (i) `chain-200` = 200 head samples for headline Tables 1+2 + Figure 2 + Appendix D; (ii) `3shard×200 = 600` paired (Appendix D preliminary); (iii) `fullval = 7405` HotpotQA validation (seed=42 done as of R-FULL-005; engineer E-017 R21 派 3-seed × 7405 paired Stage-2 vs Stage-1 in progress on server). |
| **Have we benchmarked external 2024-2026 SOTA?** | **NOT YET** in main paper body. R-FULL-001..006 reviewer fatal #3. Engineer pipeline E-010..E-016 in progress to deliver SWAP-1 (R3 → AutoGen) + SWAP-3 (R2 → ChatEval) + SWAP-4 (R2 → MAD). Both AutoGen and ChatEval and MAD already cloned on server. |

---

## 1. Datasets

### 1.1 In-paper datasets

| ID | Name | Reference | Hops | Size (in our use) | Status | License | Why |
|---|---|---|---|---|---|---|---|
| **DS-1** | **HotpotQA** distractor validation | Yang et al. 2018 (`yang2018hotpotqa`) | 2-hop | **chain-200** = 200 (head); **fullval** = 7405 | ✅ canonical (Tables 1, 2, Figure 2, Appendix D) | Apache-2.0 (research use) | Standard multi-hop QA benchmark; supports peer-calibration evaluation; validation set has gold answers + supporting facts. |
| **DS-2** | **MuSiQue** answerable validation | Trivedi et al. 2022 (`trivedi2022musique`) | 2/3/4-hop | TBD (engineer E-005 / E-006 prep; original validation = 2417 | ⏳ U-013 ✅ approved (2026-04-20); engineer pipeline | CC-BY-4.0 (research use) | Compositional multi-hop with 4-hop variant where R1 split + R2 audit have visible value; closes EXP-1 multi-dataset cap from §6 of reviewer prompt. |
| **DS-3** | **2WikiMultiHop** | Ho et al. 2020 (`ho20202wikimultihop`) | 2-hop (relational) | reserved for Stage-2 §4.4 E5 | ⏳ scope-locked Stage-2 | Apache-2.0 | Wikidata-relation multi-hop with structured supporting facts; complements HotpotQA's natural-text supporting facts. |

### 1.2 Held-out / cited but not used

(none currently)

### 1.3 Versioned seed slices (artifacts/)

| File | Lines | Bytes | Use |
|---|---|---|---|
| `artifacts/seed/hotpotqa_validation_full.jsonl` | 7405 | (large) | fullval reference (E-017 reads from this) |
| `artifacts/seed/hotpotqa_validation_200.jsonl` | 200 | small | canonical chain-200 (deterministic head-200 of validation) |
| `artifacts/seed/hotpotqa_validation_100.jsonl` | 100 | smaller | smoke / development slice |
| `artifacts/seed/hotpotqa_train_full.jsonl` | (training set) | large | NOT used for evaluation; reserved for any future training |

### 1.4 PII / license / source compliance

- HotpotQA: sourced from English Wikipedia article excerpts. **No PII** beyond what is publicly on Wikipedia. ✅ B5 statement in Appendix A of paper.
- MuSiQue: same — Wikipedia-sourced.
- 2WikiMultiHop: Wikidata-derived; no human annotation beyond automated alignment. No PII.

---

## 2. Backbone models

### 2.1 Canonical (in-paper main results)

| ID | Model | Provider channel | Use | Notes |
|---|---|---|---|---|
| **BB-1** | **`gpt-4.1-mini`** | `newapi` (`xh.v1api.cc`) — PRIMARY since R7 | Tables 1, Figure 2, Appendix D, E-017 fullval, all preliminary Stage-2 prototype | OpenAI-compatible API; size not disclosed by provider; `Random seeds: seed=42` for chain-200 (B2 §App-A, S-142 R26). Earlier runs used `oversea` (kuaipao.ai) — deprecated since model-drift event documented in Appendix B. |

### 2.2 Historical / Stage-1 ablation only

| ID | Model | Provider | Use | Notes |
|---|---|---|---|---|
| **BB-2** | **`glm-4-flash`** | Zhipu API | Table 2 mechanism ablations only | Fast/cheap; used for ablation sweep (R12). Not the canonical backbone. R-FULL-002+ ask for equivalent Table 2 on `gpt-4.1-mini` — see engineer E-014 (R13 派, queue). |

### 2.3 Available but NOT used in paper

| ID | Model | Provider | Status |
|---|---|---|---|
| `llama-3.3-70b-instruct` | NVIDIA NIM API | Available (configs/llm.json `nvidia` block); NOT used in main results. Reserved for future fallback per `U-EXEC-003` (low priority). |
| Any local-deployed model | server GPU | NOT in any submission per `experiment.md §1.3` (must not mix model societies; canonical = `gpt-4.1-mini`). Server GPU (4× RTX 3090 + 4× RTX 2080 Ti, per `ssh-server-rules.mdc`) is reserved for hypothetical Stage-3 / supplementary appendix work only. |

### 2.4 Provider switch history

- **R7 (2026-04-20)**: switched from `oversea` (kuaipao.ai, model-drift event 2026-04-19) → `newapi` (`xh.v1api.cc`); see Appendix B of paper for engineering description. All new fullval / multi-seed batches go through `newapi`.

---

## 3. Methods / Baselines (the actual runnable methods)

### 3.1 Internal methods registered in `workspace/idea04_core/methods.py::METHOD_NAMES`

(verified at R34 commit; canonical source is the file itself)

| ID | Method name | Type | What it does | In paper Table? |
|---|---|---|---|---|
| **M-1** | `single_agent` | Baseline | One agent does the whole task; no delegation. | NOT in Tables 1/2 (used as conceptual baseline only). |
| **M-2** | `central_orchestrator` | Baseline | Central node dispatches to specialists; standard MAS pattern. | NOT in Tables 1/2 (mentioned in §4.2 prose as "centralized baselines"). |
| **M-3** | `central_orchestrator_with_reflection` | Baseline | M-2 plus per-step reflexion; standard MAS+reflection pattern. | NOT in Tables 1/2. |
| **M-4** | `fixed_static_roles` | Author-internal | Fixed role-prior pipeline `decomposer → evidence_seeker → verifier → synthesizer`; deterministic accept-or-forward; **no calibration**. | ✅ Table 1 row 2 (`gpt-4.1-mini` chain-200) + Figure 2 GLM ordering. |
| **M-5** | `fixed_self_claim` | Author-internal | Same role-prior pipeline; each agent self-claims competence; routing weighted by self-claim. | ✅ Table 1 row 1 (`gpt-4.1-mini`) + headline Pareto-dominance result (Finding 4). |
| **M-6** | `fixed_random_forward` | Author-internal | Random forward routing; baseline lower-bound. | NOT in Tables 1/2 (run for negative-control purposes only). |
| **M-7** | `fixed_peer_calibrated` | Author-internal (TCPB) | Same role-prior pipeline; peer-calibration via terminal-outcome backpropagation = **TCPB Stage-1 instance**; this is the headline EDO Stage-1 prototype. | ✅ Table 1 row 3 (`gpt-4.1-mini`) + Table 2 canonical anchor (`glm-4-flash`) + Figure 2 + paired-anchor in Appendix D + E-017 paired anchor. |
| **M-8** | `fixed_self_calibrated` | Author-internal | Self-calibrated via own-outcome reflection; comparison to M-7 isolates "peer vs self" calibration signal. | NOT in Tables 1/2 (was in Round-1 but cut). |
| **M-9** | **`edo_stage2_chain`** | Stage-2 prototype | Activates the EDO Stage-2 execution loop (R1 split + R2 audit + R3 vector belief), running on chain topology only. **Degenerate** because in chain, SPLIT effectively becomes inline OUTSOURCE; AUDIT defaults to ACCEPT in this prototype run. | ✅ Appendix D paired vs M-7 (preliminary 3-shard × 200) + E-017 paired vs M-7 (3-seed × 7405 in progress). |

**Reviewer-flagged status (R-FULL-001..006)**:
- All Table 1 baselines (M-4 / M-5 / M-7) are author-internal routing variants → "S6 baseline_quality = 2-3/10" cap → forces D4 cap → forces overall ≤ 4.5 floor (the §6 hard cap chain).
- The fix is **module-swap** comparison against external 2024-SOTA systems (§4 below), NOT adding more author-internal methods.

### 3.2 Ablation method variants (Table 2, `glm-4-flash`)

These are NOT separate methods in `METHOD_NAMES` — they are M-4 / M-7 with feature flags toggled at config-time. Documented here for completeness:

| Variant label in Table 2 | M-7 with | Why it isolates |
|---|---|---|
| canonical anchor | (default) | Reference point. |
| refreshed baseline (v3 codepath) | (current production codepath at the time) | Confirms no codepath drift. |
| `+ evidence window enlarged` | `evidence_window_size = 8` (default 4) | Tests whether Finding 1's "answer-generation bottleneck" is the dominant source of error. |
| `- TCPB terminal update` | `terminal_calibration = false` | Isolates TCPB peer-calibration from the rest of the pipeline. |
| `- decomposer safety gate` | `force_forward_at_decomposer = false` | Isolates the safety prior responsible for `PAR=0` (Finding 3 honest attribution per S-140 R24). |

R-FULL-002+ asks for equivalent Table 2 on `gpt-4.1-mini` strong backbone — engineer **E-014** (R13 派, in queue). When delivered, scientist fills `_pending_data_templates.tex` TEMPLATE 2 → R##+ commit.

### 3.3 External baselines (per `external_baseline_plan.md` §3.2 — N=3 SWAP hosts)

| ID | System | Reference | Repo on server | Status (2026-04-20) |
|---|---|---|---|---|
| **EX-1** | **AutoGen** (`microsoft/autogen`) | Wu et al. 2024 (`wu2023autogen`) | `/media/data3/dengkw/idea04/external_baselines/chateval/` ✅ cloned (note: directory name was set during clone; engineer track) | E-010 step 1 (clone) ✅; step 2-3 (install + smoke) ⏳ engineer next session per `[parallel_orchestration_plan_20260420]` Section C |
| **EX-2** | **ChatEval** (`chanchimin/ChatEval`) | Chan et al. 2024 (`chan2024chateval`) | (in `external_baselines/chateval/`) ✅ cloned | E-010 step 1 ✅; step 2-3 ⏳ engineer |
| **EX-3** | **Multi-Agent Debate (MAD)** (`composable-models/llm_multiagent_debate`) | Liang et al. 2024 (`liang2023mad`) + Du et al. 2024 (`du2024improving`) | `/media/data3/dengkw/idea04/external_baselines/mad/` ✅ cloned | U-018 ✅ approved (2026-04-20); E-015 step 1 (clone) ✅; step 2-3 (install + smoke) ⏳; HotpotQA adapter (step 4) is engineer's longer 4-6h task |

External baselines NOT included (rejected paths):
- MetaGPT — too tightly coupled to software-engineering pipeline; multi-hop QA out of scope; SWAP-5 (R1 → MetaGPT) is `external_baseline_plan.md §4` future-work only.
- HuggingGPT — HF model selection not multi-hop QA target; passed over.
- Reflexion — redundant with AutoGen swap; deprioritized.

### 3.4 Module-swap comparison design

(verbatim from `external_baseline_plan.md §4`, summarised here for inventory)

| Swap ID | Host system | Original component | Replaced with | Engineer ticket | Scientist ticket |
|---|---|---|---|---|---|
| **SWAP-1** | AutoGen `GroupChatManager` | `select_speaker()` rule | Our R3 vector belief routing | E-011 (adapter) + E-012 (run) | S-121 + S-122 |
| **SWAP-3** | ChatEval `MetaReviewer.aggregate` | meta-reviewer score-aggregation | Our R2 audit decision protocol (4-class outcome + reroute) | E-011 (adapter) + E-012 (run) | S-121 + S-122 |
| **SWAP-4** | MAD `final_aggregator` | debate-then-aggregate | Our R2 audit (per-hop intervene + reroute, NOT terminal collapse) | E-016 (adapter + run) | S-131 |
| _SWAP-2_ | _AutoGen `GroupChatManager`_ | _`select_speaker()`_ | _Our 3-action policy with R1 split fallback_ | _deferred (low marginal value)_ | — |
| _SWAP-5_ | _MetaGPT pipeline_ | _Hard PM→Architect→Engineer order_ | _R1 split + 3-action policy_ | _future-work; out of scope_ | — |

Engineer pipeline E-010..E-012 + E-015 + E-016 deliver paired-bootstrap CI on **HotpotQA-200 + MuSiQue-200 × ≥3 seeds × `gpt-4.1-mini`** for SWAP-1 + SWAP-3 + SWAP-4 (3 hosts × {original, +Our R-x} × 2 benchmarks × ≥3 seeds = 36 batches). The 3-host comparison is the headline external-baseline result targeted for §4.4 of the paper (TEMPLATE 3 in `_pending_data_templates.tex`).

---

## 4. Topologies

| ID | Topology | Used in | Status |
|---|---|---|---|
| **T-1** | **Chain** (4-node `decomposer → evidence_seeker → verifier → synthesizer`) | Tables 1, 2, Figure 2, Appendix D, E-017 fullval, all SWAP comparisons (per `external_baseline_plan.md §4`) | ✅ canonical |
| **T-2** | **Star** (decomposer central + 3 spokes) | code path supports it (`workspace/idea04_core/methods.py`); NOT in any Table 1 result | implementation only |
| **T-3** | Random sparse / small-world / community-bridge | Stage-2 agenda E4 (per §4.4 of paper) | ⏳ Stage-2 future |

---

## 5. Sample sizes used

| ID | Slice | Size | Use |
|---|---|---|---|
| **SS-1** | HotpotQA chain-200 | 200 | Tables 1, 2, Figure 2 (head-200 deterministic, seed=42) |
| **SS-2** | HotpotQA 3-shard × 200 paired | 600 (3 × 200, disjoint shards [0:200] / [200:400] / [400:600]) | Appendix D preliminary Stage-2 vs Stage-1 paired |
| **SS-3** | HotpotQA fullval | **7405** | E-017 in progress (3-seed paired Stage-2 vs Stage-1, on server) |
| **SS-4** | HotpotQA-200 + MuSiQue-200 × ≥3 seeds | 200 × 2 benchmarks × 3 seeds = 1200 paired comparisons per SWAP × 3 SWAPs | E-012 + E-016 swap comparisons |

---

## 6. Metrics reported

### 6.1 Quantitative metrics (in-paper Tables)

| ID | Metric | Use | Computation |
|---|---|---|---|
| **MX-1** | **EM** (Exact Match) | Tables 1, 2 + Appendix D | HotpotQA standard span EM, Wikipedia-anchored. |
| **MX-2** | **F1** | Tables 1, 2, Figure 2, Appendix D | HotpotQA standard token-level F1 (re-implemented to match original word-tokenisation; B1 §App-A). |
| **MX-3** | **MHC** (Mean Handoff Count) | Table 1 | Routing efficiency — mean number of agent transitions per sample. |
| **MX-4** | **Tok.** (mean API tokens per sample) | Tables 1, 2 | Cost proxy. |
| **MX-5** | **PAR** (Premature Accept Rate) | mentioned in §4.3 Finding 3 (PAR$=0$ for all methods, attributed to safety gate per S-140 R24) | Fraction of samples accepted before reaching `verifier` or `synthesizer`. |
| **MX-6** | **cost-normalized F1** | Appendix D + scientist hand-off | F1 / Tok. (per-token utility) |

### 6.2 Statistical / variance metrics (E-017 incoming)

- **Paired bootstrap CI** (95%, B=10000 resamples): scripted in `scripts/paired_bootstrap_ci.py` (engineer R31). Currently used for Appendix D (single 200-sample paired); E-017 will deliver fullval × 3-seed bootstrap.
- **Paired sign-test p-value**: same script.
- **Cross-shard / cross-seed mean ± std**: cross-replication variance (Appendix D 3-shard reports σ=0.19% on token cost as benchmark of robustness).

### 6.3 Stage-2 organisational metrics (NOT in this submission)

Per §4.4 E1-E5 agenda, Stage-2 will report: persona-tag divergence, specialisation entropy, audit precision/recall, subcontract acceptance rate, split usefulness rate, average delegation depth, bridge utilisation rate, seed-level organisation stability. None claimed in current submission.

---

## 7. Status table — what's actually done as of R34 commit (2026-04-20)

| Cell | Status | Evidence |
|---|---|---|
| HotpotQA chain-200 × `fixed_peer_calibrated` (M-7) × `gpt-4.1-mini` × seed=42 | ✅ Table 1 row 3 (F1=0.7381) | `artifacts/round2_gpt41mini/run_20260414_115739/fixed_peer_calibrated/metrics.json` |
| HotpotQA chain-200 × `fixed_self_claim` (M-5) × `gpt-4.1-mini` × seed=42 | ✅ Table 1 row 1 (F1=0.7641) — headline Pareto-dominance | (same run dir family) |
| HotpotQA chain-200 × `fixed_static_roles` (M-4) × `gpt-4.1-mini` × seed=42 | ✅ Table 1 row 2 (F1=0.7454) | (same run dir family) |
| HotpotQA chain-200 × M-7 × `glm-4-flash` (Table 2 canonical) | ✅ Table 2 row 1 (F1=0.5955) | (round1 dir) |
| HotpotQA chain-200 × M-7 × `glm-4-flash` × 4 ablation variants (Table 2 rows 2-5) | ✅ Table 2 | (round1_ablation_*) |
| HotpotQA fullval × M-7 × `gpt-4.1-mini` (Figure 2 red star) | ✅ F1=0.7703 (n=7405) | `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/` |
| HotpotQA fullval × M-4 / M-5 (other 2 methods, R-FULL-001 reviewer asked for) | ❌ pending E-017 (R21 派工, in progress as of R34) | `artifacts/round2_gpt41mini_stage2_fullval/` (server) |
| HotpotQA chain-200 × `edo_stage2_chain` (M-9) | ✅ R12 + Appendix D | `artifacts/round2_gpt41mini_stage2_200/run_20260419_114943/edo_stage2_chain/` |
| HotpotQA 3-shard × 200 paired (M-9 vs M-7) | ✅ Appendix D Table 3 | `artifacts/round2_gpt41mini_3shard_paired/run_20260419_120612/` |
| HotpotQA fullval × M-9 vs M-7 paired × 3 seeds (E-017) | 🟡 in progress, server-side, ~6-8 h ETA | `artifacts/round2_gpt41mini_stage2_fullval/run_20260419_124129_seed42/` etc. — see [`parallel_orchestration_plan_20260420`](../coordination/implementation_log.md) |
| MuSiQue any | ❌ NOT yet (U-013 ✅ approved, engineer E-005/E-006 will execute) | — |
| 2WikiMultiHop any | ❌ Stage-2 future (§4.4 E5) | — |
| HotpotQA chain-200 × 4 ablation variants on `gpt-4.1-mini` (Table 2.b request) | ❌ pending E-014 (R13 派, in engineer queue) | — |
| AutoGen reproduce on HotpotQA (E-010) | 🟡 server clone ✅; install + smoke pending engineer | — |
| ChatEval reproduce on HotpotQA (E-010) | 🟡 server clone ✅; install + smoke pending engineer | — |
| MAD reproduce on multi-hop QA (E-015) | 🟡 server clone ✅; HotpotQA adapter is 4-6 h work | — |
| SWAP-1 + SWAP-3 + SWAP-4 paired comparisons (E-012 + E-016) | ❌ pending E-010+E-011+E-015 | — |

**Summary**: 6 cells done, 4 cells in flight (engineer pipeline running or engineer-next-session), 4 cells pending engineer follow-up actions queued. Reviewer fatal #3 (zero external 2024-SOTA in Table 1) is currently pending all of E-010..E-016 + E-014 + E-017 to deliver the data.

---

## 8. Open user decisions affecting benchmark

| ID | Decision | Status |
|---|---|---|
| `U-006-rerun-decide` | rerun fullval on M-4 + M-5 (figure-2 red-star + 2 missing fullval points) | ✅ approved; provider unblocked R7; E-017 R21 covers this |
| `U-013-decide` | add MuSiQue as 2nd benchmark | ✅ approved |
| `U-014-decide` | external baseline N (1/2/3) | ✅ N=2 (AutoGen + ChatEval) per R10 |
| `U-018-decide` | add MAD as 3rd external baseline (SWAP-4) | ✅ approved (a) |
| `U-020-stage2-fullval-launch-decide` | run E-017 3-seed × 7405 paired fullval | ✅ approved (b) per R21 |
| **`U-021-decide`** ⚠ | **demand.md §2 vs Appendix B/C/D/E placement (Path A/B/C/D)** | **⏳ pending user** (R32 dispatched) |

---

## 9. Cross-references

- **External-baseline design + module-swap matrix**: [`external_baseline_plan.md`](external_baseline_plan.md)
- **Page budget audit (8-page main body)**: [`page_budget_audit.md`](page_budget_audit.md)
- **Engineer execution log (E-005 / E-014 / E-017 / E-010..E-016)**: [`docs/coordination/implementation_log.md`](../coordination/implementation_log.md)
- **Sprint state + role mapping**: [`PROJECT_STRUCTURE.md`](../../PROJECT_STRUCTURE.md) §0
- **Scientist writing TODOs (S-115..S-146)**: [`docs/coordination/SCIENTIST_TODO.md`](../coordination/SCIENTIST_TODO.md) §B.5
- **User decision pool (U-XXX)**: [`docs/coordination/USER_TODO.md`](../coordination/USER_TODO.md) §A
- **Reviewer fatals + cumulative consolidation**: [`docs/coordination/SCIENTIST_TODO.md`](../coordination/SCIENTIST_TODO.md) §C

---

## 10. Maintenance

This file is the single authoritative source. **Any change to**:
- `workspace/idea04_core/methods.py::METHOD_NAMES` — update §3.1
- `external_baseline_plan.md` finalist roster — update §3.3 + §3.4
- `configs/llm.json` provider switch — update §2.4
- New benchmark dataset added — update §1
- New batch ✅ done — update §7 status table

**Owner**: scientist. Engineer ack via `implementation_log.md` triggers scientist to update this file.
