# External Baseline + Module-Swap Plan

> Created: 2026-04-20 (R9 commit) per user instruction "对比实验是要补的".
> Owner: scientist (planning) + engineer (execution per `[external_baseline_workstream_20260420]`).
> Blocks: this fix is required to close reviewer R-FULL-001 fatal #3 and S6 (baseline_quality) cap.
> Decisions needed: see USER_TODO §A `U-014-decide` (system count) + `U-015-decide` (swap scope).

---

## 1. Why this exists (gap audit)

### 1.1 What the paper has today (R8 commit, `article/build/edo_paper.pdf`)

| Table | What it shows | Type |
|---|---|---|
| **Table 1** (§4.3) | 3 methods on HotpotQA chain-200 with `gpt-4.1-mini`: `fixed_self_claim` / `fixed_static_roles` / `fixed_peer_calibrated` | All **author-internal** routing variants |
| **Table 2** (§4.x) | 5 ablation rows on HotpotQA chain-200 with `glm-4-flash`: canonical anchor / refreshed baseline / +evidence window / -TCPB / -decomposer gate | All **author-internal** ablations of OUR method |

`workspace/idea04_core/methods.py` registers 8 methods total: `single_agent`, `central_orchestrator`, `central_orchestrator_with_reflection`, `fixed_static_roles`, `fixed_self_claim`, `fixed_random_forward`, `fixed_peer_calibrated`, `fixed_self_calibrated`. **Every one of them is a different routing heuristic inside our own framework**; none reproduces an external published system's actual decision logic.

### 1.2 What §2 Related Work cites (but does NOT compare against)

Citation only ≠ baseline:

| Category | Cited in §2 | In `methods.py` as a real baseline? |
|---|---|---|
| Orchestrator MAS | AutoGen, MetaGPT, HuggingGPT, ChatDev, AgentVerse | ❌ No |
| Reflection | Reflexion, Tree-of-Thoughts, Self-Refine | ❌ No |
| Peer-critique / Debate | Multi-Agent Debate (Liang), ChatEval, Improving-Factuality (Du) | ❌ No |
| Calibration theory | Guo et al. 2017, Kadavath et al. 2022 | ❌ No (irrelevant — these are calibration metrics, not MAS systems) |
| Organisation theory | Galbraith 1973, Mintzberg 1979 | ❌ No (irrelevant — these are sociological background, not runnable systems) |

### 1.3 Reviewer R-FULL-001 fatal #3 (verbatim)

> "All baselines in Table 1 are author-internal routing variants (`fixed_peer_calibrated` / `fixed_static_roles` / `fixed_self_claim`). ZERO external 2024-2026 multi-agent SOTA (MARS, SAGE, AutoGen, MetaGPT, ReSo, AMRO-S) appears as a baseline. S6 = 3 (self-comparison only)."

This caps `D4 (empirical_results)` at 4.5 and `oral_quality_score` at ~2.5 by the reviewer's own published rubric (`prompts/reviewer_prompt.md` §2.5.1). Until external baselines land, the paper cannot exceed `weak_reject`.

### 1.4 Existing sprint coverage (E-007) and its gaps

The sprint plan `[stage2_sprint_kickoff_20260420]` `E-007` says:

> "外部 baseline：跑 1-2 个真实外部系统 (推荐 AutoGen 或 ChatEval) on HotpotQA + MuSiQue 200-sample slice. 4 d"

Gaps:

1. **No survey step** — "推荐 AutoGen 或 ChatEval" is a guess, not a vetted survey.
2. **No repo selection criteria** — open-source license / maintenance freshness / OpenAI-API compat / HotpotQA-friendly are all unverified.
3. **Full-system comparison only** — no module-swap design. This is a weaker experiment because EDO-vs-AutoGen could lose for confounded reasons (different prompts, different retrieval, different agent budgets) that have nothing to do with our R1/R2/R3 mechanisms.
4. **No reproduction validation** — without a smoke test against the original paper's reported numbers, any difference we report can be dismissed as "you didn't reproduce it correctly".
5. **No swap implementation** — no engineering for replacing the external system's manager / aggregator / scorer with our `R1` / `R2` / `R3` modules.

---

## 2. Why module-swap is the right experimental design (not full-system)

### 2.1 Confounds in full-system comparison

A naive "EDO end-to-end vs AutoGen end-to-end" comparison confounds at least 5 variables we don't control:

1. **Prompt template differences** — AutoGen's manager prompt vs our decomposer prompt
2. **Agent budget** — AutoGen typically uses 5-10 agents, our chain has 4
3. **Retrieval / tool stack** — AutoGen has function-calling, our prototype is pure text
4. **Termination policy** — AutoGen's `is_termination_msg` vs our `max_handoff`
5. **Backbone / temperature** — even with same `gpt-4.1-mini`, default temperature, retry, max-tokens differ

A reviewer can dismiss any EDO win as "you cherry-picked a configuration where their system happens to underperform". This is exactly the critique R-FULL-001 already raised in fatal #1 (Finding 4 self-falsifies because we lost to an internal baseline at same cost; an external loss would be even worse).

### 2.2 Module-swap as the controlled experiment

Treat each EDO mechanism (R1 / R2 / R3) as a **drop-in replacement** for an existing component in an external system. Hold everything else constant. This is the experimental design used by ReAct (Yao 2022), Toolformer (Schick 2023), Reflexion (Shinn 2023), and most well-cited MAS papers since 2023.

| Our mechanism | Conceptually replaces | Inside which external system |
|---|---|---|
| **R1 split** | Hard-coded role-pipeline decomposition | MetaGPT's `PM → Architect → Engineer` script; HuggingGPT's central LLM plan |
| **R2 audit** | Per-hop peer scoring + meta-reviewer aggregation | ChatEval's meta-reviewer; MAD's debate aggregator |
| **R3 vector belief** | Manager's `select_speaker(role_table)` | AutoGen's `GroupChatManager.select_speaker`; Reflexion's `selfreflection_score` |

### 2.3 Apples-to-apples isolation

For a swap experiment, we hold these constant: prompt templates of the host system / agent count / retrieval stack / termination policy / backbone / temperature / token budget / random seed. Only the swapped component changes. Any F1 / cost / MHC delta is then **attributable to the mechanism** rather than to system architecture.

---

## 3. External system candidate vetting

Selection criteria (must satisfy ALL three):

1. **Open-source repo** with permissive license (MIT / Apache-2.0 / BSD; not GPL or commercial-only)
2. **Active maintenance** (≥1 commit in last 12 months OR widely reproduced in literature)
3. **OpenAI-compatible client** OR easy adapter (since our infra runs on OpenAI-compatible API via `newapi`)

Bonus criteria (preferred):

4. Multi-hop QA-friendly (HotpotQA / MuSiQue / similar examples in repo)
5. Small enough to grok in <1 day (≤5k LOC of decision logic)
6. Has a published reproduction recipe (so we can verify our setup matches)

### 3.1 Candidate ranking

| Rank | System | Repo | License | Stars (proxy for maintenance) | Reproduction-friendliness | Best swap target |
|---|---|---|---|---|---|---|
| **1** | **AutoGen** | `microsoft/autogen` | CC-BY-4.0 + MIT (OSS components) | 30k+ | High (well-documented examples; HotpotQA tutorial exists) | **R3 vector belief** swap into `GroupChatManager.select_speaker` |
| **2** | **ChatEval** | `chanchimin/ChatEval` | MIT | 1.2k | Medium (well-scoped; meta-reviewer is a single function, easy to swap) | **R2 audit** swap into the meta-reviewer aggregation step |
| **3** | **MAD (Improving-Factuality)** | `composable-models/llm_multiagent_debate` (Du et al. 2024) | MIT | 800 | Medium-low (debate logic is short but multi-hop QA examples scarce) | **R2 audit** alternative — replace debate aggregator |
| 4 | **MetaGPT** | `geekan/MetaGPT` | MIT | 40k+ | Low (tightly-coupled software-engineering pipeline; multi-hop QA out of scope) | R1 split (hard-coded pipeline → our 3-action policy) — **only if scope allows R1 swap** |
| 5 | **HuggingGPT (JARVIS)** | `microsoft/JARVIS` | MIT | 23k+ | Low (HF model selection — multi-hop QA is not the design target) | R1 split alternative — pass over for now |
| 6 | **Reflexion** | `noahshinn/reflexion` | MIT | 2k+ | High (HotpotQA examples exist) | R3 belief swap into `selfreflection_score` — **redundant with AutoGen swap, deprioritised** |

> Engineer must verify these stars / license / freshness numbers via `git log -1` + LICENSE check during E-009; the table above is scientist's literature recall and **must be re-verified in survey ticket**.

### 3.2 Recommended target set (for 36-day deadline)

> **2026-04-20 (R17 update)**: U-018-decide → ✅ (a). Roster now expanded **N=2 → N=3** to absorb R-FULL-002 reviewer's MAD overlap-risk flag (D3 novelty cap closure). MetaGPT remains future-work (deferred); MAD ≠ MetaGPT (much smaller LOC, focused on debate aggregation, NOT software-engineering pipeline) so the +5 d delta is bounded and fits within sprint buffer.

**Confirmed: 3 systems, AutoGen + ChatEval + MAD**

Rationale:

- **AutoGen** = orchestrator-baseline anchor. R-FULL-001 reviewer-named explicitly in fatal #3. R3 vector-belief swap (SWAP-1) is the most defensible "drop-in" comparison.
- **ChatEval** = peer-critique-baseline anchor #1. R2 audit swap (SWAP-3) directly tests the mechanism that closes reviewer fatal #1 (Finding 4: "peer loses to self_claim because no per-hop intervention").
- **MAD (Multi-Agent Debate, Liang et al. 2024)** = peer-critique-baseline anchor #2. R2 audit swap (SWAP-4) closes R-FULL-002's `is_overlap_risk=TRUE` flag — reviewer explicitly wrote "TCPB's 'terminal-outcome only' is essentially a degenerate case of MAD's per-hop critique aggregator with aggregator window=full trajectory"; without an actual MAD comparison, our D3 (novelty) is capped ≤ 5.5. Adding SWAP-4 lets us numerically demonstrate the delta (per-hop audit ≠ debate aggregator) and lift the cap.
- Three systems = three independent angles of attack: covers (i) R-FULL-001 fatal #3 zero-external-baseline (AutoGen), (ii) R-FULL-001 fatal #1 Finding-4 self-falsification (ChatEval), (iii) R-FULL-002 D3 MAD overlap-risk (MAD).
- ChatEval + MAD = redundant on the surface (both peer-critique systems), but they implement very different aggregation logics: ChatEval = round-table discussion + meta-reviewer; MAD = explicit debate-then-aggregate. R2 swapping into BOTH lets us test whether per-hop audit beats the aggregator regardless of host's debate protocol.
- Within sprint budget: ~14-15 days incremental on top of E-001..E-006 (see §6 timeline); fits in original 5-6 d buffer.

**Previous MVP (1 system, AutoGen only)**: ~4-5 incremental days; closes fatal #3 partially but leaves both peer-critique angles untested. **Rejected** because it does not close R-FULL-002 D3 overlap-risk.

**Original recommendation (2 systems, AutoGen + ChatEval)**: ~9-10 incremental days; was the R10 commit choice, **superseded by R17 expansion** after R-FULL-002 reviewer batch landed.

**Aggressive-3 (3 systems, +MetaGPT/SWAP-5)**: ~21+ incremental days; **rejected** — MetaGPT is too tightly coupled to software-engineering pipeline; multi-hop QA out of scope. Stays in §4 as italic _SWAP-5_.

---

## 4. Module-swap design matrix (R17 update — N=3 hosts)

Each row = one swap experiment. All swaps share the **same backbone (`gpt-4.1-mini`), same benchmark (HotpotQA-200 + MuSiQue-200), same seed set (≥3 seeds), same token budget cap**.

| Swap ID | Host system | Original component | Replaced with | Hypothesis tested | Status |
|---|---|---|---|---|---|
| **SWAP-1** | AutoGen `GroupChatManager` | `select_speaker()` rule (round-robin / LLM-pick / custom callable) | Our R3 vector belief routing (`compute U^out for each agent, pick argmax`) | Vector belief routing > AutoGen's default `select_speaker` | ✅ active (U-015) |
| **SWAP-3** | ChatEval `llm_eval_multi_agent.py` final-judgment protocol | Multi-agent debate's terminal `final_prompt` aggregation (each agent emits judgment, final answer = majority/last-agent) | Our R2 audit decision protocol (4-class outcome + reroute) | Per-hop audit > terminal-judgment aggregation | ✅ active (U-015); ⚠ **R36 correction**: original ticket said `MetaReviewer.aggregate` — that class **does not exist** in ChatEval source. Actual aggregator is implicit in `agentverse/agents/llm_eval_multi_agent.py` `final_prompt` verbal protocol; the swap target is the **prompt-driven aggregation**, not a discrete function. See `[E-017_migration_landed_ack_20260420]` engineer-handoff inspection. |
| **SWAP-4** | MAD `final_aggregator` (Liang et al. 2024) | Debate-then-aggregate (per-hop debate critiques collapsed into final answer at terminal) | Our R2 audit (per-hop intervene + reroute, NOT terminal aggregation) | Per-hop audit ≠ debate aggregator; closes R-FULL-002 D3 `is_overlap_risk=TRUE` (TCPB ≠ degenerate MAD) | ✅ **active (U-018, R17)** |
| _SWAP-2_ | _AutoGen `GroupChatManager`_ | _`select_speaker()` rule_ | _Our 3-action policy with R1 split fallback_ | _3-action > pure outsource (when allowed)_ | ⏸ deferred (would re-litigate SWAP-1; low marginal value) |
| _SWAP-5_ | _MetaGPT pipeline_ | _Hard PM→Architect→Engineer order_ | _R1 split + 3-action policy_ | _Out of scope: MetaGPT tightly coupled to software-eng pipeline; multi-hop QA out of scope_ | ⏸ future-work |

**Reporting target**: a 4-row "External Baseline + Module-Swap" table in `§4.x` (matches scientist S-131 ticket):

```
| External system + swap target  | Host F1 | Host + Our R-x F1 | ΔF1 | Δtoken cost |
|---|---|---|---|---|
| AutoGen (GroupChatManager.select_speaker) — SWAP-1 R3 | X.XXX | X.XXX | +/− Y.YYY | +/− Z |
| ChatEval (MetaReviewer.aggregate)         — SWAP-3 R2 | X.XXX | X.XXX | +/− Y.YYY | +/− Z |
| MAD (final_aggregator, Liang 2024)        — SWAP-4 R2 | X.XXX | X.XXX | +/− Y.YYY | +/− Z |
```

Plus a single paragraph in §4.3 prose: "On all three hosts (AutoGen, ChatEval, MAD), swapping the host's [original mechanism] for our [R-x] yields F1 [+/−Y] and cost [+/−Z]. Specifically, the MAD swap (SWAP-4) directly tests R-FULL-002 reviewer's overlap-risk concern that TCPB is a degenerate case of MAD with aggregator-window = full trajectory: the empirical Δ on SWAP-4 quantifies the gap between per-hop audit (intervene + reroute) and debate-aggregator (terminal-outcome collapse) — these are **not** the same operator class even when both consume per-hop peer signals."

Plus a §2.2 Related Work paragraph (S-131 deliverable): explicitly write the TCPB-vs-MAD delta — "MAD aggregates per-hop critiques into a final answer at the trajectory terminal; TCPB inherits MAD's per-hop debate-critique consumption but routes the audit decision back into the trajectory (intervene + reroute, NOT collapse). The two systems share the per-hop critique consumption primitive but diverge on the audit-effect operator."

---

## 5. Workstream tickets (派给 engineer)

These would be added to `implementation_log.md` as `[external_baseline_workstream_20260420]` phase block, with engineer ticket IDs continuing from E-008. **R17 update**: U-018 → ✅ extends the host roster from N=2 to N=3 — adds **E-015** (reproduce MAD) + **E-016** (R2 audit swap into MAD `final_aggregator` = SWAP-4) on top of E-009..E-012.

| ID | Task | Days | Blocked on | Output |
|---|---|---:|---|---|
| **E-009** | **Survey + selection**: scientist ranks the 6 candidates in §3.1 against re-verified license / activity / repo size; engineer probes each repo (clone, install, run quickstart on 1 example). Output: short report selecting 2 (or N per `U-014`) finalists | 1 d | none | `artifacts/external_baselines/survey_report.md` (✅ done R13) |
| **E-010** | **Reproduce baseline**: for each finalist (AutoGen + ChatEval), reproduce the original published HotpotQA / MMLU number on a 50-sample slice; record reproduction error band; write a `repo_<name>_smoke.md` proving the host system works on our `newapi` endpoint | 2 d × 2 = 4 d | E-009 ✅; E-008 newapi probe ✅ | `artifacts/external_baselines/<name>/baseline_smoke_<TS>/` |
| **E-011** | **Implement swap adapter**: write `<name>_swap.py` adapter that hooks our R-x module into the host's decision point (e.g. `autogen_groupchatmanager_select_speaker_swap.py`, `chateval_finaljudgment_swap.py` ⚠ **R36 retarget** from phantom `MetaReviewer.aggregate` to the real `llm_eval_multi_agent.final_prompt` mechanism); unit test passes when adapter returns a valid choice for a known input | 2 d × 2 = 4 d | E-010 ✅ ; (R-x mechanism done: SWAP-1 needs E-004 R3 ✅, SWAP-3 needs E-003 R2 ✅) | `workspace/idea04_core/external_baselines/` + tests |
| **E-012** | **Run swap comparison**: 200-sample HotpotQA + 200-sample MuSiQue × {host original, host + our swap} × ≥3 seeds with paired-bootstrap CI; same backbone / token budget as our Stage-2 fullval | 2 d × 2 = 4 d | E-011 ✅; E-006 multi-seed harness ✅ | `artifacts/external_baselines/<name>/swap_results_<TS>/` + `paired_stats.csv` |
| **E-015** ⚡ **NEW R17** | **Reproduce MAD baseline** (Multi-Agent Debate, Liang et al. 2024, `composable-models/llm_multiagent_debate`): clone repo + license check + dependency install + reproduce original HotpotQA / multi-hop QA report on 50-sample slice; record error band; write `repo_mad_smoke.md` against `newapi` endpoint | 2 d | E-009 ✅; E-008 newapi probe ✅ | `artifacts/external_baselines/mad/baseline_smoke_<TS>/` + `repo_mad_smoke.md` |
| **E-016** ⚡ **NEW R17** | **Implement R2 audit swap into MAD `final_aggregator`** (= SWAP-4): write `mad_finalaggregator_r2audit_swap.py` adapter that replaces MAD's debate-result-aggregator with our R2 audit decision protocol (4-class outcome + reroute); unit test = adapter returns valid AuditDecision for a known per-hop input; THEN run 200-sample HotpotQA + 200-sample MuSiQue × {MAD original, MAD + R2 swap} × ≥3 seeds with paired-bootstrap CI; same backbone / token budget as Stage-2 fullval | 3 d | E-015 ✅; E-003 R2 audit ✅; E-006 multi-seed harness ✅ | `workspace/idea04_core/external_baselines/mad/mad_finalaggregator_r2audit_swap.py` + tests + `artifacts/external_baselines/mad/swap_results_<TS>/` + `paired_stats.csv` |

**Total incremental engineer time** (3 systems, R17 expansion):
- Original 2-system plan (E-009..E-012): 1 + 4 + 4 + 4 = 13 d → pipelined ~9-10 d
- R17 MAD addition (E-015 + E-016): 2 + 3 = **+5 d** (pipelined: MAD reproduce can run parallel with AutoGen/ChatEval reproduce on separate engineer-day slots; SWAP-4 must serialise after E-003 R2 audit ✅)
- **Net incremental**: ~14-15 d total, fits in original 36-day sprint with 4-5 d buffer remaining for polish + R-FULL-003 reviewer batch.

---

## 6. Time-line impact (vs original sprint plan)

> **R17 update (2026-04-20)**: U-018 → ✅ adds E-015 + E-016 (MAD reproduce + R2 swap into MAD aggregator) on top of original Option C. Net delta from original plan = **+10-11 days** (was +5-6 d for Option C; +5 d for MAD). Fits within original 5-6 d buffer because Day 1.5 already closed E-002/E-003/E-004/E-009 ahead of estimate (gain ~3-4 d) — but tightens R-FULL-003 reviewer-batch window from 3 d to 1-2 d.

The original sprint plan has buffer Days 25-28 for engineer + Days 28-35 for scientist polish + reviewer batch. Updated allocation:

- **Option C (R10 baseline)**: drop E-007 (subsumed); add E-009..E-012. Net delta = +5-6 d.
- **Option C+MAD (R17, currently active)**: Option C + E-015 + E-016. Net delta = +10-11 d. Compensated by Day 1.5 ahead-of-schedule closure of E-002/E-003/E-004/E-009.
- **Option B (serial)** and **Option D (drop AutoGen, keep MAD only)**: rejected.

**Updated recommended timeline (Option C+MAD, 3 systems, R17)**:

```
Day  1- 1.5: E-001 ✅ + E-008 ✅ + E-002 ✅ + E-003 ✅ + E-004 ✅ + E-009 ✅ (Day 1.5 closure ahead of schedule)
Day  2- 4 : E-013 ✅ (SSH inventory) + E-010 (reproduce AutoGen + ChatEval in parallel) + E-015 (reproduce MAD in parallel slot)
Day  5- 7 : E-005 (Stage-2 fullval HotpotQA + MuSiQue) + E-011 (write 2 swap adapters: AutoGen.select_speaker + ChatEval.MetaReviewer)
Day  8-10: E-006 (multi-seed CI harness, applied to BOTH our methods AND swaps) + E-012 (run SWAP-1 + SWAP-3 comparisons) + E-016 (R2 audit swap into MAD final_aggregator + run SWAP-4)
Day 11-12: E-014 (gpt-4.1-mini Table 2 ablation rerun, R-FULL-002 fix)
Day 13-16: scientist S-117 (§4 Stage-2 results) + S-121 (§4.x external comparison subsection) + S-122 (module-swap ablation table) + **S-131 (3-host §4.x table + RW §2.2 MAD delta)**
Day 17-20: scientist S-115 (§1 framing rewrite) + S-116 (§6 conclusion rewrite) + S-123 (RW §2 cross-ref actual baselines)
Day 21-23: R-FULL-003 user-triggered reviewer batch + S-104 loop
Day 24-30: final polish + last-mile lints + ARR submission prep
Day 31-35: buffer / 备稿 / ARR submission
```

This leaves 4-5 days buffer for unforeseen issues (down from 7 in original plan, still acceptable). Critical-path concern: E-016 SWAP-4 must serialise after E-003 R2 audit ✅ AND E-015 MAD reproduce ✅, so MAD swap can only start at Day 8 — if E-015 slips to Day 5+, E-016 starts at Day 8 still (parallelism absorbs it).

---

## 7. Decisions needed from user (R17 update — all decided)

| ID | Question | Recommended | Impact | Status |
|---|---|---|---|---|
| **U-014-decide** | How many external systems to target? 1 (MVP, AutoGen only) / **2 (recommended, AutoGen + ChatEval)** / 3 (aggressive, +MetaGPT) | **2** (initially) | Each additional system = +5 engineer-days | ✅ R10: 2 (AutoGen + ChatEval) |
| **U-015-decide** | Module-swap mechanism scope? **R3-only (SWAP-1)** / **R2+R3 (SWAP-1+3)** / R1+R2+R3 (full coverage incl SWAP-5) | **R2+R3 (SWAP-1+3)** to match U-012 R1+R2+R3 sprint scope while keeping engineer effort bounded | R1 swap requires MetaGPT (or HuggingGPT) reproduction = +5-7 engineer-days | ✅ R10: SWAP-1 + SWAP-3 |
| **U-016-decide** | Drop original E-007 in favour of E-010..E-012? | **Yes** (drop E-007; subsumed by the new tickets) | If kept, double-count of effort with no benefit | ✅ R10: dropped |
| **U-018-decide** | Add MAD as 3rd external baseline (SWAP-4 = R2 audit swap into MAD `final_aggregator`)? Triggered by R-FULL-002 reviewer flagging MAD `is_overlap_risk=TRUE`. (a) add / (b) skip + RW §2.2 expansion only | **(a)** add — closes D3 novelty cap; without it, paper capped at D3 ≤ 5.5 | +5 engineer-days (E-015 + E-016); fits into existing 5-6 d buffer plus Day 1.5 ahead-of-schedule margin | ✅ **R17: (a) add MAD** |

All four decisions are now ✅. Active engineer queue (R17): E-005, E-006, E-010, E-011, E-012, E-014, **E-015, E-016**. Active scientist queue (R17): S-115, S-116, S-117, S-121, S-122, S-123, **S-131**, S-009, S-010.

---

## 8. Acceptance criteria (definition of done for this workstream)

When all of the following are true, this workstream is ✅:

1. `artifacts/external_baselines/survey_report.md` exists with at least 2 finalists vetted (license + maintenance + OpenAI-compat verified).
2. `artifacts/external_baselines/<name>/baseline_smoke_<TS>/` exists for each finalist with reproduction error band ≤ 5% F1 vs original paper.
3. `workspace/idea04_core/external_baselines/<name>_swap.py` adapter exists with passing unit test.
4. `artifacts/external_baselines/<name>/swap_results_<TS>/` exists with paired-bootstrap CI on HotpotQA-200 + MuSiQue-200 × ≥3 seeds.
5. Paper §4.x has external comparison + module-swap table (≥ 2 host systems × {original, +our swap}).
6. Paper §2 Related Work updated to **point at the actual baselines** (not just `\citep{}`), via inline reference in §4.x.
7. Reviewer R-FULL-002 batch confirms `S6 (baseline_quality) ≥ 6` and `D4 ≥ 5.5` (closes the cap that triggered fatal #3).

---

## 9. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Reproduction error > 5% (we can't recover the original paper's F1 on HotpotQA) | medium | Document the error band honestly; report only swap-delta (within-system) not absolute comparison |
| Our swap LOSES to host's original mechanism on the host system | medium | This is a real research outcome; if happens, §6 conclusion honestly states "module is competitive in some hosts but not all" + Limitations explains the boundary |
| Engineer can't get host repo running with `newapi` endpoint | low | All 6 candidates use OpenAI-compatible client; `LLM_BACKEND=oversea` env override (per `configs/llm.json` newapi `note`) should work; fallback = use OpenAI's official endpoint with separate budget |
| Time blowout (E-010 takes 5 d not 2 d per system) | medium | Have a hard cutoff at Day 18; if not done, drop second system and report 1-system results with explicit limitation |
| MetaGPT (R1 swap) is too tightly coupled to swap | high if attempted | Stay at 2 systems (SWAP-1 + SWAP-3); leave R1 swap for Stage-3 / future work |

---

## 10. References

- This plan: `docs/paper/external_baseline_plan.md` (this file) — **module-swap (Axis B) design**
- **Single benchmark inventory (datasets + baselines + topologies + backbones + status table)**: [`docs/paper/benchmark_inventory.md`](benchmark_inventory.md) — see §3.3 + §3.4 there for the canonical N=3 SWAP host list (kept in sync with this file)
- **NEW (R35) — Full-system SOTA survey (Axis A)**: [`docs/paper/sota_baseline_survey_2026.md`](sota_baseline_survey_2026.md) — per user instruction "我们是要把算法跑到 SOTA". Identifies MA-RAG (arXiv:2505.20096) + ReAgent (arXiv:2503.06951) as Tier-1 finalists for direct full-system F1 comparison on HotpotQA. **Axis A (full-system head-to-head F1) and Axis B (module-swap mechanism isolation) are complementary**; the paper's §4.x will contain both — Axis A answers "do we beat SOTA?", Axis B answers "is OUR mechanism causing the win?".
- Sprint kickoff: `docs/coordination/implementation_log.md` `[stage2_sprint_kickoff_20260420]`
- Provider switch: `docs/coordination/implementation_log.md` `[provider_switch_20260420]`
- Engineer cautions: `docs/coordination/implementation_log.md` `[pinned_cautions_for_engineer_20260420]`
- External baseline workstream kickoff: `docs/coordination/implementation_log.md` `[external_baseline_workstream_20260420]`
- External baseline survey results: `artifacts/external_baselines/survey_report.md` (E-009 ✅ R13 commit)
- R17 MAD landing: `docs/coordination/implementation_log.md` `[u_018_mad_landed_20260420]`
- Reviewer fatals that this closes:
  - R-FULL-001 fatal #3 (S6=3, D4=4): `artifacts/idea_reviews/reviewer_20260419_163139_01_9e72f7/review.md`
  - R-FULL-002 D3 `is_overlap_risk=TRUE` (MAD): `artifacts/idea_reviews/reviewer_20260419_185701_*/review.md`
- Decisions: `docs/coordination/USER_TODO.md §A,§C` U-014 ✅ / U-015 ✅ / U-016 ✅ / U-018 ✅
- MAD reference paper: Liang et al. 2024, "Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate" (or Du et al. 2024, "Improving Factuality and Reasoning in Language Models through Multiagent Debate") — engineer to verify in E-015 which repo we actually clone (`composable-models/llm_multiagent_debate` is the canonical implementation cited by reviewer).
