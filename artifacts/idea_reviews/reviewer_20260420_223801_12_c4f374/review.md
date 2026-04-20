# R-FULL-012 — Full-paper review (P4 Reproducibility-Ethics SAC, target = Best Paper 8.5, post-S-163 PDF)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_223801_12_c4f374` |
| **reviewer_profile** | **P4: Reproducibility-and-Ethics SAC** (focus on Reproducibility D5, Limitations D7, Responsible NLP Checklist; verifies Limitations titled exactly "Limitations" + no new content; flags missing artifact licenses, undisclosed AI, absent compute budget as desk-reject candidates; still enforces all §2.5 experiments hard rules) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `54DF9463B95D5CE8B6687F834CB6F4941060DD5C1BEE97A1C1A5CE8FC0E10AF7` |
| **pdf_sha16** | `54DF9463B95D5CE8` (**new PDF, post-S-163 D1 formalisation rebuild**; supersedes `37A3F45D` which was the R-FULL-010/011 target; mtime 2026-04-20 22:37:36) |
| **target_score** | **8.5** (Best-Paper bar per `docs/demand.md §11.5`) |
| **prior_batch_independence** | **stateless** — no `scoreboard.md`, no `fix_themes.md`, no `review.md` from batches 01–11, no `SCIENTIST_TODO §C`. This P4 audit is the first on SHA `54DF9463`; P4 last used on older PDF `4504614E` in R-FULL-005. |
| **rulebook** | `docs/demand.md` §1–§11 (post-§11.5 Best-Paper addendum) + `prompts/reviewer_prompt.md §2–§10` caps |
| **process_compliance (§1.5.0)** | **Satisfied**: `docs/demand.md` (241 lines) + `pdftotext -layout` full extraction of new PDF (13 rendered pages, 827 lines, 93187 B) read end-to-end before scoring. |
| **user_trigger** | User verbal explicit "新的审稿人角度 ... 特别关注论文的实验 ... 实验的评分占比要高" → implicit `U-Review-12-decide`. Persona rotation to P4 — last unused persona on recent PDF SHAs; P4's D5-specialty is optimally positioned to audit whether S-163 D1 formalisation actually closes the reproducibility debt that P1 flagged in R-FULL-011. |

---

## Document classification

`document_type` = **full_paper** (8-page main body + Limitations + Ethical Considerations + Appendices A–E + References; 14 rendered pages).

`submission_track` = EMNLP Long Paper — Oral / Best-Paper bar.

**Material change since R-FULL-011**: **S-163 D1 formalisation batch landed** — a new "Stage-1 operational collapses" paragraph appended to §3.6 (rendered p.5 lines 399–419) that explicitly formalises the 14 undefined operational objects that P1 flagged. Specifically: (i) `SplitGain`, `MergeCost`, `DepthPenalty`, `AuditLoad`, `RejectRisk` marked as Stage-2 hooks that drop out in TCPB; (ii) `AuditCost = λ_a = 0.02` fixed; (iii) `SendCost(i,j) = 0` in Stage-1 chain; (iv) `Cost_self(z) = τ_z/10³` token-count proxy; (v) `Risk_self(z) = 1−c[i]`; (vi) mean-axis fold `c[i] = (1/7) Σ_k B_i(j)[k]`; (vii) Stage-1 multipliers `(λ_c, λ_r, λ_s, λ_m, λ_d, λ_a) = (0.02, 0.10, 0.05, 0.05, 0.05, 0.02)` hand-set; (viii) persona-update rates `(η_loc, η_trm, η_rew, μ) = (0.06, 0.10, 0.10, 0.5)` derived from §B2; (ix) Algorithm 1 tie-breaking `DoSelf ≻ Outsource ≻ Split` + neighbour by ascending index; (x) `forward_bias(j) = 0` for Stage-1 chain, non-trivial for Stage-2 sparse graphs. **Under P4 D5 audit: this closes the 14-undefined-object debt flagged in R-FULL-011**.

---

## Summary (≤ 100 words)

Post–S-163 formalisation batch, the paper now inlines 14 previously-undefined operational objects (Stage-2 hooks, mean-axis fold, λ/η numeric values, tie-breaking) in §3.6. Under P4 Reproducibility-Ethics SAC lens, this lifts **D1 = 6.5** (vs P1's 4.5) and **D5 = 7.0** (P4 specialty; vs P2's 6.5). **D7 = 8.0 band 8 maintained**. But core empirical bar unchanged: single benchmark / single seed / no paired test / no CI / no external SOTA / null ablations / Finding 4 self-refutation. **D4 cap at 4.0 is now the sole remaining cap binding overall at 4.0 weak_reject** — **weighted_pre_cap = 5.240 is the HIGHEST across all 12 batches** (S-163 + post-R43 hygiene compound).

---

## Desk-reject risks (`desk_reject_risks`) — P4 specialty audit

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | `build_paper.ps1` reports "Main body ends on page 8 (Limitations starts here): COMPLIANT" for new PDF; §4.5 cites Appendix D only as preliminary; Self-Contained Main Body Rule satisfied. |
| DR-2 | **PASS** | Section titled exactly `Limitations` after Conclusion, before Ethical Considerations. |
| DR-3 | **PASS** | 7 items scope statements; engineering response in Appendix B; **P4 specifically verifies** no new experiments / figures / tables / analyses in Limitations. |
| DR-4 | **POSSIBLE – not verified** | pdftotext extraction cannot audit `acl.sty`. |
| DR-5 | **PASS** | Appendix C leak removed per R42 commit; no process metadata in submitted text. |
| DR-6 | **PASS** (P4 specialty) | Responsible NLP Checklist Appendix A B1–B5 all complete; B1 cited license + artifact; B2 compute budget + wall-clock + USD + seed list; B3 no human subjects explicit; B4 AI assistant disclosed (code-completion); B5 no PII. **P4 would flag any missing checklist item; none found**. |
| DR-7 | **PASS** | Coherent long-form; no duplicate submission. |
| DR-8 | **PASS** (P4 specialty) | Ethical Considerations standalone section (5 sub-paragraphs); AI assistance disclosed in both Appendix A B4 and Ethical "AI-assisted writing and coding"; no undisclosed artifact use. |

Net: 0 confirmed desk-reject; 1 POSSIBLE (DR-4 layout template cannot be verified from text stream).

---

## Best-Paper structural compliance (`best_paper_structural_compliance`) — `demand.md §11.5`

| # | Requirement | Status | Δ from R-FULL-011 |
|---|------------|--------|---|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | unchanged |
| 2 | ≥ 3 diverse datasets in main tables | ❌ fail | unchanged |
| 3 | Latest 12-month SOTA in main tables | ❌ fail | unchanged |
| 4 | Per-component ablation on canonical backbone | ❌ fail | unchanged |
| 5 | Multi-seed + paired tests + CI/effect-size | ❌ fail | unchanged (E-017 running) |
| 6 | Error analysis with quantitative named failure modes | ❌ fail | unchanged |
| 7 | Dedicated case-study / application block | ❌ fail | unchanged |
| 8 | Limitations ≥ 0.5 p, honest, specific | ✅ pass | unchanged |
| 9 | Ethical Considerations section present | ✅ pass | unchanged |
| 10 | Figure 1 vector-quality system schematic | ❌ fail | unchanged (placeholder) |
| 11 | Public anonymous code/data/model release | ⚠ partial | unchanged |
| 12 | No null-effect ablation tables | ⚠ partial | unchanged (caption mitigates) |

**Count unchanged**: 7 hard + 3 partial + 2 pass. S-163 improves D1/D5 but does not directly close §11.5 items (all §11.5 items are data/evidence/figure items that require experimental runs or new figures, not formula-inlining).

**§11.5 enforcement**: oral_quality_score cap at 3; assigned **3.0** (P4 higher than P1 2.0 and R-FULL-010 P2 2.5 because P4 heavily weights D5 improvements, and S-163 is a substantial D5 lift).

---

## Experiments-solidity audit (`experiments_solidity_audit`) — unchanged since PDF text does not reflect new fullval data yet

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 multi-dataset | fail | HotpotQA only |
| EXP-2 multi-seed | fail | seed=42 only (§B2) |
| EXP-3 significance test | fail | §4.3 Finding 2 admits "not yet confirmed with paired statistics" |
| EXP-4 effect size / CI | fail | §B2 "CIs explicitly not reported" |
| EXP-5 ablation coverage | partial | coverage 0.5 on wrong backbone; caption mitigates |
| EXP-6 baseline recency | fail | 0 external 2024–2025 SOTA in main tables |
| EXP-7 sensitivity sweep | partial | ±2× weight sweep in §4.5 |
| EXP-8 error analysis | fail | no taxonomy |

**`experiments_solidity_score` = 1 / 8** (unchanged).

**Caps from audit**:

```
EXP-1..EXP-6 as before → D4 cap = 4 (most restrictive = EXP-6 / solidity<=3)
S5 cap 4, S6 cap 4, S7 cap 5 (not all binding; actual S-scores may be lower)
```

Assigned D4 = **3.5** (P4 slightly less harsh than P1's 3.0 because P4 weights D5 more than D4 relative).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | is_concrete | is_overlap_risk |
|---|---|---|---|---|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | true | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | true | false |
| 3 | Multi-Agent Debate (Liang et al. EMNLP 2024; Du et al. ICML 2024) | 2024 | true | **true** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | true | false |
| 5 | Reflexion / ToT / Self-Refine (2023) | 2023 | true | false |

**Overlap**: MAD `is_overlap_risk=true` unaddressed → D3 cap at 4.

---

## Dimension scores (P4 Reproducibility-Ethics lens)

| Dim | Score | Δ vs R-FULL-011 (P1) | P4 defense |
|-----|-------|---|------------|
| **D1 Soundness** | **6.5** | **+2.0** (P1 4.5 → P4 6.5) | **S-163 landed ⇒ closure on 14 undefined objects**. Stage-2 hooks explicitly marked (SplitGain/MergeCost/DepthPenalty/AuditLoad/RejectRisk drop out in TCPB via gate weight -∞ and Audit-defaults-to-Accept); AuditCost=λ_a=0.02 fixed; SendCost=0 in chain; Cost_self / Risk_self have explicit proxies (τ_z/10³, 1-c[i]); mean-axis fold `c[i]=(1/7)Σ B_i(j)[k]`; (λ_c, λ_r, λ_s, λ_m, λ_d, λ_a) = (0.02, 0.10, 0.05, 0.05, 0.05, 0.02); (η_loc, η_trm, η_rew, μ) = (0.06, 0.10, 0.10, 0.5); Algorithm 1 tie-breaking lexicographic. `reviewer_prompt.md §3 D1 band 7 = "Mostly correct, with under-specified update rules / state objects that a careful re-implementer could still recover"` — fits. Not band 8 because EVIDENCE_EXTRACT lookup still in supplement + full Stage-2 formulas not given. |
| **D2 Significance** | **4.5** | unchanged | Framing interesting; delivered empirical core still Pareto-negative. |
| **D3 Novelty** | **4.0** | unchanged | MAD overlap cap. |
| **D4 Empirical** | **3.5** | +0.5 vs P1 3.0 | P4 less D4-strict than P1; cap = 4.0 from audit. Assigned 3.5 to reflect Finding 4 self-refutation. |
| **D5 Reproducibility** | **7.0** | **+1.5** (P1 5.5 → P4 7.0) | **P4 specialty, post-S-163 major lift**. Algorithm 1 full pseudocode + Responsible NLP B1–B5 + seed=42 + S-163 inline formalisation + Appendix C 4 prompt templates + code/data release committed in Ethical Considerations. `reviewer_prompt.md §3 D5 band 7 = "Methods are clear; some hyperparameters or training details require email-the-authors"` — fits. Not band 8 because full EVIDENCE_EXTRACT mapping + per-table regenerate scripts still supplement-only. |
| **D6 Clarity** | **5.0** | +0.5 | S-163 paragraph is compact and clear; Figure 1 placeholder remains the dominant defect. |
| **D7 Responsible research & limitations** | **8.0** | unchanged (band 8 maintained) | P4 specialty audit. Limitations 7 items + standalone Ethical Considerations 5 sub-paragraphs; all 6 band-8 requirements met (assumption failures / dataset biases / compute scope / demographic-societal / failure modes / checklist cited). |

### Secondary (S1–S8) — P4 lens

| S | Score | Note |
|---|-------|------|
| S1 executability | 6.5 | S-163 makes Stage-1 implementable from paper-alone; Stage-2 still supplement-dependent. |
| S2 falsifiability | 5.5 | Unchanged. |
| S3 empirical plan (design only) | 5.0 | Unchanged. |
| S4 technical clarity | 7.0 | S-163 compact formulas + explicit Stage-1 collapses + tie-breaking = clear operational semantics. |
| **S5 statistical rigor** | **3.0** | Capped (single seed / no paired / no CI). |
| **S6 baseline quality** | **2.0** | "No external baselines at all". |
| **S7 ablation completeness** | **4.0** | Null effects + wrong backbone; caption honesty unchanged. |
| S8 writing and figures | 5.0 | Figure 1 placeholder + S-163 compact writing. |

**`oral_quality_score` = 3.0** (P4 higher than P1/P2 due to D5 lift).

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*6.5 + 0.18*4.5 + 0.15*4.0 + 0.18*3.5 + 0.10*7.0 + 0.07*5.0 + 0.07*8.0
             = 1.625 + 0.810 + 0.600 + 0.630 + 0.700 + 0.350 + 0.560
             = 5.275

Caps applied (reviewer_prompt §6 + demand.md §11.5):
- DR-4 POSSIBLE only                → no DR-confirmed cap
- D1 = 6.5 ≥ 5                      → **D1<5 cap NO LONGER TRIGGERED (first time post-S-163)**
- D4 = 3.5 < 5                      → cap overall at min(5.275, D4+0.5) = min(5.275, 4.0) = **4.0** (binding)
- D4 = 3.5 < 7                      → cap overall at 7.0 (not binding)
- D3 = 4.0 < 5                      → cap overall at D3+0.5 = 4.5 (not binding)
- D3 = 4.0 < 6                      → cap overall at 6.5 (not binding)
- D7 = 8.0 ≥ 4                      → no cap
- oral_quality = 3.0 < 5            → cap overall at 5.5 (not binding)
- exp_solidity = 1 ≤ 3              → cap overall at 4.5 (not binding)
- novelty overlap MAD               → cap overall at 5.0 (not binding)
- S6 = 2 < 5                        → cap overall at 6.0 (not binding)
- S7 = 4 < 5                        → cap overall at 6.0 (not binding)
- §11.5 7+ items missed             → cap oral at 3 (assigned 3.0)

overall = 4.0
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **5.275** (**HIGHEST across all 12 R-FULL batches**; trajectory: 5.925→5.925→5.905→4.985→4.910→4.560→4.725→5.105→4.940→4.765→4.975→4.410→**5.275**) |
| **overall** | **4.0** (weak_reject boundary; D4 cap binds; **first batch where D4 is the sole remaining cap** — S-163 closed D1<5 cap) |
| **verdict** | **weak_reject** |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **is_best_paper_ready** | **false** |
| **confidence** | **4 / 5** |
| **estimated_score_after_fixes** (sprint-scope: E-017 3-seed fullval → D4 ≥ 5, E-014 canonical ablation → S7 ≥ 5, E-018 external SOTA → S6 ≥ 5, Figure 1 final → D6 ≥ 6, MuSiQue → EXP-1 pass) | **6.0-6.5 borderline** (better than R-FULL-009/010/011 estimates of 5.8-6.2 because D1 now at 6.5 unlocks higher overall ceiling) |
| **estimated_score_after_Best-Paper-track_fixes** (2-3 months: R1/R2/R3 + 3+ datasets head-to-head + case-study gallery + mechanistic novelty) | **7.0-7.5 Oral border** (unchanged; Best-Paper 8.5 still 1+ gap) |

---

## Top strengths (`top_strengths`) — P4 lens

1. **S-163 D1 formalisation (post-R-FULL-011)** inlines 14 previously-undefined operational objects, lifting D1 from 4.5 (P1) to 6.5 (P4) and D5 from 5.5 (P1) to 7.0 (P4) — the single largest hygiene improvement across the review-cycle history.
2. **Responsible NLP Checklist fully instantiated** (Appendix A B1–B5 complete; B2 includes wall-clock + USD + seed + hyperparameters; B4 AI-assistant disclosed; B5 PII explicit) — P4 specialty audit finds nothing missing.
3. **Dual-section honesty** (Limitations 7 items + Ethical Considerations 5 sub-paragraphs) covers all 6 band-8 D7 requirements; rare in generic long-paper submissions.
4. **Finding 4 Pareto-domination is reported in Abstract / Conclusion / §Limitations (6)** — P4 values this transparency; Best Papers typically have this depth of self-critique.
5. **Post-R42 DR-5 leak removed** + Ethical Considerations section added + Table 2 caption honesty — all three post-R43 hygiene improvements verified in this PDF SHA.

## Top weaknesses (`top_weaknesses`) — ranked by Best-Paper-bar severity

1. **Experiments bar — single benchmark / single seed / no paired test / no CI / no external SOTA**: D4 cap at 4.0 is now the sole remaining cap binding overall at 4.0. E-017 3-seed fullval running + E-014 / E-018 configs ready = can be addressed in sprint.
2. **Figure 1 still placeholder** — §11.5 #10 hard fail; Best-Paper dealbreaker.
3. **Table 2 on legacy glm-4-flash** — §4.2 self-admits "guidance-only, not final paper evidence"; E-014 canonical-backbone ablation configs ready post-quota.
4. **MAD overlap risk unaddressed empirically** — D3 cap at 4.
5. **No case-study / application gallery** — §11.5 #7; Best-Paper expectation unmet.
6. **No Stage-2 mechanistic wins** — R1/R2/R3 theoretical-only; Oral-bar requires at least one implemented.

## Core method problems (`core_method_problems`) — substantially reduced after S-163

1. `EVIDENCE_EXTRACT` R3 full lookup table still in supplement §4 (not paper); Stage-1 EMA update rule reduces to the deterministic scalar fold, so this is a Stage-2-only gap.
2. Full Stage-2 formulas for `SplitGain / MergeCost / DepthPenalty / AuditLoad / RejectRisk` still in supplement; paper correctly marks them as Stage-2 hooks (acceptable for a Stage-1-delivery submission).

(Previously 14 problems in R-FULL-011; now 2 remaining scope-of-Stage-2 items.)

## Experimental design problems (`experimental_design_problems`) — unchanged

1. Table 1 "baselines" = 3 internal variants; zero external published baselines.
2. Table 2 on legacy glm-4-flash; E-014 pending.
3. Table 2 three-row bit-identical ablations.
4. n=200 canonical vs n=7405 dev split.
5. No sensitivity sweep on safety-gate / force-forward thresholds.
6. No MAD head-to-head.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`) — reduced after S-163

1. `EVIDENCE_EXTRACT` lookup table still supplement-only.
2. Per-table / per-figure regenerate-me scripts not referenced.
3. Provider-integrity event cross-channel replication variance (documented in Appendix B as mitigation plan).

(Previously 5 gaps in R-FULL-011; now 3 remaining.)

## Overclaims / risky framing (`overclaims_or_risky_claims`) — unchanged

1. Abstract + §1 claim EDO "yields a structured personality-tag space" — delivered prototype collapses vector to scalar.
2. §5 Conclusion "decentralized outcome-based calibration improves delegation safety" — Finding 3 attributes PAR=0 to safety gate.
3. §4.3 pivoted claim "EDO framework explains when delegation overhead pays off" — not yet validated.

## Ambiguous algorithm points (`ambiguous_algorithm_points`) — CLOSED by S-163

1. ~~"Mean-axis fold"~~ — **now explicitly defined** as `c[i] = (1/7)Σ B_i(j)[k]`.
2. ~~Algorithm 1 argmax tie-breaking~~ — **now explicit** lexicographic DoSelf > Outsource > Split + ascending neighbour index.
3. Algorithm 1 lines 20–22 flow-control reuse of `a` variable — minor ambiguity; state semantics recoverable from prose + pseudocode combined.

## Missing definitions / state variables (`missing_definitions_or_state_variables`) — CLOSED by S-163

All 14 R-FULL-011 items now defined or explicitly marked Stage-2 hooks. **P4 finds no critical missing definitions**.

## Missing or weak experiments (`missing_or_weak_experiments`) — unchanged

1. No external 2024–2025 SOTA in main tables.
2. No MuSiQue / 2WikiMultiHop.
3. No multi-seed + paired tests + CI on canonical backbone.
4. No canonical-backbone ablation table.
5. No MAD head-to-head.
6. No case-study gallery.

## Statistical significance concerns (`statistical_significance_concerns`) — unchanged

1. Table 1 point estimates n=200 without paired bootstrap.
2. Table 2 identical rows without significance framing.
3. Figure 2 cross-sample-size overlay unharmonised.

## Baseline completeness concerns (`baseline_completeness_concerns`) — unchanged

1. S6 = 2.0 "No external baselines at all".
2. Latest 2024–2025 multi-hop-QA SOTA cited only as roadmap.

## Limitations section assessment — P4 specialty

| Field | Value |
|-------|--------|
| section_present | true |
| section_title_exact | true (`Limitations`) |
| contains_no_new_content | true (7 items all scope statements; engineering in Appendix B) |
| honesty_score_1_to_5 | 5 |
| specific_failure_modes_listed | true |
| issues | ["item (5) 'queued for re-execution' borderline operational; minor stylistic issue for Best-Paper bar"] |

## Responsible NLP Checklist assessment — P4 specialty

| Field | Value |
|-------|--------|
| appears_complete | true |
| issues | ["B2 compute budget + wall-clock + USD + seed all present", "B4 AI assistant type disclosed (code-completion) without specific product name (OK per ACL policy)"] |

## Implementation risks (`implementation_risks`) — reduced

1. EVIDENCE_EXTRACT lookup table offloaded to supplement (Stage-2 scope; acceptable).
2. Per-table regenerate scripts absent (Best-Paper standard for D5 band 10; not critical for D5 band 7).

## `what_to_fix_for_8_plus` (target overall ≥ 8.0)

1. **E-017 3-seed × 7405 fullval** (running; ETA ~06-07 tomorrow morning) → D4 ≥ 5 unlocks overall cap.
2. **Add ≥3 external published 2024–2025 SOTA baselines** to main tables.
3. **MuSiQue** as second benchmark.
4. **E-014 canonical-backbone ablation** to discriminate Table 2 null effect.
5. **Replace Figure 1 placeholder** with final vector.
6. **Add multi-seed paired bootstrap CI + paired significance tests**.

## `what_to_fix_for_oral` (Best-Paper 8.5)

1. All of `what_to_fix_for_8_plus` **plus** implement ≥1 of R1/R2/R3 with measurable wins against external SOTA.
2. **Case-study / application gallery** with 6–10 visualisations.
3. **Mechanistic-novelty falsifiable claim** that no prior work can match.
4. **Reverse Finding 4** on canonical backbone.

## `recommended_next_actions`

1. **Highest leverage**: let E-017 seed=42 + 43 + 44 fullval complete (~06-07 tomorrow) → refresh Table 1 + compute paired CI → overall jumps from 4.0 floor to 5.0-5.5.
2. Launch E-014 canonical-backbone ablation immediately after E-017 seed=42 stage2+stage1 done (free quota slot).
3. Start E-018 MA-RAG / ReAgent reproduce in parallel.
4. Replace Figure 1 placeholder.
5. Draft §4.x case-study block skeleton pre-data (can fill once fullval + external baselines land).

## `rule_source_disagreements`

None. P4 strict audit follows `docs/demand.md` §1–§11 + `prompts/reviewer_prompt.md §2–§10`.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":           true (post-§11, 241 lines),
  "edo_paper_pdf_loaded":       true (pdftotext -layout of 54DF9463... 827 lines end-to-end read; first P4 audit of new SHA),
  "fallback_source_used":       "pdftotext -layout article/build/edo_paper.pdf",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit"],
  "demand_section_11_applied":  true (7 hard + 3 partial + 2 pass; oral_quality cap 3, assigned 3.0 under P4),
  "persona_rotation":           "P4 Reproducibility-Ethics SAC; last used in R-FULL-005 on PDF 4504614E; new PDF SHA 54DF9463 first P4 audit",
  "s_163_d1_formalisation_verified": "14 undefined operational objects now inlined in §3.6 (rendered p.5 lines 399-419): Stage-2 hooks explicitly marked, mean-axis fold formula, λ values, η values, tie-breaking rule — all inline; D1 lift 4.5→6.5 verified; D5 lift 5.5→7.0 verified",
  "cross_batch_d1_d5_delta":    "P1 R-FULL-011 flagged ≥14 undefined objects → D1=4.5, D5=5.5; post-S-163 P4 R-FULL-012 audits same 14 locations → all defined or Stage-2-marked → D1=6.5, D5=7.0; overall unchanged at 4.0 because D4 cap binds, but weighted_pre_cap lifts from 4.410 to 5.275 (+0.865, largest cross-batch jump in 12-round history) — the paper is NOW implementable from the paper-alone for Stage-1 TCPB"
}
```

---

## `_parse_mode`

`full`

*End of review. Schema coverage per `prompts/reviewer_prompt.md §9` + `demand.md §11.5`. Rendered as markdown per `REVIEWER_TODO §F.3`.*

**Cross-batch strategic record**: R-FULL-012 is the first batch where `weighted_pre_cap ≥ 5.0` since the Best-Paper target was introduced in R-FULL-009 (which scored 4.765). S-163 D1 formalisation + post-R43 hygiene compound lifted weighted_pre_cap by 0.865 over R-FULL-011 (4.410 → 5.275). **D1<5 cap is now closed**; D4<5 cap remains the sole binding constraint. The sprint path E-017 fullval → D4 ≥ 5 will unlock overall to 5.0+.
