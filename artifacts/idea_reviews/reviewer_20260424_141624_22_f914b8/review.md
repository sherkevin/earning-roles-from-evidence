# R-FULL-022 Review

```json
{
  "reviewer_id": "R-FULL-022-f914b8",
  "reviewer_profile": "P2 Empirical-NLP SAC focused on empirical results, baseline quality, ablation completeness, and statistical rigor; target=8.5 Best-Paper oral bar",
  "document_type": "full_paper",
  "submission_track": "EMNLP Long Paper - Oral evaluation",
  "summary": "I read docs/demand.md and the full article/build/edo_paper.pdf extraction end-to-end. The paper proposes EDO, a local-interaction multi-agent organization framework, while the delivered evidence is a restricted TCPB Stage-1 prototype. Current empirical support is HotpotQA-only, n=200 single-seed for main tables, with Stage-2 split/audit/persona mechanisms mostly theoretical or preliminary.",
  "desk_reject_risks": [
    "DR-1: No confirmed page-limit violation; pdfinfo shows 16 pages, with main body ending on page 8 and Limitations starting at line 672.",
    "DR-1 POSSIBLE: Section 3.8 states Stage-2 lines are 'disabled or projects'; critical EDO loop is Appendix E, not fully evaluated in main body.",
    "DR-2: PASS; exact 'Limitations' title appears after Conclusion at line 672.",
    "DR-3: PASS; Limitations list scope caveats, not new tables, figures, or results.",
    "DR-4: No visible template tampering; pdfinfo reports A4 page size and pdfTeX producer.",
    "DR-5: PASS from visible PDF text; submission is anonymous and no project links or author names are visible."
  ],
  "scores": {
    "soundness": 5.5,
    "significance": 4.5,
    "novelty": 5.0,
    "empirical_results": 3.5,
    "reproducibility": 6.5,
    "clarity": 5.0,
    "responsible_research_and_limitations": 8.0,
    "executability": 5.0,
    "falsifiability": 6.0,
    "empirical_plan": 5.0,
    "technical_clarity": 6.0,
    "technical_soundness": 5.5,
    "statistical_rigor": 2.5,
    "baseline_quality": 2.5,
    "ablation_completeness": 3.0,
    "writing_and_figures": 4.0,
    "oral_quality_score": 2.5,
    "overall": 4.0
  },
  "score_calculation": {
    "weights": {
      "soundness": 0.25,
      "significance": 0.18,
      "novelty": 0.15,
      "empirical_results": 0.18,
      "reproducibility": 0.1,
      "clarity": 0.07,
      "responsible_research_and_limitations": 0.07
    },
    "weighted_sum": 5.125,
    "caps_triggered": [
      "D4=3.5<5: cap overall to D4+0.5=4.0.",
      "experiments_solidity_score=0<=3: cap D4 at 4 and overall no higher than weak-reject range.",
      "EXP-1 fail: single benchmark caps D4 at 6.",
      "EXP-2 fail: single seed caps D4 at 5 and S5 at 4.",
      "EXP-3 fail: no paired significance test caps D4 at 6 and S5 at 5.",
      "EXP-5 coverage_ratio=0.33<0.5: cap D4 at 6 and S7 at 5.",
      "EXP-6 fail: no recent external SOTA in result tables caps D4 at 5 and S6 at 4.",
      "Best-Paper checklist misses 6+ items: oral_quality_score capped at 3."
    ],
    "final_overall": 4.0
  },
  "experiments_solidity_audit": {
    "EXP_1_multi_dataset": {
      "status": "fail",
      "evidence": "Section 4.2: 'Benchmark: HotpotQA... 200 examples'; MuSiQue and 2WikiMultiHop are 'reserved for Stage-2'."
    },
    "EXP_2_multi_seed": {
      "status": "fail",
      "evidence": "Appendix A B2: 'all chain-200 results in Table 1 and Table 2 use seed=42'."
    },
    "EXP_3_significance_test": {
      "status": "fail",
      "evidence": "Section 4.3 says the 2.6 F1 gap is 'not yet confirmed with paired statistics'."
    },
    "EXP_4_effect_size_or_CI": {
      "status": "fail",
      "evidence": "Appendix A B2 states 'Confidence intervals are explicitly not reported in this submission'."
    },
    "EXP_5_ablation_coverage": {
      "status": "partial",
      "evidence": "Table 2 ablates TCPB terminal update and decomposer gate; R1 split, R2 audit, and R3 vector-belief remain future mechanisms.",
      "claimed_essential_components": [
        "TCPB terminal update",
        "decomposer safety gate",
        "evidence window",
        "R1 split",
        "R2 recursive audit",
        "R3 vector-belief/persona update"
      ],
      "components_with_ablation": [
        "TCPB terminal update",
        "decomposer safety gate",
        "evidence window"
      ],
      "coverage_ratio": 0.33
    },
    "EXP_6_baseline_recency": {
      "status": "fail",
      "evidence": "Table 1 compares self_claim, static_roles, peer_calibrated only; MA-RAG 2025 and ReAgent 2025 are cited but not result baselines.",
      "oldest_baseline_year": 2024,
      "most_recent_baseline_year": 2025,
      "latest_sota_present": false,
      "stale_baselines": [
        "AutoGen 2024 cited but not run",
        "MetaGPT 2024 cited but not run",
        "ChatDev 2024 cited but not run"
      ],
      "missing_recent_sota": [
        "MA-RAG 2025",
        "ReAgent 2025",
        "recent HotpotQA multi-agent/RAG baselines under matched inference"
      ]
    },
    "EXP_7_sensitivity_sweep": {
      "status": "partial",
      "evidence": "Section 4.4 mentions '+/-2x sweeps <0.003 pp', but no full sweep table with tested values is shown."
    },
    "EXP_8_error_analysis": {
      "status": "fail",
      "evidence": "No quantitative named failure-mode table; Section 4 reports PAR, MHC, F1, EM, and token metrics only."
    },
    "experiments_solidity_score": 0,
    "caps_implied_by_audit": [
      "EXP-1 fail: cap D4 at 6.",
      "EXP-2 fail: cap D4 at 5 and S5 at 4.",
      "EXP-3 fail: cap D4 at 6 and S5 at 5.",
      "EXP-5 partial with coverage_ratio<0.5: cap D4 at 6 and S7 at 5.",
      "EXP-6 fail: cap D4 at 5 and S6 at 4.",
      "experiments_solidity_score<=3: cap D4 at 4."
    ]
  },
  "novelty_delta_audit": [
    {
      "prior_work_name": "AutoGen",
      "year": 2024,
      "claimed_difference": "Section 2.1 says EDO removes a global role table, central decision node, and fixed task script.",
      "is_concrete": true,
      "is_overlap_risk": true
    },
    {
      "prior_work_name": "MetaGPT",
      "year": 2024,
      "claimed_difference": "The paper contrasts preassigned software roles with value-induced persona tags under local interaction.",
      "is_concrete": true,
      "is_overlap_risk": true
    },
    {
      "prior_work_name": "Multi-Agent Debate",
      "year": 2024,
      "claimed_difference": "Section 2.2 says EDO updates routing state rather than merging critique transcripts into the current answer.",
      "is_concrete": true,
      "is_overlap_risk": false
    },
    {
      "prior_work_name": "MA-RAG",
      "year": 2025,
      "claimed_difference": "Section 2.1 says MA-RAG hard-codes a planner/step-definer/extractor/answerer retrieval stack; EDO seeks local sparse-graph organization.",
      "is_concrete": true,
      "is_overlap_risk": true
    },
    {
      "prior_work_name": "ReAgent",
      "year": 2025,
      "claimed_difference": "The paper contrasts rollback-based trajectory correction with recursive local acceptance and persona-tag updates.",
      "is_concrete": true,
      "is_overlap_risk": true
    }
  ],
  "reference_documents_consulted": {
    "demand_md_loaded": true,
    "edo_paper_pdf_loaded": true,
    "fallback_source_used": "pdftotext -layout full-document extraction from article/build/edo_paper.pdf plus pdfinfo metadata checks",
    "layout_dependent_checks_blocked": []
  },
  "rule_source_disagreements": [],
  "verdict": "weak_reject",
  "oral_eligible": false,
  "confidence": 4,
  "top_strengths": [
    "Section 3.7 explicitly separates EDO theory from the restricted TCPB prototype.",
    "Limitations lines 673-760 honestly enumerate Stage-1 scope, single benchmark, statistics, and provider risks.",
    "Related Work now names MA-RAG 2025 and ReAgent 2025 as close systems.",
    "Appendix A reports seeds, hyperparameters, compute budget, artifacts, and AI-assistance disclosure."
  ],
  "top_weaknesses": [
    "Section 4.2 reports only HotpotQA-200; MuSiQue and 2WikiMultiHop are reserved for Stage-2.",
    "Appendix A B2 states all main results use seed=42; no multi-seed variance is reported.",
    "Table 1 lacks external 2025 baselines despite citing MA-RAG and ReAgent.",
    "Figure 1 is a placeholder saying 'Final asset will be a vector PDF'.",
    "Section 3.8 says R1/R2/R3 are disabled or projected, so core EDO mechanisms are not delivered.",
    "Table 2 ablation removals match the refreshed baseline for EM/F1, leaving mechanism value unproven."
  ],
  "core_method_problems": [
    "Section 3.8 says split is disabled and contributes zero events in this submission.",
    "Section 3.8 says AUDIT is fixed to ACCEPT, eliminating the claimed recursive upstream audit.",
    "Prototype Scope Box replaces persona-tag updates with terminal-only scalar competence updates."
  ],
  "experimental_design_problems": [
    "Section 4.2 uses one HotpotQA slice, not three diverse datasets.",
    "Section 4.3 admits n=7405 full-validation for all three methods is required.",
    "Table 1 compares internal variants only, not recent external SOTA systems.",
    "No quantitative error taxonomy appears for generated wrong answers or routing failures."
  ],
  "implementation_or_reproducibility_gaps": [
    "Appendix A promises anonymous code/data supplement, but no reviewer-visible URL appears in the PDF.",
    "Appendix B reports cross-endpoint comparability as an open variable.",
    "Appendix A B2 says provider model size is not disclosed, limiting reproducibility.",
    "Stage-2 constants are hand-set priors, not searched or validated."
  ],
  "overclaims_or_risky_claims": [
    "Abstract calls EDO the main contribution while Stage-2 mechanisms are theoretical in this submission.",
    "Introduction asks whether agents can self-organize, but Section 4 only tests role-prior chain variants.",
    "Figure 2 marks peer fullval n=7405 while other full-validation re-runs remain pending."
  ],
  "ambiguous_algorithm_points": [
    "Section 3.3 defines SplitGain(z) but the operational estimator is only in supplement/Appendix E.",
    "Section 3.3 includes RejectRisk(j,z), but delivered TCPB collapses it away.",
    "Section 3.5 defines LocalValue and TerminalValue, but Stage-1 sets eta_local effectively absent.",
    "Section 4.4 reports '+/-2x sweeps' without listing parameters or tested values."
  ],
  "missing_definitions_or_state_variables": [
    "SplitGain(z) is not concretely instantiated in the main body.",
    "MergeCost(z) is not empirically calibrated in the main body.",
    "RejectRisk(j,z) is unused in delivered Stage-1 evidence.",
    "value_gain is introduced for audit events but not measured in experiments."
  ],
  "missing_or_weak_experiments": [
    "Need MuSiQue or 2WikiMultiHop main-table evaluation for compositional transfer.",
    "Need >=3 seeds for HotpotQA main comparisons.",
    "Need paired bootstrap or sign tests for headline deltas.",
    "Need MA-RAG/ReAgent or comparable 2025 baselines under matched budget.",
    "Need R1/R2/R3 ablations on the canonical gpt-4.1-mini backbone.",
    "Need quantitative error analysis with named failure modes."
  ],
  "statistical_significance_concerns": [
    "Section 4.3 says the 2.6 F1 gap is not confirmed with paired statistics.",
    "Appendix A says confidence intervals are explicitly not reported.",
    "Single seed=42 blocks variance estimates for Tables 1 and 2."
  ],
  "baseline_completeness_concerns": [
    "Table 1 uses internal variants rather than external multi-agent/RAG baselines.",
    "MA-RAG 2025 and ReAgent 2025 appear in Related Work but not evaluation.",
    "No matched central-orchestrator result appears in the visible Table 1 main results."
  ],
  "limitations_section_assessment": {
    "section_present": true,
    "section_title_exact": true,
    "contains_no_new_content": true,
    "honesty_score_1_to_5": 4.0,
    "specific_failure_modes_listed": true,
    "issues": [
      "Limitations are unusually central to the paper's contribution boundary.",
      "The section admits several issues severe enough to keep the work below completed-long-paper standard.",
      "It covers demographic and societal scope, but no stratified error analysis supports the discussion."
    ]
  },
  "responsible_nlp_checklist_assessment": {
    "appears_complete": true,
    "issues": [
      "Checklist copy appears in Appendix A; final ARR form completion still must be verified externally.",
      "AI-assistance disclosure relies on author assertion that no prose was generated.",
      "No human evaluation is conducted, which is acceptable but limits case-study strength."
    ]
  },
  "implementation_risks": [
    "Cross-endpoint provider change may make full-validation results non-comparable.",
    "Bit-identical Table 2 ablations could indicate mechanism inactivity or code-path bug.",
    "Stage-2 algorithm is pseudocode-level; delivered runtime does not execute R1/R2/R3.",
    "Anonymous supplement is referenced but not available inside the PDF for audit."
  ],
  "what_to_fix_for_8_plus": [
    "Run HotpotQA, MuSiQue, and one additional benchmark with matched baselines.",
    "Report >=3 seeds, paired tests, and 95% CIs for every headline comparison.",
    "Implement and ablate R1 split, R2 recursive audit, and R3 persona updates.",
    "Add external 2025 baselines such as MA-RAG and ReAgent under matched budget.",
    "Replace Figure 1 placeholder with a final vector schematic and self-contained caption.",
    "Add quantitative error analysis with named routing, generation, audit, and split failures."
  ],
  "what_to_fix_for_oral": [
    "Deliver completed Stage-2 evidence rather than future-work hypotheses.",
    "Show consistent gains across at least three datasets and multiple seeds.",
    "Prove novelty with empirical deltas against recent orchestration and RAG-agent systems.",
    "Provide reviewer-visible anonymous code/data links and scripts regenerating tables.",
    "Add case-study or application evidence showing why organization formation matters."
  ],
  "recommended_next_actions": [
    "Prioritize multi-seed HotpotQA plus paired CI before prose polish.",
    "Move MA-RAG/ReAgent from Related Work only into matched baseline experiments.",
    "Treat Figure 1 placeholder as a submission-blocking presentation gap.",
    "Do not claim Stage-2 mechanism value until R1/R2/R3 execute in main experiments."
  ],
  "is_8_plus_ready": false,
  "estimated_score_after_fixes": 7.2,
  "_parse_mode": "full"
}
```
