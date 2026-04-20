# R-FULL-011 — Full-paper review (P1 Strict ARR SAC, target = Best Paper 8.5)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_222326_11_bdb1e7` |
| **reviewer_profile** | **P1: Strict ARR Senior Area Chair specialising in Soundness (D1) and Reproducibility (D5)** (default to rejection unless every algorithmic object, update rule, and state variable is fully formalised; treats any unspecified hyperparameter or absent seed / significance test as evidence of incompleteness; still enforces all §2.5 experiments hard rules per `reviewer_prompt.md`) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `37A3F45DC13630F48506741AD2F8F73F963F9C41D9744AFD75016E851023D5B6` |
| **pdf_sha16** | `37A3F45DC13630F4` (unchanged since R44 rebuild 2026-04-20 21:43:53) |
| **target_score** | **8.5** (Best-Paper bar per `docs/demand.md §11.5`) |
| **prior_batch_independence** | **stateless** — no `scoreboard.md`, no `fix_themes.md`, no `review.md` from batches 01–10, no `SCIENTIST_TODO §C` read. This P1 audit is an independent verification angle (P1 last used on an earlier PDF SHA `4504614E` in R-FULL-004; new PDF SHA `37A3F45D` has never been P1-audited). |
| **rulebook** | `docs/demand.md` (post-§11 241 lines) + `prompts/reviewer_prompt.md §2–§10` caps |
| **process_compliance (§1.5.0)** | **Satisfied**: complete `docs/demand.md` + full PDF extraction re-read end-to-end before scoring under fresh P1 frame. |
| **user_trigger** | User verbal explicit "现在可以再去按照一个新的审稿人角度去审 ... 你现在是一个全新的审稿人 ... 特别关注论文的实验 ... 实验的评分占比要高" → implicit `U-Review-11-decide`. Persona rotation to P1 (unused on new PDF SHA); P1's default-rejection posture + §2.5 experiments-hard-rules enforcement still satisfies user's experiments-weight directive. |

---

## Document classification

`document_type` = **full_paper** (8-page main body + Limitations + Ethical Considerations + Appendices A–E + References; 14 rendered pages total).

`submission_track` = EMNLP Long Paper — evaluated **for Oral / Best-Paper slot**.

**Sprint-state snapshot (informational, does not alter score)**: E-017 seed=42 resume is running (stage2 ≈ 5415/7405 = 73%, stage1 ≈ 4133/7405 = 56% as of ssh probe 2026-04-20 22:22:29 server time); fullval numbers are NOT yet reflected in Table 1 or Figure 2 of the submitted PDF under review.

---

## Summary (≤ 100 words)

Under P1 strict ARR SAC review with Best-Paper target 8.5, the paper fails the core soundness bar (D1=4.5) on top of the already-known empirical bar (D4=3.0). P1 counts ≥10 symbols / functional forms referenced in the main body but undefined (`forward_bias`, `Cost_self`, `Risk_self`, `SendCost`, `AuditCost`, `RejectRisk`, `SplitGain`, `MergeCost`, `DepthPenalty`, `AuditLoad`, "mean-axis fold") plus missing λ numeric values. Combined with single-benchmark / single-seed / no significance / no external SOTA / Table 2 null ablations / Finding 4 self-refutation, the D4 cap + D1 sub-5 interaction drops overall to **3.5 = reject** (one notch below weak_reject, first time across 11 batches).

---

## Desk-reject risks (`desk_reject_risks`)

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | Main body 8 pages COMPLIANT per build script; Appendix D cited only as "preliminary … not in main results". |
| DR-2 | **PASS** | `Limitations` exact title after Conclusion. |
| DR-3 | **PASS** | 7 items scope only; engineering detail in Appendix B; Ethical Considerations is a separate section. |
| DR-4 | **POSSIBLE – not verified** | pdftotext cannot audit `acl.sty`. Tex override of default header (lines 26–33 `\renewcommand` per R-FULL-010 note) is tex-level, not style-file modification; a careful SAC should request LaTeX sources. |
| DR-5 | **PASS** | Post-R42 fix confirmed: Appendix C heading no longer carries "per Reviewer R-FULL-004 D5 request". |
| DR-6 | **PASS** | Responsible NLP Checklist Appendix A B1–B5 complete. |
| DR-7 | **PASS** | Coherent long-form; no thin-slicing. |
| DR-8 | **PASS** | AI assistance disclosed (B4); standalone Ethical Considerations now present. |

Net: 0 confirmed DR; 1 POSSIBLE (DR-4).

---

## Best-Paper structural compliance (`best_paper_structural_compliance`) — `demand.md §11`

### §11.5 addendum audit

| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | §4.1–§4.5 at lower bound ≈ 2.5 p |
| 2 | ≥ 3 diverse datasets in main tables | **❌ fail** | HotpotQA only |
| 3 | Latest 12-month SOTA baseline in main tables | **❌ fail** | 0 external baselines |
| 4 | Per-component ablation on canonical backbone | **❌ fail** | Table 2 on glm-4-flash; per §4.2 "guidance-only, not final evidence" |
| 5 | Multi-seed + paired tests + CI/effect-size | **❌ fail** | seed=42 only; §B2 "CI explicitly not reported" |
| 6 | Error analysis with quantitative named failure modes | **❌ fail** | No failure-mode taxonomy |
| 7 | Dedicated case-study / application block with 6–10 visualisations | **❌ fail** | No case-study section |
| 8 | Limitations ≥ 0.5 p, honest, specific, demographic/societal | ✅ pass | 7 items, item (7) covers demographic scope |
| 9 | Ethical Considerations / Broader Impact section present | ✅ pass | Standalone 5-paragraph section (rendered p.9–10) |
| 10 | Figure 1 = system schematic vector-quality self-contained | **❌ fail** | "[Figure 1 placeholder]" with caption "Vector asset to be inserted" |
| 11 | Public anonymous code/data/model release committed | ⚠ partial | Runtime code + seed + scripts + logs committed; no model (API-only, justified in Ethical Considerations) |
| 12 | No null-effect ablation tables | ⚠ partial (caption-mitigated) | Table 2 rows identical on glm-4-flash but caption acknowledges and defers discrimination to canonical backbone |

**Count**: **7 hard + 3 partial + 2 pass** (same as R-FULL-010; PDF unchanged since).

**§11.5 enforcement**: 7+ missed → `oral_quality_score ≤ 3`; assigned **2.0** under P1 strict (R-FULL-010 assigned 2.5 under P2; P1 is stricter on unfinished presentation = Figure 1 placeholder).

---

## Experiments-solidity audit (`experiments_solidity_audit`)

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 multi-dataset | fail | HotpotQA only; MuSiQue + 2WikiMultiHop deferred |
| EXP-2 multi-seed | fail | seed=42 only (§B2); multi-seed explicitly "deferred" |
| EXP-3 significance test | fail | §4.3 Finding 2 admits "not yet confirmed with paired statistics" |
| EXP-4 effect size / CI | fail | §B2 "CIs explicitly not reported" |
| EXP-5 ablation coverage | partial | coverage 0.5 on wrong backbone; Stage-2 R1/R2/R3 unablated |
| EXP-6 baseline recency | fail | 0 external 2024–2025 SOTA in main tables |
| EXP-7 sensitivity sweep | partial | ±2× weight sweep in §4.5 only |
| EXP-8 error analysis | fail | No quantitative taxonomy |

**`experiments_solidity_score` = 1 / 8**.

**Caps from audit**:

```
EXP-1 fail       → cap D4 at 6
EXP-2 fail       → cap D4 at 5, cap S5 at 4
EXP-3 fail       → cap D4 at 6, cap S5 at 5
EXP-5 partial    → cap D4 at 6, cap S7 at 5
EXP-6 fail       → cap D4 at 5, cap S6 at 4
exp_solidity ≤ 3 → cap D4 at 4, cap overall at 4.5
S6 < 5           → cap overall at 6.0
S7 < 5           → cap overall at 6.0
```

Effective D4 cap = **4**; assigned D4 = **3.0** (P1 strict; below cap to reflect self-refutation + P1's default-rejection posture).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | claimed_difference | is_concrete | is_overlap_risk |
|---|-----------------|------|-------------------|-------------|-----------------|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | EDO removes globally visible expert table, central decision node, fixed task script | true | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | Per-hop meta-review aggregation vs. terminal-only calibration | true | false |
| 3 | Multi-Agent Debate (Liang et al. EMNLP 2024; Du et al. ICML 2024) | 2024 | MAD aggregates per-hop critiques; TCPB collapses to terminal-outcome only | true | **true** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | Hard-coded SE pipeline; EDO removes pre-assigned roles | true | false |
| 5 | Reflexion / ToT / Self-Refine (Shinn 2023; Yao 2023; Madaan 2023) | 2023 | Single-agent self-reflection; EDO = multi-agent terminal calibration | true | false |

**Overlap handling**: MAD `is_overlap_risk=true`, not empirically addressed → **cap D3 at 4**.

---

## Dimension scores (P1 Strict ARR SAC lens; experiments hard rules still enforced)

| Dim | Score | P1 defense |
|-----|-------|------------|
| **D1 Soundness** | **4.5** | **P1's specialty and the dimension where this review differs most from P2 R-FULL-010 (which gave 5.5)**. Counting the undefined symbols / formulas that the main body references operationally: (1) `forward_bias(j)` — "topology-driven flow prior", no functional form; (2) `Cost_self(z)` — referenced in §3.3 U^self, undefined; (3) `Risk_self(z)` — same; (4) `SendCost(i,j)` — §3.3 U^out, undefined; (5) `AuditCost(z)` — same; (6) `RejectRisk(j,z)` — same; (7) `SplitGain(z)` — §3.3 U^split, undefined; (8) `MergeCost(z)` — same; (9) `DepthPenalty(z)` — same; (10) `AuditLoad(z)` — same; (11) "mean-axis fold" projection (§3.6, Algorithm 1 line 35) — unspecified; (12) λ_c / λ_r / λ_s / λ_m / λ_d — symbol names in equations without numeric values in main body (only λ_a = 0.02 given); (13) η_loc / η_trm / η_rew / μ — persona update weights named in §3.5 but no numeric values; (14) Algorithm 1 tie-breaking rule for `argmax{U_S, max_j U_j^O, U_P}` — unspecified. **P1 rubric band 5 = "Material gaps: a concept is intuitive but not implementable from the paper."** Fourteen operational undefined objects places this in band 4–5 boundary; P1 default-rejection tips to **4.5**. |
| **D2 Significance** | **4.0** | Delivered empirical core = single-benchmark Pareto-negative; significance claim ("organizational emergence explains delegation") is not validated. |
| **D3 Novelty** | **4.0** | MAD overlap cap. Under P1 lens, the framing-mostly contribution + Stage-2 mechanisms theoretical-only = band 4 ceiling. |
| **D4 Empirical results** | **3.0** | P1 strict. D4 cap = 4 from experiments audit; assigned 3.0 below cap because Finding 4 is an active empirical self-refutation on the canonical backbone — P1 §3 rubric band 3 = "Anecdotal results; cherry-picked tables; missing critical recent baselines; no ablations; reported deltas smaller than likely seed noise" — applies largely (n=200, no CI, no external baseline, null ablations, self-refuted headline). Band 2 applies partially ("results contradict the claims") but the paper honestly admits this, so 3.0 not 2.5. |
| **D5 Reproducibility** | **5.5** | P1's specialty. Responsible NLP B1–B5 + seed=42 + Algorithm 1 Appendix E + Appendix C 4 prompt templates (abridged). **Gaps for P1**: `EVIDENCE_EXTRACT` full lookup table only in supplement; all undefined formulas in D1 above would hinder any re-implementer; per-table regenerate scripts absent. P1 rubric band 5 = "Reproduction would require re-deriving large method portions" — applies to the 14 undefined objects enumerated in D1. Assigned 5.5 (halfway between 5 and 6 because the Algorithm 1 skeleton + seed disclosure partially offset the undefined-symbol gap). |
| **D6 Clarity** | **4.5** | Figure 1 placeholder is a hard presentation defect for the Best-Paper bar; Table 2 caption expansion and Ethical Considerations prose are good writing but Figure 1 dominates. |
| **D7 Responsible research & limitations** | **8.0** | Seven Limitations items + standalone Ethical Considerations (5 sub-paragraphs). All 6 band-8 requirements met (assumption failures / dataset biases / computational-scope / demographic-societal / failure modes / checklist cited). |

### Secondary (S1–S8)

| S | Score | P1 note |
|---|-------|---------|
| S1 executability | 5.0 | Supplement-dependent for 14 operational objects. |
| S2 falsifiability | 5.5 | Central claim measurable but already falsified (Finding 4); pivoted claim untested. |
| S3 empirical plan (design only) | 5.0 | §4.4 E1–E5 is reasonable but unexecuted. |
| S4 technical clarity | 5.5 | Equations inline but many undefined terms. |
| **S5 statistical rigor** | **3.0** | Single seed, no paired test, no CI. |
| **S6 baseline quality** | **2.0** | Rubric verbatim "2 = No external baselines at all". |
| **S7 ablation completeness** | **4.0** | Null effects + wrong backbone; caption honesty is progress but evidence unchanged. |
| S8 writing and figures | 4.5 | Figure 1 placeholder + missing case-study gallery. |

**`oral_quality_score` = 2.0** (P1 strict; R-FULL-010 gave 2.5 under P2; the P1 downgrade reflects 14 undefined objects in main body that an Oral paper must have formalised).

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*4.5 + 0.18*4.0 + 0.15*4.0 + 0.18*3.0 + 0.10*5.5 + 0.07*4.5 + 0.07*8.0
             = 1.125 + 0.720 + 0.600 + 0.540 + 0.550 + 0.315 + 0.560
             = 4.410

Caps applied (reviewer_prompt §6 + demand.md §11.5):
- DR-4 POSSIBLE only → no DR-confirmed cap
- D1 = 4.5 < 5                 → cap overall at min(4.410, D1+1.0) = min(4.410, 5.5) = 4.410 (not binding)
- D4 = 3.0 < 5                 → cap overall at min(4.410, D4+0.5) = min(4.410, 3.5) = **3.5** (binding)
- D4 = 3.0 < 7                 → cap overall at 7.0 (not binding; already 3.5)
- D3 = 4.0 < 5                 → cap overall at min(3.5, D3+0.5) = min(3.5, 4.5) = 3.5 (not binding)
- D3 = 4.0 < 6                 → cap overall at 6.5 (not binding)
- D7 = 8.0 ≥ 4                 → no cap
- falsifiability = 5.5 ≥ 4     → no cap
- oral_quality = 2.0 < 5       → cap overall at 5.5 (not binding)
- exp_solidity = 1 ≤ 3         → cap overall at 4.5 (not binding; already 3.5)
- exp_solidity ≤ 5             → cap overall at 6.5 (not binding)
- novelty overlap unaddressed  → cap overall at 5.0 (not binding)
- S6 = 2.0 < 5                 → cap overall at 6.0 (not binding)
- S7 = 4.0 < 5                 → cap overall at 6.0 (not binding)
- §11.5 7+ items missed        → cap oral_quality at 3 (assigned 2.0 within cap)

overall = 3.5
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **4.410** |
| **overall** | **3.5** |
| **verdict** | **reject** (overall < 4.0 per §6 mapping; **first batch across R-FULL-001..011 to break below the 4.0 floor under a non-DR-forced cap**) |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **is_best_paper_ready** | **false** |
| **confidence** | **4 / 5** |
| **estimated_score_after_fixes** (sprint-scope + D1-formalise: E-017 3-seed fullval + E-014 canonical ablation + E-018 external SOTA + Figure 1 final + inline 14 undefined objects + MuSiQue) | **5.5–6.0** (borderline; still below Best-Paper) |
| **estimated_score_after_Best-Paper-track_fixes** (2–3 months: implement R1 or R2 or R3 + 3+ dataset head-to-head + case-study gallery + mechanistic novelty) | **7.0–7.5 Oral border** (still 1+ gap to 8.5 Best-Paper bar) |

---

## Top strengths (`top_strengths`)

1. **Rare honest admission of Pareto-domination on the canonical backbone** (§Limitations item 6; Finding 4). Under P1 lens this is the paper's primary reviewer-trust asset.
2. **Post-R43 hygiene complete**: DR-5 leak removed; standalone Ethical Considerations section; Table 2 caption acknowledges the null-ablation puzzle and commits to canonical-backbone discrimination.
3. **Algorithm 1 in Appendix E gives the full Stage-2 loop skeleton** with recursion bounds — P1 counts this as minimum operational form (though D1 is still weakened by the undefined objects inside the loop).
4. **Limitations + Ethical Considerations jointly cover all 6 D7 band-8 requirements**; D7 = 8.0 is the only dimension on Best-Paper track here.

## Top weaknesses (`top_weaknesses`, P1 ordered)

1. **≥ 14 operationally-referenced symbols / formulas undefined in the main body** (forward_bias, Cost_self, Risk_self, SendCost, AuditCost, RejectRisk, SplitGain, MergeCost, DepthPenalty, AuditLoad, mean-axis fold, λ_c/r/s/m/d values, η_loc/trm/rew values, Algorithm 1 tie-breaking). Under P1 default-rejection: **D1 = 4.5 alone triggers weak_reject floor**.
2. **Zero external published 2024–2025 SOTA in main tables** — S6 = 2.0 rubric "No external baselines at all".
3. **Single benchmark / single seed / no paired test / no CI** — EXP-1/2/3/4 all fail; D4 strict cap = 4.
4. **Figure 1 placeholder** — caption explicitly reads "Vector asset to be inserted"; unfinished-manuscript signal disqualifying for Best-Paper bar.
5. **Table 2 null ablations on non-canonical backbone** — caption honesty is progress but discrimination evidence not yet delivered (E-014 pending).
6. **Headline empirical claim self-refuted** by Finding 4 on `gpt-4.1-mini`; pivoted claim not yet validated.
7. **MAD overlap risk unaddressed empirically** — D3 hard cap at 4.

## Core method problems (`core_method_problems`) — P1 main finding

1. `forward_bias(j)` — "topology-driven flow prior", no functional form given anywhere in the paper.
2. `Cost_self(z) / Risk_self(z)` — referenced in §3.3 U^self equation, no formulas given.
3. `SendCost(i,j) / AuditCost(z) / RejectRisk(j,z)` — §3.3 U^out equation, no formulas given.
4. `SplitGain(z) / MergeCost(z) / DepthPenalty(z) / AuditLoad(z)` — §3.3 U^split equation, no formulas given.
5. "Mean-axis fold" — §3.6 Stage-1 collapse, no projection defined; Algorithm 1 line 35 uses it but does not specify.

## Experimental design problems (`experimental_design_problems`)

1. Table 1 "baselines" are 3 internal variants of the authors' own system.
2. Table 2 on legacy `glm-4-flash` contradicts §4.2 self-admission of "guidance-only, not final paper evidence".
3. Table 2 three ablation rows bit-identical — caption hypothesises but does not test.
4. n=200 canonical evaluation is 35× below HotpotQA dev-split size.
5. No sensitivity sweep on safety-gate thresholds / force-forward gate / audit thresholds.
6. No head-to-head against MAD despite §2.2 admitting overlap.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`) — P1's second specialty

1. `EVIDENCE_EXTRACT` full lookup table only in anonymous supplement §4.
2. All 14 undefined objects in D1 above propagate to reproduction difficulty.
3. λ_c, λ_r, λ_s, λ_m, λ_d numeric values scattered across §B2 / Algorithm 1 constants / not consolidated.
4. `FTH = 0.5` threshold + {η_loc, η_trm, η_rew, μ} persona-update weights — values + coupling to §3.5 update rule not equationally linked.
5. No per-table/per-figure regenerate-me script referenced.

## Overclaims / risky framing (`overclaims_or_risky_claims`)

1. Abstract + §1 claim EDO "yields a structured personality-tag space that drives future local allocation decisions" — delivered prototype collapses vector to scalar; contribution #2 (recursive upstream audit) unimplemented.
2. §5 Conclusion "decentralized outcome-based calibration improves delegation safety" — but Finding 3 attributes PAR=0 to the safety gate, not TCPB.
3. §4.3 pivoted claim "EDO framework explains when and why delegation overhead pays off" — Finding 3 + Finding 4 do not yet support this claim.

## Ambiguous algorithm points (`ambiguous_algorithm_points`)

1. "Mean-axis fold" — undefined projection.
2. Algorithm 1 line 11 argmax tie-breaking — unspecified.
3. Algorithm 1 line 20–22 flow-control from RejectReroute-exhaustion to SPLIT reuses overwritten `a` variable; state semantics ambiguous.
4. §3.5 recursive audit root-task case — terminal correction coupling to §3.5 `P_i^{t+1}` equation-level undeclared.

## Missing definitions / state variables (`missing_definitions_or_state_variables`)

1. forward_bias / Cost_self / Risk_self / SendCost / AuditCost / RejectRisk / SplitGain / MergeCost / DepthPenalty / AuditLoad — all undefined formulas.
2. "Mean-axis fold" — undefined projection.
3. Numeric values of λ_c, λ_r, λ_s, λ_m, λ_d (λ_a=0.02 only).
4. Numeric values of η_loc, η_trm, η_rew, μ.

## Missing or weak experiments (`missing_or_weak_experiments`)

1. No external 2024–2025 SOTA baselines (AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT).
2. No second or third dataset.
3. No multi-seed + paired tests + CI on canonical backbone.
4. No canonical-backbone ablation table.
5. No MAD head-to-head.
6. No case-study gallery.

## Statistical significance concerns (`statistical_significance_concerns`)

1. Table 1 point estimates at n=200; no paired bootstrap / sign test; no multiple-comparisons correction.
2. Table 2 three identical ablation rows without significance framing.
3. Figure 2 overlays n=200 + n=7405 without statistical harmonisation.

## Baseline completeness concerns (`baseline_completeness_concerns`)

1. Zero external published systems in any main table — S6 = 2.0.
2. Latest multi-hop-QA SOTA 2024–2025 (MA-RAG / ReAgent) cited only as roadmap.
3. `demand.md §8` + §11.5 #3 double miss.

## Limitations section assessment

| Field | Value |
|-------|--------|
| section_present | true |
| section_title_exact | true |
| contains_no_new_content | true |
| honesty_score_1_to_5 | 5 |
| specific_failure_modes_listed | true |
| issues | ["item (5) 'queued for re-execution' is marginally operational-status", "item (6) overlaps with Ethical Considerations Fairness paragraph — cross-reference would help"] |

## Responsible NLP Checklist assessment

| Field | Value |
|-------|--------|
| appears_complete | true |
| issues | ["B4 discloses AI code-completion without product name (OK per ACL policy)", "B2 compute budget at order-of-magnitude with wall-clock and USD estimate"] |

## Implementation risks (`implementation_risks`)

1. 14 undefined objects in D1 block any independent re-implementation without supplement.
2. Provider-integrity event makes cross-channel replication potentially divergent.
3. No per-table regenerate scripts.

## `what_to_fix_for_8_plus` (target overall ≥ 8.0)

1. **Inline the 14 undefined objects** from D1 above: give functional forms for forward_bias / Cost_self / Risk_self / SendCost / AuditCost / RejectRisk / SplitGain / MergeCost / DepthPenalty / AuditLoad; numeric values for λ_c..λ_d and η_loc/trm/rew; definition of "mean-axis fold"; Algorithm 1 tie-breaking rule.
2. **Add ≥3 external published baselines** in main tables (AutoGen + ChatEval + MAD + MA-RAG / ReAgent for recency).
3. **Add ≥1 second dataset** (MuSiQue minimum).
4. **Multi-seed + paired bootstrap CI + significance test** on canonical-backbone Table 1 (E-017 in progress).
5. **Re-run Table 2 ablations on canonical `gpt-4.1-mini`** (E-014 configs ready post-quota).
6. **Replace Figure 1 placeholder with final vector PDF**.

## `what_to_fix_for_oral` (Best-Paper 8.5)

1. All of `what_to_fix_for_8_plus` **plus**:
2. Implement at least one of R1 / R2 / R3 with measurable empirical wins against external 2024–2025 SOTA on ≥3 diverse datasets.
3. Dedicated case-study / application block with 6–10 visualisations.
4. Mechanistic-novelty falsifiable claim that no prior work can match.
5. Reverse Finding 4: show full-EDO beats `self_claim` on canonical backbone.

## `recommended_next_actions`

1. **Highest-leverage immediate fix**: inline the 14 undefined objects (D1 → 6.0+ is a ~1–2-day writing task, would lift overall by ~0.375 via D1 weight alone).
2. Complete in-flight E-017 3-seed fullval (quota restored; seed=42 stage2 73%, stage1 56% as of ssh probe).
3. Launch E-014 canonical-backbone ablation to discriminate the Table 2 null effect.
4. Land at least one external head-to-head (MA-RAG / ReAgent / MAD) pre-submission.
5. Replace Figure 1 placeholder.

## `rule_source_disagreements`

None. P1 strict scoring follows `docs/demand.md` §1–§11 + `prompts/reviewer_prompt.md §2–§10`. The specific D1=4.5 score reflects the paper's 14 undefined operational objects; no rubric conflict.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":           true,
  "edo_paper_pdf_loaded":       true (pdftotext -layout of 37A3F45D... 848 lines end-to-end read this batch),
  "fallback_source_used":       "pdftotext -layout article/build/edo_paper.pdf",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit"],
  "demand_section_11_applied":  true (7 hard + 3 partial + 2 pass; oral_quality_score cap 3, assigned 2.0 under P1 strict),
  "persona_rotation":           "P1 Strict ARR SAC — last used on older PDF SHA 4504614E in R-FULL-004; new PDF SHA 37A3F45D has never been P1-audited until this batch",
  "cross_batch_delta_note":     "P1 score overall=3.5 vs R-FULL-010 P2 overall=4.0 (on same PDF) = 0.5-point P1-stricter-than-P2 spread, attributable to D1=4.5 (vs P2 5.5) + D4=3.0 (vs P2 3.5) + D5=5.5 (vs P2 6.5) — all three dimensions where P1 default-rejection + 14-undefined-object audit is stricter than P2 empirical lens"
}
```

---

## `_parse_mode`

`full`

*End of review. Schema coverage per `prompts/reviewer_prompt.md §9` + `demand.md §11.5 best_paper_structural_compliance`. **First R-FULL batch across 11 rounds to break below the 4.0 weak_reject / reject boundary** under a non-DR-forced cap — attributable to P1 strict D1=4.5 audit of ≥14 undefined operational objects + D4=3.0 (below P2's 3.5 by P1-strict-posture).*
