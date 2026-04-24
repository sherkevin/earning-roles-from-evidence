# SOTA Baseline Survey 2024–2026 — Full-System HotpotQA / Multi-hop QA Comparison

> **Created**: 2026-04-20 (R35 commit, scientist S-148 per user instruction "我们是要把算法跑到 SOTA，而不是跟自己对比，是要跟同赛道的其他解决相同问题的公开模型对比")
> **Owner**: scientist (this survey doc) + engineer (reproduce work) + user (final 选 N 个)
> **Companion docs**: [`benchmark_inventory.md`](benchmark_inventory.md) §3.3 (authoritative roster), [`external_baseline_plan.md`](external_baseline_plan.md) (existing module-swap design — this survey is a **second parallel comparison axis**, not a replacement), [`final_experiment_matrix.md`](final_experiment_matrix.md) (execution-target matrix that combines baseline roster × recognised datasizes)

---

## 0. Why this survey exists (gap audit)

### 0.1 What user pointed out (R35 trigger)

> "我们是要把算法跑到 SOTA，而不是跟自己对比，是要跟同赛道的其他解决相同问题的公开模型对比，你需要进行一轮调研工作，找找最近的适合对比的 baseline 方法"

### 0.2 What we already had (and why it's NOT enough alone)

`external_baseline_plan.md` chose **module-swap** comparison (R3→AutoGen `select_speaker`, R2→ChatEval `MetaReviewer`, R2→MAD `final_aggregator`). The rationale was "module-swap controls 5 confounds and isolates mechanism contribution."

**That rationale is methodologically defensible BUT it does NOT answer the reviewer's S6 baseline-quality question** which is "is your method actually better than the SOTA on the F1 leaderboard?". Reviewers across R-FULL-001..006 have repeatedly raised:

- "S6 = baseline_quality 2-3/10 — author-internal routing variants only"
- "EXP-6 baseline recency fail — zero external 2024-2026 SOTA in Table 1"
- "AutoGen / MetaGPT / Multi-Agent Debate / ChatEval cited but not benchmarked"

What was missing from `external_baseline_plan.md`: **direct end-to-end full-system comparison to recent published HotpotQA / MuSiQue SOTA results**, where row = independent system, column = same benchmark/backbone/sample slice F1, and our row competes head-to-head on F1 (not just mechanism delta within a swap).

### 0.3 What this survey produces

A **ranked roster of recent (2024-2026) multi-agent multi-hop-QA systems** with reported F1 numbers on HotpotQA / MuSiQue / 2WikiMultiHop, vetted on:
- (a) public open-source repo
- (b) reasonably reproducible (`gpt-4.1-mini` or LLaMA3-8B-class backbone, not 70B-only)
- (c) released 2024-01 or later
- (d) target = multi-hop QA (not generic agentic frameworks)

Final recommendation: **N=2 full-system SOTA + retain N=3 module-swap (existing plan)** for combined Table 4-row design.

---

## 1. Candidate inventory (gathered via web search 2026-04-20)

| Rank | Name | Year | Venue | Repo | Core idea | Multi-hop QA target | Backbone | Reported HotpotQA result |
|---:|---|---:|---|---|---|---|---|---|
| **1** | **MA-RAG** | 2025-05 | arXiv 2505.20096 | [`thangylvp/MA-RAG`](https://github.com/thangylvp/MA-RAG) (15 ⭐) | 4-agent RAG: Planner / Step Definer / Extractor / QA, collaborative chain-of-thought | ✅ HotpotQA + 2WikimQA + MuSiQue + NQ + TriviaQA core target | LLaMA3-8B / LLaMA3-70B / GPT-4o-mini | ✅ **claimed SOTA** on HotpotQA + multi-hop datasets across all 3 backbones |
| **2** | **ReAgent** | 2025-EMNLP | arXiv 2503.06951 | [`astridesa/ReAgent`](https://github.com/astridesa/ReAgent) (4 ⭐) | Reversible multi-agent with rollback when conflicts; Execution / Supervisory / Interaction layers | ✅ HotpotQA + 2 others core target | unspecified (likely GPT-3.5/4 family) | **+6% over forward-only baselines** on HotpotQA |
| **3** | **MAD (Du et al.)** | 2024-ICML | proceedings.mlr.press v235 | [`composable-models/llm_multiagent_debate`](https://github.com/composable-models/llm_multiagent_debate) ✅ already cloned on our server | Multi-agent debate; multiple LLMs propose-and-debate over rounds | partial (focused on math/strategic reasoning; HotpotQA NOT primary) | GPT-3.5 / GPT-4 / Bard | ❌ NOT direct on HotpotQA per published paper; Reasoning Court (below) did follow-up on HotpotQA |
| **4** | **AgentRouter** | 2025-10 | arXiv 2510.05445 | "anonymous repository" — code link unclear | KG-guided routing; heterogeneous GNN over query+entities+agents | ✅ HotpotQA + NewsQA | various | claims to "outperform single-agent and ensemble baselines" |
| **5** | **BELLE** | 2025-ACL | arXiv 2505.11811 | likely on lianjiatech (search ambiguous, link points to different BELLE LLM) | Bi-level: agents debate to plan + fast/slow debaters monitor | ✅ multi-hop QA core target | various | "outperforms strong baselines across multiple datasets" |
| **6** | **Reasoning Court** | 2025-04 | arXiv 2504.09781 | ❌ no public code in search results | Multi-agent ReAct + judge LLM verifies + synthesises; combines reasoning + retrieval + judgment | ✅ HotpotQA + MuSiQue + FEVER core target | various | "outperforms SOTA few-shot prompting" |
| **7** | **PRISM** | 2025-10 | arXiv 2510.14278 | ❌ no public code yet (only HF papers page) | 3-agent: Question Analyzer / Selector (precision) / Adder (recall) | ✅ HotpotQA + 2WikiMultiHopQA + MuSiQue + MultiHopRAG core target | various | "consistently outperforms strong baselines" |
| **8** | **MAR (Multi-Agent Reflexion)** | 2025-12? | arXiv 2512.20845 | ❓ check | Multiple reasoning personas + judge; multi-agent self-reflection | ✅ HotpotQA core target | various | EM 44 → 47 on HotpotQA |
| **9** | **AutoGen** | 2024-ICLR | arXiv 2308.08155 | [`microsoft/autogen`](https://github.com/microsoft/autogen) ✅ already cloned | Generic conversation framework with manager + specialists | ❌ generic agentic framework, not core multi-hop QA target | various | NO direct HotpotQA F1 in search results |
| **10** | **AgentVerse** | 2024-ICLR | arXiv 2308.10848 | [`OpenBMB/AgentVerse`](https://github.com/OpenBMB/AgentVerse) | Multi-agent collaboration + emergent behaviours | ❌ generic; demonstrates on text understanding / reasoning / coding | various | NO direct HotpotQA F1 in search results |
| **11** | **ChatEval** | 2024-ACL | arXiv 2308.07201 | [`chanchimin/ChatEval`](https://github.com/chanchimin/ChatEval) ✅ already cloned | Multi-agent debate for evaluation tasks | ❌ NLG evaluation, not multi-hop QA | GPT-4 | NOT direct on HotpotQA |

---

## 2. Filter criteria (must satisfy ALL three for "viable SOTA candidate")

1. **Public open-source repo** (anonymous repo / "code coming soon" disqualified — we can't reproduce in 1-2 weeks without code)
2. **Multi-hop QA core target** (HotpotQA / MuSiQue / 2WikiMultiHop reported as primary benchmark with F1 / EM numbers)
3. **Released 2024-01 or later** (recent enough that R-FULL "EXP-6 baseline recency" check passes)

| # | Candidate | (1) Open repo? | (2) Multi-hop QA core? | (3) ≥2024? | Eligible? |
|---:|---|---|---|---|---|
| 1 | **MA-RAG** | ✅ thangylvp/MA-RAG | ✅ HotpotQA + MuSiQue + 2Wiki | ✅ 2025-05 | **✅ TOP** |
| 2 | **ReAgent** | ✅ astridesa/ReAgent | ✅ HotpotQA + 2 others | ✅ 2025 EMNLP | **✅ TOP** |
| 3 | MAD (Du 2024) | ✅ composable-models | ⚠ partial (not direct on HotpotQA per paper) | ✅ ICML 2024 | ✅ retain (already in module-swap as SWAP-4 host) |
| 4 | AgentRouter | ❌ "anonymous" | ✅ HotpotQA | ✅ 2025-10 | ❌ skip (code not located) |
| 5 | BELLE | ⚠ unclear (link ambiguous) | ✅ multi-hop QA | ✅ ACL 2025 | ⚠ medium (need engineer probe to confirm code) |
| 6 | Reasoning Court | ❌ no code | ✅ HotpotQA + MuSiQue | ✅ 2025-04 | ❌ skip |
| 7 | PRISM | ❌ no public code yet | ✅ all 4 multi-hop | ✅ 2025-10 | ❌ skip (re-evaluate when code drops) |
| 8 | MAR | ❓ check | ✅ HotpotQA | ✅ 2025-12? | ❓ engineer probe needed |
| 9 | AutoGen | ✅ ✅ | ❌ not core multi-hop QA | ✅ ICLR 2024 | ✅ retain (module-swap as SWAP-1 host) |
| 10 | AgentVerse | ✅ ✅ | ❌ not core multi-hop QA | ✅ ICLR 2024 | ✅ retain (cite only; not benchmark target) |
| 11 | ChatEval | ✅ ✅ | ❌ NLG evaluation | ✅ ACL 2024 | ✅ retain (module-swap as SWAP-3 host) |

**Filter result**:
- **2 fresh full-system SOTA candidates** with all three criteria: **MA-RAG + ReAgent**
- **1 medium-confidence candidate** (BELLE — engineer needs to confirm code link)
- **1 follow-up candidate** (MAR — engineer needs to find arXiv 2512.20845 and verify)
- **3 module-swap hosts** (AutoGen, ChatEval, MAD) — already designed in [`external_baseline_plan.md`](external_baseline_plan.md), **keep as-is**, this survey does not replace them

---

## 3. Recommended baseline selection (final)

### 3.1 Two-axis comparison strategy

| Axis | Purpose | Hosts/systems | Output |
|---|---|---|---|
| **Axis A: Full-system SOTA (NEW per R35)** | Direct head-to-head F1 on HotpotQA — answers reviewer "S6 baseline_quality" | MA-RAG + ReAgent (+ optional BELLE/MAR after engineer probe) | Table comparing our TCPB Stage-2 / EDO degenerate-Stage-2 vs each SOTA on same benchmark + backbone |
| **Axis B: Module-swap (existing per R10/R17)** | Mechanism isolation — answers reviewer "is the EDO mechanism providing value beyond host system?" | AutoGen + ChatEval + MAD | Existing `external_baseline_plan.md` Table 4 design |

Both axes are needed: Axis A answers "do we beat SOTA?", Axis B answers "is OUR mechanism the cause when we win?". Reviewer fatal #3 wants Axis A; reviewer fatal #1 (Finding 4 self-falsified) is best resolved by Axis B.

### 3.2 Recommended Axis A finalists (engineer ticket E-018)

**Tier 1 (must-do, scope-locked)**:
- **MA-RAG** ([`thangylvp/MA-RAG`](https://github.com/thangylvp/MA-RAG))
  - Why: only candidate that explicitly claims SOTA on HotpotQA + MuSiQue + 2Wiki simultaneously, with code, and with a backbone (LLaMA3-8B) we can reproduce on server's RTX 3090.
  - Effort: ~4-6 h to install + reproduce on HotpotQA-200; ~1 day on HotpotQA-fullval (n=7405) if scope expands.
  - Backbone fairness: their reported numbers are on LLaMA3-8B / LLaMA3-70B / GPT-4o-mini. To compare fairly, run them with **gpt-4.1-mini** (our canonical) — adapt their LLM client. If adaptation is not trivial in 4-6h, fall back to their reported GPT-4o-mini number + cite (NOT ideal but better than nothing).

- **ReAgent** ([`astridesa/ReAgent`](https://github.com/astridesa/ReAgent))
  - Why: 2025 EMNLP-published, with code, claims +6% over forward-only baselines on HotpotQA + 2 others. The "reversible / rollback" framing is conceptually distinct from MAD's "debate" so adds breadth to our Axis A comparison.
  - Effort: similar ~4-6 h install + 200-sample reproduce.
  - Backbone fairness: paper doesn't pin a backbone in our search results; engineer should check repo's default setup.

**Tier 2 (engineer probe + decide; user sign-off if either succeeds)**:
- **BELLE** (arXiv 2505.11811) — code link ambiguous; engineer 30 min probe to find actual code repo. If found, prioritise Tier 1.
- **MAR** (arXiv 2512.20845) — newest paper; engineer probe to find code + reported HotpotQA EM 44→47 verification.

**Tier 3 (retain-from-existing-plan, NOT new from this survey)**:
- AutoGen (already cloned, SWAP-1 host)
- ChatEval (already cloned, SWAP-3 host)
- MAD (already cloned, SWAP-4 host)

### 3.3 Final benchmark table planned for §4.x of paper (combined Axis A + B)

```
Table 4 (proposed): External baseline comparison on HotpotQA
  Row 1:   MA-RAG (Tran et al. 2025)              F1 X.XXX (cited Y.YYY)  Tok ZZ
  Row 2:   ReAgent (Liu et al. EMNLP 2025)         F1 X.XXX (cited Y.YYY)  Tok ZZ
  Row 3:   MAD (Du et al. 2024)                    F1 X.XXX (reproduced)   Tok ZZ
  Row 4:   AutoGen (Wu et al. 2024)                F1 X.XXX (reproduced)   Tok ZZ
  Row 5:   ChatEval (Chan et al. 2024)             F1 X.XXX (reproduced)   Tok ZZ
  Row 6:   Our TCPB Stage-1 prototype (M-7)        F1 0.7381                Tok 6414
  Row 7:   Our EDO Stage-2 prototype (M-9)         F1 X.XXX (E-017)         Tok 4113
+ Inset table 4b (module-swap, separate axis):
  SWAP-1  AutoGen + R3                             ΔF1 ±X.XXX  Δtok ±YY%
  SWAP-3  ChatEval + R2                            ΔF1 ±X.XXX  Δtok ±YY%
  SWAP-4  MAD + R2                                 ΔF1 ±X.XXX  Δtok ±YY%
```

The combined design lets us claim:
- **(A) competitive with SOTA**: row 6/7 vs rows 1-5 — answers fatal #3
- **(B) mechanism causally contributes**: SWAPs 1/3/4 deltas — answers fatal #1
- **(C) cost-efficiency**: token-cost column — answers token-cost narrative

---

## 4. Engineer ticket dispatch (NEW — append to `[external_baseline_workstream_20260420]`)

### 4.1 Ticket: E-018 — MA-RAG + ReAgent reproduce on HotpotQA

- **ticket_id**: E-018
- **assigned_to**: engineer
- **priority**: P0 (sprint critical-path; closes fatal #3 directly)
- **estimate**: ~10-12 h wall (split = 2 systems × {clone + install + adapt LLM to newapi + smoke probe + 200-sample reproduce}). Can run in parallel on server (independent venvs).
- **task spec**:
  1. **Step 1 — clone**: `git clone https://github.com/thangylvp/MA-RAG /media/data3/dengkw/idea04/external_baselines/marag` + `git clone https://github.com/astridesa/ReAgent /media/data3/dengkw/idea04/external_baselines/reagent`. License + commit-hash check.
  2. **Step 2 — install**: separate `venv_marag` + `venv_reagent` to avoid dependency conflicts. Note: MA-RAG may need LangChain / FAISS / specific LLaMA3 setup; ReAgent unspecified.
  3. **Step 3 — LLM adaptation**: write a thin OpenAI-compat client wrapper that points to our `newapi` (`xh.v1api.cc`) using `gpt-4.1-mini`. Hide the model swap from each system's internal logic.
  4. **Step 4 — smoke probe**: 1 example end-to-end through each system; verify it returns a HotpotQA-format short answer; record `cost_breakdown.json` and `repo_<name>_smoke.md`.
  5. **Step 5 — 200-sample reproduce on HotpotQA**: same 200 head samples we use for chain-200 (`artifacts/seed/hotpotqa_validation_200.jsonl`); compute F1 + EM via our standard scorer. Output: `artifacts/external_baselines/<system>/marag_200sample_<TS>/metrics.json`.
  6. **Step 6 — cost vs paper-reported number cross-check**: if our reproduced F1 is within ±5 pp of paper's reported number (on the closest backbone they used), reproduce succeeds. If outside, write `repro_error_band.md` with hypothesis (backbone difference / prompt-template / sample-slice difference).
  7. **Step 7 — handoff**: append `[E-018_done_<TS>]` sub-entry below `[external_baseline_workstream_20260420]`. Output the row data for §4.x Table 4 rows 1+2.
- **pinned_cautions_to_acknowledge**:
  - **C-1**: newapi PRIMARY only (do NOT touch deprecated kuaipao)
  - **C-3**: install in isolated venvs (`venv_marag`, `venv_reagent`); do NOT pollute system Python or our `workspace/idea04_core/` dependencies
  - **C-5**: cost ≤ $20 per system × 2 = $40 budget (200 samples × ~5000 tokens × 4 hops ≈ 4M tokens × $1/M = $4 per system × workers=4 should keep wall-time <2h)
  - **C-7 (R22 SSH failure-mode)**: if SSH hangs see `[pinned_cautions_for_engineer_ssh_failure_mode_20260420]` 5-step Recovery playbook
  - **C-8 NEW**: if the system uses retrieval (MA-RAG does — needs an embedding index), use the same Wikipedia distractor passages as HotpotQA's gold supporting facts (i.e., re-use the question's `context` field, NOT a separate corpus). This keeps comparison fair to our `evidence_seeker` setup which also uses provided context.
- **if_blocked**:
  - If MA-RAG's LLaMA3 backbone can't be swapped to gpt-4.1-mini cleanly → fall back to running them on their own backbone + cite paper's reported number with backbone-difference disclaimer.
  - If ReAgent's repo is too sparse to install → write `repo_reagent_install_blocker.md`, scientist notifies user U-022-decide whether to drop ReAgent or wait.

### 4.2 Ticket: E-019 (Tier 2 probe) — BELLE + MAR repo locator

- **ticket_id**: E-019
- **assigned_to**: engineer
- **priority**: P2 (after E-018 underway)
- **estimate**: 30-60 min total (2 × ~20 min web search + repo probe)
- **task spec**:
  1. Search arXiv 2505.11811 (BELLE) for actual code repo (the `LianjiaTech/BELLE` link in our search was likely wrong — that's a Chinese LLM project, not the multi-agent paper). Try Google Scholar + arXiv abs page links.
  2. Search arXiv 2512.20845 (MAR) — likely 2025-12 paper; locate code.
  3. If both found: append to E-018 spec as Tier 2 systems.
  4. If neither found: skip.

---

## 5. Scientist follow-up tickets

- **S-148 (this survey doc)** — ✅ R35 commit (this file)
- **S-149** (after E-018 done): fill TEMPLATE 3 in `_pending_data_templates.tex` with rows 1+2 (MA-RAG + ReAgent F1 / Tok), keep rows 3-5 placeholder until E-012/E-016 land.
- **S-150** (after E-018 done): update `benchmark_inventory.md` §3.3 to reflect the actual eligible 2-axis baseline roster (Axis A: MA-RAG + ReAgent; Axis B: AutoGen + ChatEval + MAD).
- **S-151** (after S-149 done): update §1 Introduction + §6 Conclusion to claim "external SOTA comparison" (current Honesty re-phrase from R24 will need an update — paper claim moves from "delivered Stage-1 instance" to "evaluated against [list of] 2024-2025 SOTA on HotpotQA").

---

## 6. Open user decisions

| ID | Decision | Recommendation | Status |
|---|---|---|---|
| **U-022-decide** | (a) approve E-018 = MA-RAG + ReAgent as Tier-1 finalists / (b) want different / additional systems / (c) skip Axis A and rely on Axis B alone (NOT recommended given user's R35 instruction) | **(a) approve MA-RAG + ReAgent** | ⏳ pending user (will be added to USER_TODO §A in R35 commit) |
| **U-023-decide** (depends on E-018 outcome) | If MA-RAG / ReAgent's reproduced F1 falls below their reported number by >5 pp, accept the reproduction error and report honestly in §4.x, OR re-run on their original backbone? | TBD until E-018 produces data | ⏳ deferred until E-018 reports back |

---

## 7. References (papers cited above)

- **MA-RAG**: Tran, T. T., et al. (2025). "MA-RAG: Multi-Agent Retrieval-Augmented Generation via Collaborative Chain-of-Thought Reasoning." arXiv:2505.20096. https://github.com/thangylvp/MA-RAG
- **ReAgent**: Liu, X., et al. (2025). "ReAgent: Reversible Multi-Agent Reasoning for Knowledge-Enhanced Multi-Hop QA." EMNLP 2025 (also arXiv:2503.06951). https://github.com/astridesa/ReAgent
- **MAD (Du)**: Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., Mordatch, I. (2024). "Improving Factuality and Reasoning in Language Models through Multiagent Debate." ICML 2024. https://composable-models.github.io/llm_debate
- **Reasoning Court**: arXiv:2504.09781 (2025-04). HotpotQA + MuSiQue + FEVER. **No code** — skipped from finalists.
- **PRISM**: Nahid, M. M. H., Rafiei, D. (2025). "PRISM: Agentic Retrieval with LLMs for Multi-Hop Question Answering." arXiv:2510.14278. **No public code** — skipped.
- **AgentRouter**: Zhang, Z., Shi, K., et al. (2025). arXiv:2510.05445. "Anonymous repository" — skipped pending de-anonymization.
- **BELLE**: Zhang, T., et al. (2025). "BELLE: A Bi-Level Multi-Agent Reasoning Framework for Multi-Hop Question Answering." ACL 2025 (arXiv:2505.11811). Code link unclear — Tier 2 probe.
- **MAR**: Multi-Agent Reflexion. arXiv:2512.20845 (2025-12?). Tier 2 probe.
- **AutoGen**: Wu, Q., et al. (2024). ICLR 2024 paper + https://github.com/microsoft/autogen — already cloned on server, retained as SWAP-1 host.
- **AgentVerse**: Chen, W., et al. (2024). ICLR 2024 + https://github.com/OpenBMB/AgentVerse — cited only, not benchmark target (not multi-hop QA core).
- **ChatEval**: Chan, C.-M., et al. (2024). ACL 2024 + https://github.com/chanchimin/ChatEval — already cloned on server, retained as SWAP-3 host.

---

## 8. Maintenance

- This file is updated when: (a) E-018 reports back with reproduce numbers (R36+); (b) E-019 finds Tier 2 code (R36+); (c) any new SOTA paper drops on arXiv that should be considered (manual scientist update).
- Ownership: scientist for content; engineer ticket spec lives in `ENGINEER_TODO.md` `[external_baseline_workstream_20260420]` (or new `[sota_full_system_workstream_20260420]` if user prefers separate phase block).
- Cross-link from `benchmark_inventory.md` §3.3 once user picks finalists (U-022-decide).
