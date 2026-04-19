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

**Recommended: 2 systems, AutoGen + ChatEval**

Rationale:

- **AutoGen** = orchestrator-baseline anchor. Reviewer-named explicitly in fatal #3. R3 vector-belief swap is the most defensible "drop-in" comparison.
- **ChatEval** = peer-critique-baseline anchor. R2 audit swap directly tests the mechanism that closes reviewer fatal #1 (Finding 4: "peer loses to self_claim because no per-hop intervention").
- Two systems = two angles of attack; covers reviewer fatal #3 (zero external baselines) AND reviewer fatal #1 (Finding 4 self-falsifies).
- Within sprint budget: ~9-10 days incremental on top of E-001..E-007 already planned (see §4 below).

**MVP (1 system, AutoGen only)**: ~4-5 incremental days; closes fatal #3 partially but R2 audit value remains untested vs an external peer-critique system → reviewer can still cap S6 at ~5/10.

**Aggressive (3 systems, +MetaGPT)**: ~14 incremental days; risks burning the buffer needed for reviewer R-FULL-002 + final polish.

---

## 4. Module-swap design matrix (proposed)

Each row = one swap experiment. All swaps share the **same backbone (`gpt-4.1-mini`), same benchmark (HotpotQA-200 + MuSiQue-200), same seed set (≥3 seeds), same token budget cap**.

| Swap ID | Host system | Original component | Replaced with | Hypothesis tested |
|---|---|---|---|---|
| **SWAP-1** | AutoGen `GroupChatManager` | `select_speaker()` rule (round-robin / LLM-pick / custom callable) | Our R3 vector belief routing (`compute U^out for each agent, pick argmax`) | Vector belief routing > AutoGen's default `select_speaker` |
| **SWAP-2** | AutoGen `GroupChatManager` | `select_speaker()` rule | Our 3-action policy with R1 split fallback | 3-action > pure outsource (when allowed) |
| **SWAP-3** | ChatEval `MetaReviewer.aggregate` | Meta-reviewer's score-aggregation logic | Our R2 audit decision protocol (4-class outcome + reroute) | Per-hop audit > meta-reviewer aggregation |
| **SWAP-4** | MAD `final_aggregator` | Debate-result aggregator | Our R2 audit | Per-hop audit > debate aggregator (cross-check SWAP-3) |
| _SWAP-5_ | _MetaGPT pipeline_ | _Hard PM→Architect→Engineer order_ | _R1 split + 3-action policy_ | _Out of scope unless aggressive option chosen_ |

**Reporting target**: a 4-row "External Baseline + Module-Swap" table in `§4.x`:

```
| External system | Original mechanism F1 | + Our swap F1 | Δ | Token cost Δ |
|---|---|---|---|---|
| AutoGen (GroupChatManager) | X.XXX | X.XXX | +/− Y.YYY | +/− Z |
| ChatEval (MetaReviewer)    | X.XXX | X.XXX | +/− Y.YYY | +/− Z |
| (MAD if scope allows)      | X.XXX | X.XXX | +/− Y.YYY | +/− Z |
```

Plus a single sentence in §4.3 prose: "On both AutoGen and ChatEval, swapping the host's [original mechanism] for our [Rx] yields F1 [+/−Y] and cost [+/−Z], confirming the mechanism contribution is robust across host systems."

---

## 5. Workstream tickets (派给 engineer)

These would be added to `implementation_log.md` as `[external_baseline_workstream_20260420]` phase block, with engineer ticket IDs continuing from E-008. Estimates assume 2-system recommendation (SWAP-1 + SWAP-3).

| ID | Task | Days | Blocked on | Output |
|---|---|---:|---|---|
| **E-009** | **Survey + selection**: scientist ranks the 6 candidates in §3.1 against re-verified license / activity / repo size; engineer probes each repo (clone, install, run quickstart on 1 example). Output: short report selecting 2 (or N per `U-014`) finalists | 1 d | none | `artifacts/external_baselines/survey_report.md` |
| **E-010** | **Reproduce baseline**: for each finalist (e.g. AutoGen + ChatEval), reproduce the original published HotpotQA / MMLU number on a 50-sample slice; record reproduction error band; write a `repo_<name>_smoke.md` proving the host system works on our `newapi` endpoint | 2 d × N | E-009 ✅; E-008 newapi probe ✅ | `artifacts/external_baselines/<name>/baseline_smoke_<TS>/` |
| **E-011** | **Implement swap adapter**: write `<name>_swap.py` adapter that hooks our R-x module into the host's decision point (e.g. `autogen_groupchatmanager_select_speaker_swap.py`); unit test passes when adapter returns a valid choice for a known input | 2 d × N | E-010 ✅ ; (R-x mechanism done: SWAP-1 needs E-004 R3, SWAP-3 needs E-003 R2) | `workspace/idea04_core/external_baselines/` + tests |
| **E-012** | **Run swap comparison**: 200-sample HotpotQA + 200-sample MuSiQue × {host original, host + our swap} × ≥3 seeds with paired-bootstrap CI; same backbone / token budget as our Stage-2 fullval | 2 d × N | E-011 ✅; E-006 multi-seed harness ✅ | `artifacts/external_baselines/<name>/swap_results_<TS>/` + `paired_stats.csv` |

**Total incremental engineer time** (2 systems, MVP): 1 + (2+2+2)×2 = **13 d**, condensed to ~9-10 d if E-010/E-011/E-012 are pipelined per system. Fits in the 36-day sprint by reusing the slack between E-006 (multi-seed) and Day 28 (paper polish window).

---

## 6. Time-line impact (vs original sprint plan)

The original sprint plan has buffer Days 25-28 for engineer + Days 28-35 for scientist polish + reviewer batch. Inserting E-009..E-012 (≈9-10 d if pipelined) requires either:

- **Option A: parallel track** — engineer works on E-009..E-012 in parallel with E-006/E-007 (E-007 becomes redundant — replaced by E-010..E-012). Net delta = +5-6 days. Final sprint completion shifts from Day 28 to Day 33-34. Reviewer R-FULL-002 window shrinks from 7 days to 1-2 days. **Risky but doable.**
- **Option B: serial track** — finish all E-001..E-007 first, then E-009..E-012. Net delta = +9-10 days. Sprint slips past Day 35 deadline. **Not viable for ARR May 25.**
- **Option C: drop E-007 entirely** — the original "1-2 systems full-system comparison" is logically subsumed by E-010..E-012 (which does both reproduction AND swap). Net delta vs original plan = +5-6 days. **Recommended.**

**Recommended timeline** (Option C, 2 systems):

```
Day  1- 5: E-001 + E-008 + E-002 (current sprint)
Day  6-10: E-003 (R2 audit) + E-009 (external survey + selection in parallel)
Day 11-13: E-004 (R3 vector) + E-010 (reproduce 2 hosts in parallel)
Day 14-16: E-005 (Stage-2 fullval) + E-011 (write 2 swap adapters in parallel)
Day 17-19: E-006 (multi-seed CI, applied to BOTH our methods AND swaps) + E-012 (run swap comparisons)
Day 20-22: scientist S-117 paper §4 with both Stage-2 results AND module-swap results
Day 23-26: scientist S-115 / S-116 framing rewrite + S-121 §4.x external comparison subsection
Day 27-29: R-FULL-002 user-triggered reviewer batch + S-104 loop
Day 30-35: final polish + ARR submission
```

This leaves 5-6 days buffer for unforeseen issues, vs original plan's 7 days. Acceptable risk.

---

## 7. Decisions needed from user

| ID | Question | Recommended | Impact |
|---|---|---|---|
| **U-014-decide** | How many external systems to target? 1 (MVP, AutoGen only) / **2 (recommended, AutoGen + ChatEval)** / 3 (aggressive, +MetaGPT) | **2** | Each additional system = +5 engineer-days |
| **U-015-decide** | Module-swap mechanism scope? **R3-only (SWAP-1)** / **R2+R3 (SWAP-1+3)** / R1+R2+R3 (full coverage incl SWAP-5) | **R2+R3 (SWAP-1+3)** to match U-012 R1+R2+R3 sprint scope while keeping engineer effort bounded | R1 swap requires MetaGPT (or HuggingGPT) reproduction = +5-7 engineer-days |
| **U-016-decide** | Drop original E-007 in favour of E-010..E-012? | **Yes** (drop E-007; subsumed by the new tickets) | If kept, double-count of effort with no benefit |

If user chooses recommended (2 systems, R2+R3, drop E-007), engineer adds +5-6 days net to the sprint, which fits inside the existing buffer.

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

- This plan: `docs/paper/external_baseline_plan.md` (this file)
- Sprint kickoff: `docs/coordination/implementation_log.md` `[stage2_sprint_kickoff_20260420]`
- Provider switch: `docs/coordination/implementation_log.md` `[provider_switch_20260420]`
- Engineer cautions: `docs/coordination/implementation_log.md` `[pinned_cautions_for_engineer_20260420]`
- Reviewer fatal that this closes: `artifacts/idea_reviews/reviewer_20260419_163139_01_9e72f7/review.md` (fatal #3, S6=3, D4=4)
- Decisions to wait for: `docs/coordination/USER_TODO.md §A` U-014 / U-015 / U-016
