# R-FULL-026 Review - BP-EXPERIMENTS

reviewer_id: `R-FULL-026-BP-EXPERIMENTS-3384de`  
reviewer_profile: `BP-EXPERIMENTS`: best-paper-calibrated empirical NLP SAC focused on experiments, SOTA baselines, benchmark credibility, ablations, and statistical rigor.  
document_type: `full_paper`  
submission_track: `EMNLP Long Paper - Oral evaluation`  
target_path: `article/build/edo_paper.pdf`  
pdf_sha256: `3384DEEABF2B18A1F1114803AFA4CC563370681EE0F091D44F56FB78B7D517CC`  
created_at: `2026-04-27 15:26:49 +08:00`  
verdict: `weak_reject`  
oral_eligible: `false`  
confidence: `4`

## Summary

The paper proposes EDO-Frame for local multi-agent organization and carefully separates the full framework from the restricted TCPB prototype. Both `docs/demand.md` and the full rendered PDF were read. The manuscript is honest and more reproducible than a typical idea paper, but the empirical package remains far below an oral/best-paper bar: one 200-example HotpotQA slice, mostly single-seed point estimates, no matched external SOTA result baselines, no completed component ablations, no multi-dataset transfer, and only partial statistical evidence.

## Desk-Reject Risks

- DR-1: No confirmed page-limit violation from the rendered PDF text. Main content reaches page 8; `Limitations` starts after Conclusion and continues outside main content.
- DR-2: PASS. The section is titled exactly `Limitations`.
- DR-3: PASS with caveat. `Limitations` discusses known scope gaps and does not introduce a new table, figure, method, or result.
- DR-4: NONE OBSERVED from extracted rendered text, but template internals were not inspected.
- DR-5: NONE OBSERVED. The PDF is anonymous and uses anonymous supplement wording.
- DR-6: NONE OBSERVED. Responsible-research content appears in `Ethical Considerations`.
- DR-7: NONE OBSERVED from the visible text.
- DR-8: NONE OBSERVED. AI assistance is disclosed in `Ethical Considerations`.

## Scores

| Field | Score | Evidence |
|---|---:|---|
| soundness | 6.5 | Sections 3.1-3.7 define state, utility, TCPB reduction, and scope boundary, but full R1/R2/R3 remains unexecuted. |
| significance | 5.0 | The organizational framing is interesting, but evidence is limited to a narrow multi-hop QA slice. |
| novelty | 5.0 | Related Work names AutoGen, MetaGPT, MA-RAG, ReAgent, MAD, and ChatEval, but many deltas are framing-level. |
| empirical_results | 4.0 | Tables 1-2 are HotpotQA chain-200 only; no external result baselines or multi-dataset transfer. |
| reproducibility | 6.5 | Section 4.2 and Ethical Considerations promise code, logs, seed slice, prompts, and validation scripts. |
| clarity | 6.0 | Scope boundaries are unusually honest, but the paper still reads partly as a framework roadmap. |
| responsible_research_and_limitations | 8.0 | Limitations enumerate seven concrete scope limits plus ethics/release/AI-assistance disclosure. |
| executability | 6.0 | TCPB is implementable; full EDO still depends on supplementary pseudocode and future Stage-2 mechanisms. |
| falsifiability | 6.0 | Section 3.9 lists R1/R2/R3 hypotheses, but current evidence tests only restricted proxies. |
| empirical_plan | 4.0 | The paper names needed future rows, but the submitted evidence lacks the planned breadth. |
| technical_clarity | 6.5 | Equations and reduction are readable, though several full-method semantics live in supplement. |
| technical_soundness | 6.5 | Mirrors soundness. |
| statistical_rigor | 4.0 | Table 2 reports paired bootstrap CI and sign-test; Table 1 lacks multi-seed and paired tests. |
| baseline_quality | 3.0 | No matched external SOTA result baseline appears in Table 1 or Table 2. |
| ablation_completeness | 3.0 | Section 3.6 reports negative memory/tool toggles but no full targeted component ablation matrix. |
| writing_and_figures | 5.0 | Figures are explanatory/conceptual; Figure 3 says components remain conceptual until ablations. |
| oral_quality_score | 3.0 | Empirical package and visual polish are not oral-track ready. |
| overall | 4.5 | Deterministic weighted score is capped by experiments solidity and D4. |

## Score Calculation

weights: `0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7`

weighted_sum:

```text
0.25*6.5 + 0.18*5.0 + 0.15*5.0 + 0.18*4.0 + 0.10*6.5 + 0.07*6.0 + 0.07*8.0 = 5.6
```

caps_triggered:

- `D4 < 5`: cap overall to `D4 + 0.5 = 4.5`.
- `D4 < 7`: cap overall to at most `7.0`.
- `experiments_solidity_score <= 3`: cap overall to `4.5`.
- `S6 < 5`: cap overall to at most `6.0`.
- `S7 < 5`: cap overall to at most `6.0`.
- `SBB-1 latest SOTA result fails`: cap overall to at most `6.0`.
- `PRES-3 figure readiness partial/fails for key figures`: cap overall to at most `5.5`.

final_overall: `4.5`

## Experiments Solidity Audit

| Check | Status | Evidence |
|---|---|---|
| EXP-1 multi-dataset | fail | Section 4.2 uses HotpotQA 200 examples; MuSiQue and 2Wiki are "reserved for Stage-2 EDO benchmark transfer". |
| EXP-2 multi-seed | fail | Abstract and Table 2 say the Phi-4-mini result is single-seed; Table 1 reports one chain-200 batch. |
| EXP-3 significance test | partial | Table 2 has paired bootstrap CI and sign-test; Table 1 lacks paired tests for the gpt-4.1-mini main table. |
| EXP-4 effect size or CI | partial | Table 2 reports a 95% CI; Table 1 has point estimates only. |
| EXP-5 ablation coverage | fail | Claimed components include split, audit, persona tags, memory, tools, safety gate, topology, and TCPB calibration; no complete targeted matrix appears. |
| EXP-6 baseline recency | fail | MA-RAG and ReAgent are cited in Related Work but are not result baselines in Tables 1-2. |
| EXP-7 sensitivity sweep | fail | No threshold, topology, lambda, memory, tool, or backbone sensitivity sweep with 3+ values is reported. |
| EXP-8 error analysis | fail | Section 4.3 lists needed "manual error taxonomy" as future evidence, not completed analysis. |

experiments_solidity_score: `0`

claimed_essential_components:

- recursive split
- recursive upstream audit
- persona-tag update
- governed memory
- tag-gated tool selection
- TCPB outcome calibration
- decomposer force-forward safety gate
- sparse graph topology

components_with_ablation:

- memory/tool/drift toggles are mentioned as a negative diagnostic in Section 3.6, but not as a full main-result ablation matrix.

coverage_ratio: `0.1`

caps_implied_by_audit:

- EXP-1 fail: cap D4 at 6.
- EXP-2 fail: cap D4 at 5 and S5 at 4.
- EXP-5 coverage < 0.5: cap D4 at 6 and S7 at 5.
- EXP-6 fail: cap D4 at 5 and S6 at 4.
- experiments_solidity_score <= 3: cap D4 at 4 and overall at 4.5.

## Novelty Delta Audit

| Prior work | Year | Claimed difference | Concrete? | Overlap risk? |
|---|---:|---|---|---|
| AutoGen | 2024 | Removes global manager and global role table in favor of local sparse-neighborhood routing. | true | false |
| MetaGPT | 2024 | Avoids preassigned PM/architect/engineer pipeline, but Stage-1 still uses role-prior nodes. | partial | true |
| Multi-Agent Debate / ChatEval | 2024 | Learns future routing state from accepted-value signals rather than merging critique into current answer. | partial | true |
| MA-RAG | 2025 | Contrasts hard-coded multi-hop retrieval stack with local organization; no result baseline is provided. | partial | false |
| ReAgent | 2025 | Contrasts rollback trajectory correction with local delegation/audit, but no matched experiment is provided. | partial | false |

D3 cap rationale: the conceptual delta is clearer than a pure rename, but the delivered Stage-1 system is still a restricted fixed-topology prototype and does not empirically isolate the full local-organization mechanism.

## SOTA / Baseline / Benchmark Audit

| Check | Status | Evidence |
|---|---|---|
| SBB-1 latest SOTA result | fail | Tables 1-2 omit MA-RAG, ReAgent, MAD, and other recent result baselines. |
| SBB-2 matched baseline setting | partial | Internal methods in Table 1 share HotpotQA/gpt-4.1-mini settings; external baselines are absent. |
| SBB-3 baseline diversity | fail | Tables cover internal single-agent/static-role/peer variants and local single_agent vs chain only. |
| SBB-4 benchmark recognition | pass | HotpotQA is public and canonical for multi-hop QA. |
| SBB-5 benchmark-claim alignment | partial | HotpotQA tests multi-hop QA routing, but not broad local organization or tool/memory emergence. |
| SBB-6 scale and cherry-pick risk | fail | The main evidence is a fixed 200-example validation slice. |

caps_implied_by_audit:

- SBB-1 fail: cap S6 at 4 and D4 at 5.
- SBB-3 fail: cap S6 at 5.
- SBB-6 fail: cap D4 at 5 and oral_quality_score at 5.

## Presentation Readiness Audit

| Check | Status | Evidence |
|---|---|---|
| PRES-1 top-conference logic | partial | The paper has a clear boundary, but Stage-2 is still roadmap-heavy. |
| PRES-2 claim consistency | pass | Abstract, Section 4.3, Conclusion, and Limitations consistently bound the claims. |
| PRES-3 figure readiness | partial | Figures are conceptual; Figure 3 says the governed loop remains conceptual until ablations. |
| PRES-4 table quality | partial | Tables are readable, but lack seeds, CI markers for Table 1, and external baseline rows. |
| PRES-5 table-result consistency | pass | The prose explicitly states TCPB is F1-dominated by self_claim on gpt-4.1-mini. |
| PRES-6 claim-to-visual support | partial | Headline evidence has main-body tables, but broad EDO mechanisms remain supported conceptually. |

key_figures_with_issues:

- Figure 2 is a mechanism overview, not empirical support.
- Figure 3 explicitly notes memory/tool/audit components remain conceptual until ablations.

## Best-Paper Demand Compliance

| Demand item | Status | Evidence |
|---|---|---|
| demand_md_section_12_read | pass | `docs/demand.md` section 12 checklist was applied. |
| substantial_high_impact_completed | partial | The framework is substantial, but current evidence is explicitly restricted Stage-1 / early local diagnostic. |
| four_to_six_dataset_best_paper_bar | fail | The paper reports one dataset slice; MuSiQue and 2Wiki are future transfer work. |
| experiments_page_weight_and_depth | fail | Experiments are compact and lack full ablations, error analysis, and external baselines. |
| figure_1_and_visual_density | partial | Figure 1 is present and explanatory; figures are mostly conceptual rather than evidence-dense. |
| vector_final_visuals | partial | Rendered text confirms figures exist, but visual/vector quality cannot be fully assessed from text extraction. |
| fatal_error_avoidance | pass | No visible anonymity breach, hallucinated citation, or undisclosed AI-assistance violation was observed. |

oral_or_best_paper_cap_implied: misses core empirical items: oral_quality_score <= 3.

## Reference Documents Consulted

- demand_md_loaded: `true`
- edo_paper_pdf_loaded: `true`
- fallback_source_used: `ReadFile PDF text extraction from article/build/edo_paper.pdf`
- layout_dependent_checks_blocked: `["DR-4 template internals cannot be fully inspected from text extraction"]`
- rule_source_disagreements: `["prompts/reviewer_template.md references EMNLP 2027 in places, while docs/demand.md is EMNLP 2026; demand.md wins for this batch."]`

## Strengths

- The paper honestly states TCPB is F1-dominated by self_claim on the strong backbone.
- The method section clearly separates full EDO from restricted Stage-1 TCPB.
- Limitations and Ethical Considerations are unusually concrete and reviewer-visible.
- Related Work names several relevant multi-agent and multi-hop QA systems.

## Top Weaknesses

- Table 1 reports one HotpotQA 200-example slice without multi-seed variance or paired tests.
- Tables 1-2 omit matched external SOTA result baselines such as MA-RAG and ReAgent.
- Section 4.3 says multi-seed, transfer, ablations, and error taxonomy remain needed.
- Claimed memory/tool/audit components lack non-zero consumption-layer ablation evidence.
- Figure 3 admits the governed action loop remains conceptual until ablations.

## Problem Categories

core_method_problems:

- Section 3.9 leaves R1/R2/R3 as Stage-2 mechanisms rather than completed evidence.
- Prototype Scope Box says current code uses fixed role-prior nodes, not near-homogeneous agents.

experimental_design_problems:

- Section 4.2 uses only HotpotQA chain-200 as completed main evidence.
- Section 4.3 lists MuSiQue, 2Wiki, error taxonomy, and matched baselines as still needed.
- No full component ablation matrix covers split, audit, memory, tools, topology, and persona tags.

implementation_or_reproducibility_gaps:

- Full EDO pseudocode and executable details are pushed to the supplement rather than fully visible in the main body.
- Release is promised through anonymous supplement, but the review did not execute the code.

overclaims_or_risky_claims:

- "EDO-Frame" risks sounding like a completed system although current evidence is restricted TCPB plus diagnostics.
- The organizational-emergence framing is broader than what a single HotpotQA slice can establish.

ambiguous_algorithm_points:

- Section 3.3 says task signatures may be extracted by rules, LLM judgment, or future learned modules.
- Section 3.9 says rejection criteria live in the executable supplement rather than the main paper.

missing_definitions_or_state_variables:

- Near-homogeneous initialization is not operationally tested in the submitted main results.
- Sparse graph support is defined conceptually but not instantiated in the reported tables.

missing_or_weak_experiments:

- Missing multi-dataset results on MuSiQue and 2Wiki.
- Missing multi-seed runs for Table 1 and Table 2.
- Missing matched MA-RAG / ReAgent / MAD result rows.
- Missing per-component ablations for memory, tool gating, split, audit, and persona update.
- Missing quantitative error taxonomy.
- Missing sensitivity sweep over topology, thresholds, and update weights.

statistical_significance_concerns:

- Table 1 has no paired test or CI.
- Table 2 is single-seed despite reporting a paired bootstrap CI.
- No multiple-comparisons handling is reported across methods.

baseline_completeness_concerns:

- MA-RAG and ReAgent are cited but absent from main result tables.
- No external 2025 SOTA result baseline is matched on split, backbone, budget, and metric.
- Internal baselines do not establish community-level SOTA.

benchmark_credibility_concerns:

- HotpotQA is canonical but only one dataset family.
- The 200-example slice is too small for best-paper empirical claims.
- The benchmark tests multi-hop QA, not the broader organizational-emergence claim.

writing_logic_concerns:

- The manuscript is claim-bounded, but full EDO still reads partly as a future roadmap.
- The strongest method ideas are not matched by equally strong completed evidence.

figure_table_consistency_concerns:

- Table 1 lacks CI, seed, and external baseline columns.
- Figure 3 is conceptual and not backed by completed component ablations.
- Table 2 reports a costlier local-chain gain, not a Pareto-dominant result.

## Limitations Section Assessment

- section_present: `true`
- section_title_exact: `true`
- contains_no_new_content: `true`
- honesty_score_1_to_5: `5`
- specific_failure_modes_listed: `true`
- issues:
  - The section is honest but confirms that key empirical closure is missing.
  - It acknowledges single benchmark, single-seed, backbone sensitivity, and demographic scope gaps.

## Responsible NLP Checklist Assessment

- appears_complete: `partial`
- issues:
  - The paper discusses data, misuse, fairness, release, and AI assistance.
  - The actual ARR checklist form was not available in the PDF text.

## Implementation Risks

- Full EDO requires task-tree state, recursive audit, persona-tag updates, and sparse graphs not shown in result tables.
- Supplement-dependent implementation details may be missed by reviewers focused on the main body.
- Component toggles currently log signals rather than changing planner/checker prompts, weakening causal claims.

## What To Fix For 8 Plus

1. Add 3+ datasets across at least two task families with matched splits and metrics.
2. Add matched MA-RAG, ReAgent, MAD, and strong single-agent baselines in main tables.
3. Run at least 3 seeds with paired tests and 95% CIs for every headline comparison.
4. Add a component ablation matrix covering split, audit, memory, tools, topology, and persona update.
5. Add quantitative error taxonomy and sensitivity sweeps over critical thresholds.
6. Convert conceptual mechanism figures into evidence-linked, final vector visuals.

## What To Fix For Oral

1. Prove a completed EDO mechanism, not only a bounded TCPB prototype.
2. Show cross-dataset gains against recent SOTA baselines under matched budgets.
3. Demonstrate non-zero causal contribution for memory/tool/audit/persona components.
4. Replace roadmap-heavy Stage-2 framing with completed results or narrow claims further.
5. Add broad-committee visual evidence that directly supports the central empirical claim.

## Recommended Next Actions

1. Prioritize external matched baselines and multi-seed CI before further prose polishing.
2. Run a small but complete ablation matrix on the local open-weight setting.
3. Add MuSiQue or 2Wiki transfer before triggering another best-paper gate review.
4. Build the manual error taxonomy from existing logs as a low-cost empirical-strengthening step.

is_8_plus_ready: `false`  
estimated_score_after_fixes: `7.0`  
_parse_mode: `full`
