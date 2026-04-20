# R-FULL-008 — Full-paper review (stateless, experiments-focused P2 batch)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260420_211150_08_95e259` |
| **reviewer_profile** | **P2: Empirical-NLP SAC** (D4 / S5 / S6 / S7 specialty; strict, experiments-weighted, no score inflation) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `53F7FB9DE7A3FCB095C3C4A53D0B6D23B324E626CFF55AE921356E42C5D503BE` |
| **pdf_sha16** | `53F7FB9DE7A3FCB0` |
| **rulebook** | `d:\Codes\idea04\docs\demand.md` (read **in full** before scoring: §1 track positioning + §2 formatting + Self-Contained Main Body Rule + §3 unified characteristics + §4 7-dim review criteria + §6 Limitations + §8 experimental design standards + Submission-Ready Checklist) |
| **prior_batch_independence** | No `scoreboard.md`, no prior `review.md` from batches 01–07, no `SCIENTIST_TODO §C` or `fix_themes.md` read. Scoring from paper + rulebook only. |
| **process_compliance (§1.5.0)** | **Satisfied**: entire `docs/demand.md` (118 lines) + full `pdftotext -layout` extraction of the PDF (title through References, 13 rendered pages = 1056 extracted lines) read end-to-end before any scoring. `reference_documents_consulted.demand_md_loaded=true`, `edo_paper_pdf_loaded=true` (as pdftotext extraction, not native PDF ingestion → DR-4 marked POSSIBLE). |
| **user_trigger** | User verbal override of §F.4 24h same-SHA cooldown: "新的审稿人角度，不要被之前的审稿意见左右，你现在是一个全新的审稿人，…特别关注论文的实验，包括 benchmark 的选择、baseline 是否够切题、是否是最新的、提出的方法跑的结果是否 SOTA，实验的评分占比要高" → implicit `U-Review-8-decide`, persona = P2 (the only §0 persona whose specialty is D4/S5/S6/S7 = experiments). |

---

## Document classification

| Field | Value |
|-------|--------|
| `document_type` | **full_paper** (8-page main body + Limitations + Appendices A–E + References; 13 rendered pages total) |
| `submission_track` | EMNLP Long Paper (paper banner: "Anonymous EMNLP 2026 Submission"; rulebook target: EMNLP 2027; identical ARR core rules per `demand.md` footer) |

---

## Summary (≤ 100 words)

The paper reframes multi-agent LLM routing as "organizational emergence" (EDO) and delivers a Stage-1 prototype (TCPB) that it openly admits is Pareto-dominated by a trivial `self_claim` baseline on HotpotQA-200. Under EMNLP long-paper empirical standards (`demand.md §3 / §8`), the evaluated core is a **single public benchmark, single-seed, no significance test, no confidence intervals, and — most critically — no external 2024–2025 published baseline in the main result tables** (neither AutoGen / ChatEval / MAD / MetaGPT / MA-RAG / ReAgent, all named in §2 and as Stage-2 future work, is benchmarked). The Stage-2 mechanism designs (R1/R2/R3) are theoretical-only.

---

## Desk-reject risks (`desk_reject_risks`)

| ID | Status | Evidence (concrete, per `demand.md` §2) |
|----|--------|-----------------------------------------|
| DR-1 | **PASS** | Main body ends §5 Conclusion on rendered p.8 (pdftotext column-order line 603 sits before Limitations start at line 630, consistent with author's `scripts/build_paper.ps1` "main body 8 pages COMPLIANT"); §4.5 cites Appendix D **but explicitly as "preliminary … and do not include it in the main results"** (lines 597–600) → does not depend on appendix for headline evidence. Post–U-021 Path D `demand.md §2`: Appendices are exempt and the self-containment rule is satisfied. |
| DR-2 | **PASS** | Section titled exactly `Limitations` appears immediately after §5 Conclusion (line 630), before References. |
| DR-3 | **PASS** (borderline) | Seven Limitations items are scope statements. Item (5) references Appendix B for the provider-integrity engineering detail (cross-ref, not new content in Limitations itself). No new figures/tables/experiments in Limitations. |
| DR-4 | **POSSIBLE – cannot confirm from extraction** | pdftotext text stream cannot verify `acl.sty` modifications, font-size overrides, margin adjustments, or column-width tampering. PDF banner text says "Anonymous EMNLP 2026 Submission" which `acl.sty` in [review] mode overrides to "Anonymous ACL submission" — the author has documented (tex lines 26–33) overriding the default `acl.sty` header text. **This is a template-level textual override; whether it counts as `acl.sty` modification depends on strict interpretation of `demand.md §2` "No modifications to acl.sty or any style files are allowed". SAC should request the LaTeX sources to verify.** `layout_dependent_checks_blocked` = {DR-4 template audit}. |
| DR-5 | **POSSIBLE – process leak** | **Appendix C heading (rendered p.11) contains "For reproducibility (per Reviewer R-FULL-004 D5 request)"** (tex line 366). This embeds an **internal reviewer batch ID** ("R-FULL-004") in the submitted paper, which (a) reveals the paper has gone through a private multi-reviewer cycle outside OpenReview/ARR, and (b) is the kind of cross-referencing metadata that is expected to be stripped for anonymous submission. Not definitive author identity, but a **process-leak signal that a careful SAC would flag for rewrite before ARR upload**. |
| DR-6 | **PASS** | Appendix A "Responsible NLP Research Checklist" (rendered p.9–10) covers B1 (artifacts + licenses) / B2 (compute + wall-clock + USD + seeds + hyperparameters) / B3 (no human annotators) / B4 (AI assistant disclosure) / B5 (no PII). |
| DR-7 | **PASS** | No evidence of dual / thinly-sliced submission; paper is a coherent long-form. |
| DR-8 | **PASS** | B4 discloses AI code-completion assistant; no hallucinated citations visible; no undisclosed assistance. |

**Net**: 0 confirmed desk-reject; 2 POSSIBLE flags (DR-4, DR-5). Neither caps overall on its own, but DR-5 process-leak is actionable pre-submission.

---

## Experiments-solidity audit (`experiments_solidity_audit`) — **most critical section under P2**

| Check | Status | Evidence / one-line justification |
|-------|--------|-----------------------------------|
| EXP-1 multi-dataset | **fail** | Only HotpotQA is used for any result table. §4.2 explicitly reserves MuSiQue (Trivedi et al., 2022) and 2WikiMultiHop (Ho et al., 2020) for Stage-2 (§4.4 E5). Main tables = 1 dataset, not ≥3. |
| EXP-2 multi-seed | **fail** | §B2: "Random seeds: all chain-200 results in Table 1 and Table 2 use seed=42". §Limitations item (4): "multi-seed variance … deferred to the Stage-2 evaluation agenda". Single seed. |
| EXP-3 significance test | **fail** | §4.3 Finding 2 (lines 520–522): "The gap between the best and worst Stage-1 method is 2.6 F1 points — non-trivial at n=200 **but not yet confirmed with paired statistics**." Explicit self-admission. |
| EXP-4 effect size / CI | **fail** | §B2 (lines 783–786): "Confidence intervals are **explicitly not reported in this submission** and are flagged in §Limitations as future Stage-2 work." |
| EXP-5 ablation coverage | **partial** (but flawed) | Table 2 (rendered p.6) ablates −TCPB and −decomposer-gate; **both show literally identical numbers to the refreshed baseline** (EM=0.435 / F1=0.5597 / Tok=6,430 for baseline, −TCPB, and −gate). Zero effect ⇒ the "essential" mechanisms do not change any measured metric. Also: Table 2 is on `glm-4-flash` **not** the canonical `gpt-4.1-mini` backbone (§4.2.Note: "prior GLM results … are archived as Stage-1 guidance-only artifacts … not the final paper evidence"), so the ablation table does not cover the canonical main-result backbone. Stage-2 R1/R2/R3 mechanisms have zero ablations (unimplemented). `claimed_essential_components = [TCPB terminal update, decomposer safety gate, evidence window, R1 split, R2 audit, R3 vector-belief]`; `components_with_ablation = [TCPB terminal update (null effect on legacy backbone), decomposer gate (null effect on legacy backbone), evidence window (+2.2 F1 on legacy backbone)]`; `coverage_ratio = 3/6 = 0.50`. |
| EXP-6 baseline recency | **fail** | **Main-result baselines** (Table 1) are `self_claim`, `static_roles`, `peer_calibrated` — all three are **internal method variants of the authors' own system**, not external published baselines. oldest_baseline_year=N/A (authors' own); latest 2024-publication-year external SOTA present in a main table = **none**. AutoGen / ChatEval / MAD / MetaGPT / ChatDev / AgentVerse / Reflexion / Tree-of-Thoughts / Self-Refine are all cited in §2 Related Work but **none is benchmarked**. For an EMNLP 2026/2027 submission, HotpotQA SOTA of the past 12 months (e.g., MA-RAG, arXiv:2505.20096, 2025; ReAgent, arXiv:2503.06951, 2025; or any Multi-Agent Debate variant on multi-hop QA) is **not** included. `latest_sota_present=false`. `stale_baselines=["self_claim / static_roles / peer_calibrated are internal variants, not external published systems"]`. `missing_recent_sota=["AutoGen 2024 (Wu et al., ICLR 2024)", "ChatEval 2024 (Chan et al., ICLR 2024)", "Multi-Agent Debate 2024 (Liang et al., EMNLP 2024; Du et al., ICML 2024)", "MA-RAG (arXiv:2505.20096, 2025)", "ReAgent (arXiv:2503.06951, 2025)", "MetaGPT 2024 (Hong et al., ICLR 2024)"]`. |
| EXP-7 sensitivity sweep | **partial** | §4.5 (lines 585–587): "±2× weight-sensitivity sweeps yield < 0.003 pp F1 change". One sweep on routing weights; ≥3 values implied but not explicitly tabulated. No sweep on λ_a, λ_c, λ_r, safety-gate thresholds, or force-forward gate decision criteria. |
| EXP-8 error analysis | **fail** | §4.3 Finding 3 attributes PAR=0 to the safety gate (not TCPB) — one attribution observation, not a quantitative taxonomy. §4.5 adds "peer_calibrated reproduces ~52% of static routes" — one route-overlap number, not a named failure-mode classification. No "failure case X hop N occurs in Y% of errors with cause Z" style analysis. |

**`experiments_solidity_score` = 1 / 8** (only EXP-7 partial, counted as 0.5 under strict rubric; rounding down to integer = 1 if we count EXP-7 partial as pass, else 0).

**Caps implied by the audit (per `reviewer_prompt.md §2.5.1` & §6)**:

```
EXP-1 fail       → cap D4 at 6
EXP-2 fail       → cap D4 at 5 AND cap S5 at 4
EXP-3 fail       → cap D4 at 6 AND cap S5 at 5
EXP-5 coverage_ratio = 0.5 (borderline) → cap D4 at 6 AND cap S7 at 5
EXP-6 fail (no external / no recent SOTA)
                 → cap D4 at 5 AND cap S6 at 4
experiments_solidity_score <= 3
                 → cap D4 at 4 AND cap overall at 4.5
S6 (baseline_quality) < 5 (it is 2)
                 → cap overall at min(overall, 6.0)
S7 (ablation_completeness) < 5 (it is 3.5)
                 → cap overall at min(overall, 6.0)
```

**Effective D4 cap = min(6, 5, 6, 6, 5, 4) = 4**.

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | claimed_difference | is_concrete | is_overlap_risk |
|---|-----------------|------|-------------------|-------------|-----------------|
| 1 | AutoGen (Wu et al., ICLR 2024) | 2024 | EDO removes (i) globally visible expert table at init, (ii) central decision node owning routing, (iii) fixed task script (§2.1). AutoGen = manager agent dispatches to specialists; EDO = local sparse-graph visibility only. | **true** | false |
| 2 | ChatEval (Chan et al., ICLR 2024) | 2024 | ChatEval = per-hop peer critique aggregated by meta-reviewer (§2.2). TCPB = terminal-only outcome calibration; EDO adds recursive upstream audit but not per-hop debate. | **true** | false |
| 3 | Multi-Agent Debate (Liang et al. 2024; Du et al. ICML 2024) | 2024 | "MAD aggregates per-hop critiques into final decision; TCPB collapses critique into terminal-outcome only and uses peer signal for backbone competence update only" — inferred from §2.2 prose. | **true** | **true** |
| 4 | MetaGPT (Hong et al., ICLR 2024) | 2024 | Hard-coded SE pipeline (PM → architect → engineer); EDO removes the pre-assigned role order (§2.1). | true | false |
| 5 | Reflexion / ToT / Self-Refine (Shinn 2023; Yao 2023; Madaan 2023) | 2023 | Single-agent self-reflection; EDO = multi-agent terminal-outcome calibration without per-hop self-score. | true | false |

**Overlap handling**: MAD `is_overlap_risk=true`. §2.2 devotes ~2 sentences to MAD but **the paper has zero empirical head-to-head against MAD** in main tables. Per `reviewer_prompt.md §2.5.2` hard rule: "If any prior work is `is_overlap_risk=true` and the paper does not directly address the overlap, cap D3 at 4". → **D3 cap at 4**.

Additional missing coverage (named in §2 but not benchmarked): AutoGen, ChatEval, MAD — all three are explicitly Stage-2 future-work items in the paper's SWAP matrix (`external_baseline_plan.md` is referenced via the SCIENTIST_TODO but the submitted paper does not discharge them).

---

## Dimension scores

| Dim | Score | Defense (evidence-tied) |
|-----|-------|-------------------------|
| **D1 Soundness** | **5.5** | Formal utility functions U^self / U^out / U^split (§3.3, lines 319–330), FIT cosine similarity inline (§3.3 line 315), TCPB scalar utility inline displayed equation (§3.6 line 390), full pseudocode Appendix E Algorithm 1 (36 lines including recursion bounds H_max=4 / d_max=3 / n_max=12 / k_max=3). **Gaps**: λ_c, λ_r, λ_s, λ_m, λ_d named in §3.3 equations but numeric values not in main body (only λ_a = 0.02 in §3.6; others implicit in Algorithm 1 constants); `forward_bias(j)` functional form not defined (used in §3.6 equation); `Cost_self / Risk_self / SendCost / AuditCost / RejectRisk / SplitGain / MergeCost / DepthPenalty / AuditLoad` are symbol names without concrete computations. Many pointers to `[Anonymous Suppl.]` §1–3 / §4 for actual definitions. §B2 admits "all are hand-set priors, not searched". |
| **D2 Significance** | **4.5** | Framing (organizational emergence from local interaction) is theoretically interesting, relevant to LLM multi-agent trends. **But** the delivered empirical core is a self-admitted Pareto-dominated negative result on 1 benchmark with 1 seed; this does not demonstrate the significance claim. Impact limited to "direction of research" at this submission. |
| **D3 Novelty** | **4.0** (cap-bound) | ≥3 named priors with concrete deltas present (passes the ≥3-concrete gate). **But** MAD `is_overlap_risk=true` not empirically addressed (§2.2 only 2 sentences, no benchmark) → `reviewer_prompt.md §2.5.2` hard cap = 4. Secondary concern: contribution claim #1 (reframing routing as organizational emergence) is framing-mostly; the concrete mechanisms (R1 split, R2 recursive audit, R3 vector-belief personality tags) that would earn D3 above 5 are explicitly **unimplemented and untested** in the present submission (§Limitations item (1)). |
| **D4 Empirical results** | **3.5** (cap-bound to 4) | Single benchmark / single seed / no paired test / no CI / no external baseline / Table 2 ablations show null effects on a non-canonical backbone / headline result is self-admitted Pareto-dominated by a trivial baseline. Deterministic D4 cap = min(6,5,6,6,5,4) = 4; my assigned D4=3.5 acknowledges that even within the admissible band, the headline evidence actively refutes the method's primary empirical claim (peer_calibrated F1 < self_claim F1 at equal cost, Finding 4). |
| **D5 Reproducibility** | **6.5** | Strong. Algorithm 1 full Appendix E; Responsible NLP B1-B5 complete; hyperparameters tabulated (B2); seed disclosed (=42); anonymous code/data supplement cited. **Gaps**: full mapping table for `EVIDENCE_EXTRACT` R3 only in supplement not paper; numeric values for several λ constants only in Algorithm 1 constants header; `forward_bias(j)` topology-prior formula not in paper. A competent group could replicate Stage-1 within ±10% in 1–2 weeks; Stage-2 is unreproducible because unimplemented. |
| **D6 Clarity** | **5.0** | Clear topic sentences, logical flow OK, equations readable. **Major defect**: **Figure 1 is a [placeholder]** (PDF p.3, explicit text "Vector asset to be inserted"; caption says "Final asset will be a vector PDF; this submission renders the placeholder so that all LaTeX figure numbering resolves correctly"). For a long-paper submission this is a clear unfinished-manuscript signal. Figure 2 is a real matplotlib bar chart and is legible. Table captions are self-contained. |
| **D7 Responsible research & limitations** | **7.5** | Seven Limitations items (1)–(7), specific and honest: (1) restricted Stage-1 scope; (2) entanglement with safety priors; (3) backbone-sensitive ordering with conjectural framing ("we conjecture … not validated by the present submission"); (4) single-seed statistical limitation; (5) provider-integrity cross-endpoint caveat with Appendix B cross-ref; (6) Pareto-domination as delivered-system limitation; (7) demographic/societal scope (English Wikipedia, Western/biographical skew, no multilingual). Responsible NLP Checklist B1–B5 all filled. Misses: broader societal-impact study (paper admits this in item 7). |

### Secondary (S1–S8)

| S | Score | Note |
|---|-------|------|
| S1 executability | 5.5 | Many `[Anonymous Suppl.]` pointers weaken direct implementability from paper alone. |
| S2 falsifiability | 6.0 | Central empirical claim tied to F1 / cost / PAR — measurable, and the negative result is openly reported. |
| S3 empirical plan (design only) | 5.0 | §4.4 E1–E5 design is reasonable but unexecuted; delivered core is narrow. |
| S4 technical clarity | 6.0 | Equations inline, symbols mostly introduced with semantics, but many constants / predicates hidden in supplement. |
| **S5 statistical rigor** | **3.0** | Single seed, no paired test, no CI, no multiple-comparisons correction. Capped by EXP-2 (=4) and EXP-3 (=5). |
| **S6 baseline quality** | **2.0** | "No external baselines at all" in main tables. Per S6 rubric: "2 = No external baselines at all." `demand.md §3` "strong baselines = latest SOTA + multiple competitive systems" fails outright. This is the single most damaging dimension for EMNLP long-paper acceptance. |
| **S7 ablation completeness** | **3.5** | Table 2 ablations show null effects for the two "essential" mechanisms on a legacy backbone; Stage-2 R1/R2/R3 ablations absent. Per S7 rubric: "3.5 ≈ gesture at ablation but not quantitatively effective on canonical setup." |
| S8 writing & figures | 5.0 | Figure 1 placeholder is the dominant drag; Table 1/2/3 are fine; Figure 2 is publication-quality. |

**`oral_quality_score` = 2.5** — per `reviewer_prompt.md §5 / §7 Hard Forbidden Behaviors`: "never grants Oral-eligibility on a single-benchmark or methodology-note submission". Delivered content is methodology-note-adjacent: full framework (EDO) is theoretical, delivered instance (TCPB) is a self-admitted Pareto-dominated negative result.

---

## Score calculation (deterministic)

```
raw_weighted = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*5.5 + 0.18*4.5 + 0.15*4.0 + 0.18*3.5 + 0.10*6.5 + 0.07*5.0 + 0.07*7.5
             = 1.375 + 0.810 + 0.600 + 0.630 + 0.650 + 0.350 + 0.525
             = 4.940

Caps applied (in order, per reviewer_prompt §6):
- DR-4 POSSIBLE + DR-5 POSSIBLE → no DR-confirmed cap (4.0 cap NOT applied)
- D4 = 3.5 < 5 → cap overall at min(4.940, D4+0.5) = min(4.940, 4.0) = 4.0
- D4 = 3.5 < 7 → cap overall at 7.0 (not binding; already 4.0)
- D3 = 4.0 < 5 → cap overall at min(4.0, D3+0.5) = min(4.0, 4.5) = 4.0 (not binding)
- D3 = 4.0 < 6 → cap overall at 6.5 (not binding)
- D7 = 7.5 ≥ 4  → no cap
- falsifiability = 6 ≥ 4 → no cap
- oral_quality_score = 2.5 < 5 → cap overall at 5.5 (not binding)
- experiments_solidity_score = 1 ≤ 3 → cap overall at 4.5 (not binding)
- experiments_solidity_score = 1 ≤ 5 → cap overall at 6.5 (not binding)
- novelty_delta_audit has 1 `is_overlap_risk=true` unaddressed (MAD) → cap overall at 5.0 (not binding)
- S6 = 2.0 < 5 → cap overall at min(4.0, 6.0) = 4.0 (not binding)
- S7 = 3.5 < 5 → cap overall at min(4.0, 6.0) = 4.0 (not binding)

overall = 4.0
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **4.940** |
| **overall** | **4.0** |
| **verdict** | **weak_reject** (overall ∈ [4.0, 5.5) per §6 mapping; sits exactly at the weak_reject/reject boundary) |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **confidence** | **4 / 5** (I am familiar with the multi-agent LLM area and can verify every dimension from the rendered text; one notch below 5 because the PDF was consumed via `pdftotext -layout` rather than as a native PDF attachment, blocking DR-4 template checks.) |
| **estimated_score_after_fixes** | **5.8–6.2** (see `what_to_fix_for_8_plus` — realistic post-fix projection lands mid-borderline because D3 MAD-overlap cap and S6 external-baseline cap are stickier than D4 alone) |

---

## Top strengths (`top_strengths`)

1. Rare authorial honesty: §Limitations item (6) and Conclusion explicitly admit Pareto-domination as a delivered-system limitation, not disguising Finding 4.
2. Strong provider-integrity hygiene: Appendix B separates the engineering response from Limitations (DR-3 PASS) and Appendix A B1–B5 is fully filled.
3. Algorithm 1 in Appendix E fully specifies the Stage-2 execution loop with recursion bounds and a clean degenerate Stage-1 projection — a reproducible operational reference.
4. Figure 2 is publication-quality and correctly visualises the backbone-sensitive ordering inversion between glm-4-flash and gpt-4.1-mini.

## Top weaknesses (`top_weaknesses`, ordered by severity)

1. **Zero external published baselines** in main tables — Table 1 baselines (`self_claim` / `static_roles` / `peer_calibrated`) are all internal variants of the authors' own system; no AutoGen / ChatEval / MAD / MA-RAG / ReAgent / MetaGPT benchmarked (S6 = 2).
2. **Single benchmark (HotpotQA only)** — MuSiQue and 2WikiMultiHop are explicitly deferred to Stage-2 (§4.2, §4.4 E5); fails `demand.md §8` "3–5 diverse datasets" (EXP-1 fail).
3. **Headline result is self-falsifying**: Finding 4 shows `peer_calibrated` (the proposed TCPB) is F1-dominated by `self_claim` at identical token cost — the paper's main method loses to a trivial baseline on the canonical backbone.
4. **No paired significance test / no CI / single seed** — gap of 2.6 F1 at n=200 is reported but not confirmed (EXP-2, EXP-3, EXP-4 all fail).
5. **Table 2 ablations show null effects on a non-canonical backbone** — disabling TCPB or the safety gate yields literally identical EM=0.435 / F1=0.5597 / Tok=6,430 on glm-4-flash; the "essential" mechanisms are not shown to be essential on the canonical backbone.
6. **MAD overlap not empirically addressed** — §2.2 discusses Multi-Agent Debate in 2 sentences and admits is_overlap_risk, but no head-to-head in main tables (D3 cap = 4).

## Core method problems (`core_method_problems`) — category (i)

1. §3.3 utility equations define λ_c / λ_r / λ_s / λ_m / λ_d / λ_a symbols but only λ_a = 0.02 has a numeric value in the main body; remaining λ values live in the anonymous supplement, weakening direct reproducibility.
2. §3.6 TCPB scoring includes `forward_bias(j)` as "a topology-driven flow prior" — no functional form given in main body or Appendix E.
3. §3.4 recursive upstream audit is claimed as a key differentiator from TCPB but in the delivered Stage-1 prototype `AUDIT defaults to ACCEPT on every return` (§3.6 line 384–385; Algorithm 1 default) — the delivered system does not exercise the claimed audit mechanism at all.
4. §3.5 personality-tag update equation P_i^{t+1} uses {η_loc, η_trm, η_rew, μ} weights without numeric values in the main body (Algorithm 1 uses ν=0.2 for belief EMA but that is a different update rule).

## Experimental design problems (`experimental_design_problems`) — category (ii)

1. Main results (Table 1) use **only** internal variants as "baselines" — this is self-comparison + two trivial ablations, not an external baseline set.
2. Table 2 ablations are on `glm-4-flash`, **not** the canonical `gpt-4.1-mini` — an ablation on the non-canonical backbone cannot support claims on the canonical backbone (author concedes in §4.2 "GLM results are archived as Stage-1 guidance-only artifacts … not the final paper evidence").
3. Table 2 mechanism ablations (−TCPB, −gate) produce numbers identical to the baseline — either the ablation code path is buggy or the mechanisms have literally no effect; neither case supports the headline contribution.
4. n=200 for the canonical Stage-1 result is an order of magnitude below typical HotpotQA sample sizes (7405 dev split); the paper's own §4.3 mentions n=7405 full-validation for `peer_calibrated` (F1=0.7703) but does not refresh Table 1 with this measurement.
5. No sensitivity sweep on safety-gate thresholds, force-forward-gate decision criteria, or audit thresholds — only the routing weights (0.55, 0.20, 0.10) are swept.

## Implementation / reproducibility gaps (`implementation_or_reproducibility_gaps`) — category (iii)

1. `EVIDENCE_EXTRACT` R3 "lookup-table from `e.decision` and `e.value_gain` to per-axis EMA increments" — the full mapping table is not in the paper (Appendix C.4 says "full mapping table appears in the anonymous executable specification supplement §4").
2. `SplitGain(z) / MergeCost(z) / DepthPenalty(z) / AuditLoad(z)` formulas not given in main body or appendices; only symbolic names used in §3.3 equations.
3. `Cost_self` and `Risk_self` referenced in U^self equation but never defined.
4. `FTH = 0.5` named as F1 threshold for terminal update sign (Algorithm 1 line 35) but §3.5 update rule uses `η_loc, η_trm, η_rew` without cross-referencing FTH.
5. `∆+ = +0.06, ∆− = −0.10, ρ = 0.5` listed in §B2 as "update step sizes / momentum" but no equation in the paper uses these symbols.

## Overclaims / risky framing (`overclaims_or_risky_claims`) — category (iv)

1. Abstract / §1 claims EDO yields "a structured personality-tag space that drives future local allocation decisions" — delivered prototype collapses this vector to a scalar; the claim is promissory.
2. §1 Introduction paragraph 5 lists four contributions; contributions 2 and 3 describe mechanisms (recursive upstream audit, value-induced personality tags) that are not empirically demonstrated in the delivered system.
3. §4.3 Finding 1 "The routing mechanism is secondary to generation quality on this benchmark/topology combination" is a strong negative finding, yet the paper still pivots in §5 Conclusion to claim "the HotpotQA evidence supports the narrower premise that decentralized outcome-based calibration improves delegation safety" — but Finding 3 attributes PAR=0 to the safety gate not TCPB.
4. Appendix C heading "For reproducibility (per Reviewer R-FULL-004 D5 request)" leaks internal reviewer process metadata into the submitted paper (DR-5 POSSIBLE).

## Ambiguous algorithm points (`ambiguous_algorithm_points`)

1. §3.6: "the vector belief B_i^t(j) is collapsed onto a scalar c[i] via mean-axis fold" — "mean-axis fold" is not defined (presumably `c[i] = mean(B_i[solve, decompose, …])` but the operational definition is not stated).
2. Algorithm 1 line 11: `a ← argmax{U_S, max_j U_j^O, U_P}` — tie-breaking rule not specified.
3. Algorithm 1 line 22: "else a ← SPLIT ▷ escalate to RESPLIT" — the escalation condition post-RejectReroute-exhaustion is flow-controlled but Line 25 "if a = SPLIT then" uses the same `a` that was possibly overwritten inside the if/else chain; the state-flow semantics are ambiguous without a flowchart.
4. §3.5 recursive audit: what happens if the root task has no parent to audit the final accept? (Algorithm 1 line 35 applies a terminal correction; the coupling to §3.5 update is not equated explicitly.)

## Missing definitions / state variables (`missing_definitions_or_state_variables`)

1. `forward_bias(j)` — "topology-driven flow prior", no functional form.
2. `Cost_self(z)`, `Risk_self(z)`, `SendCost(i,j)`, `AuditCost(z)`, `RejectRisk(j,z)` — symbols used in §3.3 utility equations, formulas not given in main body.
3. `SplitGain(z)`, `MergeCost(z)`, `DepthPenalty(z)`, `AuditLoad(z)` — Split utility in §3.3, formulas not given.
4. "Mean-axis fold" — the Stage-1 projection from R7 vector to scalar (§3.6).
5. Numeric values of λ_c, λ_r, λ_s, λ_m, λ_d (λ_a=0.02 is the only one given in the main body; others only referenced).

## Missing or weak experiments (`missing_or_weak_experiments`)

1. No external 2024–2025 published SOTA in main tables (AutoGen / ChatEval / Multi-Agent Debate / MA-RAG / ReAgent / MetaGPT all missing).
2. No second dataset (MuSiQue / 2WikiMultiHop deferred to Stage-2 E5).
3. No multi-seed runs with paired significance tests on canonical backbone.
4. No confidence intervals or effect sizes on canonical-backbone Table 1.
5. No ablation of TCPB/gate on canonical `gpt-4.1-mini` backbone (only the legacy glm-4-flash variant).
6. No head-to-head against Multi-Agent Debate despite §2.2 acknowledging overlap risk.

## Statistical significance concerns (`statistical_significance_concerns`)

1. Table 1 reports point estimates for n=200; no paired bootstrap / paired t / sign test despite 3-method comparison; no multiple-comparisons correction.
2. Table 2 "ablation" numbers are identical across −TCPB / −gate / baseline — if this is not a code-path bug, the effect is exactly zero; reporting three identical rows without a significance statement is unusual.
3. Figure 2 overlays chain-200 (n=200) and fullval (n=7405) data points for peer_calibrated only; cross-backbone comparison at different n is not statistically framed.

## Baseline completeness concerns (`baseline_completeness_concerns`)

1. Zero external published systems in any main table — the authors' own method variants are the only comparators.
2. Latest SOTA for multi-hop QA on HotpotQA from the past 12 months (MA-RAG 2025, ReAgent EMNLP 2025) is named in Related Work as Stage-2 roadmap but not benchmarked.
3. `demand.md §8` explicitly requires "strong baselines including latest SOTA" and "minimum 3–5 diverse datasets" — both are missed.

## Limitations section assessment

| Field | Value |
|-------|--------|
| section_present | true |
| section_title_exact | true (`Limitations`) |
| contains_no_new_content | true (items (1)–(7) are scope statements; engineering details for (5) are in Appendix B) |
| honesty_score_1_to_5 | 5 |
| specific_failure_modes_listed | true (Pareto-domination, backbone sensitivity, single-seed, single-benchmark, cross-endpoint variability, demographic scope) |
| issues | ["item (5) footnote 'the two affected method runs are queued for re-execution' is marginally process-tracking; `demand.md §6` requires Limitations discuss scope/honesty not operational status — but this is a borderline stylistic issue, not DR-3"] |

## Responsible NLP Checklist assessment

| Field | Value |
|-------|--------|
| appears_complete | true |
| issues | ["B4 discloses AI code-completion assistant but does not name the product (OK per ACL policy which does not require naming)", "B2 compute budget is in USD+wall-clock+calls order-of-magnitude; OK"] |

## Implementation risks (`implementation_risks`)

1. Many `[Anonymous Suppl.]` cross-references for operational formulas (`EVIDENCE_EXTRACT` mapping, full ϕ rule set, safety-gate thresholds) — a replicator without the supplement would fail.
2. `forward_bias(j)` is used in the delivered TCPB utility but never formulated; a reimplementer cannot recover it from the paper.
3. `FTH = 0.5` + `η_loc, η_trm, η_rew` update weights listed in §B2 but the coupling to §3.5 update rule requires guessing.
4. Algorithm 1 line 35 Stage-1 fallback ("project B^{t+1} → c via mean-axis fold") depends on an unspecified fold; a reimplementer would guess.
5. Reliance on an OpenAI-compatible provider channel whose model drift (§Limitations item 5 / Appendix B) was a mid-submission event; replicators may see different results on a different channel.

## `what_to_fix_for_8_plus`

1. **Add ≥3 external published baselines to main tables** (AutoGen / ChatEval / MAD minimally; MA-RAG 2025 or ReAgent 2025 for recency SOTA) — closes S6 / EXP-6.
2. **Run main results on ≥2 datasets** (add MuSiQue at minimum; 2WikiMultiHop preferred) — closes EXP-1.
3. **Move to multi-seed (≥3) + paired bootstrap CI + paired significance test** on the canonical-backbone Table 1 — closes EXP-2 / EXP-3 / EXP-4.
4. **Re-run Table 2 ablations on canonical `gpt-4.1-mini` backbone** and ensure mechanism removal changes F1 (or drop the ablation and explain why mechanisms are null-effect).
5. **Benchmark Multi-Agent Debate head-to-head** on HotpotQA to close MAD overlap risk — closes D3 cap.
6. **Replace Figure 1 placeholder with the final vector PDF** — closes D6 / S8 presentation defect.

## `what_to_fix_for_oral`

Oral requires `oral_quality_score ≥ 8.5` which this submission cannot reach at current scope. Minimally:

1. Implement at least one of R1 / R2 / R3 and demonstrate empirical wins against both the Stage-1 baseline and an external 2024-2025 SOTA, on ≥2 datasets.
2. Add ≥3 diverse benchmarks (HotpotQA + MuSiQue + 2WikiMultiHop + at least one non-QA task family where "organizational emergence" would be expected to help).
3. Deliver a concrete falsifiable claim tied to an emergent-organization metric (specialisation entropy, persona-divergence, or similar) that prior systems demonstrably fail on.
4. Replace the Finding 4 Pareto-domination story with a setting where the full-EDO system actually wins.

## `recommended_next_actions`

1. Fix the Appendix C heading to remove "per Reviewer R-FULL-004 D5 request" — this is a 5-minute pre-submission anonymization fix.
2. Land the 3-seed × 7405 fullval paired-bootstrap pipeline (the paper itself mentions "full-validation pass" is in flight); update Table 1 once all three methods settle on canonical backbone.
3. Reproduce at least AutoGen + ChatEval + MAD on HotpotQA with module-swap comparison as described in §4.4 E5; add a compact external-baseline table before Stage-2 completes.
4. Replace Figure 1 placeholder with the final vector PDF; this is a trivial-looking but reviewer-visible defect.

## `rule_source_disagreements`

None. Scoring follows `d:\Codes\idea04\docs\demand.md` §1–§8 (EMNLP 2027 rulebook, which per footer is identical to the 2026 ARR CFP that the paper banner uses) and `prompts/reviewer_prompt.md §2.5 / §3 / §4 / §6 / §7` caps. The rulebook note that "baselines from before 2025 are presumed stale unless explicitly justified" (`reviewer_prompt.md §1.5.2`) is consistent with the paper's 2026 submission banner; the latest published SOTA from the past 12 months relative to a 2026-cycle ARR submission means 2024 Q4 – 2025 Q4 work must be present as a baseline, and this submission has zero such systems in main tables.

## `reference_documents_consulted`

```
{
  "demand_md_loaded":           true,
  "edo_paper_pdf_loaded":       true (as pdftotext -layout extraction; native PDF attachment not used → DR-4 template tampering cannot be verified from text stream, marked POSSIBLE),
  "fallback_source_used":       "pdftotext -layout article/build/edo_paper.pdf (86364 B extraction, 1056 lines, read end-to-end)",
  "layout_dependent_checks_blocked": ["DR-4 acl.sty modification audit — requires LaTeX sources or native PDF ingestion"]
}
```

---

## `_parse_mode`

`full`

*End of review (human-readable schema coverage per `prompts/reviewer_prompt.md §9` fields rendered as markdown, per `REVIEWER_TODO §F.3` "only review.md is the required artifact; review.json not generated").*
