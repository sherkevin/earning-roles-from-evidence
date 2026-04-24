# R-FULL-009 — Full-paper review (P5 Best-Paper-Committee strict, target = Best Paper 8.5)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_212755_09_e1858f` |
| **reviewer_profile** | **P5: Best-Paper-Committee chair simulating an Oral-track gatekeeper** (only `oral_quality_score ≥ 8.5` grants Oral; default `oral_quality_score ≤ 6` unless Best-Paper-tier evidence present) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `53F7FB9DE7A3FCB095C3C4A53D0B6D23B324E626CFF55AE921356E42C5D503BE` |
| **pdf_sha16** | `53F7FB9DE7A3FCB0` (unchanged since R-FULL-007 / R-FULL-008) |
| **target_score** | **8.5** (Best Paper / Oral bar; set by `docs/demand.md §11.5` user directive "我们对标的就是 best paper") |
| **prior_batch_independence** | stateless — no `scoreboard.md`, no `fix_themes.md`, no `review.md` from batches 01–08, no `SCIENTIST_TODO §C` read. |
| **rulebook** | `docs/demand.md` (post-2026-04-20 update: **§11 Best-Paper Structural Template** and **§11.5 Best-Paper Submission-Ready Checklist addendum** are part of the authoritative rulebook now; §2–§10 remain in force) |
| **process_compliance (§1.5.0)** | **Satisfied**: complete `docs/demand.md` (post-§11 update, 241 lines) + full `pdftotext -layout` extraction of the PDF (1056 lines) read end-to-end this batch. `demand_md_loaded=true`, `edo_paper_pdf_loaded=true` (pdftotext extraction → DR-4 layout template check marked POSSIBLE). |
| **user_trigger** | User verbal explicit override of §F.4 24h same-SHA cooldown: "按这个要求 [demand.md §11 Best-Paper supplement] 和审稿模版审一次稿" → implicit `U-Review-9-decide`. Persona = P5 (the only §0 persona explicitly tagged with Best-Paper / Oral-track gatekeeping). |

---

## Document classification

`document_type` = **full_paper** (8-page main body + Limitations + 5 Appendices A–E + References; 13 rendered pages).

`submission_track` = EMNLP Long Paper — evaluated **for Oral / Best-Paper slot** per `demand.md §11.5`.

---

## Summary (≤ 100 words)

An organizational-emergence framing (EDO) that delivers a Stage-1 prototype (TCPB) which the paper itself admits is Pareto-dominated by a trivial `self_claim` baseline on HotpotQA-200 single-seed. Against the **Best-Paper bar** (`demand.md §11`), the submission fails 9–10 of 12 §11.5 addendum items: single benchmark (no ≥3 datasets), no external 2024–2025 SOTA in main tables, no multi-seed / paired tests / CI, null-effect Table 2 ablations on a legacy non-canonical backbone, no case-study gallery, no Ethical Considerations section, Figure 1 placeholder, and a headline result that actively refutes the method. oral_quality_score ≤ 3 per §11.5 enforcement.

---

## Desk-reject risks (`desk_reject_risks`) — against `docs/demand.md §2`

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | Main body ends §5 Conclusion on rendered p.8 (build script COMPLIANT); §4.5 cites Appendix D **only as "preliminary … do not include in the main results"** → Self-Contained Main Body Rule satisfied; Appendices B/C/D/E exempt per post-U-021 `demand.md §2`. |
| DR-2 | **PASS** | Section titled exactly `Limitations` immediately after Conclusion, before References. |
| DR-3 | **PASS** (borderline) | 7 Limitations items are scope statements + cross-refs; no new experiments / figures / tables. |
| DR-4 | **POSSIBLE – not verified** | pdftotext extraction cannot audit `acl.sty` modifications. Tex-level override of default "Anonymous ACL submission" header to "Anonymous EMNLP 2026 Submission" (tex lines 26–33) is `\renewcommand`-based, not a style-file edit. A careful SAC should request LaTeX sources. |
| DR-5 | **POSSIBLE – process leak** | Appendix C heading contains "For reproducibility (per Reviewer R-FULL-004 D5 request)" (tex line 366). Internal reviewer batch ID in submitted paper = process-leak metadata; pre-submission must be stripped. |
| DR-6 | **PASS** | Responsible NLP Research Checklist Appendix A B1–B5 complete; AI assistance disclosed (B4); no PII (B5). |
| DR-7 | **PASS** | Coherent long-form, no thin-slicing signal. |
| DR-8 | **PASS** | No ethics red flags. **However**: `demand.md §11.1` / §11.2 Best-Paper template expects an independent **Ethical Considerations** section; its absence here is a §11.5 item-9 miss (not DR-8) — see Best-Paper compliance block. |

Net: 0 confirmed desk-reject; 2 POSSIBLE (DR-4, DR-5) identical to R-FULL-008 observations (re-derived stateless).

---

## Best-Paper structural compliance (`best_paper_structural_compliance`) — `demand.md §11.5`

### §11.1 Section-page allocation audit

| §11.1 item | Expected page range | Delivered | Status |
|-----------|--------------------:|-----------|--------|
| Introduction | 1 – 1.5 | ≈ 1.2 p (p.1–p.2) | ✅ |
| Background / Related Work | 0.75 – 1.5 | ≈ 1 p (p.2–p.3) | ✅ |
| Method | 1.5 – 3 | ≈ 3 p (p.3–p.6) | ✅ |
| **Experiments (THE heaviest)** | **2.5 – 4** | ≈ **2.5 p** (p.6–p.8) at lower bound | ⚠ **borderline** — meets lower bound but no case-study / application block as §11.4 expects |
| Conclusion | 0.5 – 1 | ≈ 0.5 p (p.8) | ✅ |
| Limitations | 0.5 – 2 (Best Papers 1–2) | ≈ 1 p (p.8–p.9), 7 items | ✅ (meets Best-Paper depth) |
| Ethical Considerations | 0.5 – 1 (optional but Best-Paper common) | absent (subsumed into Limitations item 7 demographic/societal) | ❌ missed |

### §11.5 addendum Best-Paper checklist (12 items)

| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | §4 at ≈ 2.5 p lower bound; no case-study block |
| 2 | ≥ 3 diverse datasets in main tables | **❌ fail** | HotpotQA only; MuSiQue + 2WikiMultiHop = Stage-2 future (§4.2 / §4.4 E5) |
| 3 | Latest 12-month SOTA baseline in main tables | **❌ fail** | zero external published baselines in Table 1/2; AutoGen / ChatEval / MAD / MetaGPT / MA-RAG / ReAgent cited in §2 but none benchmarked |
| 4 | Full ablation matrix with per-component ablation (not single "remove whole system") | **❌ fail** | Table 2 has per-component ablation attempts but all show null effects (item 12) on non-canonical backbone (see §11.1 audit) |
| 5 | Multi-seed + paired tests + CI/effect-size on headline comparisons | **❌ fail** | §B2: seed=42 only; §Limitations (4): CI / multi-seed / paired tests explicitly deferred; §4.3 Finding 2: "not yet confirmed with paired statistics" |
| 6 | Error analysis with quantitative named failure modes (not one case) | **❌ fail** | Finding 3 PAR attribution is one observation; §4.5 route-overlap 52 % is one number; no named failure-mode taxonomy |
| 7 | Dedicated case-study / application block with 6–10 visualisations | **❌ fail** | §4.5 is a paragraph (5 lines); no case-study section; Infini-gram mini 2025 used 7 contamination-case Figures by comparison |
| 8 | Limitations ≥ 0.5 page, honest, specific, covers demographic/societal scope | ✅ pass | 7 items, ~1 full page, covers Pareto-domination (item 6), societal/demographic (item 7), integrity event (item 5) |
| 9 | Ethical Considerations / Broader Impact section present | **❌ fail** | No standalone section; subsumed (partially) into Limitations item 7 |
| 10 | Figure 1 = system schematic in Intro, vector-quality, self-contained caption | **❌ fail** | **Figure 1 is explicitly a "[Figure 1 placeholder]"** with caption "Vector asset to be inserted" (PDF p.3). This alone is a Best-Paper dealbreaker. |
| 11 | Public anonymous code/data/model release committed | ⚠ partial | Appendix A B1 commits to runtime code + seed slice + validation scripts + per-run logs; MIT license. No model checkpoints (API-only system). OK for API-based work. |
| 12 | No null-effect ablation tables | **❌ fail** | Table 2 rows {−TCPB, −gate, refreshed-baseline} have literally identical EM/F1/Tok (0.435/0.5597/6430); this is the exact pattern §11.5 item 12 prohibits for Best-Paper evidence integrity |

**Items missed count**: **9 hard failures (#2, #3, #4, #5, #6, #7, #9, #10, #12) + 2 partial (#1, #11)**.

**§11.5 enforcement mapping**:

```
6+ items missed → oral_quality_score ≤ 3 (clear reject for Best-Paper track)
→ oral_quality_score capped at 3.
Assigned oral_quality_score = 2.0
```

---

## Experiments-solidity audit (`experiments_solidity_audit`)

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 multi-dataset | **fail** | HotpotQA only; see §11.5 #2 |
| EXP-2 multi-seed | **fail** | seed=42 only; §B2 |
| EXP-3 significance test | **fail** | §4.3 Finding 2 explicit self-admission |
| EXP-4 effect size / CI | **fail** | §B2: CIs "explicitly not reported" |
| EXP-5 ablation coverage | **partial** | coverage_ratio = 0.5 (TCPB, gate, evidence window on legacy backbone); but 3 rows share identical numbers = null-effect signal; Stage-2 R1/R2/R3 unablated |
| EXP-6 baseline recency | **fail** | zero external 2024–2025 SOTA in main tables; stale = N/A because "baselines" are authors' own internal variants |
| EXP-7 sensitivity sweep | **partial** | ±2× routing-weight sweep in §4.5; other priors (λ_a, safety-gate thresholds, force-forward gate decisions) unswept |
| EXP-8 error analysis | **fail** | no quantitative failure-mode taxonomy |

**`experiments_solidity_score` = 1 / 8**.

**Caps implied by audit** (per `reviewer_prompt.md §2.5.1`):

```
EXP-1 fail: cap D4 at 6
EXP-2 fail: cap D4 at 5 AND cap S5 at 4
EXP-3 fail: cap D4 at 6 AND cap S5 at 5
EXP-5 coverage_ratio 0.5 borderline: cap D4 at 6 AND cap S7 at 5
EXP-6 fail: cap D4 at 5 AND cap S6 at 4
experiments_solidity_score <= 3: cap D4 at 4 AND cap overall at 4.5
S6 < 5 (assigned 2): cap overall at 6.0
S7 < 5 (assigned 3.5): cap overall at 6.0
```

Effective D4 cap = **4**; scoring D4 = **3.5** (below cap, to reflect Finding 4 self-refutation on canonical backbone).

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | claimed_difference | is_concrete | is_overlap_risk |
|---|-----------------|------|-------------------|-------------|-----------------|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | Removes (i) globally visible expert table at init, (ii) central decision node, (iii) fixed task script (§2.1). | true | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | Per-hop peer critique → meta-reviewer; TCPB = terminal-outcome only (§2.2). | true | false |
| 3 | Multi-Agent Debate (Liang et al., EMNLP 2024; Du et al., ICML 2024) | 2024 | MAD per-hop debate aggregation; TCPB collapses critique into terminal-only. | **true** | **true** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | Hard-coded SE pipeline; EDO removes pre-assigned role order. | true | false |
| 5 | Reflexion / Tree-of-Thoughts / Self-Refine (Shinn 2023; Yao 2023; Madaan 2023) | 2023 | Single-agent self-reflection; EDO = multi-agent terminal-outcome without per-hop self-score. | true | false |

**Overlap handling**: MAD `is_overlap_risk=true`; §2.2 discusses MAD in 2 sentences, no head-to-head benchmark in main tables. Per `reviewer_prompt.md §2.5.2` hard rule: **cap D3 at 4**. Additional Best-Paper miss: §11.5 item #3 requires latest 2024–2025 SOTA baseline, which would include MAD head-to-head; this is doubly-missed.

---

## Dimension scores (P5 Best-Paper-Committee strict lens)

| Dim | Score | Best-Paper-lens defense |
|-----|-------|--------------------------|
| **D1 Soundness** | **5.5** | Formal utility functions + Algorithm 1 + FIT cosine + Stage-1 scoring equation present; λ values partially hidden in supplement; `forward_bias(j)` functional form undefined; many "hand-set priors, not searched" (§B2). |
| **D2 Significance** | **4.0** | Best-Paper significance band 8 requires "strong impact on a specific subfield with clear cross-area relevance". Delivered empirical story is a self-admitted single-benchmark Pareto-negative result; organizational-emergence framing is interesting but unvalidated in this submission. |
| **D3 Novelty** | **4.0** (cap) | ≥3 named priors with concrete deltas present but MAD overlap unaddressed → hard cap 4. Under P5 Best-Paper lens: delivered novelty is "reframing + restricted prototype"; mechanistic differentiators (R1 / R2 / R3) are theoretical-only per §Limitations (1). |
| **D4 Empirical results** | **3.5** (cap = 4.0) | Against Best Paper §11.1 Experiments "2.5–4 p, THE heaviest section" + §11.5 6–10 case visualisations: section meets lower page bound but has zero case study, zero external baseline, single-seed, no significance, null ablations. Finding 4 actively refutes headline claim on canonical backbone. |
| **D5 Reproducibility** | **6.0** | Algorithm 1 Appendix E full pseudocode ✓; Responsible NLP B1–B5 ✓; seed + hyperparameters tabulated ✓. **Gaps for Best Paper**: full `EVIDENCE_EXTRACT` mapping table offloaded to supplement; several λ constants without values; `forward_bias(j)` undefined; public code exists in anonymous supplement but not every table/figure has a regenerate-this-row script attached (Best Paper standard). |
| **D6 Clarity** | **4.5** | **Figure 1 placeholder is a Best-Paper dealbreaker**. §11.3 "Best-Paper consensus: Figure 1 almost always in Introduction to 'understand at a glance'"; current paper renders the placeholder with caption "Vector asset to be inserted". Figure 2 is publication-quality. Text flow is clear. Under Best-Paper lens, the F1 placeholder alone docks this dimension by 2+ bands. |
| **D7 Limitations** | **7.5** | 7 items (1)–(7) specific and honest. Best Paper bar 8 requires "checklist clearly addressed" + "demographic/societal risks" both present — satisfied; but item 5 (Provider Integrity) is idiosyncratic to this submission's process, not the kind of scope-limit a Best Paper typically emphasises. Honest and specific. |

### Secondary dimensions (S1–S8)

| S | Score | Note under Best-Paper lens |
|---|-------|-----------------------------|
| S1 Executability | 5.5 | Supplement-dependent for some operational details. |
| S2 Falsifiability | 5.5 | Central claim measurable; but the falsification already happened (Finding 4) and the paper pivots rather than re-designing. |
| S3 Empirical plan (design only) | 4.5 | §4.4 E1–E5 is a reasonable agenda but unexecuted; Best Paper bar rewards executed deep design. |
| S4 Technical clarity | 5.5 | Equations + pseudocode present; some symbol definitions offloaded to supplement. |
| **S5 Statistical rigor** | **3.0** | Single seed, no paired test, no CI (capped by EXP-2 @ 4, EXP-3 @ 5; take min). |
| **S6 Baseline quality** | **2.0** | S6 rubric verbatim: "2 = No external baselines at all". Table 1 baselines are authors' own internal method variants. |
| **S7 Ablation completeness** | **3.5** | Table 2 null effects + wrong backbone + no Stage-2 ablation. |
| **S8 Writing and figures** | **4.0** | Figure 1 placeholder + absent case-study gallery (§11.3 expects 6–12 Figures in Experiments) + no Ethical Considerations section. Against Best-Paper camera-ready standard this is several bands below 8. |

**`oral_quality_score` = 2.0** — per `demand.md §11.5` 9 items missed → cap at 3; assigned 2.0 because `reviewer_prompt.md §7` "never grants Oral-eligibility on a single-benchmark or methodology-note submission" compounds with the Pareto-negative headline.

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*5.5 + 0.18*4.0 + 0.15*4.0 + 0.18*3.5 + 0.10*6.0 + 0.07*4.5 + 0.07*7.5
             = 1.375 + 0.720 + 0.600 + 0.630 + 0.600 + 0.315 + 0.525
             = 4.765

Caps applied (per reviewer_prompt §6 + demand.md §11.5):
- DR-4 + DR-5 POSSIBLE only → no DR-confirmed cap
- D1 = 5.5 ≥ 5 → no D1 cap
- D4 = 3.5 < 5 → cap overall at min(4.765, D4+0.5) = min(4.765, 4.0) = 4.0
- D4 = 3.5 < 7 → cap overall at 7.0 (not binding)
- D3 = 4.0 < 5 → cap overall at min(4.0, D3+0.5) = min(4.0, 4.5) = 4.0 (not binding)
- D3 = 4.0 < 6 → cap overall at 6.5 (not binding)
- D7 = 7.5 ≥ 4 → no cap
- falsifiability = 5.5 ≥ 4 → no cap
- oral_quality_score = 2.0 < 5 → cap overall at 5.5 (not binding)
- experiments_solidity_score = 1 ≤ 3 → cap overall at 4.5 (not binding)
- experiments_solidity_score ≤ 5 → cap overall at 6.5 (not binding)
- novelty_delta_audit MAD overlap unaddressed → cap overall at 5.0 (not binding)
- S6 = 2.0 < 5 → cap overall at min(4.0, 6.0) = 4.0 (not binding)
- S7 = 3.5 < 5 → cap overall at min(4.0, 6.0) = 4.0 (not binding)
- demand.md §11.5: 9 items missed → cap oral_quality_score at 3 (already 2.0, not binding)

overall = 4.0
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **4.765** |
| **overall** | **4.0** |
| **verdict** | **weak_reject** (at reject/weak_reject boundary) |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** (target 8.0) |
| **is_best_paper_ready** | **false** (target 8.5); gap = **4.5 overall** + **6.5 oral_quality_score** points |
| **confidence** | **4 / 5** |
| **estimated_score_after_fixes** (sprint-scope: 4 exp fixes + Figure 1 + remove leak + Table 2 re-run) | **5.8–6.2** (overall reaches borderline; Best-Paper bar **still unreachable** because §11.5 items #7 case study + #9 Ethical section + mechanistic novelty from Stage-2 implementation are out-of-sprint scope) |
| **estimated_score_after_Best-Paper-track fixes** (2–3 month agenda: implement R1 or R2 or R3 with empirical wins on ≥3 datasets + head-to-head against MAD/AutoGen/MA-RAG/ReAgent + case-study gallery + Ethical section + Figure 1 final + remove all §11.5 misses) | **7.0–7.5** (Oral border; Best-Paper 8.5 requires an original mechanistic result no prior work has produced, which would require a genuinely novel Stage-2 R2 audit mechanism that measurably beats per-hop debate baselines) |

---

## Top strengths (`top_strengths`)

1. Rare authorial honesty: §Limitations item (6) and Conclusion explicitly admit Pareto-domination on the canonical backbone — Best Papers value this depth of self-critique.
2. Limitations section (7 items, ~1 page) meets Best-Paper depth-1-page guidance (§11.1); Responsible NLP Checklist B1–B5 fully filled.
3. Algorithm 1 Appendix E gives the full Stage-2 operational loop with recursion bounds + clean degenerate projection — a reproducible operational reference at Best-Paper-level specification detail.
4. Figure 2 backbone-sensitivity visualisation is publication-quality and correctly shows the ordering inversion between glm-4-flash and gpt-4.1-mini.

## Top weaknesses (`top_weaknesses`, ranked by Best-Paper-bar severity)

1. **Figure 1 is a placeholder** — `demand.md §11.3` Best-Paper consensus: "Figure 1 = system schematic in Introduction, vector-quality". Current caption literally says "Vector asset to be inserted". This alone is disqualifying for Best Paper.
2. **Zero external published 2024–2025 SOTA in main tables** — §11.5 item #3 hard fail; Table 1/2 are authors' own internal variants; no AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT benchmarked.
3. **Single benchmark only (HotpotQA)** — §11.5 item #2 + `demand.md §8` "minimum 3–5 diverse datasets" hard fail.
4. **Table 2 null-effect ablations on non-canonical backbone** — three rows {−TCPB, −gate, baseline} = identical EM=0.435 / F1=0.5597 / Tok=6430 on glm-4-flash, which §4.2 itself labels "guidance-only, not final paper evidence". §11.5 item #12 hard fail.
5. **Headline result self-falsified** (Finding 4: peer_calibrated F1 < self_claim F1 at equal cost on canonical backbone) — the paper's main method loses to a trivial baseline; Best Papers do not claim victory on a Pareto-dominated prototype.
6. **No case-study / application gallery** — §11.5 item #7 hard fail; Best Papers typically include 6–10 case visualisations in Experiments (Infini-gram mini used 7).
7. **No Ethical Considerations section** — §11.5 item #9 hard fail; standard Best-Paper structural expectation.
8. **No multi-seed / paired test / CI** — §11.5 item #5 hard fail.
9. **MAD overlap unaddressed empirically** — D3 cap at 4; §11.5 Best-Paper novelty expects falsifiable mechanistic differentiation from all named close priors.
10. **DR-5 POSSIBLE process leak**: Appendix C heading "per Reviewer R-FULL-004 D5 request" (tex line 366) — internal reviewer-batch metadata inside submitted paper.

## Core method problems (`core_method_problems`)

1. `forward_bias(j)` topology-driven flow prior in §3.6 TCPB utility — no functional form given in main body or appendices.
2. §3.4 recursive upstream audit is claimed as a key differentiator; delivered Stage-1 sets `AUDIT defaults to ACCEPT on every return` (§3.6 line 384; Algorithm 1 line 18) — the claimed audit mechanism is not exercised in the reported experiments.
3. §3.3 utility equations use λ_c / λ_r / λ_s / λ_m / λ_d as coefficients but only λ_a = 0.02 has a numeric value in the main body; remaining λ values in the supplement.
4. §3.5 persona update uses {η_loc, η_trm, η_rew, μ} weights without numeric values in the main body; Algorithm 1 instead uses ν=0.2 for belief EMA (different update rule).
5. `Cost_self / Risk_self / SendCost / AuditCost / RejectRisk / SplitGain / MergeCost / DepthPenalty / AuditLoad` — symbolic names in §3.3 equations without concrete computations.

## Experimental design problems (`experimental_design_problems`)

1. Table 1 "baselines" are 3 internal method variants of the authors' own system — no external comparator.
2. Table 2 on `glm-4-flash` not canonical `gpt-4.1-mini` — §4.2 itself concedes GLM results are "guidance-only, not the final paper evidence" yet uses them as the only ablation evidence in main body.
3. Table 2 three ablation rows numerically identical → null-effect mechanism or code-path bug — either interpretation damages the "essential mechanism" claim.
4. n=200 canonical Stage-1 evaluation 35× below the HotpotQA dev-split size; §4.3 mentions n=7405 full-validation for peer_calibrated (F1=0.7703) but does not refresh Table 1.
5. No sensitivity sweep on safety-gate thresholds, force-forward-gate decision criteria, or audit thresholds.
6. No head-to-head against MAD despite §2.2 naming MAD and admitting overlap risk.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`)

1. `EVIDENCE_EXTRACT` R3 full lookup table offloaded to anonymous supplement §4.
2. `SplitGain(z) / MergeCost(z) / DepthPenalty(z) / AuditLoad(z)` formulas not given.
3. `Cost_self / Risk_self` referenced but undefined.
4. `FTH = 0.5` terminal threshold + `η_loc / η_trm / η_rew / ρ` coupling to §3.5 update rule not equationally linked.
5. No per-table/per-figure regenerate-me script referenced (Best-Paper reproducibility standard).

## Overclaims / risky framing (`overclaims_or_risky_claims`)

1. Abstract + §1 claim EDO "yields a structured personality-tag space that drives future local allocation decisions" — delivered prototype collapses the vector to a scalar; contribution #2 (recursive upstream audit) is unimplemented.
2. §5 Conclusion pivots to "decentralized outcome-based calibration improves delegation safety" — but §4.3 Finding 3 attributes PAR=0 to the safety gate, not to TCPB.
3. Appendix C heading internal reviewer batch ID leak (DR-5 POSSIBLE).
4. §4.3 "The paper contribution should therefore pivot from 'peer_calibrated is best' to 'the EDO framework explains when and why delegation overhead pays off'" — the pivoted claim is also unvalidated: Finding 3 shows TCPB does not explain PAR behaviour (safety gate does).

## Ambiguous algorithm points (`ambiguous_algorithm_points`)

1. "Mean-axis fold" (§3.6) — not defined; presumed `c[i] = mean(B_i[solve, decompose, …])` but not stated.
2. Algorithm 1 line 11 `a ← argmax{U_S, max_j U_j^O, U_P}` — tie-breaking rule unstated.
3. Algorithm 1 lines 20–22: flow-control from `RejectReroute`-exhaustion to `SPLIT` uses overwritten `a` variable; state transitions ambiguous without a flowchart.
4. §3.5 update coupling: if root task has no parent, terminal correction in Algorithm 1 line 35 applies; equation-level coupling to §3.5 `P_i^{t+1}` not shown.

## Missing definitions / state variables (`missing_definitions_or_state_variables`)

1. `forward_bias(j)` — functional form.
2. `Cost_self(z)`, `Risk_self(z)`, `SendCost(i,j)`, `AuditCost(z)`, `RejectRisk(j,z)` — formulas.
3. `SplitGain(z)`, `MergeCost(z)`, `DepthPenalty(z)`, `AuditLoad(z)` — formulas.
4. "Mean-axis fold" projection.
5. Numeric values for λ_c, λ_r, λ_s, λ_m, λ_d (only λ_a = 0.02 is in the main body).

## Missing or weak experiments (`missing_or_weak_experiments`)

1. No external 2024–2025 SOTA in main tables (AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT).
2. No second or third dataset (MuSiQue / 2WikiMultiHop deferred to Stage-2).
3. No multi-seed runs with paired significance tests on canonical backbone.
4. No confidence intervals or effect sizes on canonical-backbone Table 1.
5. No canonical-backbone ablation table (Table 2 is on legacy glm-4-flash).
6. No MAD head-to-head head-to-head despite overlap risk.
7. No dedicated case-study / application block with visualisation gallery (Best-Paper expectation).

## Statistical significance concerns (`statistical_significance_concerns`)

1. Table 1 point estimates at n=200; no paired bootstrap / sign test; no multiple-comparisons correction.
2. Table 2 three ablation rows share identical EM / F1 / Tok numbers — either null effect or bug; no significance framing either way.
3. Figure 2 overlays n=200 chain and n=7405 fullval data on one panel without statistical harmonisation.

## Baseline completeness concerns (`baseline_completeness_concerns`)

1. Zero external published systems in main tables (S6 = 2.0 per rubric "No external baselines at all").
2. Latest SOTA 2024–2025 multi-hop-QA systems (MA-RAG arXiv:2505.20096, ReAgent arXiv:2503.06951) cited only as Stage-2 roadmap, not benchmarked.
3. `demand.md §8` "strong baselines including latest SOTA" + `demand.md §11.5 #3` "latest 12-month SOTA baseline in main tables" — double miss.

## Limitations section assessment

| Field | Value |
|-------|--------|
| section_present | true |
| section_title_exact | true |
| contains_no_new_content | true |
| honesty_score_1_to_5 | 5 |
| specific_failure_modes_listed | true |
| issues | ["Item (5) footnote 'two affected method runs are queued for re-execution' is marginally operational-status, borderline; a Best-Paper Limitations would frame it as 'Cross-endpoint comparability is an open variable' only without the queued-for-re-execution phrasing"] |

## Responsible NLP Checklist assessment

| Field | Value |
|-------|--------|
| appears_complete | true |
| issues | ["B4 discloses AI code-completion without product name (OK per ACL policy); B2 compute budget at order-of-magnitude"] |

## Implementation risks (`implementation_risks`)

1. Heavy reliance on `[Anonymous Suppl.]` for operational definitions; replicator without supplement fails.
2. `forward_bias(j)` undefined; recoverable only from supplement.
3. λ numeric values scattered across §3.3 / §3.6 / §B2 / Algorithm 1 constants header; not consolidated.
4. "Mean-axis fold" unspecified — replicator must guess.
5. Provider-integrity event (§Limitations 5 + Appendix B) makes cross-channel reproduction potentially irreproducible.

## `what_to_fix_for_8_plus` (generic accept, target overall ≥ 8.0)

1. **Add ≥3 external 2024–2025 SOTA baselines to main tables** (AutoGen + ChatEval + MAD at minimum; MA-RAG / ReAgent for recency) — closes S6 and EXP-6.
2. **Run main results on ≥2 datasets** (MuSiQue minimum) — closes EXP-1.
3. **Multi-seed (≥3) + paired bootstrap CI + paired significance tests** on canonical-backbone Table 1 — closes EXP-2 / EXP-3 / EXP-4.
4. **Re-run Table 2 ablations on canonical `gpt-4.1-mini`** and verify mechanism removal changes F1 (or explain the null effect explicitly).
5. **Replace Figure 1 placeholder with final vector PDF**.
6. **Remove "per Reviewer R-FULL-004 D5 request" from Appendix C heading** (tex line 366) — DR-5 POSSIBLE pre-submission fix.

## `what_to_fix_for_oral` (Oral / Best-Paper bar, target overall ≥ 8.5)

1. Implement at least one of R1 (split) / R2 (audit) / R3 (vector-belief routing) and demonstrate measurable empirical wins against both the Stage-1 baseline and ≥3 external 2024–2025 SOTA on ≥3 diverse datasets with multi-seed paired significance.
2. Add a **dedicated Case Study / Application block in Experiments** with 6–10 visualisation Figures — §11.5 #7 (Infini-gram mini's contamination-case study is the reference model).
3. Add a standalone **Ethical Considerations / Broader Impact** section before References — §11.5 #9.
4. Deliver a mechanistic-novelty claim that no prior work (AutoGen / ChatEval / MAD / MetaGPT / MA-RAG / ReAgent) can match — e.g., a theorem about when recursive audit improves over per-hop debate, or an emergent-organisation metric (specialisation entropy / persona divergence) that prior systems demonstrably fail on.
5. Reverse Finding 4: show the full-EDO system beats `self_claim` on the canonical backbone at equal or lower cost, on ≥2 benchmarks.
6. Public-release code + data + per-table regenerate scripts, with reviewer-visible reproducibility receipts in the main body (not just in supplement).

## `recommended_next_actions`

1. Immediately fix the Appendix C DR-5 POSSIBLE leak (5-minute edit).
2. Re-run Table 2 ablations on canonical `gpt-4.1-mini` backbone to resolve the null-effect signal (blocked on quota; but the 4 new gpt-4.1-mini ablation configs already exist in the anonymous supplement per `ENGINEER_TODO` cross-refs).
3. Land the 3-seed × 7405 full-validation paired-bootstrap pipeline; update Table 1 once all three methods settle.
4. Benchmark AutoGen + ChatEval + MAD + MA-RAG + ReAgent head-to-head on HotpotQA (and, if possible, MuSiQue); include in a main-body external-baseline table.
5. Replace Figure 1 placeholder with final vector asset.
6. Add a Case Study block to Experiments (6–10 case visualisations) and an Ethical Considerations section.

## `rule_source_disagreements`

None. Scoring follows `docs/demand.md` §1–§11 (including the new §11 Best-Paper Structural Template and §11.5 addendum added 2026-04-20) and `prompts/reviewer_prompt.md` §2–§10. `demand.md §11.5` enforcement (oral_quality_score cap by items-missed count) is consistent with `reviewer_prompt.md §5` Oral-gate rubric.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":           true (post-2026-04-20 §11 Best-Paper supplement, 241 lines),
  "edo_paper_pdf_loaded":       true (pdftotext -layout extraction, 1056 lines),
  "fallback_source_used":       "pdftotext -layout article/build/edo_paper.pdf (native PDF attachment not used)",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit — requires LaTeX sources"],
  "demand_section_11_applied":  true (Best-Paper Structural Template + §11.5 addendum applied; 9 of 12 items failed → oral_quality_score capped at 3)
}
```

---

## `_parse_mode`

`full`

*End of review. Human-readable schema coverage per `prompts/reviewer_prompt.md §9` + `demand.md §11.5 best_paper_structural_compliance`.*
