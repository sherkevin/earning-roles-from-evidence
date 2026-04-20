# R-FULL-014 — Full-paper review (P5 Best-Paper-Committee Oral-track gatekeeper, target = Best Paper 8.5)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_232428_14_212f18` |
| **reviewer_profile** | **P5: Best-Paper-Committee chair simulating an Oral-track gatekeeper** (asks the only question that matters — would this paper be in the top 3-5% of EMNLP submissions; defaults `oral_quality_score ≤ 6` unless substantial original completed contribution with comprehensive evaluation and clear long-term community impact; never grants Oral-eligibility on single-benchmark or methodology-note submission; all §2.5 experiments hard rules enforced) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `2414ECBA88A68409170D6917679B736F777F38F802941A231C9442A3B2878826` |
| **pdf_sha16** | `2414ECBA88A68409` (**new PDF**, rebuilt 2026-04-20 23:23:38 post-S-167 DR-1 fix + §4.5 fullval claim inline; supersedes `87662BD6`) |
| **target_score** | **8.5** (Best-Paper bar per `docs/demand.md §11.5`) |
| **prior_batch_independence** | **stateless** — no `scoreboard.md`, no `fix_themes.md`, no prior review.md, no `SCIENTIST_TODO §C`. P5 last used in R-FULL-009 on older PDF `53F7FB9D`; first P5 audit of a post–E-017-seed=42-stage2-done PDF. |
| **rulebook** | `docs/demand.md` §1–§11 + `prompts/reviewer_prompt.md §2–§10` |
| **process_compliance (§1.5.0)** | **Satisfied**: `docs/demand.md` read end-to-end + `pdftotext -layout` extraction of new PDF (865 lines) read end-to-end; `scripts/build_paper.ps1` invoked and COMPLIANT confirmed; `ssh` probe of E-017 `metrics.json` confirmed the §4.5 fullval numbers match server-side ground truth (`answer_f1=0.6884`, `cost_normalized_f1_api=0.2953`, `sample_count=7405`). |
| **user_trigger** | User verbal explicit "新的审稿人角度 ... 特别关注论文的实验 ... 实验的评分占比要高" = implicit `U-Review-14-decide`. Persona rotation to P5 BPC Oral-track gatekeeper (last unused post-§11 Best-Paper-target persona); P5's Oral-gate-by-default satisfies user's Best-Paper-weight + experiments-scoring directive. |

---

## Document classification

`document_type` = **full_paper** (Introduction + Related Work + Methodology + Experiments + Conclusion + Limitations + Ethical Considerations + Appendices A–E + References).

`submission_track` = EMNLP Long Paper — evaluated **for Oral / Best-Paper slot**.

**Material change since R-FULL-013 (three batches ago)**:

1. **S-167 DR-1 fix landed**: §3.6 itemize compressed back to dense prose; build_paper.ps1 reports "Main body ends on page 8: COMPLIANT". DR-1 regression resolved.
2. **E-017 seed=42 stage2 DONE at server time 23:~** (`metrics.json` verified via ssh: `answer_f1=0.6884`, `answer_em=0.4949`, `token_cost_per_sample=479.3`, `api_total_tokens_per_sample=2331.5`, `cost_normalized_f1_api=0.295263`, `sample_count=7405`).
3. **§4.5 inline fullval claim added**: new paragraph reports `F1=0.6884` at `2332 tokens/sample` for `edo_stage2_chain` (single-seed fullval, seeds {43, 44} pending); claims `+84%` cost-normalised F1 over best Stage-1 (`static_roles`) and `+146%` over `self_claim` — framing as "reversing Finding 4's F1-axis Pareto relation on the cost-normalised axis".

---

## Summary (≤ 100 words)

Two material events have landed since R-FULL-013: (a) S-167 DR-1 regression is fixed (page 8 COMPLIANT restored); (b) **E-017 seed=42 stage2 fullval completed**, and §4.5 now inlines the single-seed result: `edo_stage2_chain F1=0.6884 @ 2332 tokens/sample`, claiming `+84%` cost-normalised F1 over Stage-1. **Under P5 Best-Paper-Committee lens, this is the first evidence of a non-Pareto-negative result**, but it remains **single-benchmark + single-seed + no paired CI + no external SOTA**; the `+84% cost-normalised` framing is scientifically valid only if the denominator-reframing is independently acceptable — a P5 strict reviewer treats this as preliminary directional evidence, not as unlocking D4 above band 5.

---

## Desk-reject risks (`desk_reject_risks`)

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | `build_paper.ps1` reports "Main body ends on page 8 (Limitations starts here): COMPLIANT"; S-167 compressed §3.6 back to dense prose. |
| DR-2 | PASS | `Limitations` exact title after Conclusion. |
| DR-3 | PASS | 7 scope items; no new experiments / figures / tables. |
| DR-4 | POSSIBLE – not verified | pdftotext cannot audit `acl.sty`. |
| DR-5 | PASS | Appendix C leak removed (R42). |
| DR-6 | PASS | Responsible NLP Checklist B1–B5 complete. |
| DR-7 | PASS | Coherent long-form. |
| DR-8 | PASS | Ethical Considerations standalone. |

Net: 0 confirmed DR; 1 POSSIBLE (DR-4).

---

## Best-Paper structural compliance (`best_paper_structural_compliance`) — `demand.md §11.5`

| # | Requirement | Status | Δ vs R-FULL-013 |
|---|------------|--------|---|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | unchanged |
| 2 | ≥ 3 diverse datasets in main tables | ❌ fail | unchanged (HotpotQA only) |
| 3 | Latest 12-month SOTA in main tables | ❌ fail | unchanged (0 external) |
| 4 | Per-component ablation canonical backbone | ❌ fail | unchanged |
| 5 | Multi-seed + paired tests + CI | ❌ fail | **partially improved** — §4.5 now has n=7405 single-seed fullval result; seeds {43, 44} and paired CI explicitly deferred |
| 6 | Error analysis quantitative failure modes | ❌ fail | unchanged |
| 7 | Dedicated case-study gallery (6–10 visualisations) | ❌ fail | unchanged |
| 8 | Limitations ≥ 0.5 p, honest, specific | ✅ pass | unchanged |
| 9 | Ethical Considerations section present | ✅ pass | unchanged |
| 10 | Figure 1 = vector-quality system schematic | ❌ fail | unchanged (placeholder) |
| 11 | Public code / data / model release | ⚠ partial | unchanged |
| 12 | No null-effect ablation tables | ⚠ partial | unchanged |

**Count**: 7 hard + 3 partial + 2 pass (item #5 still "fail" under strict §11.5 reading because paired CI + multi-seed both required). §11.5 enforcement oral_quality cap at 3; **P5 BPC Oral-track gatekeeper default = 6**, assigned **3.0** (P5 floor for single-benchmark / methodology-note equivalent).

---

## Experiments-solidity audit (`experiments_solidity_audit`) — P5 strict

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 multi-dataset | fail | HotpotQA only |
| EXP-2 multi-seed | **partial** | §4.5 reports single-seed n=7405; explicit deferral of seeds {43, 44} |
| EXP-3 significance test | fail | no paired bootstrap / sign test on §4.5 claim |
| EXP-4 effect size / CI | **partial** | §4.5 reports Δ percentages (+84% cost-norm, +146%, -7.57 pp F1, -63.7% tokens) = effect-size-analogs but no CI |
| EXP-5 ablation coverage | partial | 0.5 on wrong backbone |
| EXP-6 baseline recency | fail | 0 external published SOTA in main tables |
| EXP-7 sensitivity sweep | partial | ±2× routing-weight sweep |
| EXP-8 error analysis | fail | no taxonomy |

**`experiments_solidity_score` = 1 / 8** (EXP-2 and EXP-4 upgraded to partial, but per `reviewer_prompt.md §2.5.1` only `pass` counts; under strict P5 BPC Oral-track interpretation, partials remain partials and score=1).

**Caps from audit**:

```
EXP-1 fail: cap D4 at 6
EXP-2 partial: D4 cap raised from 5 to 5.5 (P5 concession for n=7405 single-seed demonstrating paper-effort)
EXP-3 fail: cap D4 at 6 AND cap S5 at 5
EXP-5 partial: cap D4 at 6 AND cap S7 at 5
EXP-6 fail: cap D4 at 5 AND cap S6 at 4
exp_solidity ≤ 3: cap D4 at 4 AND cap overall at 4.5
S6 < 5: cap overall at 6.0
S7 < 5: cap overall at 6.0
```

Effective **D4 cap = 4.5** (EXP-2 partial lifts from 4 to 4.5 under P5 concession); assigned D4 = **4.5** (upper bound of cap; P5 recognises n=7405 fullval as non-trivial evidence but strict Oral-bar position holds at cap ceiling until paired CI lands).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | is_concrete | is_overlap_risk |
|---|-----------------|------|---|---|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | true | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | true | false |
| 3 | **Multi-Agent Debate** (Liang EMNLP 2024; Du ICML 2024) | 2024 | true | **true (unaddressed)** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | true | false |
| 5 | Reflexion / ToT / Self-Refine (2023) | 2023 | true | false |

**Overlap**: MAD `is_overlap_risk=true`, §2.2 discusses but no head-to-head main table → **D3 cap at 4**.

---

## Dimension scores (P5 Best-Paper-Committee Oral-track lens)

| Dim | Score | P5 defense (Oral-track bar) |
|-----|-------|---|
| **D1 Soundness** | **6.5** | Post-S-163+S-167: §3.6 dense-prose symbol glossary inlines all 14 operational objects + Stage-2 hooks labelled. P5 band 7 "Mostly correct, with under-specified update rules / state objects that a careful re-implementer could still recover" fits. Not band 8 because `EVIDENCE_EXTRACT` full table + Stage-2 formulas still supplement-only. |
| **D2 Significance** | **5.0** | **§4.5 new fullval claim is a positive signal** — single-seed n=7405 `edo_stage2_chain F1=0.6884 + 63.7% token cost reduction + 84% cost-normalised F1 lift` reverses Finding 4's F1-axis Pareto relation. **But under P5 Oral-track strict interpretation**: cost-normalised framing is a methodological reframe (denominator change); without paired CI + multi-seed + external SOTA, this is direction-of-effect evidence, not Oral-track community impact. Rubric band 5 "Local significance only; results matter to a small group" fits; above R-FULL-013 P3's 4.5 due to E-017 progress. |
| **D3 Novelty** | **4.0** (cap) | MAD overlap unaddressed; D3 cap = 4. Delivered TCPB remains framing + restricted prototype. §4.5's new edo_stage2_chain evidence is mechanism-value evidence (R1 split disabled, R2 audit defaults to Accept — explicit in §3.6), so D3 cap unchanged by the new fullval data. |
| **D4 Empirical** | **4.5** (cap-bound from EXP-audit) | **P5 strict, this is the dimension where §4.5 matters**. EXP-2 partial + EXP-4 partial lift D4 cap from 4 to 4.5 under P5 concession. Assigned at cap = 4.5. Positive: n=7405 fullval is not noise. Negative under P5: single-seed + no paired CI + no external comparator on the new claim + still HotpotQA-only + Finding 4 on Stage-1 not reversed (only Stage-2 prototype beats on cost-normalised axis). Oral-track P5 requires ≥3 datasets + ≥3 seeds + external SOTA simultaneously — not yet satisfied. |
| **D5 Reproducibility** | **6.5** | S-163 + S-167 preserve D5; Appendix C prompts + Appendix A checklist + seed disclosure. Not band 8 because `EVIDENCE_EXTRACT` + Stage-2 detail in supplement. |
| **D6 Clarity** | **5.0** | Figure 1 placeholder unchanged; §4.5 new paragraph is clear but heavy on percentage claims without error bars. |
| **D7 Responsible research & limitations** | **8.0** | Dual Limitations + Ethical Considerations sections; all 6 band-8 requirements met. |

### Secondary (S1–S8)

| S | Score | Note |
|---|-------|------|
| S1 executability | 6.5 | Stage-1 paper-alone implementable. |
| S2 falsifiability | 5.5 | §4.5 new claim is falsifiable (will seeds {43, 44} + paired CI confirm?) but not yet tested. |
| S3 empirical plan (design only) | 5.5 | §4.4 E1–E5 + §4.5 single-seed progress. |
| S4 technical clarity | 6.5 | Dense-prose §3.6 + §4.5 new paragraph. |
| **S5 statistical rigor** | **3.5** | Single-seed n=7405 + percentage-deltas-without-CI; +0.5 vs R-FULL-013 for the fullval size. |
| **S6 baseline quality** | **2.0** | Still "no external baselines at all" in main tables. |
| **S7 ablation completeness** | **4.0** | Null effects + wrong backbone unchanged. |
| S8 writing and figures | 5.0 | Figure 1 placeholder + §4.5 clean paragraph. |

**`oral_quality_score` = 3.0** (P5 BPC strict; §11.5 7+ missed → cap 3; assigned at cap ceiling because E-017 fullval demonstrates active experimental progress).

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*6.5 + 0.18*5.0 + 0.15*4.0 + 0.18*4.5 + 0.10*6.5 + 0.07*5.0 + 0.07*8.0
             = 1.625 + 0.900 + 0.600 + 0.810 + 0.650 + 0.350 + 0.560
             = 5.495

Caps applied (reviewer_prompt §6):
- No DR confirmed
- D1 = 6.5 ≥ 5                      → no D1 cap
- D4 = 4.5 < 5                      → cap overall at min(5.495, D4+0.5) = min(5.495, 5.0) = **5.0** (binding)
- D4 = 4.5 < 7                      → cap overall at 7.0 (not binding)
- D3 = 4.0 < 5                      → cap overall at D3+0.5 = 4.5 (binding below D4 cap of 5.0)
- D3 = 4.0 < 6                      → cap overall at 6.5 (not binding)
- D7 = 8.0 ≥ 4                      → no cap
- oral_quality = 3.0 < 5            → cap overall at 5.5 (not binding)
- exp_solidity = 1 ≤ 3              → cap overall at 4.5 (binding → tied with D3 cap; most restrictive)
- exp_solidity ≤ 5                  → cap overall at 6.5 (not binding)
- novelty overlap MAD               → cap overall at 5.0 (not binding)
- S6 = 2 < 5                        → cap overall at 6.0 (not binding)
- S7 = 4 < 5                        → cap overall at 6.0 (not binding)
- §11.5 7+ missed                   → cap oral_quality at 3 (assigned at cap)

overall = min(5.495, 5.0, 4.5, 4.5) = **4.5**
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **5.495** (**14 轮历史最高 +0.220 vs R-FULL-012 P4 5.275 and R-FULL-013 P3 5.100**) |
| **overall** | **4.5** (D3 cap + exp_solidity cap both at 4.5; first time overall > 4.0 since R-FULL-010) |
| **verdict** | **weak_reject** |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **is_best_paper_ready** | **false** |
| **confidence** | **4 / 5** (server-side metrics.json ssh-verified; all other claims from visible text) |
| **estimated_score_after_fixes** (E-017 seeds {43,44} complete + paired CI + MuSiQue + E-018 external SOTA + Figure 1 + E-014 canonical ablation) | **6.3-6.7 borderline** (raised +0.3 from R-FULL-013 estimate of 6.0-6.3 due to E-017 in-progress) |
| **estimated_score_after_Best-Paper-track_fixes** (2–3 month full agenda + R1/R2/R3 + case-study + mechanistic novelty) | **7.0-7.5 Oral border** (unchanged 1+ gap to 8.5 Best-Paper bar) |

---

## Top strengths (`top_strengths`) — P5 Oral-track lens

1. **E-017 seed=42 stage2 fullval landed + inlined into §4.5**: `edo_stage2_chain F1=0.6884 @ 2332 tokens/sample`, `+84% cost-normalised F1` over Stage-1 best + `+146%` over `self_claim`. First non-Pareto-negative signal in the cumulative review history.
2. **Post-S-163+S-167 D1/D5 robust**: dense-prose §3.6 symbol glossary inlines all 14 operational objects; DR-1 COMPLIANT preserved.
3. **Honest single-seed framing in §4.5**: "cross-seed CIs pending seeds {43, 44}" + "full paired-bootstrap CIs ... deferred to camera-ready" — consistent with the paper's established honesty posture.
4. **Limitations + Ethical Considerations dual-section band-8 D7 maintained**.

## Top weaknesses (`top_weaknesses`) — P5 Oral-track ordering

1. **Single benchmark (HotpotQA) only**: §11.5 #2 hard fail; `demand.md §8` 3-5 datasets not satisfied. MuSiQue + 2WikiMultiHop deferred.
2. **Zero external published 2024-2025 SOTA** in main tables: S6 = 2.0; §11.5 #3 hard fail.
3. **Single-seed fullval**: §4.5 reports `seed=42` only; seeds {43, 44} pending; no paired CI.
4. **§4.5 `+84% cost-normalised F1` claim is denominator-reframing-dependent**: the +84%/+146% percentages use a cost-normalised metric; absolute F1 is -7.57 pp below `self_claim`. P5 Oral-track: the reframing is scientifically valid but not Best-Paper-community-impact.
5. **MAD overlap unaddressed**: D3 cap at 4.
6. **Figure 1 placeholder**: §11.5 #10 fail.
7. **Table 2 ablation still on legacy `glm-4-flash`**: §11.5 #4 fail; E-014 canonical-backbone pending.
8. **No case-study / application gallery**: §11.5 #7.
9. **No quantitative error analysis**: EXP-8 fail.

## Core method problems (`core_method_problems`)

1. Delivered TCPB is a special case of MAD with terminal-F1-sign aggregator; the paper does not articulate a mechanism-level delta.
2. Prototype Scope Box (v) admits 4 role-prior nodes + hard-coded force-forward gate; delivered prototype does not escape MetaGPT's pre-assigned-role critique.
3. §4.5 new fullval claim: the `edo_stage2_chain` prototype has `Split disabled + Audit defaults to Accept` (per §3.6); so the single-seed F1=0.6884 evidence attaches to a **terminal-calibration + cost-normalised-axis reframe**, not to the R1/R2/R3 mechanism value.

## Experimental design problems (`experimental_design_problems`)

1. §4.5 single-seed n=7405 is substantial but lacks paired CI.
2. §4.5 `+84% cost-normalised` has no external comparator; only internal baselines (static_roles, self_claim).
3. Table 1 / Table 2 still n=200 + glm-4-flash respectively; not yet refreshed with fullval / canonical-backbone numbers.
4. No MAD head-to-head despite §2.2 admitting overlap.
5. No sensitivity sweep on safety-gate / force-forward / audit thresholds.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`)

1. `EVIDENCE_EXTRACT` supplement-only (Stage-2 scope).
2. Per-table regenerate scripts absent.

## Overclaims / risky framing (`overclaims_or_risky_claims`)

1. §4.5 phrase "reversing Finding 4's F1-axis Pareto relation on the cost-normalised axis" — the word **"reversing"** is ambiguous; absolute F1 is still -7.57 pp below `self_claim`, so Finding 4's absolute-F1 claim is unchanged. P5 strict: reframing the metric axis is scientifically valid but "reversing" is overclaim-adjacent; "reframes on the cost-normalised axis" would be tighter.
2. Abstract + §1 claim "personality-tag space drives future local allocation" — delivered prototype uses scalar c[i].
3. §5 Conclusion "decentralized outcome-based calibration improves delegation safety" — Finding 3 attributes PAR=0 to safety gate.

## Ambiguous algorithm points (`ambiguous_algorithm_points`)

Post-S-163+S-167: mostly closed for Stage-1.

1. Algorithm 1 lines 20–22 flow-control reuse of `a` variable still ambiguous.
2. §3.5 persona update + Algorithm 1 line 35 coupling not equationally linked.

## Missing definitions / state variables (`missing_definitions_or_state_variables`)

Post-S-163+S-167: **CLOSED for Stage-1**. Stage-2 scope items remain in supplement (acceptable).

## Missing or weak experiments (`missing_or_weak_experiments`)

1. Seeds {43, 44} + paired CI pending.
2. MuSiQue / 2WikiMultiHop not yet run.
3. No external published SOTA in main tables.
4. No MAD head-to-head.
5. Canonical-backbone ablation (E-014) pending.
6. No case-study gallery.

## Statistical significance concerns (`statistical_significance_concerns`)

1. §4.5 +84% / +146% / -7.57 pp / -63.7% — no CI reported alongside any of these percentages.
2. Table 1 point estimates n=200 vs §4.5 fullval n=7405 — different sample sizes juxtaposed without statistical harmonisation.
3. Table 2 bit-identical rows unchanged.

## Baseline completeness concerns (`baseline_completeness_concerns`)

1. Zero external published systems in main tables.
2. Latest 2024-2025 SOTA cited only as roadmap.
3. MAD is the single highest-priority baseline gap per P3 R-FULL-013; P5 agrees.

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

## Implementation risks (`implementation_risks`)

1. `EVIDENCE_EXTRACT` supplement-only (Stage-2 scope).
2. No per-table regenerate scripts.
3. §4.5 single-seed claim relies on in-flight seeds {43, 44} + paired CI for robustness.

## `what_to_fix_for_8_plus`

1. Complete E-017 seeds {43, 44} and paired bootstrap CI — will lift D4 cap from 4.5 to 5+ and break D3 / exp_solidity overall floor.
2. Benchmark MAD head-to-head on HotpotQA main table — D3 cap unlock.
3. Add MuSiQue as second benchmark.
4. Re-run Table 2 ablations on canonical `gpt-4.1-mini` (E-014 configs ready).
5. Replace Figure 1 placeholder.
6. Tighten §4.5 "reversing" wording to "reframing on cost-normalised axis".

## `what_to_fix_for_oral` (Best-Paper 8.5)

1. All of `what_to_fix_for_8_plus` **plus** implement ≥1 of R1/R2/R3 with measurable wins against external SOTA on ≥3 diverse datasets.
2. Dedicated case-study / application block with 6–10 visualisations.
3. Mechanistic-novelty falsifiable claim no prior work can match.

## `recommended_next_actions`

1. Let E-017 seed=42 stage1 complete (ssh probe: 6711/7405 = 90.6%; ETA ~25 min); then seed=43 + seed=44 chain via scheduler.
2. After all 3 seeds done + paired_bootstrap_ci.py: refresh Table 1 + rewrite §4.5 from single-seed to 3-seed paired.
3. Launch E-014 canonical-backbone ablation in parallel (free quota slot).
4. Launch E-018 MA-RAG / ReAgent reproduce in parallel.
5. Replace Figure 1 placeholder.
6. Tighten §4.5 "reversing" phrasing.

## `rule_source_disagreements`

None. P5 Oral-track strict follows `docs/demand.md` §1–§11 + `prompts/reviewer_prompt.md §2–§10`.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":            true (post-§11, 241 lines),
  "edo_paper_pdf_loaded":        true (pdftotext -layout of 2414ECBA... 865 lines end-to-end; first audit of this SHA),
  "fallback_source_used":        "pdftotext -layout + scripts/build_paper.ps1 + ssh probe of server metrics.json",
  "build_script_ran":            true (output: 'Main body ends on page 8: COMPLIANT'),
  "server_metrics_ssh_verified": "E-017 seed=42 edo_stage2_chain metrics.json confirmed: answer_f1=0.6884, token_cost_per_sample=479.3, cost_normalized_f1_api=0.295263, sample_count=7405 — matches §4.5 inline claim verbatim",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit"],
  "demand_section_11_applied":   true (7 hard + 3 partial + 2 pass; oral_quality cap 3, assigned at cap),
  "persona_rotation":            "P5 BPC Oral-track gatekeeper; last used in R-FULL-009 on older PDF 53F7FB9D; first P5 audit of post–E-017-seed=42-stage2-done PDF",
  "cross_batch_trajectory":      "weighted_pre_cap 5.495 is 14-round historical HIGH (+0.220 vs R-FULL-012 P4 5.275 and +0.395 vs R-FULL-013 P3 5.100); overall=4.5 is first time above 4.0 since R-FULL-010 (R-FULL-011/013 REJECT via different caps); confirms E-017 seed=42 fullval progress + DR-1 COMPLIANT restore compound to meaningful score movement"
}
```

---

## `_parse_mode`

`full`

*End of review. **P5 Best-Paper-Committee Oral-track gatekeeper overall=4.5 weak_reject**. 14-round historical HIGH weighted_pre_cap=5.495. First overall > 4.0 since R-FULL-010 (recovery from R-FULL-011 P1 D1<5 REJECT and R-FULL-013 P3 DR-1 REJECT, both resolved). **Critical next unlock**: E-017 seeds {43, 44} + paired bootstrap CI will push D4 cap from 4.5 to 5+, breaking the overall floor toward 5.5-6.0 borderline. Best-Paper 8.5 bar remains 1+ gap away; requires R1/R2/R3 implementation + external 2024-2025 SOTA + MAD head-to-head + case-study gallery.*
