# R-FULL-018 — Full-paper review (P2 Empirical-NLP SAC STRICT experiments-weighted, target = Best Paper 8.5)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260421_091514_18_df7917` |
| **reviewer_profile** | **P2: Empirical-NLP SAC** (focused on Empirical Results D4, Baseline Quality S6, Ablation Completeness S7, Statistical Rigor S5; demands ≥3 diverse datasets, latest published SOTA, full ablation matrix, multi-seed runs with paired significance tests, honest error analysis; flags single-benchmark / single-seed papers as **borderline-reject by construction**) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `D6A67296A7542C6D8C39CC4709CD16CCC04683FD6C0BE603D3C0B83D979C43EE` |
| **pdf_sha16** | `D6A67296A7542C6D` (same as R-FULL-017 target; post-S-173 DR-1 recovery + build-script logic fix; mtime 2026-04-21 08:57:21) |
| **target_score** | **8.5** (Best-Paper bar per `docs/demand.md §11.5`) |
| **prior_batch_independence** | **stateless** — no `scoreboard.md`, no `fix_themes.md`, no `review.md` from batches 01–17, no `SCIENTIST_TODO §C`. P2 last used in R-FULL-010 on older PDF `37A3F45D`; first P2 audit of SHA `D6A67296` with post-S-173 theorems-in-Appendix-F structure + cost-normalised Pareto axis reframe. |
| **rulebook** | `docs/demand.md §1–§11` + `prompts/reviewer_prompt.md §2–§10` |
| **process_compliance (§1.5.0)** | **Satisfied**: `docs/demand.md` + `pdftotext -layout` extraction of PDF (923 lines / 103635 B / 15 pages) read end-to-end. |
| **user_trigger** | User verbal explicit: "现在可以再去按照一个新的审稿人角度去审 ... 特别关注论文的实验 ... 实验的评分占比要高 ... 按照best paper的要求严格审稿" → implicit `U-Review-18-decide`. P2 Empirical-NLP SAC is **the direct-fit persona** for user's experiments-weight emphasis + Best-Paper strictness. |

---

## Document classification

`document_type` = **full_paper**. `submission_track` = EMNLP Long Paper — Oral / Best-Paper bar.

**DR-1 PASS entry** (verified by 3 methods): main body 8 pages COMPLIANT (Limitations on p9, 0 preceding lines); post-S-173 4 theorems moved to Appendix F.

---

## Summary (≤ 100 words)

P2 experiments-strict audit of post-S-173 PDF: structural fixes land (D1=6.5 post-S-163/S-173, DR-1 PASS), but **core P2 bar is unmet**. `experiments_solidity_score=1/8` — **every single EXP-2/3/4/6/8 check fails**, EXP-1 single benchmark, EXP-5 ablations on non-canonical backbone with null effects. Zero external published 2024–2025 SOTA baselines in main tables. Single-seed (seed=42) fullval `F1=0.6884` vs `self_claim` 0.7641 on canonical backbone — an F1-axis loss despite cost-normalised reframing (`F1/1k tok +84%`). Paired-bootstrap CI deferred to camera-ready. **P2 borderline-reject-by-construction criterion**: single-benchmark / single-seed → **weak_reject 4.5** (D4 cap binding).

---

## Desk-reject risks (`desk_reject_risks`)

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | fixed build_paper.ps1: main body p8 COMPLIANT (Limitations on p9, 0 preceding lines); pdftotext -f 8 / -f 9 independent verification |
| DR-2 | PASS | `Limitations` exact title after Conclusion |
| DR-3 | PASS | 7 items scope only; engineering in Appendix B; theorems in Appendix F |
| DR-4 | POSSIBLE – not verified | pdftotext cannot audit `acl.sty` |
| DR-5 | PASS | No process leak |
| DR-6 | PASS | B1–B5 complete |
| DR-7 | PASS | Coherent long-form |
| DR-8 | PASS | AI assistance disclosed + Ethical Considerations |

Net: 0 confirmed DR; 1 POSSIBLE (DR-4).

---

## Best-Paper structural compliance (`best_paper_structural_compliance`)

### §11.5 addendum 12-item checklist — P2 strict experiments-weighted verdict

| # | Requirement | Status | P2 evidence |
|---|------------|--------|-------------|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | lower bound; Best-Paper typically 3-4 p |
| 2 | **≥ 3 diverse datasets in main tables** | **❌ fail (P2 disqualifying)** | HotpotQA ONLY; MuSiQue + 2WikiMultiHop deferred to Stage-2; P2 rubric: "single-benchmark → borderline-reject by construction" |
| 3 | **Latest 12-month SOTA baseline in main tables** | **❌ fail (P2 disqualifying)** | **Zero external 2024-2025 SOTA in main tables**; AutoGen/ChatEval/MAD/MA-RAG/ReAgent/MetaGPT cited in Related Work §2 only; **S6 = 2.0 "No external baselines at all"** per rubric |
| 4 | **Per-component ablation on canonical backbone** | **❌ fail** | Table 2 on legacy `glm-4-flash`; §4.2 self-admits "guidance-only, not the final paper evidence"; canonical `gpt-4.1-mini` ablation pending E-014 |
| 5 | **Multi-seed + paired tests + CI/effect-size** | **❌ fail (P2 disqualifying)** | seed=42 only for Stage-2 fullval; seeds 43/44 pending; paired-bootstrap CI explicitly "deferred to camera-ready"; P2 rubric: "single-seed → borderline-reject" |
| 6 | Error analysis with quantitative named failure modes | ❌ fail | No taxonomy |
| 7 | Dedicated case-study / application block | ❌ fail | No case-study section |
| 8 | Limitations ≥ 0.5 p, honest, specific | ✅ pass | 7 items |
| 9 | Ethical Considerations section | ✅ pass | 5 sub-paragraphs |
| 10 | Figure 1 vector-quality system schematic | ❌ fail | Still placeholder "[Figure 1 placeholder]" |
| 11 | Public anonymous code/data/model release | ⚠ partial | Code + data; no model (API-only) |
| 12 | **No null-effect ablation tables** | ⚠ partial | Table 2 bit-identical rows; caption mitigates but does not resolve |

**Count**: 7 hard + 3 partial + 2 pass. **§11.5 enforcement**: 7+ missed → `oral_quality_score ≤ 3`; **P2 assigns 2.5** (P2 stricter than P5 R-FULL-017 3.0 on experiments-focused dimensions).

**P2 critical observation**: items #2 + #3 + #5 are the **single-benchmark-single-seed-no-external-SOTA triad** that P2 rubric explicitly calls "borderline-reject by construction". All three still failing.

---

## Experiments-solidity audit (`experiments_solidity_audit`) — P2 specialty deep audit

| Check | Status | P2 evidence (strict) |
|-------|--------|----------------------|
| **EXP-1 multi-dataset** | **fail** | HotpotQA only; main tables use single benchmark; demand.md §8 requires 3-5 datasets |
| **EXP-2 multi-seed** | **fail** | §B2 + §4.5: single seed=42; seeds 43/44 pending; "Paired CI deferred to camera-ready" |
| **EXP-3 significance test** | **fail** | §4.3 Finding 2: "not yet confirmed with paired statistics" (2.6 F1 point gap at n=200); no paired bootstrap / sign test / paired t reported anywhere |
| **EXP-4 effect size / CI** | **fail** | No confidence intervals reported; §B2 explicit "CIs not reported in this submission"; Table 1 + Table 2 + §4.5 fullval all point estimates only |
| **EXP-5 ablation coverage** | **partial** | Table 2 on non-canonical `glm-4-flash`; 3 bit-identical rows; R1/R2/R3 Stage-2 mechanisms unablated; coverage_ratio on canonical backbone = 0 |
| **EXP-6 baseline recency** | **fail** | Zero external 2024-2025 SOTA in main tables; oldest_baseline_year = N/A (authors' own variants); most_recent_baseline_year = N/A; latest_sota_present = **false**; missing_recent_sota = [AutoGen 2024, ChatEval 2024, MAD 2024, MA-RAG 2025, ReAgent EMNLP 2025, MetaGPT 2024] |
| **EXP-7 sensitivity sweep** | **partial** | ±2× weight sweep in §4.5 (single hyperparameter); no sweep on safety-gate thresholds / force-forward gate / audit predicates |
| **EXP-8 error analysis** | **fail** | Finding 3 attributes PAR=0 to safety gate (one observation); §4.5 52% route overlap (one number); no quantitative error taxonomy with named failure modes |

**`experiments_solidity_score` = 1 / 8** (only EXP-7 partial counts as 1).

**P2 cap cascade**:
```
EXP-1 fail      → cap D4 at 6
EXP-2 fail      → cap D4 at 5, S5 at 4
EXP-3 fail      → cap D4 at 6, S5 at 5
EXP-5 partial   → cap D4 at 6, S7 at 5 (coverage on canonical = 0)
EXP-6 fail      → cap D4 at 5, S6 at 4
exp_solidity≤3  → cap D4 at 4, overall at 4.5
```

Effective D4 cap = 4; assigned **D4 = 4.0** (same as R-FULL-016 P1). Assigned S5 = 3.0, S6 = 2.0, S7 = 4.0 (all below P2 rubric ≥5 threshold).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | is_concrete | is_overlap_risk |
|---|---|---|---|---|
| 1 | AutoGen (Wu, ICLR 2024) | 2024 | true | false |
| 2 | ChatEval (Chan, ICLR 2024) | 2024 | true | false |
| 3 | Multi-Agent Debate (Liang/Du 2024) | 2024 | true | **true** |
| 4 | MetaGPT (Hong, ICLR 2024) | 2024 | true | false |
| 5 | Reflexion / ToT / Self-Refine (2023) | 2023 | true | false |

MAD overlap unaddressed → **D3 cap at 4**.

---

## Dimension scores (P2 Empirical-NLP SAC strict lens)

| Dim | Score | P2 defense |
|-----|-------|------------|
| **D1 Soundness** | **6.5** | Post-S-163 Symbol Glossary + post-S-173 Appendix F (1-locality / complexity / convergence / reduction proofs). Band 7 "Mostly correct, under-specified update rules recoverable". P2 is not the D1-strict persona (that's P1) so assigned 6.5 without further scrutiny. |
| **D2 Significance** | **4.5** | Delivered empirical story = single-benchmark Pareto-negative F1 with cost-normalised reframing. P2 significance bar: requires multi-dataset impact → not yet met. |
| **D3 Novelty** | **4.0** (cap) | MAD overlap cap. Reframing-only novelty + Stage-2 theoretical-only. |
| **D4 Empirical** | **4.0** (cap = 4.5) | **P2 specialty — strictest view**. All P2 hard rules fail: single benchmark, single seed, no paired significance, no CI, no external SOTA, null ablations on non-canonical backbone, no quantitative error taxonomy. P2 rubric band 4 "single benchmark, single seed, weak/stale baselines, no ablations; results may be within noise" fits exactly. Not 3 because Finding 4 self-refutation is honest + §4.5 cost-normalised reframing is a concrete datapoint (even at single seed). Not 5 because single-seed is disqualifying at that band. |
| **D5 Reproducibility** | **6.5** | Algorithm 1 + S-163 + Appendix C + Appendix F + B1–B5 + seed disclosed. Band 7 "methods clear; some details email-authors". |
| **D6 Clarity** | **5.0** | Figure 1 placeholder remains primary drag; Appendix F adds rigor. |
| **D7 Responsible research & limitations** | **8.0** | Limitations + Ethical Considerations covers all 6 band-8 requirements. |

### Secondary (S1–S8)

| S | Score | P2 note |
|---|-------|---------|
| S1 executability | 6.5 | Stage-1 implementable from paper-alone post-S-163 + Appendix F |
| S2 falsifiability | 5.5 | Central claim measurable; paired CI pending |
| S3 empirical plan (design only) | 5.5 | §4.4 E1-E5 reasonable but unexecuted |
| S4 technical clarity | 7.0 | Post-S-173 Appendix F gives formal proofs |
| **S5 statistical rigor** | **3.0** | P2 specialty harsh: single seed, no paired, no CI. Capped by EXP-2 (S5 ≤ 4) and EXP-3 (S5 ≤ 5). |
| **S6 baseline quality** | **2.0** | **P2 specialty harsh**. Rubric verbatim: "2 = No external baselines at all". Authors' own 3 internal variants ≠ external baselines. |
| **S7 ablation completeness** | **4.0** | Null effects on non-canonical backbone; Stage-2 R1/R2/R3 unablated; coverage_ratio on canonical = 0. |
| S8 writing and figures | 5.0 | Figure 1 placeholder |

**`oral_quality_score` = 2.5** — P2 strict: §7 "never grants Oral-eligibility on a single-benchmark or methodology-note submission"; §11.5 7+ missed → cap 3; P2 stricter than P5 (2.5 vs 3.0).

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*6.5 + 0.18*4.5 + 0.15*4.0 + 0.18*4.0 + 0.10*6.5 + 0.07*5.0 + 0.07*8.0
             = 1.625 + 0.810 + 0.600 + 0.720 + 0.650 + 0.350 + 0.560
             = 5.315

Caps applied:
- DR-4 POSSIBLE only               → no DR cap
- D1 = 6.5 ≥ 5                     → no D1 cap
- D4 = 4.0 < 5                     → cap overall at min(5.315, D4+0.5) = 4.5 (binding)
- D4 = 4.0 < 7                     → cap at 7.0 (not binding)
- D3 = 4.0 < 5                     → cap at D3+0.5 = 4.5 (tied)
- D3 = 4.0 < 6                     → cap at 6.5 (not binding)
- oral_quality = 2.5 < 5           → cap at 5.5 (not binding)
- exp_solidity = 1 ≤ 3             → cap at 4.5 (tied)
- novelty overlap MAD              → cap at 5.0 (not binding)
- S6 = 2.0 < 5                     → cap at 6.0 (not binding)
- S7 = 4.0 < 5                     → cap at 6.0 (not binding)
- §11.5 7+ missed                  → cap oral at 3 (assigned 2.5)

overall = 4.5
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **5.315** (P2 stricter than P5 R-FULL-017 5.350 by -0.035; same PDF different persona; P2 stricter than P1 R-FULL-016 5.490 by -0.175 on D2+D3+D4 empirical bars) |
| **overall** | **4.5 weak_reject 连续 5 轮 > 4.0** (R-FULL-014/015/016/017/018) |
| **verdict** | **weak_reject** |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **is_best_paper_ready** | **false** |
| **confidence** | **4 / 5** |
| **estimated_score_after_fixes** (E-017 seed=43+44 + paired CI + E-014 canonical + E-018 external SOTA + MuSiQue + Figure 1) | **6.0–6.3 borderline** (P2 stricter than P5's 6.2 projection on D4/S5/S6/S7 experiments bars) |
| **estimated_score_after_Best-Paper-track_fixes** | **7.0–7.5 Oral border** |

---

## Top strengths (`top_strengths`)

1. **S-173 DR-1 recovery completed in single session** (user-flag → reviewer-verify → fix → 3 independent PASS verifications). Post-S-173 theorem proofs preserved via Appendix F F.1-F.4 (decentralization / complexity / convergence / TCPB reduction).
2. **S-163 Symbol Glossary (§3.6)** — Stage-1 TCPB implementable from paper-alone (14 undefined operational objects now formalised or Stage-2-marked).
3. **§4.5 cost-normalised Pareto-axis reframing**: single-seed canonical-backbone fullval `F1=0.6884 n=7405 → F1/1k tok=0.2953 = +84% vs static_roles +146% vs self_claim` — concrete Stage-2 evidence even at single seed, reframes Finding 4 on a different axis (without reversing the F1-axis loss which P2 flags).
4. **Dual-section honesty** (Limitations + Ethical Considerations) band 8 D7.

## Top weaknesses (`top_weaknesses`) — P2 experiments-strict ordered

1. **Zero external 2024-2025 SOTA baselines in main tables (S6 = 2.0)** — disqualifying for Best-Paper bar; AutoGen/ChatEval/MAD/MA-RAG/ReAgent are Related Work citations only.
2. **Single benchmark (HotpotQA)** — §11.5 #2 + demand.md §8 both require 3-5 datasets; MuSiQue + 2WikiMultiHop deferred.
3. **Single-seed fullval (seed=42 only)** + **no paired bootstrap CI** (deferred to camera-ready) — P2 rubric "borderline-reject by construction".
4. **Finding 4 F1-axis Pareto-dominance still not reversed** on canonical backbone: TCPB `peer_calibrated` F1=0.7381 < `self_claim` F1=0.7641 at equal cost; cost-normalised reframing ($-63.7\%$ tokens, +84% normalised) is a denominator switch, not an F1 victory.
5. **Table 2 ablations on non-canonical `glm-4-flash`** — §4.2 self-admits "guidance-only, not final paper evidence" yet remains the sole ablation evidence in main body; E-014 canonical ablation pending post-quota.
6. **Figure 1 still placeholder** — §11.5 #10.
7. **MAD overlap unaddressed empirically** — D3 cap 4; §2.2 prose-only.
8. **No quantitative error taxonomy with named failure modes** — EXP-8 fail.
9. **No case-study / application block** — §11.5 #7; Best-Paper convention (Infini-gram 2025: 7 case figures; Image Transcreation 2024: gallery).

## Experimental design problems (`experimental_design_problems`) — P2 specialty

1. Table 1 "baselines" = 3 internal variants (`self_claim`, `static_roles`, `peer_calibrated`); **zero external published systems**.
2. Table 2 on legacy `glm-4-flash`; canonical-backbone ablation (E-014) pending.
3. Table 2 three-row bit-identical ablations on wrong backbone; caption mitigates but doesn't resolve.
4. §4.5 fullval seed=42 only; paired-bootstrap CI across ≥3 seeds deferred to camera-ready.
5. No sensitivity sweep on safety-gate thresholds / force-forward-gate decision rules / audit-LLM-fallback predicates.
6. No head-to-head against MAD despite §2.2 acknowledging overlap.
7. n=200 for canonical Stage-1 comparison is 35× below HotpotQA dev-split size; only one Stage-2 method has n=7405 data.

## Missing or weak experiments (`missing_or_weak_experiments`)

1. No external 2024-2025 SOTA in main tables (AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT).
2. No MuSiQue / 2WikiMultiHop / any compositional-QA second benchmark.
3. Only seed=42 fullval for `edo_stage2_chain`; seeds 43/44 + full paired-bootstrap CI pending.
4. No canonical-backbone ablation (E-014 blocked on quota slot).
5. No MAD head-to-head (E-015/E-016 blocked on E-017 freeing quota).
6. No case-study gallery (6-10 visualisations).
7. No quantitative error taxonomy with failure-mode frequencies.

## Statistical significance concerns

1. Table 1 n=200 point estimates without paired bootstrap / sign test / permutation.
2. Table 2 three identical rows without significance framing; caption acknowledges but doesn't test.
3. §4.5 single-seed fullval — paired-bootstrap CI deferred ("ready for camera-ready"); P2 considers this **disqualifying for submission-version claims**.

## Baseline completeness concerns

1. S6 = 2.0 "No external baselines at all" — main tables use authors' own internal variants only.
2. Latest multi-hop-QA SOTA from past 12 months (MA-RAG 2025 / ReAgent EMNLP 2025) cited only as Stage-2 roadmap items.
3. `demand.md §8` + `§11.5 #3` requirement "strong baselines including latest SOTA" — double miss.

## Limitations section assessment

| Field | Value |
|-------|--------|
| section_present | true |
| section_title_exact | true |
| contains_no_new_content | true |
| honesty_score_1_to_5 | 5 |
| specific_failure_modes_listed | true |
| issues | ["item (5) 'queued for re-execution' borderline operational"] |

## Responsible NLP Checklist assessment

| Field | Value |
|-------|--------|
| appears_complete | true |
| issues | [] |

## `what_to_fix_for_8_plus` (P2 strict ranking, target overall ≥ 8.0)

1. **[Highest P2 leverage]** E-017 seeds 43 + 44 + paired_bootstrap_ci → D4 ≥ 5 unlocks D4<5 cap → overall 4.5 → 5.0-5.5.
2. **E-018 ≥2 external 2024-2025 SOTA reproduce** (MA-RAG + ReAgent minimum; MAD adds D3 relief) → S6 ≥ 5.
3. **MuSiQue second benchmark** → EXP-1 close.
4. **E-014 canonical-backbone ablation** → discriminate Table 2 null effect; S7 ≥ 5.
5. **Quantitative error analysis** with named failure modes (hop-count × failure-type matrix) → EXP-8 close.
6. **Replace Figure 1 placeholder**.

## `what_to_fix_for_oral` (Best-Paper 8.5)

1. All of `what_to_fix_for_8_plus` **plus**:
2. **Reverse Finding 4 on F1-axis** (not cost-normalised denominator switch): show full-EDO beats `self_claim` on F1 at equal or lower cost on ≥1 benchmark.
3. Implement ≥ 1 of R1 / R2 / R3 with measurable wins against external SOTA.
4. **Case-study / application gallery** (6-10 visualisations) demonstrating organisational-emergence behaviour.
5. **Mechanistic-novelty falsifiable claim** beyond reframing.

## `recommended_next_actions`

1. **[Highest priority]**: let E-017 seed=43+44 fullval complete (scheduler chained); run `paired_bootstrap_ci.py` on 3 seeds; refresh Table 1 with multi-seed CI and paired significance.
2. Launch E-014 canonical-backbone ablation immediately once quota slot free.
3. Launch E-018 MA-RAG + ReAgent reproduce on HotpotQA in parallel.
4. Draft §4 error-taxonomy block (hop-count × failure-type matrix) from existing per-run logs — does not require new LLM calls.
5. Replace Figure 1 placeholder (blocked on user illustration).

## `rule_source_disagreements`

None.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":           true,
  "edo_paper_pdf_loaded":       true (pdftotext -layout 103635 B / 923 lines / 15 pages end-to-end),
  "fallback_source_used":       "pdftotext -layout article/build/edo_paper.pdf",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit"],
  "demand_section_11_applied":  true (7 hard + 3 partial + 2 pass; oral_quality cap 3; P2 assigned 2.5),
  "persona_rotation":           "P2 Empirical-NLP SAC; last used in R-FULL-010 on older PDF 37A3F45D; first P2 audit of SHA D6A67296 post-S-173 + post-R48-theoretical-depth + post-§4.5-Pareto-axis-reframe",
  "weighted_pre_cap_18_round_trajectory": "5.925→5.925→5.905→4.985→4.910→4.560→4.725→5.105→4.940→4.765→4.975→4.410→5.275→5.100→5.495→5.580→5.490→5.350→**5.315 (R-FULL-018 P2)**. P2 stricter than P5 R-FULL-017 by -0.035 (very close; P2 stricter on S5/S6 compensates for D2 tolerance); stricter than P1 R-FULL-016 by -0.175 (P2 stricter on empirical dimensions).",
  "p2_verdict_rationale":       "P2 rubric explicitly calls single-benchmark / single-seed / no-external-SOTA → 'borderline-reject by construction'. Current paper hits all three. Despite D1 + D5 + D7 being band 7-8 after post-S-163/S-173 hygiene work, D4 cap binds at 4.5 and overall cannot exceed 4.5 until E-017 seed=43/44 + paired CI + ≥1 external SOTA lands. P2 confirms (for the 2nd time after R-FULL-003/007/008/010) that experiments_solidity is the sole gating cap for this paper."
}
```

---

## `_parse_mode`

`full`

*End of review. P2 Empirical-NLP SAC specialty audit finds same core weakness pattern as R-FULL-010 P2 (experiments_solidity = 1/8, D4 cap, S6 = 2.0, Finding 4 F1-axis loss) with additional hygiene-layer improvements verified post-S-163/S-173 (D1 = 6.5 vs R-FULL-010 P2 5.5; D5 = 6.5 vs R-FULL-010 P2 6.5; D7 = 8.0 vs R-FULL-010 P2 7.5). **overall stays at 4.5 weak_reject** — consecutive 5 R-FULL batches (R-FULL-014/015/016/017/018) stable at 4.5 = sprint critical-path (E-017 fullval + experiments-pipeline) is the binding constraint; S-163/S-173 hygiene work has maxed out its contribution; further gains await the experiments landing.*
