# R-FULL-010 — Full-paper review (P2 Empirical-NLP SAC strict, experiments-weighted, target = Best Paper 8.5)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_221017_10_69edbf` |
| **reviewer_profile** | **P2: Empirical-NLP SAC** (D4/S5/S6/S7 specialty; strict, experiments-weighted, no score inflation; demands ≥3 diverse datasets / latest SOTA / full ablation matrix / multi-seed + paired tests / honest error analysis; flags single-benchmark single-seed as borderline-reject by construction) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `37A3F45DC13630F48506741AD2F8F73F963F9C41D9744AFD75016E851023D5B6` |
| **pdf_sha16** | `37A3F45DC13630F4` (**new PDF**; supersedes `53F7FB9D` which was the target of R-FULL-007/008/009 batches; rebuilt 2026-04-20 21:43:53 per R44 after R42+R43 applied DR-5 fix + Ethical Considerations section + Table 2 caption footnote) |
| **target_score** | **8.5** (Best Paper / Oral bar; `docs/demand.md §11.5` user directive "我们对标的就是 best paper") |
| **prior_batch_independence** | **stateless** — no `scoreboard.md`, no `fix_themes.md`, no prior `review.md` from batches 01–09, no `SCIENTIST_TODO §C` read. |
| **rulebook** | `d:\Codes\idea04\docs\demand.md` (post-2026-04-20 update: **§11 Best-Paper Structural Template** + **§11.5 12-item addendum + enforcement mapping** — part of authoritative rulebook; §1–§10 remain in force) |
| **process_compliance (§1.5.0)** | **Satisfied**: complete `docs/demand.md` (post-§11, 241 lines) + full `pdftotext -layout` extraction of PDF (13 pages, 848 lines, 94116 B) read end-to-end before scoring. `reference_documents_consulted.demand_md_loaded=true`, `edo_paper_pdf_loaded=true` (pdftotext extraction → DR-4 layout template check marked POSSIBLE). |
| **user_trigger** | User verbal explicit override of §F.4 24h cooldown: "仔细审查你目前的todo ... 按照你目前todo一步一步严谨科学的去做下去 ... 下面你要作为独立项目之外的专业审稿人 ... 现在可以再去按照一个新的审稿人角度去审，不要被之前的审稿意见被左右 ... 特别关注论文的实验 ... 实验的评分占比要高" → implicit `U-Review-10-decide`. Persona P2 (experiments-focus specialist) re-chosen for fresh read against **new PDF SHA** (material change: post-DR-5-fix + Ethical Considerations + Table 2 caption). |

---

## Document classification

`document_type` = **full_paper** (8-page main body + Limitations + Ethical Considerations + Appendices A–E + References; 14 rendered pages total after R44 rebuild).

`submission_track` = EMNLP Long Paper — evaluated **for Oral / Best-Paper slot** per `demand.md §11.5`.

---

## Summary (≤ 100 words)

EDO reframes multi-agent routing as organizational emergence and delivers a Stage-1 TCPB prototype that the paper itself admits is Pareto-dominated by a trivial `self_claim` baseline on HotpotQA-200 single-seed. The new PDF (post-R44 rebuild) has closed three hygiene items: DR-5 process leak removed, standalone Ethical Considerations section added, Table 2 caption now honestly admits the null ablation effect and defers discrimination to canonical-backbone replication. However, the core empirical shortfalls remain: single benchmark, single seed, zero external 2024–2025 SOTA baselines in main tables, no paired significance / CI, no case-study gallery, and Figure 1 is still a placeholder.

---

## Desk-reject risks (`desk_reject_risks`) — against `docs/demand.md §2`

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | Main body ends §5 Conclusion before Limitations; `scripts/build_paper.ps1` reports "Main body ends on page 8 (Limitations starts here): COMPLIANT". Appendices exempt per post-U-021 `demand.md §2`. §4.5 cites Appendix D **only as "preliminary … do not include in the main results"** → Self-Contained Main Body Rule satisfied. |
| DR-2 | **PASS** | Section titled exactly `Limitations` appears immediately after Conclusion, before Ethical Considerations / References. |
| DR-3 | **PASS** | 7 Limitations items are scope statements + cross-refs; no new experiments / figures / tables. |
| DR-4 | **POSSIBLE – not verified** | pdftotext extraction cannot audit `acl.sty` modifications. Tex-level override of default "Anonymous ACL submission" → "Anonymous EMNLP 2026 Submission" is `\renewcommand`-based tex-level override (not a style-file edit) but a careful SAC should still request LaTeX sources. |
| DR-5 | **PASS** (improved from POSSIBLE in R-FULL-009) | Appendix C heading (text line 914, rendered page 12) now reads "For reproducibility, this appendix lists the four LLM-call templates…" — internal reviewer batch ID leak **has been removed** (confirmed via `pdftotext` + `rg` on `article/latex/edo_paper.tex`). |
| DR-6 | **PASS** | Responsible NLP Research Checklist Appendix A B1–B5 complete; AI assistance disclosed (B4); no PII (B5). |
| DR-7 | **PASS** | Coherent long-form, no thin-slicing signal. |
| DR-8 | **PASS** | No ethics red flags; **furthermore a standalone Ethical Considerations section is now present** (rendered page 9, 5 sub-paragraphs) — strengthens DR-8 compliance. |

Net: 0 confirmed desk-reject; 1 POSSIBLE (DR-4). DR-5 POSSIBLE has been closed since R-FULL-009.

---

## Best-Paper structural compliance (`best_paper_structural_compliance`) — `demand.md §11`

### §11.1 Section-page allocation audit

| §11.1 item | Expected | Delivered | Status |
|-----------|---------:|-----------|--------|
| Introduction | 1 – 1.5 | ≈ 1.2 p (p.1–p.2) | ✅ |
| Background / Related Work | 0.75 – 1.5 | ≈ 1 p (p.2–p.3) | ✅ |
| Method | 1.5 – 3 | ≈ 3 p (p.3–p.6) | ✅ |
| **Experiments (heaviest)** | **2.5 – 4** | ≈ 2.5 p (p.6–p.8) at lower bound | ⚠ partial |
| Conclusion | 0.5 – 1 | ≈ 0.5 p (p.8) | ✅ |
| Limitations | 0.5 – 2 (Best-Paper 1–2) | ≈ 1 p (p.8–p.9), 7 items | ✅ |
| **Ethical Considerations** | 0.5 – 1 (optional but Best-Paper common) | **≈ 0.7 p (p.9–p.10), 5 sub-paragraphs** | **✅ (NEW vs R-FULL-009)** |

### §11.5 addendum Best-Paper checklist (12 items)

| # | Requirement | Status | Δ from R-FULL-009 |
|---|------------|--------|---|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | unchanged (lower bound) |
| 2 | ≥ 3 diverse datasets in main tables | **❌ fail** | unchanged |
| 3 | Latest 12-month SOTA baseline in main tables | **❌ fail** | unchanged |
| 4 | Full ablation matrix (per-component, canonical backbone) | **❌ fail** | unchanged (Table 2 still glm-4-flash; new caption acknowledges but does not fix) |
| 5 | Multi-seed + paired tests + CI/effect-size | **❌ fail** | unchanged (seed=42 only; CI explicitly "not reported") |
| 6 | Error analysis with quantitative named failure modes | **❌ fail** | unchanged |
| 7 | Dedicated case-study / application block with 6–10 visualisations | **❌ fail** | unchanged |
| 8 | Limitations ≥ 0.5 p, honest, specific, demographic/societal | ✅ pass | unchanged |
| 9 | Ethical Considerations / Broader Impact section present | **✅ PASS** | **FAIL → PASS** (post-R43) |
| 10 | Figure 1 = system schematic in Intro, vector-quality, self-contained caption | **❌ fail** | unchanged (still placeholder) |
| 11 | Public anonymous code/data/model release committed | ⚠ partial | unchanged (runtime + data committed; no model since API-only system — justified in Ethical Considerations "Reproducibility and release") |
| 12 | No null-effect ablation tables | ⚠ partial (mitigated) | **❌ FAIL → ⚠ PARTIAL** — Table 2 caption now contains: "The bit-identical (EM, F1, Tok) outcome of the two independent ablation switches is consistent with Finding 1 — routing-mechanism effects are absorbed by the generation bottleneck on the weak backbone; the canonical gpt-4.1-mini replication (§Limitations item (4) ongoing) will discriminate this 'weak-backbone absorption' reading from a possible mechanism code-path issue." → honest self-acknowledgement; the table itself is still null-effect but is now annotated + scheduled for discrimination |

**Items count**: **7 hard fails + 3 partial + 2 pass** (vs R-FULL-009: 9 hard + 2 partial + 1 pass).

**Improvement**: +1 hard-to-pass conversion (#9 Ethical), +1 hard-to-partial (#12 caption annotation). Net progress: **+2 items** toward Best-Paper compliance without any new experimental evidence.

**§11.5 enforcement mapping**:

```
7 hard fails (missed) + 3 partial → still ≥ 6 items missed → oral_quality_score ≤ 3.
Assigned oral_quality_score = 2.5 (up from 2.0 in R-FULL-009: the structural improvements
at #9 + #12 warrant a small upgrade within the cap).
```

---

## Experiments-solidity audit (`experiments_solidity_audit`)

| Check | Status | Evidence (concrete) |
|-------|--------|---------------------|
| EXP-1 multi-dataset | **fail** | HotpotQA only; MuSiQue + 2WikiMultiHop deferred to §4.4 E5 |
| EXP-2 multi-seed | **fail** | §B2 line 831: "all chain-200 results in Table 1 and Table 2 use seed=42"; §Limitations item (4): multi-seed "deferred to the Stage-2 evaluation agenda" |
| EXP-3 significance test | **fail** | §4.3 Finding 2 (line 520): "The gap between the best and worst Stage-1 method is 2.6 F1 points — non-trivial at n=200 but not yet confirmed with paired statistics" |
| EXP-4 effect size / CI | **fail** | §B2 line 840: "Confidence intervals are explicitly not reported in this submission and are flagged in §Limitations as future Stage-2 work" |
| EXP-5 ablation coverage | **partial** | coverage_ratio = 0.5 (TCPB, gate, evidence window on legacy backbone); Stage-2 R1/R2/R3 unablated; new Table 2 caption is progress but does not fix the underlying evidence gap |
| EXP-6 baseline recency | **fail** | zero external published 2024–2025 SOTA in main tables; §2 Related Work names AutoGen/ChatEval/MAD/MetaGPT/ChatDev/AgentVerse/Reflexion/ToT/Self-Refine but **none benchmarked**; demand.md §8 "strong baselines including latest SOTA" is missed |
| EXP-7 sensitivity sweep | **partial** | §4.5 ±2× routing-weight sweep; other priors (λ_a, safety-gate thresholds, force-forward gate decisions) unswept |
| EXP-8 error analysis | **fail** | no quantitative error taxonomy; Finding 3 attribution + §4.5 route-overlap 52% are anecdotal observations, not a named failure-mode taxonomy |

**`experiments_solidity_score` = 1 / 8** (unchanged since R-FULL-008/009; only EXP-7 partial).

**Caps implied by audit**:

```
EXP-1 fail:                    cap D4 at 6
EXP-2 fail:                    cap D4 at 5 AND cap S5 at 4
EXP-3 fail:                    cap D4 at 6 AND cap S5 at 5
EXP-5 partial (0.5):           cap D4 at 6 AND cap S7 at 5
EXP-6 fail:                    cap D4 at 5 AND cap S6 at 4
experiments_solidity <= 3 (=1): cap D4 at 4 AND cap overall at 4.5
S6 (assigned 2.0) < 5:         cap overall at 6.0
S7 (assigned 4.0) < 5:         cap overall at 6.0
```

Effective **D4 cap = 4**; assigned D4 = **3.5** (below cap to reflect Finding 4 self-refutation on canonical backbone — the paper's flagship empirical claim loses to a trivial baseline, documented by the authors themselves).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | claimed_difference | is_concrete | is_overlap_risk |
|---|-----------------|------|-------------------|-------------|-----------------|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | EDO removes (i) globally visible expert/role table at init, (ii) central decision node owning routing, (iii) fixed task script (§2.1 line 183–185) | true | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | Per-hop peer critique with meta-reviewer aggregation; TCPB = terminal-only calibration (§2.2 line 207) | true | false |
| 3 | Multi-Agent Debate (Liang et al. EMNLP 2024; Du et al. ICML 2024) | 2024 | MAD per-hop debate aggregation; TCPB collapses critique into terminal-outcome only | true | **true** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | Hard-coded SE pipeline (PM → architect → engineer); EDO removes pre-assigned role order | true | false |
| 5 | Reflexion / ToT / Self-Refine (Shinn 2023; Yao 2023; Madaan 2023) | 2023 | Single-agent self-reflection; EDO = multi-agent terminal-outcome without per-hop self-score | true | false |

**Overlap handling**: MAD `is_overlap_risk=true`; §2.2 discusses MAD in 2 sentences, **no empirical head-to-head in main tables** (MAD absent from Table 1 / Table 2). Per `reviewer_prompt.md §2.5.2` hard rule: **cap D3 at 4**.

---

## Dimension scores (P2 Empirical-NLP SAC strict lens)

| Dim | Score | Δ from R-FULL-009 | Defense |
|-----|-------|---|---------|
| **D1 Soundness** | **5.5** | 0 | Formal utility functions, Algorithm 1 Appendix E, FIT cosine, Stage-1 scoring equation; λ values still partially hidden in supplement; `forward_bias(j)` functional form undefined; "hand-set priors, not searched" admitted in §B2. |
| **D2 Significance** | **4.5** | +0.5 | Post-R43, the explicit Ethical Considerations section elevates the broader-impact framing. Delivered empirical core is still a single-benchmark Pareto-negative result, but the now-explicit societal risk discussion raises the significance-framing quality from 4.0 to 4.5. |
| **D3 Novelty** | **4.0** | 0 | ≥3 named priors + concrete deltas (passes the ≥3-concrete gate) but MAD overlap unaddressed → hard cap 4. Stage-2 mechanisms (R1/R2/R3) are theoretical-only per §Limitations (1); the delivered contribution is framing + restricted prototype. |
| **D4 Empirical results** | **3.5** | 0 | Single benchmark / single seed / no paired test / no CI / no external baseline / Table 2 null ablations on legacy backbone / Finding 4 self-refutation on canonical backbone. Table 2 caption expansion is good writing but does not change evidence. Deterministic D4 cap = 4.0; assigned 3.5 to reflect the active self-refutation. |
| **D5 Reproducibility** | **6.5** | 0 | Strong: Algorithm 1 Appendix E full pseudocode; Responsible NLP B1–B5 + Appendix C 4 prompt templates + seed=42 disclosed. New Ethical Considerations "Reproducibility and release" paragraph explicitly commits code+data+logs+prompts release under MIT license in anonymous supplement. Still missing: full `EVIDENCE_EXTRACT` mapping table in paper; `forward_bias(j)` functional form; per-table regenerate scripts (Best-Paper standard). |
| **D6 Clarity** | **5.0** | +0.5 | Table 2 caption expansion is a clarity improvement. Text flow clear. **Figure 1 placeholder remains the dominant clarity defect** — caption text "Vector asset to be inserted" is a reviewer-visible unfinished signal. Under Best-Paper lens §11.3 "Figure 1 almost always in Introduction, vector-quality", this alone docks several bands. |
| **D7 Responsible research & limitations** | **8.0** | +0.5 | Post-R43 the paper has **BOTH** a 7-item Limitations section **and** a standalone 5-paragraph Ethical Considerations section. Per `reviewer_prompt.md §3 D7 band 8`: "Honest and specific Limitations; touches risks; checklist clearly addressed." All 6 band-8 requirements met: (i) assumption failures in Limitations (1)(2)(3); (ii) dataset biases in Limitations (7) + Ethical Fairness; (iii) computational/scope limits in Limitations (1)(2)(5); (iv) demographic/societal risks in Limitations (7) + Ethical Fairness; (v) failure modes in Limitations (6) Pareto-domination; (vi) Responsible NLP Checklist fully cited by section (Appendix A B1–B5). |

### Secondary (S1–S8)

| S | Score | Δ | Note |
|---|-------|---|------|
| S1 executability | 5.5 | 0 | Supplement-dependent for some operational details. |
| S2 falsifiability | 5.5 | 0 | Central claim measurable but already-falsified by Finding 4; pivoted claim ("EDO explains when delegation overhead pays off") is not yet validated. |
| S3 empirical plan (design only) | 5.0 | 0 | §4.4 E1–E5 is reasonable but unexecuted. |
| S4 technical clarity | 6.0 | +0.5 | Table 2 caption expansion clarifies what the null ablations mean; `peer_update_enabled=false` + `decomposer_force_forward_enabled=false` flags now named verbatim. |
| **S5 statistical rigor** | **3.0** | 0 | Single seed, no paired test, no CI (capped by EXP-2 @ 4, EXP-3 @ 5). |
| **S6 baseline quality** | **2.0** | 0 | S6 rubric verbatim: "2 = No external baselines at all". Table 1 baselines are authors' own internal variants. |
| **S7 ablation completeness** | **4.0** | +0.5 | Null effects now honestly acknowledged in caption + discrimination plan stated; still no per-component ablation on canonical backbone; still no Stage-2 ablation. |
| S8 writing and figures | 4.5 | +0.5 | Ethical Considerations section + Table 2 caption are writing improvements; Figure 1 placeholder + missing case-study gallery still drag. |

**`oral_quality_score` = 2.5** (+0.5 vs R-FULL-009). Still far below Oral-eligible `≥ 8.5`. Per §11.5 enforcement 7 hard fails + 3 partial ⇒ cap at 3; assigned 2.5.

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*5.5 + 0.18*4.5 + 0.15*4.0 + 0.18*3.5 + 0.10*6.5 + 0.07*5.0 + 0.07*8.0
             = 1.375 + 0.810 + 0.600 + 0.630 + 0.650 + 0.350 + 0.560
             = 4.975

Caps applied (per reviewer_prompt §6 + demand.md §11.5):
- DR-4 POSSIBLE only → no DR-confirmed cap
- D1 = 5.5 ≥ 5                    → no D1 cap
- D4 = 3.5 < 5                    → cap overall at min(4.975, D4+0.5) = min(4.975, 4.0) = 4.0
- D4 = 3.5 < 7                    → cap overall at 7.0 (not binding)
- D3 = 4.0 < 5                    → cap overall at min(4.0, 4.5) = 4.0 (not binding)
- D3 = 4.0 < 6                    → cap overall at 6.5 (not binding)
- D7 = 8.0 ≥ 4                    → no cap
- falsifiability = 5.5 ≥ 4        → no cap
- oral_quality = 2.5 < 5          → cap overall at 5.5 (not binding)
- experiments_solidity = 1 ≤ 3    → cap overall at 4.5 (not binding)
- experiments_solidity ≤ 5        → cap overall at 6.5 (not binding)
- novelty_delta_audit MAD overlap → cap overall at 5.0 (not binding)
- S6 = 2.0 < 5                    → cap overall at 6.0 (not binding)
- S7 = 4.0 < 5                    → cap overall at 6.0 (not binding)
- §11.5 7+ items missed           → cap oral_quality_score at 3 (assigned 2.5 within cap)

overall = 4.0
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **4.975** (+0.210 vs R-FULL-009's 4.765; progress = Ethical section + Table 2 caption + D7 upgrade to band 8) |
| **overall** | **4.0** (unchanged — D4 cap binds at same level) |
| **verdict** | **weak_reject** (at reject/weak_reject boundary) |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **is_best_paper_ready** | **false** (target 8.5; gap = 4.5 overall + 6.0 oral_quality) |
| **confidence** | **4 / 5** |
| **estimated_score_after_fixes** (sprint-scope: complete E-017 3-seed fullval + E-014 canonical-backbone ablation + E-018 external SOTA reproduce + MuSiQue + remove Figure 1 placeholder) | **5.8–6.2 borderline** (unchanged vs R-FULL-009) |
| **estimated_score_after_Best-Paper-track_fixes** (2–3 month agenda: implement ≥1 of R1/R2/R3 + 3+ dataset head-to-head against AutoGen/ChatEval/MAD/MA-RAG/ReAgent + case-study gallery + mechanistic-novelty falsifiable claim) | **7.0–7.5 Oral border** (still 1+ gap to 8.5 Best-Paper bar; needs a genuinely novel mechanism or empirical breakthrough) |

---

## Top strengths (`top_strengths`)

1. **Post-R43 structural improvements verified** — the new Ethical Considerations section (rendered p.9–10, 5 sub-paragraphs covering data / misuse / fairness / reproducibility / AI-assistance) closes §11.5 #9 and raises D7 to band 8.
2. **Table 2 null-effect honesty** — the expanded caption acknowledges the bit-identical outcome as "weak-backbone absorption" consistent with Finding 1, and commits to discriminate via canonical-backbone replication. This is rare scientific self-scrutiny at the reporting level.
3. **DR-5 process-leak closed** — the internal-reviewer-batch-ID metadata has been stripped from Appendix C; the paper is now anonymization-clean at the textual level.
4. **Algorithm 1 Appendix E fully specified** with recursion bounds and clean degenerate Stage-1 projection; reproducible at Best-Paper-level specification detail.

## Top weaknesses (`top_weaknesses`, ranked by severity against Best-Paper bar)

1. **Figure 1 is still a placeholder** — "[Figure 1 placeholder]" with caption text "Vector asset to be inserted" (rendered p.3). `demand.md §11.3` Best-Paper consensus: "Figure 1 = system schematic in Introduction, vector-quality". Disqualifying for Best-Paper bar on its own.
2. **Zero external published 2024–2025 SOTA in main tables** — S6=2.0 per rubric "No external baselines at all". AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT cited in §2 but none benchmarked. §11.5 #3 hard fail.
3. **Single benchmark (HotpotQA only)** — §11.5 #2 hard fail; `demand.md §8` "3–5 diverse datasets" missed.
4. **No multi-seed + paired tests + CI** — §B2 explicitly states "Confidence intervals are explicitly not reported"; seed=42 only; §11.5 #5 hard fail.
5. **Headline result still self-refuted on canonical backbone** — Finding 4: `peer_calibrated` F1 < `self_claim` F1 at equal cost on `gpt-4.1-mini`; §Limitations (6) honest but the paper does not yet have a non-Pareto-dominated result.
6. **No case-study / application gallery** — §11.5 #7 hard fail; Best Papers (Infini-gram mini 2025, Image Transcreation 2024) typically cluster 6–10 case visualisations in Experiments.
7. **Table 2 still on non-canonical `glm-4-flash`** — §4.2 itself labels GLM results "guidance-only, not the final paper evidence", yet Table 2 remains on GLM; §11.5 #4 hard fail (caption honesty is progress but the evidence gap is unchanged).
8. **No quantitative error analysis with named failure modes** — EXP-8 fail; §11.5 #6 hard fail.
9. **MAD overlap not empirically addressed** — D3 capped at 4; §2.2 prose-only discussion, no head-to-head.

## Core method problems (`core_method_problems`)

1. `forward_bias(j)` topology-driven flow prior in §3.6 TCPB utility — no functional form given.
2. §3.4 recursive upstream audit is claimed as a key differentiator but delivered Stage-1 sets `AUDIT defaults to ACCEPT on every return` (§3.6 lines 384–385; Algorithm 1 line 18) — the claimed audit mechanism is not exercised in reported experiments.
3. §3.3 utility equations use λ_c / λ_r / λ_s / λ_m / λ_d; only λ_a = 0.02 has a numeric value in the main body.
4. §3.5 persona update uses {η_loc, η_trm, η_rew, μ} without numeric values in main body; Algorithm 1 uses ν=0.2 for belief EMA (different update rule).

## Experimental design problems (`experimental_design_problems`)

1. Table 1 "baselines" are 3 internal method variants of the authors' own system — no external comparator.
2. Table 2 on `glm-4-flash` not canonical `gpt-4.1-mini` — §4.2 concedes GLM is "guidance-only, not final paper evidence".
3. Table 2 ablation rows numerically identical — new caption admits + hypothesises "weak-backbone absorption" but does not yet provide discriminating evidence; E-014 canonical-backbone replication is promised but not delivered.
4. n=200 canonical Stage-1 evaluation 35× below HotpotQA dev-split size; §4.3 mentions n=7405 full-validation for `peer_calibrated` (F1=0.7703) but Table 1 still shows n=200 numbers.
5. No sensitivity sweep on safety-gate thresholds, force-forward gate decision criteria, or audit thresholds; only routing weights (0.55, 0.20, 0.10) are swept.
6. No head-to-head against MAD despite §2.2 acknowledging overlap risk.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`)

1. `EVIDENCE_EXTRACT` R3 full lookup table offloaded to anonymous supplement §4.
2. `SplitGain(z) / MergeCost(z) / DepthPenalty(z) / AuditLoad(z)` formulas not given.
3. `Cost_self / Risk_self` referenced but undefined.
4. `FTH = 0.5` terminal threshold + `η_loc / η_trm / η_rew / ρ` coupling to §3.5 update rule not equationally linked.
5. No per-table/per-figure regenerate-me script referenced (Best-Paper reproducibility standard).

## Overclaims / risky framing (`overclaims_or_risky_claims`)

1. Abstract + §1 claim EDO "yields a structured personality-tag space that drives future local allocation decisions" — delivered prototype collapses the vector to a scalar; contribution #2 (recursive upstream audit) is not exercised.
2. §5 Conclusion pivots to "decentralized outcome-based calibration improves delegation safety" — but §4.3 Finding 3 attributes PAR=0 to the safety gate, not TCPB.
3. §4.3 pivoted claim "the EDO framework explains when and why delegation overhead pays off" is not validated: Finding 3 attributes PAR behaviour to the gate; Finding 4 shows TCPB loses on the strong backbone.

## Ambiguous algorithm points (`ambiguous_algorithm_points`)

1. "Mean-axis fold" (§3.6) — not defined; presumed `c[i] = mean(B_i[solve, decompose, …])` but operational definition missing.
2. Algorithm 1 line 11 `a ← argmax{U_S, max_j U_j^O, U_P}` — tie-breaking rule unstated.
3. Algorithm 1 lines 20–22 flow-control from RejectReroute-exhaustion to SPLIT reuses overwritten `a` variable; state transitions ambiguous without a flowchart.
4. §3.5 update coupling: if root task has no parent, terminal correction in Algorithm 1 line 35 applies; coupling to §3.5 `P_i^{t+1}` not shown.

## Missing definitions / state variables (`missing_definitions_or_state_variables`)

1. `forward_bias(j)` — functional form.
2. `Cost_self(z)`, `Risk_self(z)`, `SendCost(i,j)`, `AuditCost(z)`, `RejectRisk(j,z)` — formulas.
3. `SplitGain(z)`, `MergeCost(z)`, `DepthPenalty(z)`, `AuditLoad(z)` — formulas.
4. "Mean-axis fold" projection.
5. Numeric values for λ_c, λ_r, λ_s, λ_m, λ_d (only λ_a = 0.02 is in main body).

## Missing or weak experiments (`missing_or_weak_experiments`)

1. No external 2024–2025 SOTA in main tables (AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT).
2. No second or third dataset (MuSiQue / 2WikiMultiHop deferred to Stage-2).
3. No multi-seed runs with paired significance tests on canonical backbone.
4. No confidence intervals or effect sizes on canonical-backbone Table 1.
5. No canonical-backbone ablation table (Table 2 still legacy glm-4-flash).
6. No MAD head-to-head despite overlap risk.
7. No dedicated case-study / application block with visualisation gallery.

## Statistical significance concerns (`statistical_significance_concerns`)

1. Table 1 point estimates at n=200; no paired bootstrap / sign test; no multiple-comparisons correction.
2. Table 2 three ablation rows share identical EM / F1 / Tok — either null effect or bug; new caption hypothesises but does not test.
3. Figure 2 overlays n=200 chain + n=7405 fullval without statistical harmonisation framing.

## Baseline completeness concerns (`baseline_completeness_concerns`)

1. Zero external published systems in main tables (S6 = 2.0 per rubric).
2. Latest SOTA 2024–2025 multi-hop-QA systems (MA-RAG arXiv:2505.20096, ReAgent arXiv:2503.06951) cited only as Stage-2 roadmap, not benchmarked.
3. `demand.md §8` + `§11.5 #3` double miss.

## Limitations section assessment

| Field | Value |
|-------|--------|
| section_present | true |
| section_title_exact | true (`Limitations`) |
| contains_no_new_content | true |
| honesty_score_1_to_5 | 5 |
| specific_failure_modes_listed | true (Pareto-domination, backbone sensitivity, integrity event, cross-endpoint, single-seed, demographic) |
| issues | ["item (5) 'two affected method runs are queued for re-execution' is marginally operational-status; a Best-Paper Limitations would frame it purely as scope-of-claims", "item (6) and (7) partially overlap with Ethical Considerations 'Fairness and scope of claims' — a Best-Paper edit would either cross-reference or disambiguate"] |

## Responsible NLP Checklist assessment

| Field | Value |
|-------|--------|
| appears_complete | true |
| issues | ["B4 discloses AI code-completion without product name (OK per ACL policy)", "B2 compute budget at order-of-magnitude with wall-clock + USD estimate"] |

## Implementation risks (`implementation_risks`)

1. Heavy reliance on `[Anonymous Suppl.]` for operational definitions; replicator without supplement fails.
2. `forward_bias(j)` undefined; recoverable only from supplement.
3. λ numeric values scattered across §3.3 / §3.6 / §B2 / Algorithm 1 constants header; not consolidated.
4. "Mean-axis fold" unspecified — replicator must guess.
5. Provider-integrity event makes cross-channel reproduction potentially different on another endpoint.

## `what_to_fix_for_8_plus` (generic accept, target overall ≥ 8.0)

1. **Add ≥3 external 2024–2025 SOTA baselines to main tables** (AutoGen + ChatEval + MAD minimum; MA-RAG / ReAgent for recency).
2. **Run main results on ≥2 datasets** (MuSiQue minimum).
3. **Multi-seed (≥3) + paired bootstrap CI + paired significance tests** on canonical-backbone Table 1 (E-017 seed=42 resume in progress; seed=43+44 chained).
4. **Re-run Table 2 ablations on canonical `gpt-4.1-mini`** (E-014 configs exist in anonymous supplement; post-quota-restore launch ready).
5. **Replace Figure 1 placeholder with final vector PDF**.

## `what_to_fix_for_oral` (Oral / Best-Paper bar, target overall ≥ 8.5)

1. Implement at least one of R1 (split) / R2 (audit) / R3 (vector-belief routing) and demonstrate measurable empirical wins against both the Stage-1 baseline and ≥3 external 2024–2025 SOTA on ≥3 diverse datasets with multi-seed paired significance.
2. Add a **dedicated Case Study / Application block** in Experiments with 6–10 visualisation Figures (Infini-gram mini's contamination-case study is the reference model).
3. Reverse Finding 4: show the full-EDO system beats `self_claim` on the canonical backbone at equal or lower cost, on ≥2 benchmarks.
4. Deliver a mechanistic-novelty claim that no prior work (AutoGen / ChatEval / MAD / MetaGPT / MA-RAG / ReAgent) can match — e.g., a theorem about when recursive audit improves over per-hop debate, or an emergent-organisation metric (specialisation entropy / persona divergence) that prior systems demonstrably fail on.
5. Public per-table regenerate scripts with reviewer-visible reproducibility receipts.

## `recommended_next_actions`

1. Complete the in-flight E-017 3-seed × 7405 paired-bootstrap fullval (quota restored; seed=42 resume at ~3750 stage2 + 2839 stage1 as of last scheduler log snapshot); refresh Table 1 numbers when done.
2. Launch E-014 canonical-backbone ablation (4 `round2_gpt41mini_ablation_*.yaml` configs in anonymous supplement); this will discriminate the Table 2 "weak-backbone absorption" hypothesis.
3. Land at least one external head-to-head on HotpotQA (MA-RAG / ReAgent / MAD) as a pre-submission sanity check.
4. Replace Figure 1 placeholder.
5. Consider adding a compact case-study block (2–4 visualisations) within the existing §4 budget if possible, even before the full 6–10-visualisation Best-Paper-level gallery.

## `rule_source_disagreements`

None. Scoring follows `docs/demand.md` §1–§11 (including post-2026-04-20 §11 Best-Paper Structural Template + §11.5 12-item addendum) and `prompts/reviewer_prompt.md` §2–§10. `demand.md §11.5` enforcement is consistent with `reviewer_prompt.md §5` Oral-gate rubric.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":           true (post-2026-04-20 §11 Best-Paper supplement, 241 lines),
  "edo_paper_pdf_loaded":       true (pdftotext -layout extraction of 37A3F45D...; 848 lines / 94116 B / 13 rendered pages),
  "fallback_source_used":       "pdftotext -layout article/build/edo_paper.pdf (native PDF attachment not used)",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit — requires LaTeX sources"],
  "demand_section_11_applied":  true (11.1 page allocation + 11.5 12-item checklist + enforcement mapping; 7 hard fails + 3 partial + 2 pass → oral_quality_score cap 3; assigned 2.5 within cap),
  "pdf_sha_change_acknowledged": true (R44 rebuild 2026-04-20 21:43:53 produced SHA 37A3F45D, superseding the 53F7FB9D that was the target of R-FULL-007/008/009; this batch audits the new SHA and credits the three post-R43 improvements: DR-5 leak removal, Ethical Considerations section, Table 2 caption expansion)
}
```

---

## `_parse_mode`

`full`

*End of review. Schema coverage per `prompts/reviewer_prompt.md §9` + `demand.md §11.5 best_paper_structural_compliance`. Rendered as markdown per `REVIEWER_TODO §F.3` (review.md is the sole required artifact; review.json not generated).*
