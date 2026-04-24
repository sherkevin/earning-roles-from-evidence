# Review of `article/build/edo_paper.pdf` (R-FULL-006)

> **Reviewing standard**: EMNLP 2026 Long Paper Track. Stateless reviewer; did not consult prior R-FULL-001/002/003/004/005 review content, scoreboard, or fix_themes during scoring. Prior batch existence and persona rotation are known only as facts (used to pick a non-overlapping persona angle); per-dimension scores are derived independently from the paper text + `prompts/reviewer_prompt.md` rubric + `docs/demand.md` rulebook.
>
> **User feedback acknowledgment**: "不够严厉，你的审稿太过于温和" (regarding R-FULL-005). I have admitted in `R-FULL-005/review.md` STRICT REVISION errata block that R-FULL-005 inflated D1=5.5 / D5=5.5 / D6=6.0 / D7=7.5 / S1-S4 / S7-S8 / oral by giving credit for "scientist made hygiene effort" rather than evaluating content quality against rubric bands. R-FULL-006 P5 strict scoring is calibrated to that admission.

## Metadata

| Field | Value |
|---|---|
| `reviewer_id` | `reviewer_20260419_214636_06_c5c5ad` |
| `reviewer_profile` | **P5 — Best-Paper-Committee chair simulating an Oral-track gatekeeper.** Asks the only question that matters: would this paper be in the top 3-5% of EMNLP submissions? Defaults `oral_quality_score <= 6` unless the paper presents a substantial, original, completed contribution with comprehensive evaluation and clear long-term community impact; never grants Oral-eligibility on a single-benchmark or methodology-note submission. |
| `target` | `d:\Codes\idea04\article\build\edo_paper.pdf` (**365.1 KB / 13 pages, mtime 2026-04-19 21:45:58, SHA256 prefix `8161E9D33B81223D`**) — this is a NEW PDF version (different from R-FULL-005's `4504614E`); scientist re-built the PDF in the ~30-60 min window between R-FULL-005 landing and this user trigger |
| `submission_track` | `EMNLP Long Paper - Oral evaluation` |
| `document_type` | `partial_paper` (full structural form expanded to 13 pages: Abstract / §1-§5 / Limitations / Appendix A B1-B5 / Appendix B / **Appendix C (LLM Prompt Templates, NEW)** / **Appendix D (Preliminary Stage-2 3-shard, NEW)** / Algorithm 1 (Appendix E, NEW location) / References. Stage-2 mechanisms (R1 split / R2 audit / R3 vector belief) admittedly NOT implemented in main results; Appendix D shows preliminary degenerate-Stage-2 3-shard result whose authors themselves admit is "inside noise") |
| `stateless` | confirmed: did not read R-FULL-001/002/003/004/005 review.md during scoring (used only persona-rotation fact) |
| `§F.2 input integrity` | PASS |
| `§F.4 cooldown` | **PDF SHA changed since R-FULL-005** (`4504614E` → `8161E9D3`); cooldown does NOT apply because this is a different PDF version. User explicit verbal trigger constitutes implicit `U-Review-6-decide`. |

## Headline Scores

| Field | Value |
|---|---|
| **`overall`** | **4.5 / 10** (cap-bound; raw weighted_sum = 4.560 < 4.5 cap-floor only by margin) |
| **`verdict`** | **`weak_reject`** |
| **`oral_eligible`** | `false` (oral_quality_score=3.0 < 8.5; D3=4.0 < 7.0; D2=4.0 < 7.0) |
| **`confidence`** | `4` (PDF text via pdftotext-layout extraction; layout-dependent checks for Figure 1 quality + DR-4 template tampering blocked, but structural reading is highly reliable since I have the full 13-page text) |
| **`is_8_plus_ready`** | `false` |
| **`estimated_score_after_fixes`** | `5.5-6.0` (after MuSiQue + 3-seed CI + 1 external SOTA baseline + 1 Stage-2 mechanism actually delivered with empirical win) |
| **acceptance probability**, my estimate | **~10%** at ARR May 2026 (well below typical EMNLP Long Paper acceptance ~23% due to single-benchmark + single-seed + headline self-falsification structural blockers) |

## Critical Comparison: R-FULL-005 (soft) vs R-FULL-006 (P5 strict)

This batch is explicitly stricter than R-FULL-005 per user feedback "不够严厉". Both batches review essentially the same paper structure (R-FULL-005 PDF SHA `4504614E`; R-FULL-006 PDF SHA `8161E9D3` adds 2 pages of Appendix C/D + FIT formula + TCPB scoring + Limitations items 6+7 + random seed). The strictness adjustment is real and measurable:

| Dim | R-FULL-005 soft | R-FULL-005 errata strict | **R-FULL-006 P5 strict (this)** | Notes |
|---|---:|---:|---:|---|
| D1 soundness | 5.5 | 4.5 | **5.0** | New PDF added FIT + TCPB scoring formulas (real improvement); but multiple λ + Cost/Risk/SplitGain/MergeCost/DepthPenalty/AuditLoad/SendCost functional forms still undefined; persona-update µ/η coefficients undefined → band 5 ("Material gaps; concept intuitive but not implementable") with mitigations up |
| D2 significance | 4.0 | 4.0 | **4.0** | Unchanged: Pareto-dominated headline + Stage-2 mechanisms still not implemented; Appendix D preliminary inside noise |
| D3 novelty | 4.0 | 4.0 | **4.0** | Unchanged: Multi-Agent Debate `is_overlap_risk=true` still not benchmarked (D3 hard cap at 4 per §3) |
| D4 empirical_results | 4.0 | 4.0 | **4.0** | Unchanged: capped by EXP audit (single-bench + single-seed + no significance + no external SOTA + headline self-falsified) |
| D5 reproducibility | 5.5 | 4.0 | **5.0** | New PDF: prompt templates inline in Appendix C (was supplement only) + FIT defined + TCPB scoring formula + random seed=42 = substantial reproducibility improvement; but EVIDENCE_EXTRACT lookup table + multiple λ values + functional forms still in supplement → band 5 "Reproduction would require re-deriving large method portions" |
| D6 clarity | 6.0 | 5.0 | **5.0** | Figure 1 caption explicitly admits placeholder ("Vector asset to be inserted") still in this PDF; Algorithm 1 now in Appendix E (separated from §3.6 main-body reference, minor structural friction) |
| D7 limitations | 7.5 | 5.5 | **6.0** | New PDF expanded Limitations 5→7 items: item (6) Pareto-domination explicit + item (7) demographic/societal/multilingual scope ✓; but per-method failure-mode breakdown still missing; multiple "Stage-2 will fix" pattern items pull toward band 5-6 → band 6 honest |
| S1 executability | 5.0 | 4.5 | **4.5** | TCPB Stage-1 mostly executable from paper now (Algorithm 1 + B2 + Appendix C prompts + FIT + TCPB scoring); but full EDO Stage-2 R1/R2/R3 still requires supplement |
| S2 falsifiability | 5.5 | 4.5 | **4.5** | TCPB sub-claim is falsifiable AND self-falsified (admitted in §5 Conclusion + Limitations item 6); central EDO claim "emergent organization from local interaction" still NOT testable as designed because Stage-2 mechanisms not implemented |
| S3 empirical_plan | 6.0 | 5.0 | **5.0** | §4.4 E1-E5 5-study agenda + 8 organizational metrics + Appendix D preliminary execution attempt; plan well-designed but execution mostly absent |
| S4 technical_clarity | 6.0 | 5.0 | **5.5** | New PDF: FIT explicit formula + TCPB scoring formula + Appendix C prompts inline = real clarity improvement on previously-undefined symbols |
| S5 statistical_rigor | 2.0 | 2.0 | **2.5** | Appendix D Table 3 reports cross-shard mean ± std (n=3 shards) — mild improvement over zero variance reporting in Tables 1-2; but n=3 is far below standard, no paired test, no CI |
| S6 baseline_quality | 2.0 | 2.0 | **2.0** | Unchanged: zero external 2024-2026 SOTA in Table 1 |
| S7 ablation_completeness | 5.5 | 4.5 | **5.0** | Same Table 2 (glm-4-flash only) + §4.5 sensitivity sweep + Appendix D's "with vs without Stage-2 mechanism" semi-ablation as preliminary; coverage_ratio ≈ 0.5 |
| S8 writing_and_figures | 6.0 | 5.0 | **5.0** | Figure 1 placeholder still in PDF; Algorithm 1 (Appendix E) nicely formatted; multiple Appendices well-organized; bibliography 12+ named entries |
| **oral_quality_score** | 3.0 | 2.5 | **3.0** | "Reject; major rework required" tier per §5 mapping. P5 strict default = no Oral path on single-benchmark / single-seed / headline-self-falsified submission, regardless of writing quality. The +1 over R-FULL-005 errata 2.5 reflects meaningful Stage-2 preliminary engineering (Appendix D) |
| **`weighted_sum`** | **4.910** | **4.300** | **4.560** | R-FULL-006 P5 strict raw is +0.260 above R-FULL-005 errata raw, reflecting actual content improvements; but -0.350 below R-FULL-005 soft, reflecting the strictness correction |
| **`overall`** (after caps) | 4.5 | 4.3 | **4.5** | Cap binding: D4 < 5 + experiments_solidity_score ≤ 3 both pin at 4.5 |
| **`verdict`** | weak_reject | weak_reject | **weak_reject** | All three converge: weak_reject |

**Key observation**: scientist did REAL work (5+ substantive PDF additions in <60 min after R-FULL-005), and that improvement is visible in `weighted_sum` rising from R-FULL-005 errata strict 4.300 → R-FULL-006 strict 4.560 (+0.260). But the cap floor at 4.5 (driven by `experiments_solidity_score = 1/8`) absorbs the improvement. **The lever for moving overall above 4.5 is exclusively `experiments_solidity_score` — D5/D7/S4 improvements alone cannot break the cap because their weights (0.10/0.07/0) are too small to overcome the §6 D4 + experiments_solidity caps.**

## Summary (≤ 100 words)

The paper proposes Emergent Delegation Organization (EDO) with full Stage-2 algorithm specified (Appendix E) but the delivered TCPB system is a degenerate Stage-1 instance (SPLIT disabled, AUDIT defaults to ACCEPT, vector belief collapsed to scalar). New PDF version (since R-FULL-005) adds: FIT formula in §3.3, TCPB scoring formula in §3.6, Appendix C with 4 LLM prompt templates, Appendix D with 3-shard preliminary Stage-2 result (admittedly inside noise), Limitations expanded to 7 items including societal scope, random seed disclosure. These are real improvements (D5/D7/S4 lifted from R-FULL-005 strict) but `experiments_solidity_score = 1/8` cap (single benchmark + single seed + no significance + no external SOTA) still binds final overall at 4.5.

## Reference Documents Consulted

| Field | Value |
|---|---|
| `demand_md_loaded` | `true` — `docs/demand.md` re-verified for §2 page rule, §6 Limitations rule, §7 Responsible NLP Checklist |
| `edo_paper_pdf_loaded` | partial — read via `pdftotext -layout` extraction (full 86 KB text dumped); did NOT read PDF as native PDF attachment |
| `fallback_source_used` | `pdftotext -layout` extraction at `$env:TEMP\edo_paper_r6_strict_audit.txt` (deleted post-review per §F.3) |
| `layout_dependent_checks_blocked` | DR-4 (template tampering); D6 Figure 1 final visual quality (caption admits placeholder); some figure positioning checks |
| `rule_source_disagreements` | (empty) — no rubric clauses conflict with `docs/demand.md` |

## Verified Document Structure (from pdftotext page markers)

| PDF Page | Content (mapped from pdftotext line ranges) |
|---:|---|
| 1 | Abstract + §1 Introduction (with new sentences "the Stage-2 mechanisms are theoretical in this submission") |
| 2 | §1 cont. + §2 Related Work start |
| 3 | §2 (orchestration / reflection / organization theory) + Figure 1 placeholder |
| 4 | §3.1 Problem formulation (with new "decentralized within a fixed role-prior topology with hand-tuned safety priors") + §3.2 Agent state + §3.3 Task signatures (with NEW explicit FIT formula at line ~308-312) |
| 5 | §3.3 utility equations / §3.4 Recursive audit / §3.5 Personality update / §3.6 with NEW explicit TCPB scoring formula `U^out = 0.55 c[j] + 0.20 accept(j) + 0.10 forward_bias(j) - λ_a audit(z)` |
| 6 | §3.7 Why separation matters / Prototype Scope Box / §3.8 Stage-2 Roadmap / §4.1 What current evidence establishes |
| 7 | §4.2 setup / §4.3 Findings 1-2 + Table 1 + Table 2 + Figure 2 |
| 8 | §4.3 Findings 3-4 (Finding 3 NEW: PAR=0 attributed to safety gate, NOT TCPB) / §4.4 / §4.5 (with new Appendix D reference) / §5 Conclusion (rewritten honest version) / Limitations item (1) start |
| 9 | Limitations items (2)-(7) (item 6 Pareto-dominated NEW + item 7 demographic/societal NEW) + Appendix A B1 |
| 10 | Appendix A B2 (with NEW random-seed paragraph: "all chain-200 results use seed=42") / B3 / B4 / B5 |
| 11 | Appendix B Provider Integrity Event (full) + **Appendix C: LLM Prompt Templates start** |
| 12 | Appendix C cont. (LLM_DECOMPOSE / AUDIT-LLM-fallback / EVIDENCE_EXTRACT mapping) + **Appendix D: Preliminary Stage-2 Prototype 3-Shard Paired Result + Table 3** + Algorithm 1 (Appendix E) start |
| 13 | Algorithm 1 cont. + References (12+ entries) |

**Main body §1-§5 + Limitations all in pages 1-9 cap-compliant** ✅. Appendices A-E + References spread across pages 9-13 (not counted toward 8-page main-body limit).

## Step 2: Desk-Reject Pre-flight (DR-1 .. DR-8)

| ID | Trigger | Status | Evidence |
|---|---|---|---|
| **DR-1** | Page-limit (main body > 8 pages) | **PASS** | §5 Conclusion title at PDF page 8 (pdftotext line 531, between page-7 marker line 496 and page-8 marker line 568); Limitations title at pdftotext line 560 still on page 8. Pages 9-13 = Limitations cont. + Appendix A/B/C/D + Algorithm 1 + References (all excluded from 8-page main body cap per `docs/demand.md §2`). |
| **DR-2** | Limitations title exact | **PASS** | Title is exactly "Limitations" |
| **DR-3** | New material in Limitations | **PASS** | All 7 items are scope statements; item (5) cross-references Appendix B; item (6) Pareto-domination scope statement; item (7) demographic/societal scope. No new methods/experiments/results inside §Limitations. |
| **DR-4** | Template tampering | **NA** | Cannot confirm from pdftotext extraction |
| **DR-5** | Anonymization breach | **PASS** | "Anonymous EMNLP 2026 Submission"; "anonymous code/data supplement"; "[Anonymous Suppl.]"; **Appendix C heading explicitly says "per Reviewer R-FULL-004 D5 request"** — this is a borderline anonymization concern (revealing internal review batch ID) but likely will be removed in camera-ready; flagged for awareness, not as DR-5 trigger |
| **DR-6** | Responsible NLP Checklist skipped | **PASS** | Appendix A B1-B5 complete with new random-seed paragraph in B2 |
| **DR-7** | Dual / sliced submission | **NA** | No obvious slicing markers |
| **DR-8** | Ethics policy violation | **PASS** | B4 AI assistant disclosure explicit; no hallucinated citations detected |

**Result**: 0 confirmed desk-reject triggers. **However**, the "per Reviewer R-FULL-004 D5 request" phrase in Appendix C heading is a process-leak that should be removed before final submission (mentioning internal review batch IDs in the paper itself is unusual and could trigger DR-5 anonymization concerns at strict interpretation, even if the batch IDs are scientist-internal not author-identifying).

## Step 3: Experiments-Solidity Pre-Audit

| Check | Status | Evidence |
|---|---|---|
| EXP-1 multi-dataset (≥3 datasets, ≥2 task families) | **fail** | Same as R-FULL-005: HotpotQA only. Appendix D 3-shard paired result is also HotpotQA. |
| EXP-2 multi-seed (≥3 seeds, list reported) | **fail** | §Limitations item (4) admits "deferred to Stage-2"; B2 now discloses seed=42 but it's a single seed identification |
| EXP-3 significance test (paired) | **fail** | §4.3 Finding 2 still admits "not yet confirmed with paired statistics"; Appendix D Table 3 reports `mean ± std` for n=3 shards which is NOT a paired statistical test (no paired bootstrap, no sign test, no permutation) |
| EXP-4 effect size or 95% CI | **partial** | NEW: Appendix D Table 3 has `mean ± std` for 3 shards (1.05 pp F1 std) — first variance-style reporting in the paper, but n=3 is far below standard for effect-size estimation |
| EXP-5 ablation coverage | **partial** | Same Table 2 (glm-4-flash, 4 variants) + §4.5 weight sensitivity + static-path overlap; Appendix D's "with vs without R1/R2 active" semi-ablation as preliminary; coverage_ratio ≈ 0.5; Stage-2 mechanism components (R1 R2 R3) still 0 ablation |
| EXP-6 baseline recency (latest SOTA, ≥50% baselines from past 24 mo) | **fail** | Unchanged: Table 1 = author-internal routing variants; AutoGen / MAD / ChatEval cited but not benchmarked; latest_sota_present = false |
| EXP-7 sensitivity sweep (≥3 values per critical hyperparameter) | **partial** | §4.5 weight ±2× narrative only; 1 hyperparameter; the 9 hand-set priors in B2 not individually swept |
| EXP-8 error analysis (named failure modes, not single case) | **partial** | NEW: Appendix D notes "EM trends mildly negative... missing synthesizer pass that future Stage-2 iterations must restore" — explicit failure mode hypothesis. Combined with §4.5 static-path overlap + Finding 4 narrative; still no per-method failure-mode breakdown table |

**experiments_solidity_score = 1 / 8** (only EXP-5 borderline-pass)

**Caps implied by audit (per §2.5.1)**:
- EXP-1 fail → cap D4 at 6
- EXP-2 fail → cap D4 at 5 + cap S5 at 4
- EXP-3 fail → cap D4 at 6 + cap S5 at 5
- EXP-6 fail → cap D4 at 5 + cap S6 at 4
- experiments_solidity_score ≤ 3 → **cap overall at 4.5** (binding)
- experiments_solidity_score ≤ 5 → cap overall at 6.5 (subsumed)

## Step 4: Novelty Delta Audit

Same as R-FULL-005 structurally — paper still has 12 named priors, MAD remains `is_overlap_risk=true` and is NOT benchmarked. §3.1 added "decentralized within a fixed role-prior topology with hand-tuned safety priors" honest-framing addition does not change the novelty audit.

| Prior Work | Year | Concrete delta? | `is_overlap_risk` |
|---|---:|---|---|
| AutoGen | 2024 | true | false |
| MetaGPT | 2024 | true | false |
| Reflexion | 2023 | true | false |
| **Multi-Agent Debate (Liang et al.; Du et al.)** | **2024** | partial | **TRUE — TCPB is degenerate case of MAD per-hop aggregator with full-trajectory window; not benchmarked** |
| ChatDev | 2024 | true | false |

**Caps**: cap D3 at 4 (per §3 D3 hard rule, MAD overlap unaddressed); cap overall at 5.0 (per §6, not binding because 4.5 < 5.0).

## Step 5: ARR 7-Dimension Scores (D1-D7)

See the Critical Comparison table above for the full justifications. Key scoring decisions:

- **D1 = 5.0**: Algorithm 1 (Appendix E) full Stage-2 PROCESS recursion + NEW FIT formula in §3.3 + NEW TCPB scoring formula in §3.6 are real and substantive. But: λ_c, λ_r, λ_s, λ_d, λ_m all numeric values undefined (only λ_a = 0.02 mentioned); functional forms of Cost_self / Risk_self / SendCost / AuditCost (numeric) / RejectRisk / SplitGain / MergeCost / DepthPenalty / AuditLoad / forward_bias all undefined; persona update µ / η_loc / η_trm / η_rew undefined; AUDIT non-default rule decision-table in supplement; EVIDENCE_EXTRACT lookup table in supplement. Per band 5 ("Material gaps: a concept is intuitive but not implementable from the paper") with mitigating FIT/TCPB additions → 5.0.

- **D2 = 4.0**: Pareto-dominated headline + Stage-2 mechanisms admittedly not implemented + Appendix D preliminary inside noise. Limited significance unchanged structurally.

- **D3 = 4.0**: Capped by MAD overlap unaddressed (per §3 D3 hard rule).

- **D4 = 4.0**: Capped by EXP audit (single-bench + single-seed + no significance + no external SOTA + headline self-falsified). Per band 4 ("Single benchmark, single seed, weak baselines, no ablations; results may be within noise").

- **D5 = 5.0**: Substantial reproducibility improvement (4 prompt templates inline + FIT defined + TCPB scoring defined + random seed=42 disclosed) but EVIDENCE_EXTRACT lookup table + multiple λ values + functional forms still in supplement. Per band 5 ("Reproduction would require re-deriving large method portions") with mitigations up.

- **D6 = 5.0**: Figure 1 placeholder still in PDF (caption explicitly says "Vector asset to be inserted"); Algorithm 1 in Appendix E (separated from §3.6 main-body reference creates minor reading friction). Per band 5 ("Substantial revision needed for figure quality").

- **D7 = 6.0**: New items (6) Pareto-domination + (7) demographic/societal scope are real additions; but per-method failure-mode breakdown still missing, multiple "Stage-2 will fix" pattern items pull toward band 5-6 → band 6 honest. Item (7) is 1 sentence — would need expansion to ~3 sentences with concrete multilingual / cultural-bias examples to reach band 7-8.

## Step 5 cont.: ARR 8 Secondary Dimension Scores (S1-S8)

| Dim | Score | Brief rationale |
|---:|---:|---|
| **S1 executability** | **4.5** | TCPB Stage-1 mostly executable from paper now; full EDO Stage-2 still requires supplement |
| **S2 falsifiability** | **4.5** | TCPB testable AND self-falsified; central EDO claim still not testable as designed |
| **S3 empirical_plan** | **5.0** | §4.4 E1-E5 plan + Appendix D preliminary execution attempt; plan well-designed but main execution absent |
| **S4 technical_clarity** | **5.5** | NEW FIT + TCPB scoring formulas + Appendix C prompts add clarity; multiple λ + functional forms still undefined |
| **S5 statistical_rigor** | **2.5** (capped at 4 by EXP-2; capped at 5 by EXP-3) | Appendix D Table 3 has cross-shard mean ± std (n=3) — first variance reporting; mostly point estimates |
| **S6 baseline_quality** | **2.0** (capped at 4 by EXP-6) | Zero external 2024-2026 SOTA in Table 1; AutoGen/MAD/ChatEval cited but not benchmarked |
| **S7 ablation_completeness** | **5.0** | Table 2 (glm-4-flash) + Appendix D semi-ablation; Stage-2 components still 0 ablation |
| **S8 writing_and_figures** | **5.0** | Figure 1 placeholder still; Algorithm 1 (Appendix E) nicely formatted; bibliography 12+ entries |

## `oral_quality_score` (P5 STRICT view)

**`oral_quality_score = 3.0`**

Per §5 mapping: band 3 = "Reject; major rework required". P5 strict view ("Best-Paper-Committee chair simulating an Oral-track gatekeeper... never grants Oral-eligibility on a single-benchmark or methodology-note submission") rules:
- Substantial? **NO** — Stage-2 mechanisms theoretical, only TCPB delivered, and TCPB is Pareto-dominated
- Original? **PARTIAL** — framing original but mechanism overlaps MAD without benchmark
- Completed? **NO** — admittedly Stage-2 not implemented, Appendix D preliminary inside noise
- Comprehensive evaluation? **NO** — single benchmark, single seed
- Long-term community impact? **UNCLEAR** — Pareto-dominated headline suppresses impact

P5 verdict: not on a path to acceptance, not Oral. The +1 over R-FULL-005 errata 2.5 reflects acknowledgment of meaningful Stage-2 preliminary engineering (Appendix D) which signals ongoing improvement trajectory.

## Step 7: Score Calculation (deterministic, with caps shown)

```
weighted_sum = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*5.0 + 0.18*4.0 + 0.15*4.0 + 0.18*4.0 + 0.10*5.0 + 0.07*5.0 + 0.07*6.0
             = 1.250 + 0.720 + 0.600 + 0.720 + 0.500 + 0.350 + 0.420
             = 4.560

caps_triggered (in order):
  - DR confirmed:                          NO (all PASS or NA)
  - D1 (Soundness) < 5:                    NO (D1=5.0)
  - D4 (Empirical) < 5:                    YES (D4=4.0) → cap overall at min(weighted_sum, D4 + 0.5)
                                                          = min(4.560, 4.5) = 4.5  ← BINDING (raw > cap)
  - D4 (Empirical) < 7:                    YES (D4=4.0) → cap at 7.0 (not binding)
  - D3 (Novelty) < 5:                      YES (D3=4.0) → cap at min(4.5, 4.5) = 4.5 (already at floor)
  - D3 (Novelty) < 6:                      YES (D3=4.0) → cap at 6.5 (not binding)
  - D7 (Limitations) < 4:                  NO (D7=6.0)
  - falsifiability < 4:                    NO (S2=4.5)
  - oral_quality_score < 5:                YES (oral=3.0) → cap at 5.5 (not binding)
  - experiments_solidity_score ≤ 3:        YES (1) → cap at 4.5  ← BINDING (same)
  - experiments_solidity_score ≤ 5:        YES (1) → cap at 6.5 (subsumed)
  - novelty_delta_audit unaddressed
    `is_overlap_risk=true` (MAD):          YES → cap at 5.0 (not binding 4.5 < 5.0)
  - S6 (baseline_quality) < 5:             YES (S6=2.0) → cap at 6.0 (not binding)
  - S7 (ablation_completeness) < 5:        NO (S7=5.0)

final_overall = 4.5  →  verdict per §6 thresholds: overall in [4.0, 5.5) → "weak_reject"
```

**Triple-binding cap @ 4.5**: D4 < 5 + experiments_solidity_score ≤ 3 + (D3<5 dim cap) all converge at 4.5. Raw weighted_sum 4.560 > 4.5 → cap binds → final 4.5.

## Honest Acknowledgment of Scientist's Real Improvements (R-FULL-005 → R-FULL-006 PDF)

Despite the cap-bound final overall = 4.5 (unchanged), the new PDF reflects substantive scientist work in the ~30-60 minute window between R-FULL-005 landing and this trigger:

1. ✅ **§3.3 explicit FIT formula** added: `Fit(P, ϕ) = ⟨P, ϕ⟩/(‖P‖·‖ϕ‖) ∈ [0, 1]; in Stage-1 TCPB, P and ϕ collapse onto a scalar (mean-axis fold)` — closes S-137 (R-FULL-004 NEW-2)
2. ✅ **§3.6 explicit TCPB scoring formula** added: `U_i^out(z, j) = 0.55 c[j] + 0.20 accept(j) + 0.10 forward_bias(j) - λ_a audit(z)` with λ_a = 0.02 — closes S-136 (R-FULL-004 NEW-1)
3. ✅ **Appendix C: LLM Prompt Templates** (≤ 1 page, 4 templates: LLM_ANSWER / LLM_DECOMPOSE / AUDIT-LLM-fallback / EVIDENCE_EXTRACT) — closes S-138 (R-FULL-004 NEW-3)
4. ✅ **Appendix D: Preliminary Stage-2 3-shard paired result** with Table 3 (+1.65 pp F1, -37.1% tokens, but explicitly admitted "inside noise") — first Stage-2 empirical signal, even if preliminary
5. ✅ **§B2 random seed disclosure**: "all chain-200 results in Table 1 and Table 2 use seed=42 for both example slicing (deterministic first-200 of the HotpotQA validation split) and any internal stochasticity" — closes S-140 (R-FULL-005 NEW-2)
6. ✅ **§Limitations expanded 5→7 items**: item (6) "Delivered-system Pareto-domination" now explicit (was previously only in Conclusion narrative); item (7) "Demographic and societal scope: HotpotQA is sourced exclusively from English Wikipedia and skews toward Western, biographical, and factual entities; the present evaluation does not test multilingual generalisation, low-resource language behaviour, or culturally diverse query distributions" — closes S-139 (R-FULL-005 NEW-1)
7. ✅ **§5 Conclusion rewritten honest**: "EDO proposes three moves... None is empirically demonstrated here; the delivered TCPB system is a restricted Stage-1 instantiation that implements only the third (terminal supervision) in fixed-topology, role-prior form, and is Pareto-dominated by a simpler self-claim baseline at equal token cost on a single benchmark — a delivered-system limitation, not a refutation of the broader framework" — addresses R-FULL-005 over-claim concern
8. ✅ **§3.1 honest framing addition**: "decentralized within a fixed role-prior topology with hand-tuned safety priors (role-prior nodes decomposer/evidence_seeker/verifier/synthesizer and a hand-coded force-forward gate, with routing weights locally computed)" — addresses R-FULL-005 over-claim #3
9. ✅ **Finding 3 honesty correction**: NEW text "The PAR= 0 outcome is attributable to the decomposer force-forward gate (Algorithm 1 line 11), a fixed safety prior that already saturates PAR for self_claim and static_roles; the TCPB peer-calibration mechanism itself does not provide additional PAR reduction in the delivered Stage-1 configuration. The safety gate is robust to backbone change; TCPB's PAR contribution on top of the gate is not demonstrated here." — addresses R-FULL-005 over-claim #2

These improvements are visible in the dimension-level score increases (D5 4.0→5.0, D7 5.5→6.0, S4 5.0→5.5, S5 2.0→2.5, etc.) summing to **weighted_sum +0.260 over R-FULL-005 strict errata raw**. But the §6 D4 + experiments_solidity caps absorb the improvement and final overall remains 4.5.

## `top_strengths` (4 items)

1. **Substantive reproducibility improvements landed**: §3.3 explicit FIT formula + §3.6 explicit TCPB scoring formula + Appendix C 4 LLM prompt templates + B2 random seed=42 disclosure together close most of the previously-open D5 reproducibility gaps. A competent group can now ~80% reproduce TCPB from the paper alone (was ~30%).
2. **Limitations section is best-in-class for honesty**: 7 items including item (6) explicit Pareto-domination admission and item (7) demographic/societal scope; §5 Conclusion explicitly states "None is empirically demonstrated here" for Stage-2 mechanisms; rare academic honesty.
3. **Algorithm 1 (Appendix E) specifies the full EDO Stage-2 PROCESS recursion** with R1/R2/R3 line markers + bounds (Hmax=4, kmax=3, dmax=3, nmax=12) + Stage-1 fallback projection — meaningful formalization commitment.
4. **Appendix D shows nascent Stage-2 engineering**: 3-shard paired comparison of TCPB vs degenerate-Stage-2 prototype with token-cost reduction (-37.1%) measurable across shards (σ=0.19%); the F1 effect is honestly admitted as inside noise — preliminary but real engineering progress signal.

## `top_weaknesses` (6 items, ordered by severity, P5 strict)

1. **STRUCTURAL FATAL — `experiments_solidity_score = 1/8`**: single HotpotQA + single seed + zero paired statistical test + zero external 2024-2026 SOTA. §6 cap locks `overall` at 4.5 regardless of any improvement on writing/algorithm/framing. **This is the only structural blocker; everything else is secondary.** The paper cannot exceed 4.5 until at least 4 of the 8 EXP checks pass.
2. **STRUCTURAL FATAL — Stage-2 mechanisms (R1 split / R2 audit / R3 vector belief) admittedly NOT implemented**: Algorithm 1 (Appendix E) specifies the full Stage-2 loop, but Table 1 reports only its degenerate Stage-1 instance (TCPB). What the paper claims as "main contribution: EDO framework + Stage-2 mechanisms as proposed components" is structurally NOT what the paper measures empirically. Appendix D 3-shard preliminary attempts a degenerate-Stage-2 step but explicitly reports F1 inside noise.
3. **STRUCTURAL FATAL — All Table 1 baselines are author-internal routing variants**: Zero external 2024-2026 multi-agent SOTA in Table 1. AutoGen / MetaGPT / Multi-Agent Debate / ChatEval all CITED in §2 but ZERO benchmarked. Multi-Agent Debate specifically is `is_overlap_risk=true` in §2.5.2 audit (TCPB's terminal-outcome is degenerate case of MAD's per-hop aggregator). Caps D3 at 4 + caps overall at 5.0.
4. **D5/D1 — multiple coefficients and functional forms still undefined**: λ_c, λ_r, λ_s, λ_d, λ_m all numeric values undefined (only λ_a=0.02 mentioned); functional forms of Cost_self / Risk_self / SendCost / AuditCost (as a function) / RejectRisk / SplitGain / MergeCost / DepthPenalty / AuditLoad / forward_bias all undefined; persona update µ / η_loc / η_trm / η_rew undefined; EVIDENCE_EXTRACT lookup table in supplement. Reading paper alone allows ~80% reproduction of TCPB but exact replication still requires anonymous supplement.
5. **D6/S8 — Figure 1 caption explicitly admits placeholder** ("Vector asset to be inserted; full design specification in the anonymous figure-prompt supplement"). For an EMNLP submission targeting Oral consideration this is inappropriate; Figure 1 is the methods-section opening figure and should be camera-ready quality at submission.
6. **D7 — Limitations item (7) demographic/societal scope is 1 sentence**, no concrete multilingual / dataset-bias / cultural-bias examples; no per-method failure-mode breakdown table; multiple Limitations items are framed as "Stage-2 will fix this" pattern (band 5 territory) rather than honest scope-bounding (band 7+ territory).

## `core_method_problems`

1. EDO Stage-2 mechanisms (R1 split / R2 audit / R3 vector belief) admittedly NOT implemented as live mechanisms in main results; Algorithm 1 (Appendix E) lines 14-16 (split branch), 16-23 (audit branch), 32-34 (vector update) all gated to default behavior in delivered TCPB.
2. Algorithm 1 references multiple undefined coefficients λ_c, λ_r, λ_s, λ_d, λ_m and undefined functions Cost_self / SendCost / AuditCost / SplitGain / MergeCost / DepthPenalty / AuditLoad. While the recently-added §3.6 TCPB scoring formula partially closes the Stage-1 instantiation gap, full Stage-2 utility computation remains unspecified.
3. AUDIT non-default rule (Algorithm 1 line 16) — paper now provides Appendix C.3 LLM-fallback variant decision rules in narrative form, but the rule-based default referenced in §3.8 is still in supplement.
4. EVIDENCE_EXTRACT(e, ϕ(z)) → R^7 mapping (Algorithm 1 line 33) — paper Appendix C.4 confirms it's a "deterministic rule-based mapping", but the full mapping table is in supplement §4.
5. Persona update equation §3.5 µ / η_loc / η_trm / η_rew — values not given for either Stage-1 or Stage-2 instances.

## `experimental_design_problems`

1. Single benchmark only (HotpotQA distractor n=200); MuSiQue + 2WikiMultiHop both already cited (§4.2, §4.4 E5) as "reserved for Stage-2".
2. Single seed reported in Table 1 / Table 2; B2 NEW disclosure of seed=42 confirms single-seed status.
3. No paired bootstrap / sign test / permutation test in body; §4.3 Finding 2 explicitly admits "not yet confirmed with paired statistics".
4. Zero external multi-agent system baselines in Table 1 — most consequential omission is Multi-Agent Debate (Liang et al., 2024).
5. Table 2 ablation glm-4-flash only — no equivalent on canonical strong backbone (gpt-4.1-mini).
6. Appendix D preliminary Stage-2 result reports n=3 shards × 200 paired samples, but explicitly admits F1 effect "inside noise"; cannot bear weight as Stage-2 mechanism validation.

## `implementation_or_reproducibility_gaps`

1. EVIDENCE_EXTRACT lookup table in supplement (Appendix C.4 confirms).
2. Multiple λ values (λ_c, λ_r, λ_s, λ_d, λ_m) numeric assignments not in paper.
3. AUDIT default rule-based decision rule + threshold values in supplement (§3.8 references "executable spec [Anonymous Suppl.] §4").
4. forward_bias(j) "topology-driven flow prior" (§3.6 TCPB scoring formula component) — functional form not defined.
5. Persona update §3.5 coefficients µ / η_loc / η_trm / η_rew not given.

## `overclaims_or_risky_claims`

1. Conclusion still says "EDO proposes three moves... None is empirically demonstrated here" — this is honest. ✓
2. Abstract says "EDO ... yields a structured personality-tag space that drives future local allocation decisions" — but the personality-tag space is PROPOSED, not implemented or measured. Should add "proposed in this submission" qualifier.
3. Abstract still says "decentralized outcome-based calibration improves delegation safety and stabilizes routing without a central controller" — Finding 3 NEW correction text now explicitly attributes PAR=0 to the safety gate, NOT to TCPB. Abstract should be updated to reflect this Finding 3 correction (currently still implies TCPB drives delegation safety).

## `ambiguous_algorithm_points`

1. Algorithm 1 line 3 / line 5: λ_c (in Cost_self term) and λ_a (in AuditCost term) — λ_a is given as 0.02 in §3.6 TCPB scoring formula but for the abstract Algorithm 1 formulation, λ_a value applicability is unclear; λ_c not given anywhere.
2. Algorithm 1 line 7: SPLITGAIN, MERGECOST functional forms undefined; λ_m, λ_d undefined.
3. Algorithm 1 line 16: AUDIT default = ACCEPT (Stage-1); non-default rule in supplement.
4. Algorithm 1 line 33: EVIDENCE_EXTRACT lookup table in supplement.
5. forward_bias(j) in §3.6 TCPB scoring formula — "topology-driven flow prior" functional form not defined.

## `missing_definitions_or_state_variables`

1. λ_c, λ_r, λ_s, λ_d, λ_m coefficient values (§3.3 utility).
2. µ, η_loc, η_trm, η_rew (§3.5 persona update equation).
3. AUDIT default rule-based decision rule + thresholds (§3.8 R2).
4. EVIDENCE_EXTRACT(·) lookup table (§3.8 R3, Algorithm 1 line 33).
5. forward_bias(j) functional form (§3.6 TCPB scoring formula).

## `missing_or_weak_experiments`

1. No second benchmark — MuSiQue or 2WikiMultiHop both cited as "reserved" in §4.2.
2. No multi-seed runs (admitted deferred in Limitations 4 + B2 single seed=42).
3. No paired bootstrap / sign test / permutation test in body.
4. Zero external multi-agent system baselines (AutoGen / MetaGPT / Multi-Agent Debate / ChatEval all cited but not benchmarked).
5. Table 2 ablation missing on canonical strong backbone (gpt-4.1-mini).
6. Appendix D preliminary Stage-2 result n=3 shards is too small for any conclusion; needs scale-up to multi-seed × multi-benchmark.

## `statistical_significance_concerns`

1. Table 1 / Table 2 / Figure 2 all point estimates only.
2. §4.3 Finding 2 explicitly admits headline 2.6 F1-point gap "non-trivial at n=200 but not yet confirmed with paired statistics".
3. Appendix D Table 3 mean ± std for n=3 shards is NOT a paired statistical test; cross-shard std (σ=0.19% tokens, σ=1.05 pp F1) is a variance estimate, not a significance test.

## `baseline_completeness_concerns`

1. Zero external 2024-2026 multi-agent system baselines in Table 1.
2. Multi-Agent Debate is `is_overlap_risk=true` in novelty audit but not benchmarked.
3. "Centralized baselines" referenced in §4.2 ("compare ... and centralized baselines under shared inputs") but no central_orchestrator row in Table 1.

## `limitations_section_assessment`

| Field | Value |
|---|---|
| `section_present` | `true` |
| `section_title_exact` | `true` |
| `contains_no_new_content` | `true` — all 7 items are scope statements; item (5) cleanly cross-references Appendix B; items (6) and (7) are NEW scope additions |
| `honesty_score_1_to_5` | `4` |
| `specific_failure_modes_listed` | `partial` — Pareto-domination (item 6) is explicit, but per-method failure-mode breakdown still missing |
| `issues` | (1) Item (7) demographic/societal scope is 1 sentence; needs ~3 sentences with concrete multilingual / cultural-bias examples for band 7+; (2) Items (1), (4), (5) have "Stage-2 will fix this" framing (band 5 future-work pattern); (3) No per-method failure-mode breakdown table; (4) No annotator-bias / construct-validity discussion despite using HotpotQA EM/F1 metrics that are known to penalize semantically-correct paraphrases |

## `responsible_nlp_checklist_assessment`

| Field | Value |
|---|---|
| `appears_complete` | `true` — B1 / B2 / B3 / B4 / B5 all answered |
| `issues` | (1) B2 hyperparameters list still says "0.55, 0.20, 0.10, etc." with "etc." obscuring whether all weights are listed; (2) B2 NEW random-seed disclosure (seed=42) closes a major gap, but multi-seed structure not yet present; (3) Appendix C heading text "per Reviewer R-FULL-004 D5 request" is a process-leak that should be removed before camera-ready (mentioning internal review batch IDs in a paper is unusual and could be flagged for anonymization concerns) |

## `implementation_risks`

1. External `edo_lite_executable_spec.md` still referenced for ϕ extraction, multiple λ values, AUDIT default rule, EVIDENCE_EXTRACT lookup — replication blocked without anonymous supplement.
2. Provider variability documented in Appendix B; cross-endpoint comparability open variable.
3. fullval n=7405 only valid for peer_calibrated method; other 2 method runs queued for re-execution per Limitations (5) — full Table 1 fullval ranking cannot be reproduced from paper alone in current state.
4. Single-seed runs make any reported metric a single-realization sample.
5. Appendix C.3 AUDIT-LLM-fallback variant decision rules are inline, but the default rule-based AUDIT is in supplement; this asymmetry could confuse implementers.

## `what_to_fix_for_8_plus` (6 items, in order of structural impact)

1. **Add MuSiQue as second benchmark** (already cited in §4.2 as reserved). Single change moves EXP-1 fail → pass; necessary to start unlocking the §6 cap on overall. Without this, no improvement to D5/D7/clarity can break the 4.5 floor.
2. **Run all main results with ≥3 seeds + 95% bootstrap CI + paired sign test in Table 1**. Addresses EXP-2/EXP-3/EXP-4 simultaneously. Currently the only variance reporting is Appendix D's n=3 shards.
3. **Add Multi-Agent Debate (Liang et al., 2024) as benchmarked baseline in Table 1**. Directly addresses §2.5.2 unaddressed `is_overlap_risk=true`. Closes D3 cap at 4.
4. **Add Table 2 ablation on canonical strong backbone (gpt-4.1-mini)** — currently glm-4-flash only.
5. **Replace Figure 1 placeholder with finished vector PDF**. Caption already specifies the design; this is purely production work, not research.
6. **Inline the remaining undefined functional forms in §3.6 or Appendix C** (forward_bias, AUDIT default rule, EVIDENCE_EXTRACT lookup table, λ_c value). Each is small (1-3 lines). Together they close most of D5/D1 remaining gaps.

## `what_to_fix_for_oral` (5 items)

1. **Implement at least one of R1/R2/R3 and demonstrate empirical value on multiple benchmarks**. Currently the proposed contribution (EDO Stage-2 framework) is structurally not what is measured. R2 audit is highest-ROI candidate (closest neighbor mechanism that could empirically reverse Finding 4).
2. **Show non-trivial improvement over external 2024-2026 SOTA on at least two benchmarks**. Currently the proposed method LOSES to its simplest baseline at equal token cost on the only benchmark.
3. **Expand Limitations item (7) demographic/societal scope** from 1 sentence to ~3 sentences with concrete multilingual / dataset-bias / annotator-bias / cultural-bias examples; add per-method failure-mode breakdown table (could be Appendix F).
4. **Replace Figure 1 placeholder** AND **add a Figure 3 visualizing emergent specialization metrics** (per-agent action frequencies / persona-tag divergence over time) from a Stage-2 run; this gives §1.3 contribution claim "structured personality-tag space" empirical visibility.
5. **Remove "per Reviewer R-FULL-004 D5 request" phrase from Appendix C heading** — internal review process notes should not appear in the paper itself.

## `recommended_next_actions` (4 items, smallest-cost first)

1. **5-minute fix**: remove "per Reviewer R-FULL-004 D5 request" from Appendix C heading + tighten Abstract to reflect Finding 3 correction (PAR=0 is gate, not TCPB).
2. **30-minute fix**: inline forward_bias / AUDIT default rule / EVIDENCE_EXTRACT lookup table / λ_c value into §3.6 or Appendix C.
3. **1-2 days fix**: replace Figure 1 placeholder with finished vector PDF (caption + design spec already exist in supplement).
4. **Sprint priority**: complete the in-flight engineer workstream (E-017 3-seed × 7405 fullval + E-009..E-016 external baselines + E-014 gpt-4.1-mini Table 2 ablation + E-015/E-016 MAD + R2 audit Stage-2 mechanism implementation). Without these, the 4.5 cap floor cannot break.

## Honest Final Verdict

Compared to R-FULL-005 (which I admit was scored too softly — see R-FULL-005 STRICT REVISION errata), this PDF version is **measurably improved**: 9 substantive scientist additions (FIT formula, TCPB scoring formula, Appendix C with 4 prompt templates, Appendix D with 3-shard preliminary Stage-2, B2 random seed, Limitations items 6+7, Conclusion rewrite, §3.1 honest framing, Finding 3 PAR-attribution correction). My P5 strict scoring reflects these improvements: D5 lifted from R-FULL-005 errata strict 4.0 → 5.0; D7 from 5.5 → 6.0; S4 from 5.0 → 5.5. Raw `weighted_sum` is now 4.560 (vs R-FULL-005 errata strict 4.300 = +0.260 measurable improvement).

**However**, the §6 cap structure means raw improvement does not translate to overall improvement. `overall = 4.5` remains the cap floor as long as `experiments_solidity_score = 1` and D4 < 5. **Scientist work on D5/D7/clarity dimensions, while real, cannot move the needle past 4.5 because their weights (0.10/0.07) are too small to overcome the experiments-solidity cap.** The only lever is experimental rigor: any 3 of the 8 EXP checks newly passing (e.g., +MuSiQue + multi-seed + paired CI) would push experiments_solidity_score from 1 to 4 and remove the §6 cap.

The paper currently sits in **`weak_reject`** territory, structurally bounded by `experiments_solidity_score = 1`. After the in-flight engineer workstream lands (E-017 fullval + E-009..E-016 external baselines + E-014 gpt-4.1-mini Table 2 + Stage-2 mechanism implementation), `overall` is honestly projectable to 5.5-6.0 (`borderline`). For Oral consideration, the Stage-2 mechanism actually winning on multi-benchmark + multi-seed + external SOTA comparison is required — currently 0% delivered.

I recommend the authors **withdraw and revise** before ARR May 2026 to include the missing benchmarks/baselines/Stage-2 mechanism. Submitting as-is is unlikely to clear `weak_reject` regardless of further hygiene improvements.

## Reviewer-Only Boundary Compliance (per `REVIEWER_TODO §F.1.4 / §F.1.5`)

- ✅ Did NOT modify any TODO file outside `REVIEWER_TODO.md` and `artifacts/idea_reviews/` during the review itself
- ✅ Did NOT participate in §A decisions
- ✅ Did NOT read past R-FULL-001/002/003/004/005 review.md / scoreboard.md / fix_themes.md / SCIENTIST_TODO §C content during scoring (used only persona-rotation fact)
- ✅ Did NOT trigger S-104 (scientist's responsibility per §11.4)
- Will leave §F.4 1-line ack in `ENGINEER_TODO.md`
- Will dispatch new S-XXX TODOs to scientist per user's standing instruction "你不要忘了给科学家下任务"
- Will add R-FULL-005 STRICT REVISION errata acknowledgment per user feedback "不够严厉" — done
- Temporary PDF text extraction at `$env:TEMP\edo_paper_r6_strict_audit.txt` deleted post-review per §F.3
- This `review.md` is the only required product per §F.3
