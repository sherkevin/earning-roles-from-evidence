# R-FULL-007 — Full-paper review (stateless batch)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260419_233800_07_53f7fb` |
| **reviewer_profile** | **P2: Empirical-NLP SAC** (D4 / S5 / S6 / S7 / S5 specialty; strict, no score inflation) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `53F7FB9DE7A3FCB095C3C4A53D0B6D23B324E626CFF55AE921356E42C5D503BE` |
| **pdf_sha16** | `53F7FB9DE7A3FCB0` (first 16 hex of SHA256; index key) |
| **prior_batch_independence** | No `scoreboard.md`, no prior `review.md`, no `SCIENTIST_TODO` §C read for this batch. |
| **rulebook** | `d:\Codes\idea04\docs\demand.md` — read **in full** before scoring (§2 page limit + Self-Contained Main Body Rule + Limitations). |
| **process_compliance** | **§1.5.0 satisfied**: entire `demand.md` + full `pdftotext -layout` extraction of the PDF (title through references) read end-to-end for this review. |

---

## Summary (≤ 200 words)

The paper reframes multi-agent routing as organizational emergence (EDO) and positions TCPB as an honest Stage-1 prototype. Writing is unusually self-critical (Pareto-dominated peer calibration vs. self-claim on HotpotQA chain-200; backbone-sensitive ordering). Under **current EMNLP long-paper empirical standards** (`demand.md` §3 / §8), however, the **evaluated core** remains a **single public benchmark** with **dominant n=200 reporting** for method ordering, **no paired significance tests or CIs in the submission**, **no multi-dataset main results**, and **no external full-system baselines in the main tables**—so empirical claims are structurally under-powered for acceptance. Formatting: **DR-1 PASS** under post–U-021 `demand.md` (8-page main body; appendices exempt; §4.5 + Appendix D narrative is careful not to treat preliminary Stage-2 shards as headline evidence). **Overall remains cap-bound (~4.5)** by `experiments_solidity_score` and D4 caps, not by desk reject.

---

## Desk-reject risks (`desk_reject_risks`)

| ID | Status | Evidence / notes |
|----|--------|------------------|
| DR-1 | **PASS** | Main narrative ends with §5 Conclusion on page 8; Limitations follows; appendices follow. Self-contained rule: headline Table 1 / Figure 2 in main body; §4.5 gives preliminary Appendix D numbers **in prose** and explicitly states headline claims are **not** based on that preliminary table. Algorithm semantics: §3.6 prose + utility formulas; full pseudocode in Appendix E per rulebook. |
| DR-2 | **PASS** | Section titled exactly `Limitations` after Conclusion. |
| DR-3 | **PASS** | Limitations discuss scope; engineering detail in Appendix B, not new experiments in Limitations. |
| DR-4 | **POSSIBLE – not verified** | Template tampering not audited from LaTeX sources this batch; no visible font trick in PDF text. |
| DR-5 | **PASS** | Anonymous submission framing respected in visible text. |
| DR-6 | **PASS** | Appendix A checklist present; AI use disclosed in B4. |
| DR-7 | **PASS** | Reads as one coherent long submission, not thin-sliced duplicate. |
| DR-8 | **PASS** | No ethics red flags in visible text. |

---

## Experiments solidity audit (`experiments_solidity_audit`)

| Check | Result | One-line justification |
|-------|--------|-------------------------|
| EXP-1 multi-dataset | **fail** | Primary reported comparisons are HotpotQA; MuSiQue / transfer is future (§4.4 E5), not main tables. |
| EXP-2 multi-seed | **fail** | Chain-200 and Table 1 narrative center on **seed=42**; full multi-seed settlement explicitly deferred (Limitations item 4, §4.5). |
| EXP-3 significance | **fail** | No paired test reported for headline ordering; paper notes 2.6 F1 gap at n=200 is not confirmed with paired stats. |
| EXP-4 CI / effect size | **fail** | B2 states CIs not reported; deferred to Stage-2 agenda. |
| EXP-5 ablation | **pass** | Table 2 + §4.5 sensitivity / route overlap support targeted ablations on Stage-1 knobs. |
| EXP-6 baseline recency | **fail** | Related work names strong 2024 systems, but **main result tables** are internal method variants, not reproduced external full pipelines (module-swap / SOTA rows not in body for this PDF version). |
| EXP-7 sensitivity | **partial** | ±2× weight sweep reported as tiny F1 movement in §4.5. |
| EXP-8 error analysis | **fail** | Qualitative failure-mode accounting is thin vs. rubric (no quantitative error taxonomy). |

**experiments_solidity_score**: **1 / 8** (only EXP-5 clear pass).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | claimed_difference | is_concrete | is_overlap_risk |
|---|-----------------|------|-------------------|-------------|-----------------|
| 1 | AutoGen | 2024 | Removes global orchestrator / fixed expert table vs. local graph + terminal calibration | true | false |
| 2 | ChatEval | 2024 | Peer/meta review per hop vs. terminal-only calibration in TCPB prototype | true | false |
| 3 | Multi-Agent Debate (Liang et al.; Du et al.) | 2024 | Multi-agent deliberation vs. outcome-grounded delegation ladder | true | **true** |

**Overlap handling**: §2.2 discusses MAD, but **no empirical head-to-head** in main evaluation → **D3 cap at 4** per prompt hard rule.

---

## Dimension scores

| Dim | Score | Brief defense |
|-----|-------|----------------|
| D1 | **5.5** | FIT / utility structure + Appendix E loop; hand-tuned λs and many priors still limit formal closure. |
| D2 | **5.0** | Interesting org framing; delivered empirical story is partly a **negative / limitation** result on F1. |
| D3 | **4.0** | Named priors + deltas; **MAD overlap risk** without benchmarked isolation. |
| D4 | **4.0** | Single-benchmark dominance, single-seed slice for ordering claims, no significance/CIs in paper → hard-stop band. |
| D5 | **6.0** | Appendix C templates + checklist + seed disclosure; still heavy reliance on anonymous supplement for full prompts. |
| D6 | **5.5** | Figure 2 useful; **Figure 1 placeholder** hurts presentation tier. |
| D7 | **7.5** | Limitations are detailed and honest (Pareto, backbone sensitivity, demographic scope item 7, stats limits). |

### Secondary (S1–S8)

| S | Score | Note |
|---|-------|------|
| S1 | 5.5 | Runnable spec exists per checklist, but many knobs in pseudocode. |
| S2 | 6.0 | Claims tied to measurable F1 / cost / PAR; negative results stated clearly. |
| S3 | 4.0 | Design in §4.4 is ambitious; **executed** design is narrow. |
| S4 | 6.0 | Equations + cross-ref to Appendix E help. |
| S5 | **3.5** | Single-seed + no reported paired tests. |
| S6 | **3.5** | No recent external full-system baseline in main tables. |
| S7 | **5.5** | Table 2 helps; safety-prior / gate interaction could use more factorial coverage. |
| S8 | 5.0 | Placeholder Figure 1. |

**oral_quality_score**: **3.0** — not Oral-track; empirical breadth is far below top 3–5% bar.

---

## Score calculation (deterministic caps)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*5.5 + 0.18*5.0 + 0.15*4.0 + 0.18*4.0 + 0.10*6.0 + 0.07*5.5 + 0.07*7.5
             = 1.375 + 0.9 + 0.6 + 0.72 + 0.6 + 0.385 + 0.525
             = 5.105

Caps applied (per reviewer_prompt §6):
- experiments_solidity_score <= 3  → cap overall at 4.5
- D4 = 4 (<5)                    → cap overall at min(overall, D4+0.5) = 4.5
- D3 = 4 (<5)                    → cap overall at min(overall, D3+0.5) = 4.5

overall = 4.5
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **5.105** |
| **overall** | **4.5** |
| **verdict** | **weak_reject** |
| **oral_eligible** | **false** |
| **confidence** | **8** / 10 |

---

## Top weaknesses (ranked)

1. **Empirical breadth**: Single public benchmark drives claims; MuSiQue / broader transfer still roadmap.
2. **Statistical hygiene**: n=200 ordering story without paired tests; CIs deferred—weak for EMNLP long-track soundness.
3. **External baselines**: Related work is strong, but main tables do not yet show competitive external systems at full pipeline level.
4. **Novelty defense vs. MAD**: Overlap risk named but not empirically isolated.
5. **Figure 1**: Placeholder signals unfinished camera-ready polish.

## Strengths

1. Rare honesty about Pareto limits of peer calibration vs. simpler baselines on strong backbone.
2. Clear separation of proposed Stage-2 mechanisms vs. delivered Stage-1 TCPB.
3. Provider-integrity narrative separated from Limitations (Appendix B) — DR-3 hygiene.
4. Appendix D + §4.5 alignment on token savings vs. EM / F1 uncertainty (post–S-145 style wording observed).

## `rule_source_disagreements`

None; scoring follows `d:\Codes\idea04\docs\demand.md` §2 (including Self-Contained Main Body Rule) and `reviewer_prompt.md` caps.

## `recommended_next_actions` (non-binding; user/scientist authority)

1. Complete E-017 multi-seed fullval + paired bootstrap; update Table 1 / narrative when all three methods settle.
2. Land MuSiQue (or second task family) with same rigor as HotpotQA for EXP-1.
3. Integrate agreed external baselines (AutoGen / ChatEval / MAD or SOTA survey picks) into **main** tables.
4. Replace Figure 1 placeholder with vector final.
5. Consider quantitative error analysis (failure types vs. hop count / decomposition).

## `estimated_score_after_fixes`

If experiments_solidity reaches **≥4/8** with multi-dataset + multi-seed + significance + external baselines, **overall could move toward 5.5–6.0 band** (still subject to D3 if MAD overlap unaddressed). Not estimating ≥7 without Oral-tier breadth.

---

*End of review (human-readable schema coverage per `prompts/reviewer_prompt.md` §9 fields rendered as markdown).*
