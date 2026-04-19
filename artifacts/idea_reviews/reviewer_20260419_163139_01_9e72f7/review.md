# Review of `article/build/edo_paper.pdf`

- reviewer_id: `reviewer_20260419_163139_01_9e72f7`
- reviewer_profile: P5 (Best-Paper-Committee chair / Oral-track gatekeeper)
- model: human/agent (Cursor session, no remote LLM call)
- target: `article/build/edo_paper.pdf` (extracted via pdftotext to `_edo_paper_text_for_review.txt`, 54 KB / 513 lines / 9 pages)
- document_type: `partial_paper`
- verdict: **`weak_reject`**
- confidence: `3` (PDF text only — layout-dependent checks blocked)
- is_8_plus_ready: `false`
- oral_eligible: `false`
- estimated_score_after_fixes: `6.0`

## Scores

| dim | score | notes |
|---|---:|---|
| D1 soundness | 5.0 | Method equations in §3 mostly stated, but key functions (Fit, evidence_extract) and λ/η coefficients undefined |
| D2 significance | 4.5 | Reframing is interesting; author's own Finding 1 admits "backbone quality dominates all method differences" |
| D3 novelty | 4.0 | Capped at 5 by §2.5.2 hard rule (zero named prior works); honest score is 4 because reframing-only |
| D4 empirical_results | 4.0 | Capped at 4.5 by experiments_solidity_score=0; single benchmark / single seed / no significance / no ablation in body / all baselines author-internal |
| D5 reproducibility | 6.0 | Concrete artifact paths + runtime files; no anonymous code link / no compute budget |
| D6 clarity | 6.5 | Well-organized; Algorithm 1 referenced but absent from PDF; some external-reference dependence |
| D7 limitations | 6.0 | Title exact, honest about EDO not implemented; runtime-drift discussion borders on DR-3 (new content) |
| S1 executability | 5.0 | Heavy reliance on external `edo_lite_executable_spec.md` |
| S2 falsifiability | 5.0 | Headline empirical claim is admitted-falsified by author's Finding 4 |
| S3 empirical_plan | 5.0 | E1-E5 sketched but not executed |
| S4 technical_clarity | 6.0 | Equations clear; multiple symbols undefined |
| S5 statistical_rigor | 2.0 | No CI / no paired test / no multi-seed |
| S6 baseline_quality | 3.0 | All baselines author-internal; zero external 2024-2026 SOTA |
| S7 ablation_completeness | 3.0 | Ablations exist as external file references only; coverage_ratio in body = 0 |
| S8 writing_and_figures | 5.0 | Writing OK; ZERO figures in PDF; Algorithm 1 missing |
| **oral_quality_score** | **2.5** | "Reject" tier per §5 mapping; nowhere near top 25% |
| **overall** | **4.5** | Capped at 4.5 by D4<5, D3<5, experiments_solidity_score<=3 |

## Score Calculation

```
weighted_sum = 0.25*5.0 + 0.18*4.5 + 0.15*4.0 + 0.18*4.0 + 0.10*6.0 + 0.07*6.5 + 0.07*6.0
             = 1.25 + 0.81 + 0.60 + 0.72 + 0.60 + 0.455 + 0.42
             = 4.855

caps_triggered:
  - D4<5 (D4=4.0):                       cap overall to min(4.855, D4+0.5) = 4.5
  - D3<5 (D3=4.0):                       cap overall to min(4.5, D3+0.5)  = 4.5  (already at floor)
  - experiments_solidity_score<=3 (=0):  cap overall to 4.5  (already at floor)

final_overall = 4.5  →  verdict = weak_reject  (overall in [4.0, 5.5))
```

## Reference Documents Consulted

- `docs/demand.md` loaded: `true` (read in this session; no rule-source disagreements observed)
- `article/build/edo_paper.pdf` loaded as PDF: `false` — used pdftotext extraction at `artifacts/idea_reviews/_edo_paper_text_for_review.txt`
- Layout-dependent checks blocked:
  - DR-1 precise page boundary
  - DR-4 template tampering
  - D6 figure quality (Algorithm 1, Figure 1, Figure 2 absent from extraction)
  - S8 caption quality

## Summary

EDO reframes decentralized multi-agent routing as 'organizational emergence' under local interaction; full method (recursive split + audit + persona vector) is admitted-not-implemented. The actually delivered system is a Stage-1 prototype TCPB on a single benchmark (HotpotQA, n=200, single seed, no significance tests, no ablation table in body, all baselines author-internal). Author's own Finding 4 admits the proposed method (peer_calibrated F1=0.7381) loses to a simpler baseline (self_claim F1=0.7641) at equal token cost, and Finding 1 admits backbone quality dominates all method differences. Reference list contains only 4 ACL template default citations.

## Top Strengths

1. Honest framing in §3.7 + §3.8 + §3.9: explicitly separates aspirational EDO theory from delivered TCPB prototype, with `Prototype Scope Box` enumerating what is/isn't implemented and Stage-2 Roadmap (R1/R2/R3) marking what's missing.
2. Limitations section is unusually self-critical: §5 explicitly says 'current codebase does not implement the complete EDO method' and 'recursive split value, local audit superiority, or personality-tag emergence from near-homogeneous initialization' are not established.
3. Backbone-sensitivity finding (Finding 1 + Finding 2 + dedicated Limitations paragraph) is itself a publishable observation: method ordering inverts between glm-4-flash and gpt-4.1-mini, which is empirically interesting even if it undermines the proposed method.
4. Reproducibility infrastructure: concrete artifact paths (`artifacts/round2_gpt41mini/run_20260414_115739/`, `artifacts/seed/hotpotqa_validation_200.jsonl`), runtime files named (`workspace/idea04_core/runner.py`), and validation scripts referenced — well above average for an anonymous submission.

## Top Weaknesses (ordered by severity)

1. **FATAL** — Headline empirical claim is falsified by author's own Finding 4 (§4.3): "peer_calibrated uses the same token budget as self_claim (both 6,414/sample) but achieves lower F1" — proposed TCPB method (F1=0.7381) is Pareto-dominated by simpler self_claim (F1=0.7641) on the canonical run.
2. **FATAL** — Single benchmark (HotpotQA only) + single seed + no paired significance test in Table 1 + no ablation table in paper body. Per reviewer §2.5.1 hard rules, `experiments_solidity_score=0` caps overall at 4.5.
3. **FATAL** — All baselines in Table 1 are author-internal routing variants (fixed_peer_calibrated / fixed_static_roles / fixed_self_claim). ZERO external 2024-2026 multi-agent SOTA (MARS, SAGE, AutoGen, MetaGPT, ReSo, AMRO-S) appears as a baseline. S6=3 (self-comparison only).
4. **FATAL** — Reference list contains exactly 4 ACL template default citations (Ando&Zhang 2005, Andrew&Gao 2007, Gusfield 1997, Rasooli&Tetreault 2015) — none related to multi-agent systems. Bibliography was not compiled. This is a desk-reject-adjacent quality signal.
5. Related Work §2.1 / §2.2 / §2.3 names ZERO specific prior systems despite the field having well-known orchestrator (AutoGen, MetaGPT) and peer-critique (MARS, SAGE) baselines. Per §2.5.2 hard rule, D3 capped at 5; my honest score is 4 because the paper does not articulate concrete deltas.
6. Algorithm 1 referenced in §3.7 but the actual Algorithm 1 box is NOT rendered in the extracted PDF text. Figure 1 and Figure 2 (planned per project SCIENTIST_TODO) absent from PDF. The paper has Table 1 only — zero figures and zero pseudocode boxes.

## Desk-Reject Risks

- DR-1 (POSSIBLE): pdftotext suggests §4.6 + §5 cross to page 9; main body may exceed strict 8-page limit — needs PDF render verification.
- DR-3 (POSSIBLE): Limitations contains detailed engineering description of `ModelDriftError` runtime guard — borders on new content.
- DR-5 (POSSIBLE): Inline paths to project-internal files (`workspace/idea04_core/runner.py`, `artifacts/edo_lite_executable_spec.md`) could be deanonymizing.
- DR-6: Responsible NLP Checklist not visible.
- DR-8 (POSSIBLE): 4-reference bibliography matching ACL template defaults strongly suggests bibliography was never compiled.

## Experiments Solidity Audit (score = 0 / 8)

| check | status | evidence |
|---|---|---|
| EXP-1 multi-dataset | fail | HotpotQA only |
| EXP-2 multi-seed | fail | Point estimates only; "not yet confirmed with paired statistics" |
| EXP-3 significance test | fail | No paired bootstrap / sign test in Table 1 |
| EXP-4 effect size or CI | fail | No CI columns; no Cohen's d |
| EXP-5 ablation coverage | partial | All ablations referenced via external files; coverage_ratio in body = 0.0 |
| EXP-6 baseline recency | fail | Author-internal variants only; zero external 2024-2026 SOTA |
| EXP-7 sensitivity sweep | partial | `round1_v3_weight_sensitivity.md` referenced but not in paper body |
| EXP-8 error analysis | partial | Interpretive comments only; no quantitative failure-mode breakdown |

## Novelty Delta Audit

3 candidate prior works identified by their generic mention; ZERO are NAMED with concrete deltas:

| prior_work | year | claimed_difference | concrete? | overlap_risk? |
|---|---:|---|---|---|
| AutoGen / MetaGPT (orchestrator MAS) | 2024 | "no global expert table, only local visibility" (architectural) | ❌ | ❌ |
| Reflexion / ToT / multi-agent self-critique | 2023 | "terminal outcome instead of self-critique" | ❌ | ⚠ |
| MARS / SAGE / AMRO-S / Brain-Inspired Graph MAS | 2026 | NOT NAMED IN PDF | ❌ | ⚠ |

Per §2.5.2 hard rule: cap D3 at 5 (cannot identify 3 named prior works with concrete deltas).

## Limitations Section Assessment

- section_present: ✅
- section_title_exact: ✅ ("Limitations")
- contains_no_new_content: ❌ (engineering description of ModelDriftError fix is borderline-new content)
- honesty: 4/5
- specific_failure_modes_listed: ✅
- issues:
  - Engineering ModelDriftError discussion borders on DR-3 violation
  - No societal risks discussed
  - Responsible NLP Checklist not visible in PDF
  - Does not flag that TCPB itself is empirically dominated by self_claim (Finding 4 limitation of delivered system, not just future EDO)

## Responsible NLP Checklist

Not visible in PDF body. Cannot verify completeness. License / consent / AI-assistance disclosure all missing from extracted text.

## What to Fix for 8+ Overall

1. Add a second benchmark (MuSiQue strongly preferred — already named in §4.4 as future work).
2. Run all main results with >=3 seeds + 95% bootstrap CIs + paired sign test in Table 1.
3. Embed actual ablation table (TCPB-on/off, gate-on/off, weight perturbation) IN paper body, not as external file references.
4. Replace at least 2 of 4 author-internal baselines with external 2024-2026 multi-agent systems (MARS for peer-critique, AutoGen for orchestrator).
5. Compile bibliography. Cite at least 15-20 named prior works in §2 with concrete deltas. Current 4-template-default reference list is unacceptable.
6. Render Algorithm 1 box in §3.7 + Figure 1 + Figure 2 in PDF.

## What to Fix for Oral (top 3-5%)

7. Implement at least one of (R1) split / (R2) recursive audit / (R3) persona vector and demonstrate empirical value (otherwise EDO remains aspirational).
8. Show non-trivial improvement over external 2024-2026 SOTA (currently proposed method LOSES to simpler self_claim).
9. Quantitative error analysis with named failure modes.
10. Sensitivity sweep IN paper body across >=3 critical hyperparameters.
11. Community-impact case study showing how EDO/TCPB changes practitioner workflow vs. orchestrator MAS.
12. Address page-limit risk (trim §4.6 bullets or fold §3.8 into §3.7).

## Recommended Next Actions (ordered by urgency)

1. **URGENT** — Pivot positioning. Current empirical evidence does NOT support "EDO improves multi-agent routing" narrative because Finding 4 admits TCPB loses to self_claim. Either (a) reframe as "Stage-1 backbone-sensitivity negative result + Stage-2 roadmap" and accept oral_quality_score <= 5, or (b) implement Stage-2 mechanisms before resubmission.
2. **URGENT** — Compile real bibliography. 4 ACL-template-default references are desk-reject-adjacent.
3. Add MuSiQue as second benchmark (lowest-cost path to EXP-1 pass).
4. Move ablation tables and weight-sensitivity table from external artifacts INTO paper body (lowest-cost path to S7 >= 6 and EXP-5 pass).

## Implementation Risks

- External `edo_lite_executable_spec.md` is canonical implementation spec but not part of submission.
- Utility weights, accept margin, gate threshold, momentum all undisclosed in paper.
- No compute / token budget.
- Provider `kuaipao.ai` non-standard; replication on standard API may differ.
- fullval (n=7405) for two of three methods admitted invalid; only one method has full validation.

## Rule Source Disagreements

None observed. Reviewer prompt rubric is consistent with `docs/demand.md` as I have read it: 8-page main body (DR-1 ↔ demand.md §2 'Page Limit'); exact 'Limitations' title (DR-2 ↔ demand.md §2 'Mandatory Section'); ARR 7-dimension scoring (D1..D7 ↔ demand.md §4 'Review Criteria'); 'substantial / original / completed / concrete evaluation' four-part test (↔ demand.md §1 'Track Core Positioning').
