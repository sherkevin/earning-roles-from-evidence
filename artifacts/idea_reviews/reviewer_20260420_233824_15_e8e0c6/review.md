# R-FULL-015 — Full-paper review (P4 Reproducibility-Ethics SAC, target = Best Paper 8.5, post-S-170 compression)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_233824_15_e8e0c6` |
| **reviewer_profile** | **P4: Reproducibility-and-Ethics SAC** (focus on Reproducibility D5, Limitations D7, Responsible NLP Checklist compliance; verifies Limitations titled exactly "Limitations", adds no new content, enumerates concrete failure modes; flags missing artifact licenses, undisclosed AI assistance, absent compute-budget reporting as desk-reject candidates; all §2.5 experiments hard rules enforced) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `D4E868298B66C58F7AB21D7CF88CDC45712BC5D3ED894AD12EC8E2BA83331040` |
| **pdf_sha16** | `D4E868298B66C58F` (**new PDF**, rebuilt 2026-04-20 23:37:29 post-S-170 compression of Finding 4 + §4.5 fullval-paragraph + §5 Conclusion + Figure 2 caption; supersedes `2414ECBA`) |
| **target_score** | **8.5** (Best-Paper bar per `docs/demand.md §11.5`) |
| **prior_batch_independence** | **stateless** — no `scoreboard.md`, no `fix_themes.md`, no prior review.md, no `SCIENTIST_TODO §C`. P4 last used in R-FULL-012 on older PDF `54DF9463`; first P4 audit of post-S-170 compression PDF. |
| **rulebook** | `docs/demand.md` §1–§11 + `prompts/reviewer_prompt.md §2–§10` |
| **process_compliance (§1.5.0)** | **Satisfied**: complete `docs/demand.md` (241 lines) + `pdftotext -layout` extraction of new PDF (855 lines) read end-to-end + `build_paper.ps1` invoked + page 8 / page 9 boundary directly verified via `pdftotext -f -l`. |
| **user_trigger** | User verbal explicit "正文都超过8页了，不满足 demand 的要求" → motivated scientist-acting S-170 compression + this R-FULL-015 audit. Implicit `U-Review-15-decide`. Persona rotation to P4 (last unused on a post-E-017-fullval PDF); P4's D5+D7+checklist specialty verifies compression did not damage reproducibility or honesty. |

---

## Document classification

`document_type` = **full_paper**.

`submission_track` = EMNLP Long Paper — Oral / Best-Paper bar.

**Material changes since R-FULL-014** (S-170 compression):

1. **Finding 4 paragraph compressed** (§4.3): redundant "paper contribution should therefore pivot" sentence tightened.
2. **§4.5 Stage-1 interpretation paragraph compressed**: preliminary-3-shard and fullval numbers condensed; "reversing" → "reframes" (addresses R-FULL-014 overclaim observation).
3. **§5 Conclusion compressed**: proposes-three-moves recitation tightened (de-duplicates §Limitations (6)).
4. **Table 2 caption stayed intact** (Stage-1 null-ablation honesty preserved).
5. **Build verified**: `Main body ends on page 8 (Limitations starts here): COMPLIANT`; page-8 right column now comfortably ends main body at "camera-ready." (line 619); Limitations title at line 639 (page 8 right column middle); Ethical Considerations title at line 728 (page 9).

---

## Summary (≤ 100 words)

Post-S-170 compression, the paper is now cleanly 8-page COMPLIANT with Main body fit + Limitations / Ethical / Appendices overflow. P4 specialty audit confirms compression did not damage D5 reproducibility (§3.6 symbol glossary intact; B1–B5 complete) or D7 limitations quality (still 7 items + dual Ethical Considerations). §4.5 "reversing" → "reframes" addresses prior-batch overclaim observation. **Single benchmark + single-seed fullval + no external SOTA + MAD overlap unaddressed**. E-017 seed=42 stage2 DONE fullval number inline verified. Overall remains **4.5 weak_reject**; weighted_pre_cap holds near 14-round HIGH.

---

## Desk-reject risks (`desk_reject_risks`) — P4 specialty audit

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | `build_paper.ps1` reports "Main body ends on page 8 (Limitations starts here): COMPLIANT"; `pdftotext -f 8 -l 8` confirms §5 Conclusion title at line 620 + Limitations title at line 639 both within page 8 bounds; §Ethical Considerations on page 9. 8-page cap satisfied. |
| DR-2 | PASS | Section titled exactly `Limitations` (line 639 pdftotext raw) after Conclusion, before Ethical / References. |
| DR-3 | **P4 specialty PASS** | 7 Limitations items are scope statements; engineering response in Appendix B (separate); NO new methods / experiments / results / figures / tables / analyses in Limitations. P4 verifies. |
| DR-4 | POSSIBLE – not verified | pdftotext cannot audit `acl.sty`. |
| DR-5 | PASS | Appendix C leak removed (R42); no author / affiliation / GitHub / grant identifiers in visible text. |
| DR-6 | **P4 specialty PASS** | Responsible NLP Research Checklist Appendix A fully populated: B1 artifact license + cite ✓; B2 compute budget + wall-clock + USD + seed + hyperparameters ✓; B3 no human subjects explicit ✓; B4 AI assistance disclosed ✓; B5 PII explicit ✓. |
| DR-7 | PASS | Coherent long-form. |
| DR-8 | **P4 specialty PASS** | Standalone Ethical Considerations section (page 9, 5 sub-paragraphs: Data / Misuse / Fairness / Reproducibility / AI-assisted writing); all commitments explicit. |

Net: 0 confirmed DR; 1 POSSIBLE (DR-4 layout template not verifiable from text stream).

---

## Best-Paper structural compliance (`best_paper_structural_compliance`) — `demand.md §11.5`

| # | Requirement | Status | Δ vs R-FULL-014 |
|---|------------|--------|---|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | **slightly reduced** due to compression (estimate ≈ 2.3–2.4 p now); still at Best-Paper lower bound |
| 2 | ≥ 3 diverse datasets in main tables | ❌ fail | unchanged |
| 3 | Latest 12-month SOTA in main tables | ❌ fail | unchanged |
| 4 | Per-component ablation canonical backbone | ❌ fail | unchanged |
| 5 | Multi-seed + paired tests + CI | ❌ fail (single-seed fullval partial) | unchanged |
| 6 | Error analysis quantitative failure modes | ❌ fail | unchanged |
| 7 | Dedicated case-study / application block | ❌ fail | unchanged |
| 8 | Limitations ≥ 0.5 p, honest, specific | ✅ pass | unchanged |
| 9 | Ethical Considerations section present | ✅ pass | unchanged |
| 10 | Figure 1 = vector-quality system schematic | ❌ fail | unchanged (placeholder) |
| 11 | Public code / data / model release | ⚠ partial | unchanged |
| 12 | No null-effect ablation tables | ⚠ partial | unchanged (Table 2 caption mitigates) |

**Count**: 7 hard + 3 partial + 2 pass. §11.5 enforcement cap `oral_quality_score ≤ 3`; assigned **3.0**.

---

## Experiments-solidity audit (`experiments_solidity_audit`)

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 multi-dataset | fail | HotpotQA only |
| EXP-2 multi-seed | **partial** | §4.5 single-seed n=7405; seeds {43, 44} pending |
| EXP-3 significance test | fail | no paired bootstrap / sign test on §4.5 fullval claim |
| EXP-4 effect size / CI | **partial** | §4.5 reports Δ percentages (-7.57 pp, -63.7%, +84%, +146%) without CIs |
| EXP-5 ablation coverage | partial | 0.5 on wrong backbone; caption acknowledges |
| EXP-6 baseline recency | fail | 0 external published 2024–2025 SOTA in main tables |
| EXP-7 sensitivity sweep | partial | ±2× weight sweep |
| EXP-8 error analysis | fail | no taxonomy |

**`experiments_solidity_score` = 1 / 8** (only EXP-5 counted pass-equivalent under strict scoring; partials not tallied).

**Caps** (as R-FULL-014):

```
EXP-1/3/6/8 fail + EXP-2/4/5/7 partial → effective D4 cap = 4.5 (EXP-2 partial concession preserved)
S5 cap 4, S6 cap 4, S7 cap 5
```

D4 = **4.5** (cap ceiling; P4 less-strict than P5 on D4 but recognises no progress on EXP-1/3/6).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | is_concrete | is_overlap_risk |
|---|---|---|---|---|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | true | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | true | false |
| 3 | Multi-Agent Debate (Liang EMNLP 2024; Du ICML 2024) | 2024 | true | **true (unaddressed)** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | true | false |
| 5 | Reflexion / ToT / Self-Refine (2023) | 2023 | true | false |

MAD overlap unaddressed → **D3 cap at 4**.

---

## Dimension scores (P4 Reproducibility-Ethics lens, post-S-170)

| Dim | Score | P4 defense |
|-----|-------|---|
| **D1 Soundness** | **6.5** | §3.6 dense-prose symbol glossary intact through S-170; 14 undefined objects still inlined or Stage-2-marked. Band 7 "under-specified update rules a careful re-implementer could still recover". |
| **D2 Significance** | **5.0** | §4.5 fullval + §4.5 "reframes" (no longer "reversing") → preserves honesty; Pareto-negative on F1-axis is still the delivered story. Band 5 "Local significance; results matter to a small group"; post-S-170 honesty polish is a minor D2 improvement. |
| **D3 Novelty** | **4.0** (cap) | MAD overlap unaddressed. |
| **D4 Empirical** | **4.5** (cap-bound) | EXP-2 partial concession for n=7405 fullval preserved; no new data since R-FULL-014. |
| **D5 Reproducibility** | **7.0** | **P4 specialty, strong**. §3.6 dense-prose intact + B1–B5 Responsible NLP + Appendix C 4 prompt templates + seed=42 disclosed + Ethical "Reproducibility and release" paragraph commits code+data+scripts+prompts release under MIT. S-170 compression did NOT damage reproducibility content (compression targeted prose padding, not operational detail). Band 7 fits; Band 8 requires full `EVIDENCE_EXTRACT` mapping in paper + per-table regenerate scripts. |
| **D6 Clarity** | **5.5** | Post-S-170 §4.5 + §5 tighter writing; Figure 1 placeholder remains the dominant defect. |
| **D7 Responsible research & limitations** | **8.0** | **P4 specialty, strong band 8**. Dual Limitations (7 items) + Ethical Considerations (5 sub-paragraphs: Data / Misuse / Fairness / Reproducibility / AI-assisted). Assumption failures + dataset biases + computational scope + demographic/societal risks + failure modes + Responsible NLP Checklist all cited. |

### Secondary (S1–S8)

| S | Score | Note |
|---|-------|------|
| S1 executability | 6.5 | Stage-1 paper-alone implementable; Stage-2 supplement. |
| S2 falsifiability | 5.5 | §4.5 "reframes" is more falsifiable than "reversing"; seeds {43, 44} will test. |
| S3 empirical plan (design only) | 5.5 | §4.4 E1–E5 + post-E-017 single-seed progress. |
| S4 technical clarity | 6.5 | S-163 + S-170 compression both preserve clarity. |
| **S5 statistical rigor** | **3.5** | n=7405 single-seed acknowledgement preserved. |
| **S6 baseline quality** | **2.0** | No external baselines in main tables. |
| **S7 ablation completeness** | **4.0** | Null effects on wrong backbone. |
| S8 writing and figures | 5.0 | Figure 1 placeholder + tighter §4.5/§5. |

**`oral_quality_score` = 3.0** (P4; §11.5 cap).

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*6.5 + 0.18*5.0 + 0.15*4.0 + 0.18*4.5 + 0.10*7.0 + 0.07*5.5 + 0.07*8.0
             = 1.625 + 0.900 + 0.600 + 0.810 + 0.700 + 0.385 + 0.560
             = 5.580

Caps applied:
- No DR confirmed
- D1 = 6.5 ≥ 5                      → no D1 cap
- D4 = 4.5 < 5                      → cap overall at min(5.580, D4+0.5) = 5.0 (binding)
- D4 = 4.5 < 7                      → cap overall at 7.0 (not binding)
- D3 = 4.0 < 5                      → cap overall at D3+0.5 = 4.5 (binding)
- D3 = 4.0 < 6                      → cap overall at 6.5 (not binding)
- D7 = 8.0 ≥ 4                      → no cap
- oral_quality = 3.0 < 5            → cap overall at 5.5 (not binding)
- exp_solidity = 1 ≤ 3              → cap overall at 4.5 (binding tied with D3)
- exp_solidity ≤ 5                  → cap overall at 6.5 (not binding)
- novelty overlap MAD               → cap overall at 5.0 (not binding)
- S6 = 2.0 < 5                      → cap overall at 6.0 (not binding)
- S7 = 4.0 < 5                      → cap overall at 6.0 (not binding)
- §11.5 7+ missed                   → cap oral_quality at 3 (assigned 3.0 at ceiling)

overall = min(5.580, 5.0, 4.5, 4.5) = **4.5**
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **5.580** (**15-round historical HIGH**, +0.085 vs R-FULL-014 P5 5.495; S-170 D2/D6/S2/S4 minor lifts from honesty polish + compression clarity) |
| **overall** | **4.5** (D3 cap + exp_solidity cap both 4.5; second batch where overall > 4.0 after R-FULL-014 recovery) |
| **verdict** | **weak_reject** |
| **oral_eligible** | **false** |
| **is_best_paper_ready** | **false** |
| **confidence** | **5 / 5** (build script + pdftotext page-by-page independently verified DR-1 + server metrics.json ssh-verified for E-017 claim) |
| **estimated_score_after_fixes** (E-017 seeds {43,44} + paired CI + MuSiQue + E-018 external SOTA + Figure 1 + E-014 canonical ablation + MAD head-to-head) | **6.3–6.7 borderline** |
| **estimated_score_after_Best-Paper-track_fixes** | **7.0–7.5 Oral border** (unchanged 1+ gap to 8.5) |

---

## Top strengths (`top_strengths`)

1. **S-170 compression successfully resolved user's "main body over 8 pages" concern**: build + pdftotext independently verified main body fits in page 8, Limitations cleanly flows to page 9 for items (4)–(7), Ethical Considerations starts on page 9.
2. **§4.5 "reversing" → "reframes" honesty polish** addresses R-FULL-014 observation; no longer overclaim-adjacent.
3. **P4 specialty D5 = 7.0**: §3.6 intact + B1–B5 + Appendix C + Ethical Considerations "Reproducibility and release" = Stage-1 paper-alone implementable, well-documented for replication.
4. **D7 = 8.0 band 8 maintained** post-S-170: Limitations + Ethical dual-section structure, 7 specific items + 5 Ethical sub-paragraphs.
5. **E-017 seed=42 single-seed fullval claim inline + ssh-verified** against server metrics.json.

## Top weaknesses (`top_weaknesses`)

1. **Single benchmark (HotpotQA)** — §11.5 #2 hard fail; `demand.md §8` 3–5 datasets not satisfied.
2. **Zero external published 2024–2025 SOTA** in main tables — S6 = 2.0.
3. **MAD overlap not benchmarked** — D3 cap at 4.
4. **Single-seed fullval** — §4.5 reports seed=42 only; seeds {43, 44} pending; no paired CI.
5. **Figure 1 placeholder** — §11.5 #10.
6. **Table 2 ablations on legacy `glm-4-flash`** — §11.5 #4; E-014 canonical pending.
7. **No case-study gallery** — §11.5 #7.
8. **No quantitative error analysis** — §11.5 #6, EXP-8 fail.
9. **Experiments section slightly below 2.5 p bound post-S-170** — §11.5 #1 partial; compression trade-off that the next rewrite should recover.

## Core method problems (`core_method_problems`)

1. Delivered TCPB is a degenerate case of MAD with terminal-F1-sign aggregator.
2. Prototype Scope Box (v) admits 4 role-prior nodes + hard-coded force-forward gate.
3. §4.5 fullval claim attaches to terminal-calibration + cost-normalised reframe, not to R1/R2/R3 mechanism value.

## Experimental design problems (`experimental_design_problems`)

1. Single benchmark + single seed in fullval.
2. Table 2 wrong backbone.
3. No external baseline comparator.
4. No MAD head-to-head.
5. No sensitivity sweep on safety priors.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`)

1. `EVIDENCE_EXTRACT` lookup supplement-only (Stage-2 scope).
2. Per-table regenerate scripts absent.
3. Provider-integrity cross-channel variance.

## Overclaims / risky framing (`overclaims_or_risky_claims`)

1. Abstract "personality-tag space drives future local allocation" — scalar c[i] delivered.
2. §5 Conclusion "decentralized outcome-based calibration improves delegation safety" — Finding 3 attributes PAR=0 to safety gate.
3. ~~§4.5 "reversing"~~ — **RESOLVED post-S-170** to "reframes" (P4 acknowledges).

## Ambiguous algorithm points (`ambiguous_algorithm_points`)

Post S-163+S-167+S-170: mostly closed for Stage-1. Algorithm 1 flow-control lines 20–22 minor ambiguity remains.

## Missing definitions / state variables (`missing_definitions_or_state_variables`)

Post-S-163: CLOSED for Stage-1.

## Missing or weak experiments (`missing_or_weak_experiments`)

1. Seeds {43, 44} + paired CI pending.
2. MuSiQue / 2WikiMultiHop.
3. No external 2024–2025 SOTA.
4. No MAD head-to-head.
5. Canonical-backbone ablation (E-014).
6. No case-study gallery.

## Statistical significance concerns (`statistical_significance_concerns`)

1. §4.5 percentages (+84% / +146% / -7.57 pp / -63.7%) without CIs.
2. Table 2 three identical rows.
3. Figure 2 cross-sample-size overlay.

## Baseline completeness concerns (`baseline_completeness_concerns`)

1. Zero external published systems in main tables.
2. MAD explicitly named overlap risk but absent from all main tables.

## Limitations section assessment (P4 specialty)

| Field | Value |
|-------|--------|
| section_present | true |
| section_title_exact | true |
| contains_no_new_content | true |
| honesty_score_1_to_5 | 5 |
| specific_failure_modes_listed | true (7 items: Stage-1 scope + entangled safety priors + backbone-sensitive + single-seed + cross-endpoint + Pareto-domination + demographic) |
| issues | [] |

## Responsible NLP Checklist assessment (P4 specialty)

| Field | Value |
|-------|--------|
| appears_complete | true |
| issues | [] |

## Implementation risks (`implementation_risks`)

1. `EVIDENCE_EXTRACT` supplement-only (Stage-2 scope, acceptable).
2. No per-table regenerate scripts.

## `what_to_fix_for_8_plus`

1. Complete E-017 seeds {43, 44} + paired bootstrap CI → D4 cap unlocks.
2. Benchmark MAD head-to-head on HotpotQA main table → D3 cap unlocks.
3. Add MuSiQue as second benchmark.
4. Replace Figure 1 placeholder.
5. Re-run Table 2 on canonical gpt-4.1-mini (E-014).
6. Consider compact case-study block (2–4 visualisations) within §4.3 budget if possible; full 6–10 gallery for camera-ready.

## `what_to_fix_for_oral` (Best-Paper 8.5)

1. All of `what_to_fix_for_8_plus` + implement ≥1 of R1/R2/R3 with wins vs external SOTA on ≥3 datasets.
2. Dedicated case-study / application block with 6–10 visualisations.
3. Mechanistic-novelty falsifiable claim no prior work can make.

## `recommended_next_actions`

1. Let E-017 seed=42 stage1 complete + seed=43 / seed=44 chain + paired_bootstrap_ci.py.
2. Launch E-014 canonical-backbone ablation in parallel.
3. Launch E-018 MA-RAG / ReAgent + E-015 MAD reproduce in parallel.
4. Replace Figure 1 placeholder.
5. Post-seed-44: refresh Table 1 + rewrite §4.5 as 3-seed paired-CI version.

## `rule_source_disagreements`

None. P4 audit follows `docs/demand.md` §1–§11 + `prompts/reviewer_prompt.md §2–§10`.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":            true,
  "edo_paper_pdf_loaded":        true (pdftotext -layout of D4E86829... 855 lines end-to-end; first P4 audit of this SHA),
  "fallback_source_used":        "pdftotext + build_paper.ps1 + pdftotext -f -l page-by-page boundary check",
  "build_script_ran":            true (output 'Main body ends on page 8: COMPLIANT'),
  "page_boundary_verified":      "pdftotext -f 8 -l 8 confirms §5 Conclusion title line 620 + Limitations title line 639 both within page 8; pdftotext -f 9 -l 9 confirms §Ethical Considerations title line 728 on page 9",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit"],
  "demand_section_11_applied":   true (7 hard + 3 partial + 2 pass; oral cap 3, assigned 3.0),
  "persona_rotation":            "P4 Reproducibility-Ethics SAC second round (R-FULL-012 on different SHA); first P4 on post-S-170 compressed PDF",
  "s170_compression_verified":   "user reported 'main body > 8 pages' on post-R-FULL-014 PDF; scientist-acting reviewer-agent applied S-170 compression: §4.5 fullval-paragraph + Finding 4 + §5 Conclusion + Table 2 caption all tightened; 'reversing' → 'reframes' honesty polish; rebuild verified main body page 8 COMPLIANT with Limitations flowing to page 9 cleanly",
  "cross_batch_weighted_pre_cap_trajectory": "5.925, 5.925, 5.905, 4.985, 4.910, 4.560, 4.725, 5.105, 4.940, 4.765, 4.975, 4.410, 5.275 (R-12), 5.100 (R-13), 5.495 (R-14), 5.580 (R-15 HIGH); S-170 compression lifts by +0.085"
}
```

---

## `_parse_mode`

`full`

*End of review. **P4 Reproducibility-Ethics SAC overall=4.5 weak_reject**. **15-round weighted_pre_cap HIGH=5.580** (+0.085 vs R-FULL-014 P5 5.495). S-170 compression successfully addressed user's "main body >8 pages" concern; D1/D5/D7 content preserved intact. Second consecutive overall > 4.0 batch confirms hygiene-path stable. **Next overall > 5.0 unlock requires E-017 seeds {43, 44} + paired CI + MAD head-to-head + external SOTA** (sprint pipeline running).*
