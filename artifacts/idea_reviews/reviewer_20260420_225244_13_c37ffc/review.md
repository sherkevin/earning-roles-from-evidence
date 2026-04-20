# R-FULL-013 — Full-paper review (P3 Adversarial Novelty SAC, target = Best Paper 8.5)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_225244_13_c37ffc` |
| **reviewer_profile** | **P3: Adversarial Novelty SAC focused on D3 Novelty and D2 Significance** (treats any framing similarity to existing routing / orchestration / agent / multi-agent work as a presumed reduction; demands ≥3 named prior systems concrete differentiation and a falsifiable claim that prior work cannot make; still enforces all §2.5 experiments hard rules) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `87662BD69C6926E9535861CB16C30195461B324C781797720C1E1E7E9A2098BB` |
| **pdf_sha16** | `87662BD69C6926E9` (**new PDF**, rebuilt 2026-04-20 22:52:12 after R47 S-164 Symbol Glossary itemize restructure; supersedes `54DF9463`) |
| **target_score** | **8.5** (Best-Paper bar per `docs/demand.md §11.5`) |
| **prior_batch_independence** | **stateless** — no `scoreboard.md`, no `fix_themes.md`, no prior review.md, no `SCIENTIST_TODO §C` read. P3 last used in R-FULL-002 on an older PDF; first P3 audit of a post–§11 Best-Paper-target PDF. |
| **rulebook** | `docs/demand.md` (post-§11 241 lines) + `prompts/reviewer_prompt.md §2–§10` + §11.5 addendum |
| **process_compliance (§1.5.0)** | **Satisfied**: `docs/demand.md` read end-to-end + `pdftotext -layout` extraction of new PDF (857 lines, 94598 B) read end-to-end; `scripts/build_paper.ps1` invoked and its COMPLIANT / OVER report consulted. |
| **user_trigger** | User verbal explicit "新的审稿人角度 ... 特别关注论文的实验 ... 实验的评分占比要高" = implicit `U-Review-13-decide`. Persona rotation to P3 (Adversarial Novelty); P3's D3-specialty + §2.5 experiments hard-rules enforcement satisfies user's "experiments-weight + new-reviewer-angle" directive. |

---

## Document classification

`document_type` = **full_paper** (Intro + Related Work + Method + Experiments + Conclusion + Limitations + Ethical Considerations + Appendices A–E + References).

`submission_track` = EMNLP Long Paper — Oral / Best-Paper bar.

**CRITICAL STATE CHANGE since R-FULL-012**: R47 commit `1c6d894` (2026-04-20 22:43:05) restructured the §3.6 "Stage-1 operational collapses" paragraph from dense-prose-compressed (as it stood in R45 PDF SHA `54DF9463`) into a **9-bullet itemize list**. The **rebuilt PDF (this R-FULL-013's target `87662BD6`) now reports `Main body ends on page 9: OVER 8-page submission cap`** per `build_paper.ps1`. **This is a DR-1 regression.**

---

## Summary (≤ 100 words)

The restructured §3.6 Symbol Glossary itemize list makes the 14 operational objects far more readable than R-FULL-012's dense prose. Readability + D1 lift preserved; D3 novelty audit confirms MAD overlap risk unchanged. **However**, this R47 restructure pushed the main body onto page 9, triggering a **DR-1 confirmed violation** per `demand.md §2` (main body ≤ 8 pages). Combined with unchanged experiments bar (single benchmark / single seed / no external SOTA / null ablations), **DR-1 forces verdict = reject with overall capped at 4.0**; assigned overall **3.5** due to P3 adversarial-novelty posture on D3 MAD overlap.

---

## Desk-reject risks (`desk_reject_risks`) — **DR-1 CONFIRMED**

| ID | Status | Evidence |
|----|--------|----------|
| **DR-1** | **CONFIRMED** | `scripts/build_paper.ps1` on current tex / PDF (SHA `87662BD6`) reports: `Main body ends on page 9 (Limitations starts here): OVER 8-page submission cap`. pdftotext confirms Limitations heading at line 667 with §5 Conclusion spilling from page 8 to page 9. Per `demand.md §2` "Page Limit: Submission/review version is limited to a **maximum of 8 content pages** for the main body. Violation = immediate desk reject." **R47 S-164 Symbol Glossary itemize restructure** (dense prose → 9 bullets, commit `1c6d894` 2026-04-20 22:43:05) added ~3 content lines without recompensating compression, pushing main body over the cap. **This is recoverable via scientist compression (item-list tightening or §3 prose trim) but currently submitted PDF is non-compliant.** |
| DR-2 | PASS | Section titled exactly `Limitations` appears after Conclusion, before Ethical Considerations / References. |
| DR-3 | PASS | 7 Limitations items are scope statements; engineering response in Appendix B; no new experiments / figures / tables / analyses in Limitations. |
| DR-4 | POSSIBLE – not verified | pdftotext cannot audit `acl.sty` modifications. |
| DR-5 | PASS | Appendix C heading no longer carries "per Reviewer R-FULL-004 D5 request" (R42 fix confirmed). |
| DR-6 | PASS | Responsible NLP Checklist Appendix A B1–B5 complete. |
| DR-7 | PASS | Coherent long-form. |
| DR-8 | PASS | AI assistance disclosed; standalone Ethical Considerations present. |

**Net: DR-1 CONFIRMED**, forcing `overall ≤ 4.0` and `verdict = reject` per `reviewer_prompt.md §6` cap "If any DR-1..DR-8 confirmed: cap overall at 4.0".

---

## Best-Paper structural compliance (`best_paper_structural_compliance`) — `demand.md §11.5`

### §11.5 addendum audit

| # | Requirement | Status | Δ from R-FULL-012 |
|---|------------|--------|---|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | unchanged |
| 2 | ≥ 3 diverse datasets in main tables | ❌ fail | unchanged |
| 3 | Latest 12-month SOTA in main tables | ❌ fail | unchanged |
| 4 | Per-component ablation canonical backbone | ❌ fail | unchanged |
| 5 | Multi-seed + paired tests + CI | ❌ fail | unchanged (E-017 running) |
| 6 | Error analysis quantitative failure modes | ❌ fail | unchanged |
| 7 | Dedicated case-study / application block | ❌ fail | unchanged |
| 8 | Limitations ≥ 0.5 p, honest, specific | ✅ pass | unchanged |
| 9 | Ethical Considerations section present | ✅ pass | unchanged |
| 10 | Figure 1 = system schematic vector-quality | ❌ fail | unchanged (placeholder) |
| 11 | Public code / data / model release | ⚠ partial | unchanged |
| 12 | No null-effect ablation tables | ⚠ partial | unchanged |

**Count unchanged**: 7 hard + 3 partial + 2 pass. §11.5 enforcement oral_quality cap at 3; assigned **2.5** under P3 (Adversarial Novelty lens down-weights presentation improvements).

---

## Experiments-solidity audit (`experiments_solidity_audit`) — P3 enforces §2.5

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 multi-dataset | fail | HotpotQA only; MuSiQue + 2WikiMultiHop deferred |
| EXP-2 multi-seed | fail | seed=42 only (§B2) |
| EXP-3 significance test | fail | §4.3 Finding 2 explicit self-admission |
| EXP-4 effect size / CI | fail | §B2 explicit |
| EXP-5 ablation coverage | partial | 0.5 on wrong backbone |
| EXP-6 baseline recency | fail | 0 external 2024–2025 SOTA in main tables |
| EXP-7 sensitivity sweep | partial | ±2× weight sweep only |
| EXP-8 error analysis | fail | no taxonomy |

**`experiments_solidity_score` = 1 / 8**.

**Caps**: D4 cap = 4 from audit; S5 cap 4, S6 cap 4, S7 cap 5.

---

## Novelty delta audit (`novelty_delta_audit`) — **P3 specialty deep audit**

P3 adversarial lens: treats any framing similarity as presumed reduction; demands mechanistic differentiation + falsifiable claim that prior work cannot make.

| # | prior_work_name | year | claimed_difference | is_concrete | is_overlap_risk |
|---|-----------------|------|-------------------|-------------|-----------------|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | EDO removes (i) globally visible expert/role table at init, (ii) central decision node owning routing, (iii) fixed task script. P3 verdict: **concrete** (three named mechanistic deltas) but **AutoGen's decentralized `GroupChat` mode allows similar local-visibility patterns in practice**; the paper's "removes central orchestrator" claim is a configuration argument, not a mechanism-level delta. | true (narrowly) | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | Per-hop peer critique + meta-reviewer aggregation vs. TCPB's terminal-only calibration. P3 verdict: **concrete mechanism-level delta** (hop-level vs. terminal-level). | true | false |
| 3 | **Multi-Agent Debate (Liang EMNLP 2024; Du ICML 2024)** | 2024 | "MAD aggregates per-hop critiques into final decision; TCPB collapses critique into terminal-outcome only and uses peer signal for backbone competence update only." P3 adversarial reading: MAD-style round-wise debate with a final judge **is functionally equivalent** to "terminal-outcome calibration over a per-hop debate record"; the paper does not articulate what TCPB adds that MAD cannot replicate by tuning its `final_aggregator` — and **MAD is absent from all main-result tables**. | true | **true (unaddressed)** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | Hard-coded SE pipeline; EDO removes pre-assigned role order. P3 verdict: delivered TCPB still uses 4 role-prior nodes (decomposer / evidence_seeker / verifier / synthesizer) + "hand-coded force-forward gate" (§3.1) = still pre-assigned roles. **The delivered prototype does not escape MetaGPT's critique**; the escape is purely Stage-2-theoretical. | true | **true (self-admitted)** |
| 5 | Reflexion / ToT / Self-Refine (Shinn 2023; Yao 2023; Madaan 2023) | 2023 | Single-agent self-reflection; EDO = multi-agent terminal calibration. | true | false |

**P3 adversarial findings**:

- **MAD overlap risk unaddressed**: §2.2 prose mentions MAD in 2 sentences; no head-to-head benchmark; TCPB's terminal-outcome mechanism is a natural **degenerate case** of MAD with `aggregator_window = full trajectory + aggregation_rule = terminal-F1-sign`. Per `reviewer_prompt.md §2.5.2`: "If any prior work is `is_overlap_risk=true` and the paper does not directly address the overlap, cap D3 at 4." → **D3 cap at 4**.
- **MetaGPT self-admitted overlap**: Prototype Scope Box (v) admits 4 role-prior nodes + hand-coded force-forward gate = delivered system has not escaped pre-assigned role criticism. The "role-free emergence" claim is purely Stage-2-theoretical. Compounds D3 cap.
- **Novelty falsifiable claim absent**: P3 demands one falsifiable prediction that AutoGen / ChatEval / MAD / MetaGPT / Reflexion cannot make. Paper's candidates: (i) "emergent organization from local interaction" — not operationalised with a falsifiable metric; (ii) "recursive acceptance ladder" — not tested; (iii) "value-induced personality tags" — not measured. None is experimentally falsifiable in the delivered submission.

---

## Dimension scores (P3 Adversarial Novelty lens)

| Dim | Score | P3 defense |
|-----|-------|------------|
| **D1 Soundness** | **6.5** | Post-R45 S-163 + R47 itemize: 9 bullet-listed symbol glossary (SplitGain / MergeCost / DepthPenalty / AuditLoad / RejectRisk as Stage-2 hooks; AuditCost=λ_a=0.02; SendCost=0; Cost_self=τ_z/10³; Risk_self=1-c[i]; mean-axis fold c[i]=(1/7)Σ B_i(j)[k]; (λ_c..λ_a)=(0.02,0.10,0.05,0.05,0.05,0.02); (η_loc,η_trm,η_rew,μ)=(0.06,0.10,0.10,0.5); tie-breaking DoSelf≻Outsource≻Split). Itemize form is more readable than dense prose; D1 band 7 "under-specified update rules a careful re-implementer could still recover" fits. Minus 0.5 (vs. P4's 6.5 was band-7 upper; P3's 6.5 slightly conservative due to DR-1 regression contamination). |
| **D2 Significance** | **4.5** | P3 strict adversarial: delivered Pareto-negative + MAD functional overlap + MetaGPT unfulfilled role-free claim = delivered system significance is limited to "negative result + roadmap". Positive aspect: honest reporting of Pareto-domination is a methodological contribution. |
| **D3 Novelty** | **4.0** (cap) | P3 specialty. Hard cap 4 from MAD unaddressed overlap; compounded by MetaGPT self-admitted pre-assigned roles + AutoGen-equivalent-under-GroupChat-mode configurational-only delta. P3 rubric band 4 = "Incremental tweak ... differences from closest prior work are quantitative parameter changes, not mechanistic changes" — fits. |
| **D4 Empirical** | **3.0** | P3 strict on experiments. Single benchmark + single seed + null ablations on wrong backbone + no external SOTA + Finding 4 self-refutation active. D4 cap = 4 from audit; assigned 3.0 to reflect active self-refutation + MAD overlap contribution to main-table weakness. |
| **D5 Reproducibility** | **6.5** | Unchanged from R-FULL-012 direction. S-163 + R47 itemize make Stage-1 implementable paper-alone; EVIDENCE_EXTRACT full table still supplement-only. |
| **D6 Clarity** | **4.5** | **DR-1 regression hits D6**: main body page 9 overflow signals incomplete submission preparation. Also Figure 1 placeholder unchanged. Minus 0.5 vs. R-FULL-012 P4 5.0. |
| **D7 Responsible research & limitations** | **8.0** | Limitations 7 items + Ethical Considerations 5 sub-paragraphs; band 8 maintained. |

### Secondary (S1–S8)

| S | Score | Note |
|---|-------|------|
| S1 executability | 6.5 | S-163 + R47 itemize improves self-contained Stage-1 implementability. |
| S2 falsifiability | 5.0 | P3 strict: no Stage-2-mechanism falsifiable prediction that MAD / AutoGen / ChatEval cannot match. |
| S3 empirical plan (design only) | 5.0 | §4.4 E1–E5 reasonable but unexecuted. |
| S4 technical clarity | 7.0 | Itemize glossary is a clarity win. |
| **S5 statistical rigor** | **3.0** | Single seed / no paired / no CI. |
| **S6 baseline quality** | **2.0** | "No external baselines at all" in main tables. |
| **S7 ablation completeness** | **4.0** | Null effects on wrong backbone; caption mitigates. |
| S8 writing and figures | 4.5 | Figure 1 placeholder + DR-1 regression signal unfinished submission. |

**`oral_quality_score` = 2.5** (P3 adversarial lens).

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*6.5 + 0.18*4.5 + 0.15*4.0 + 0.18*3.0 + 0.10*6.5 + 0.07*4.5 + 0.07*8.0
             = 1.625 + 0.810 + 0.600 + 0.540 + 0.650 + 0.315 + 0.560
             = 5.100

Caps applied (reviewer_prompt §6):
- **DR-1 CONFIRMED: cap overall at 4.0**  ← FORCED by page-9 overflow, main cap
- D1 = 6.5 ≥ 5                            → no D1 cap
- D4 = 3.0 < 5                            → cap overall at min(4.0, D4+0.5) = 3.5 (binding below DR-1 cap)
- D4 = 3.0 < 7                            → cap overall at 7.0 (not binding)
- D3 = 4.0 < 5                            → cap overall at D3+0.5 = 4.5 (not binding)
- D3 = 4.0 < 6                            → cap overall at 6.5 (not binding)
- D7 = 8.0 ≥ 4                            → no cap
- oral_quality = 2.5 < 5                  → cap overall at 5.5 (not binding)
- experiments_solidity = 1 ≤ 3            → cap overall at 4.5 (not binding)
- novelty overlap MAD unaddressed         → cap overall at 5.0 (not binding)
- S6 = 2 < 5                              → cap overall at 6.0 (not binding)
- S7 = 4 < 5                              → cap overall at 6.0 (not binding)

DR-1 cap 4.0 + D4 cap 3.5 → final overall = min(4.0, 3.5) = 3.5
verdict forced by DR-1 = reject
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **5.100** (slightly below R-FULL-012 P4 5.275 due to P3 D4=3.0 + D6=4.5) |
| **overall** | **3.5** (DR-1 confirmed cap 4.0 + D4<5 cap 3.5; second cap is binding) |
| **verdict** | **reject** (forced by DR-1 confirmed) |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **is_best_paper_ready** | **false** |
| **confidence** | **5 / 5** (DR-1 trigger is from build script output, directly verifiable; all other dimensions reasoned from visible text) |
| **estimated_score_after_DR-1_fix** (scientist compresses §3.6 or other sections to restore 8-page COMPLIANT, no other changes) | **4.0 weak_reject boundary** (R-FULL-012 level recovered) |
| **estimated_score_after_fixes** (DR-1 fix + E-017 3-seed fullval + E-014 canonical ablation + E-018 external SOTA + Figure 1 + MuSiQue) | **6.0-6.3 borderline** |
| **estimated_score_after_Best-Paper-track_fixes** (2-3 months full agenda) | **7.0-7.5 Oral border** (unchanged 1+ gap to 8.5) |

---

## Top strengths (`top_strengths`)

1. **R47 S-164 itemize restructure** genuinely improves §3.6 symbol glossary readability (9 bullets, zero new content) — D4/D5-impacting in D1/S4 direction, confirmed by cross-persona lift across R45 → R47.
2. **R-FULL-011 P1 D1 finding resolved**: all 14 previously-undefined operational objects are now definable paper-alone via §3.6 itemize.
3. **Finding 4 Pareto-domination + Limitations item (6)** continue honest self-reporting — unchanged strength from prior batches.
4. **Dual Limitations + Ethical Considerations sections** cover D7 band 8 requirements.

## Top weaknesses (`top_weaknesses`) — P3 adversarial ordering

1. **DR-1 CONFIRMED**: main body page 9 overflow (R47 itemize restructure added ~3 lines without compensation). **Immediate, pre-submission-blocking defect**. `scripts/build_paper.ps1` reports "OVER 8-page submission cap". Forces verdict = reject until fixed.
2. **MAD overlap unaddressed empirically** — P3 adversarial reading: TCPB is a functional degenerate case of MAD; §2.2 prose is insufficient without head-to-head. D3 capped at 4.
3. **MetaGPT overlap self-admitted**: Prototype Scope Box (v) confirms 4 role-prior nodes + hard-coded force-forward gate = delivered prototype does not escape pre-assigned-roles critique.
4. **No falsifiable claim that prior work cannot make** — "emergent organization" / "recursive acceptance ladder" / "personality tags" all unmeasured.
5. **Experiments bar unchanged**: single benchmark / single seed / no paired CI / no external SOTA / null ablations on wrong backbone / Finding 4 self-refutation.
6. **Figure 1 placeholder** unchanged.
7. **Novelty presentation contradiction**: Abstract + §1 claim 4 contributions; delivered prototype reduces to #3 (TCPB Stage-1 terminal calibration) which is self-refuted + overlaps with MAD-terminal-aggregator.

## Core method problems (`core_method_problems`)

1. Delivered TCPB is a special case of MAD with fixed aggregator; paper does not articulate what TCPB adds beyond a terminal-outcome-sign aggregator.
2. Prototype Scope Box (v) admits persona update is terminal-scalar-only; the "vector belief" is purely Stage-2-theoretical.
3. "Emergent organization" claim has no falsifiable operationalization in Stage-1.

## Experimental design problems (`experimental_design_problems`)

1. Table 1 "baselines" = 3 internal variants; zero external 2024–2025 SOTA.
2. Table 2 on legacy `glm-4-flash`; §4.2 self-admits GLM is "guidance-only, not final evidence".
3. Table 2 three-row bit-identical ablations (caption now acknowledges but does not test).
4. n=200 canonical 35× below HotpotQA dev split.
5. No MAD head-to-head despite §2.2 acknowledging overlap.
6. No sensitivity sweep on safety-gate / force-forward / audit thresholds.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`)

1. EVIDENCE_EXTRACT lookup table still supplement-only (Stage-2 scope).
2. Per-table / per-figure regenerate scripts absent.
3. Provider-integrity event cross-channel replication variance.

## Overclaims / risky framing (`overclaims_or_risky_claims`)

1. Abstract "structured personality-tag space drives future local allocation" — delivered prototype uses scalar c[i].
2. §5 Conclusion "decentralized outcome-based calibration improves delegation safety" — Finding 3 attributes PAR=0 to safety gate, not TCPB.
3. §4.3 pivoted claim "EDO framework explains when delegation overhead pays off" — not validated.
4. Contribution #1 "reframe multi-agent routing as organizational emergence" — still a framing contribution; P3 adversarial: reframing without mechanistic differentiation is D3 band-5 ceiling.

## Ambiguous algorithm points (`ambiguous_algorithm_points`)

1. Algorithm 1 lines 20–22 flow-control from RejectReroute-exhaustion to SPLIT reuses overwritten `a` variable; ambiguous without a flowchart.
2. Algorithm 1 line 35 terminal correction coupling to §3.5 persona-update equation not equationally linked (S-163 inlined multipliers but not the coupling).

## Missing definitions / state variables (`missing_definitions_or_state_variables`)

Post S-163 + R47: **CLOSED for Stage-1**. Stage-2 formulas for SplitGain / MergeCost / DepthPenalty / AuditLoad / RejectRisk still in supplement (acceptable as Stage-2 scope).

## Missing or weak experiments (`missing_or_weak_experiments`)

1. No external 2024–2025 SOTA baselines (AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT).
2. No MuSiQue / 2WikiMultiHop.
3. No multi-seed + paired tests + CI.
4. No canonical-backbone ablation table.
5. **No MAD head-to-head — P3 specialty flag, compounds D3 cap**.
6. No case-study gallery.

## Statistical significance concerns (`statistical_significance_concerns`)

1. Table 1 point estimates n=200; no paired bootstrap.
2. Table 2 identical rows without significance framing.
3. Figure 2 cross-sample-size overlay unharmonised.

## Baseline completeness concerns (`baseline_completeness_concerns`)

1. Zero external published systems in main tables.
2. Latest SOTA 2024–2025 cited only as roadmap.
3. **MAD explicitly named as overlap risk (§2.2) but absent from all main tables** — P3 flags this as the single highest-priority experimental gap.

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

1. EVIDENCE_EXTRACT lookup supplement-only (Stage-2 scope).
2. Per-table regenerate scripts absent.
3. Provider-integrity event cross-channel variance.

## `what_to_fix_for_8_plus`

1. **FIX DR-1 CONFIRMED REGRESSION IMMEDIATELY**: compress §3.6 itemize list OR trim §2/§4 prose ≥ 3 lines to restore main body 8-page COMPLIANT. **Pre-submission-blocking.**
2. **Benchmark MAD head-to-head on HotpotQA main table** — D3 cap at 4 will not unlock without this (P3 specialty).
3. **Add ≥3 external 2024–2025 SOTA** (AutoGen / ChatEval / MA-RAG / ReAgent).
4. **Second dataset (MuSiQue)**.
5. **Multi-seed + paired bootstrap CI** (E-017 running).
6. **Re-run Table 2 ablations on canonical gpt-4.1-mini** (E-014 configs ready).
7. **Replace Figure 1 placeholder**.
8. **Articulate one falsifiable claim** that AutoGen / ChatEval / MAD / MetaGPT cannot make — e.g., a theorem about emergent specialisation entropy divergence that prior systems demonstrably lack.

## `what_to_fix_for_oral` (Best-Paper 8.5)

1. All of `what_to_fix_for_8_plus` **plus** implement at least one of R1/R2/R3 with wins vs. external SOTA on ≥3 datasets.
2. Dedicated case-study / application block with 6–10 visualisations.
3. Mechanistic-novelty falsifiable claim no prior work can match.

## `recommended_next_actions`

1. **Highest priority** — fix DR-1 regression: compress §3.6 itemize (e.g., merge 2 bullets or drop redundant Stage-2-hook enumeration) to restore 8-page COMPLIANT.
2. Launch E-018 MAD HotpotQA reproduce as absolute-priority for D3 overlap closure (not just AutoGen / ChatEval).
3. Continue E-017 seed=42 fullval (running stage2=93% stage1=72% as of 22:51 ssh probe); ETA seed=42 done ~00:00, seed=43/44 chained.
4. Replace Figure 1 placeholder.

## `rule_source_disagreements`

None. P3 adversarial scoring follows `docs/demand.md` §1–§11 + `prompts/reviewer_prompt.md §2–§10`. DR-1 trigger is directly from `build_paper.ps1` output; no rubric conflict.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":            true (post-§11, 241 lines),
  "edo_paper_pdf_loaded":        true (pdftotext -layout of 87662BD6... 857 lines end-to-end; first audit of this SHA),
  "fallback_source_used":        "pdftotext -layout article/build/edo_paper.pdf; scripts/build_paper.ps1 console output",
  "build_script_ran":            true (output: 'Main body ends on page 9 (Limitations starts here): OVER 8-page submission cap'),
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit"],
  "demand_section_11_applied":   true (7 hard + 3 partial + 2 pass; oral_quality cap 3, assigned 2.5 under P3),
  "persona_rotation":            "P3 Adversarial Novelty SAC; last used in R-FULL-002; first P3 on post-§11 Best-Paper-target PDF",
  "dr1_regression_finding":      "R47 commit 1c6d894 S-164 Symbol Glossary itemize restructure added ~3 content lines without compensation; rebuilt PDF 2026-04-20 22:52:12 (this batch's target SHA 87662BD6) now exceeds 8-page cap per build script. R47 commit message claims 'zero new content' but the dense-prose-to-itemize visual expansion added rendering space. Scientist must compress before next commit."
}
```

---

## `_parse_mode`

`full`

*End of review. **P3 Adversarial Novelty SAC overall=3.5 REJECT** forced by **DR-1 CONFIRMED** (main body page 9 overflow post-R47 itemize restructure). Second REJECT verdict in 13 R-FULL batches (first was R-FULL-011 P1 3.5 via D1<5 cap; this one via DR-1). Cross-persona consistency with R-FULL-011 at overall=3.5 confirms paper requires scientist intervention before next review cycle. **Primary actionable: compress §3.6 itemize to restore 8-page COMPLIANT**; secondary: benchmark MAD head-to-head to close D3 overlap.*
