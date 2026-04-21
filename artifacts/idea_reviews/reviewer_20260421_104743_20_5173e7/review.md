# R-FULL-020-B — Full-paper review (P2 Empirical-NLP SAC STRICT, target = Best Paper 8.5)

## Batch metadata

| Field | Value |
|-------|--------|
| **review_run_id** | `reviewer_20260421_104743_20_5173e7` |
| **reviewer_profile** | **P2: Empirical-NLP SAC** (focused on D4 / S5 / S6 / S7; treats single-benchmark + single-seed + weak baseline coverage as borderline-reject by construction) |
| **target_pdf** | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| **pdf_sha256** | `5173E71FD1E1AF49604B036F54D9CF48F5B89F0C3A6E102C83F273B59DE2ADFA` |
| **pdf_sha16** | `5173E71FD1E1AF49` |
| **target_score** | **8.5** (Best-Paper bar per `docs/demand.md §11.5`) |
| **prior_batch_independence** | **stateless** — this batch is written as a fresh P2 review of the current PDF; no prior `review.md` is used as evidence. |
| **rulebook** | `docs/demand.md §1–§11` + `prompts/reviewer_prompt.md §2–§10` |
| **process_compliance (§1.5.0)** | **Satisfied**: `docs/demand.md` read end-to-end; current `article/build/edo_paper.pdf` read end-to-end (16 pages in current build). |

---

## Document classification

`document_type` = **full_paper**. `submission_track` = EMNLP Long Paper — Best-Paper / Oral bar.

**DR-1 PASS**: current build reports main body page 8 COMPLIANT and `Limitations` starts on page 9.

---

## Summary (≤ 100 words)

This revision improves the paper's **reviewer awareness**: §2 now names **MA-RAG 2025** and **ReAgent 2025**, and §2.2 gives a concrete textual delta between TCPB/EDO and MAD-style critique aggregation. However, the **empirical core is still the same bottleneck**: one benchmark, one seed, zero paired significance tests, zero confidence intervals, and zero external 2024–2025 SOTA systems in the main result tables. Under a strict P2 lens, the paper is still **borderline-reject by construction**. The revision raises D3 modestly, but **D4/S5/S6/S7 remain the binding weaknesses**, so the verdict stays **4.5 weak_reject**.

---

## Desk-reject risks (`desk_reject_risks`)

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | **PASS** | Current build: main body ends on page 8; `Limitations` starts on page 9 |
| DR-2 | PASS | Exact section title `Limitations` after Conclusion |
| DR-3 | PASS | No new experimental claims inside `Limitations` |
| DR-4 | POSSIBLE – not verified | Text/PDF reading cannot fully audit `acl.sty` tampering |
| DR-5 | PASS | No internal reviewer-id/process leak remains |
| DR-6 | PASS | Responsible NLP checklist appears complete and consistent |
| DR-7 | PASS | Coherent long-paper manuscript rather than thin slice |
| DR-8 | PASS | AI assistance disclosed; Ethical Considerations present |

Net: **0 confirmed desk rejects; 1 POSSIBLE (DR-4)**.

---

## Best-Paper structural compliance (`best_paper_structural_compliance`)

### §11.5 addendum

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Experiments ≥ 2.5 content pages | ⚠ partial | close to lower bound, but still not Best-Paper-heavy |
| 2 | ≥ 3 diverse datasets in main tables | **❌ fail** | HotpotQA only |
| 3 | Latest 12-month SOTA in main tables | **❌ fail** | MA-RAG/ReAgent now cited in §2, but still absent from result tables |
| 4 | Per-component ablation on canonical backbone | **❌ fail** | only legacy `glm-4-flash` Table 2 ablations |
| 5 | Multi-seed + paired tests + CI/effect-size | **❌ fail** | single seed=42; paired CI deferred |
| 6 | Quantitative error analysis | **❌ fail** | no failure-mode frequency table |
| 7 | Dedicated case-study / application block | **❌ fail** | none |
| 8 | Honest Limitations ≥ 0.5 page | ✅ pass | strong |
| 9 | Ethical Considerations section | ✅ pass | present |
| 10 | Figure 1 high-quality system schematic | ❌ fail | still placeholder |
| 11 | Public anonymous code/data/model release | ⚠ partial | code/data yes, model no |
| 12 | No null-effect ablation table | ⚠ partial | Table 2 caption is honest, but null-effect rows remain unresolved |

**Count**: 7 hard + 3 partial + 2 pass.  
Per `docs/demand.md §11.5`, this keeps `oral_quality_score ≤ 3`.

---

## Experiments-solidity audit (`experiments_solidity_audit`)

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 (multi-dataset) | **fail** | HotpotQA only |
| EXP-2 (multi-seed) | **fail** | seed=42 only |
| EXP-3 (significance test) | **fail** | no paired bootstrap / sign test in submission-version headline results |
| EXP-4 (effect size or CI) | **fail** | no 95% CI in main claims |
| EXP-5 (ablation coverage) | **partial** | some ablation exists, but only on non-canonical backbone and without Stage-2 component coverage |
| EXP-6 (baseline recency) | **fail** | zero external 2024–2025 SOTA in main tables |
| EXP-7 (sensitivity sweep) | **partial** | limited weight sweep exists |
| EXP-8 (error analysis) | **fail** | no quantitative taxonomy |

**`experiments_solidity_score` = 1 / 8**.

P2 consequence:
- single benchmark,
- single seed,
- no significance,
- no CI,
- no external recent SOTA,
- incomplete canonical ablation,

jointly keep **D4 capped at 4** and therefore **overall capped at 4.5**.

---

## Novelty delta audit (`novelty_delta_audit`)

| # | prior_work_name | year | claimed_difference | is_concrete | is_overlap_risk | P2 note |
|---|-----------------|------|-------------------|-------------|-----------------|---------|
| 1 | AutoGen | 2024 | removes central router / global expert table | true | false | concrete and still relevant |
| 2 | ChatEval | 2024 | current-turn critique aggregation vs routing-state calibration | true | false | concrete |
| 3 | Multi-Agent Debate | 2024 | edge-level accepted-value update rather than debate transcript aggregation | true | true | **now directly addressed in §2.2 text**, so the earlier “unaddressed overlap” problem is reduced, but still lacks empirical head-to-head |
| 4 | MA-RAG | 2025 | fixed retrieval stack vs local-visibility social updating | true | false | good addition to §2 |
| 5 | ReAgent | 2025 | rollback control protocol vs reputation/routing update process | true | false | good addition to §2 |

**P2 reading**: the revision meaningfully improves prior-work positioning, so D3 no longer deserves the harsher “paper is unaware of 12-month SOTA” interpretation. But because the paper still has **no main-table comparison** to those systems, this remains mostly a **textual clarification**, not an empirical novelty confirmation.

---

## Dimension scores (P2 strict empirical lens)

| Dim | Score | Rationale |
|-----|-------|-----------|
| **D1 Soundness** | **6.5** | method objects remain formalized enough for Stage-1 |
| **D2 Significance** | **4.5** | still limited by single-benchmark, single-seed evidence |
| **D3 Novelty** | **5.0** | improved from prior P2-style reading because §2 now directly names MA-RAG/ReAgent and concretely distinguishes MAD-style critique aggregation from routing-state calibration; still not stronger without head-to-head |
| **D4 Empirical** | **4.0** | strict P2 cap: single benchmark, seed, no CI, no recent SOTA baselines in tables |
| **D5 Reproducibility** | **6.5** | solid for a paper-only description |
| **D6 Clarity** | **5.0** | Figure 1 placeholder still hurts |
| **D7 Responsible research** | **8.0** | strong Limitations + Ethical coverage |

### Secondary (S1–S8)

| S | Score | Note |
|---|-------|------|
| S1 executability | 6.5 | Stage-1 executable from paper + appendices |
| S2 falsifiability | 5.5 | clearer than before, but main claim still under-tested |
| S3 empirical plan | 5.5 | reasonable future plan, not yet delivered |
| S4 technical clarity | 7.0 | improved by cleaner positioning and formal appendices |
| **S5 statistical rigor** | **3.0** | single seed, no paired test, no CI |
| **S6 baseline quality** | **2.0** | **still no external baselines in main tables** |
| **S7 ablation completeness** | **4.0** | canonical-backbone / Stage-2 component ablation still absent |
| S8 writing and figures | 5.0 | Figure 1 placeholder persists |

**`oral_quality_score` = 2.5**.

---

## Score calculation

```text
raw_weighted
= 0.25*6.5 + 0.18*4.5 + 0.15*5.0 + 0.18*4.0 + 0.10*6.5 + 0.07*5.0 + 0.07*8.0
= 1.625 + 0.810 + 0.750 + 0.720 + 0.650 + 0.350 + 0.560
= 5.465

Caps applied:
- D4 = 4.0 < 5          → overall capped at 4.5 (binding)
- experiments_solidity=1 → overall capped at 4.5 (binding)
- oral_quality=2.5       → oral cap unchanged
- S6 = 2.0               → ceiling remains low even after empirical improvements
```

| Field | Value |
|-------|--------|
| **weighted_sum_pre_cap** | **5.465** |
| **overall** | **4.5 weak_reject** |
| **verdict** | **weak_reject** |
| **oral_eligible** | **false** |
| **is_8_plus_ready** | **false** |
| **is_best_paper_ready** | **false** |
| **confidence** | **4 / 5** |

---

## Top strengths (`top_strengths`)

1. **Current PDF is cleaner and more reviewer-aware than earlier versions**: related work is now materially better calibrated to 2025 systems.
2. **MAD overlap is now textually addressed with a concrete mechanistic distinction**, which is a real improvement in D3 framing.
3. **Stage-1 method description remains reproducible and internally consistent**.
4. **Limitations + Ethical sections are strong and honest**.

## Top weaknesses (`top_weaknesses`)

1. **No external 2024–2025 SOTA systems in the main result tables**. Citing MA-RAG/ReAgent in §2 is not a substitute for benchmarking them.
2. **Single benchmark**: HotpotQA only.
3. **Single seed**: seed=42 only.
4. **No paired significance test / no CI** for the current submission-version headline claims.
5. **Canonical-backbone ablation missing**; Table 2 remains on `glm-4-flash`.
6. **Figure 1 still placeholder**.
7. **No quantitative error taxonomy** despite repeated reviewer requests.

---

## Missing or weak experiments (`missing_or_weak_experiments`)

1. MA-RAG / ReAgent / MAD / AutoGen / ChatEval **must appear in main tables**, not only in Related Work.
2. MuSiQue / 2WikiMultiHop or another second/third benchmark is still absent.
3. E-017 three-seed paired fullval is still not landed in the paper.
4. E-014 canonical-backbone ablation is still missing.
5. No quantitative failure-mode table.

---

## Statistical significance concerns

1. Table 1 remains based on `n=200` with no paired bootstrap.
2. §4.4/§4.5 still defer CI/statistics rather than presenting them.
3. Single-seed fullval cannot support Best-Paper-bar claims.

---

## Baseline completeness concerns

1. **S6 remains 2.0 by P2 rubric** because the main tables still contain only author-internal variants.
2. The revision now shows awareness of **MA-RAG 2025** and **ReAgent 2025**, which is good, but this only fixes the *citation gap*, not the *baseline gap*.
3. Without external main-table baselines, the paper cannot establish that its method is competitive, only that it is internally coherent.

---

## What to fix for 8+ (target overall ≥ 8.0)

1. **Land E-017 seeds 43/44 + paired bootstrap CI**.
2. **Put at least two external 2024–2025 SOTA systems in the main tables**.
3. **Add a second benchmark** (MuSiQue minimum).
4. **Add canonical-backbone ablation**.
5. **Add quantitative error analysis**.
6. Replace Figure 1 placeholder.

---

## What to fix for Oral / Best-Paper (target overall ≥ 8.5)

1. All of the above.
2. Reverse the current “single-benchmark / single-seed / no external-SOTA” triad.
3. Show that the method is not only conceptually distinct, but **empirically competitive** against the newest systems it now cites.

---

## Recommended next actions

1. **Highest priority**: finish `E-017` and report paired CI in the paper.
2. **Next highest**: land `E-018` / `E-015` main-table external baselines.
3. Add the first quantitative error taxonomy from existing logs; this is the only meaningful non-LLM empirical improvement available immediately.
4. Land canonical-backbone Table 2 replacement.
5. Replace Figure 1 placeholder.

---

## Reference documents consulted

```json
{
  "demand_md_loaded": true,
  "edo_paper_pdf_loaded": true,
  "pdf_sha256": "5173E71FD1E1AF49604B036F54D9CF48F5B89F0C3A6E102C83F273B59DE2ADFA",
  "persona": "P2 Empirical-NLP SAC strict",
  "target_score": 8.5,
  "key_change_vs_immediately_previous_pdf": "§2 now includes MA-RAG 2025 + ReAgent 2025 and a concrete MAD-vs-TCPB mechanistic distinction, but experiments remain unchanged in substance",
  "core_verdict_rationale": "The revision improves reviewer-facing novelty positioning, but the empirical package still fails the P2 core triad: single benchmark, single seed, zero recent external SOTA in main tables. Therefore D4 remains capped at 4 and overall remains 4.5 weak_reject."
}
```

---

## `_parse_mode`

`full`

*End of review. This batch gives credit for the related-work / novelty-defense improvements, but under a strict experiments-weighted SAC lens, the submission still cannot clear the empirical bar until multi-seed statistics, external main-table SOTA baselines, and at least one additional benchmark land in the paper itself.*
