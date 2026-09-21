# EMNLP 2026 Long Paper Track - Best Paper Excellence Demand File

> HISTORICAL EMNLP specification. For AAMAS 2027, [REQUIREMENTS.md](paper/aamas2027/REQUIREMENTS.md) and [AAMAS_TASKS.md](coordination/AAMAS_TASKS.md) supersede this file. In particular, fixed dataset counts, universal SOTA/positive ablation targets, and ACL limitations-page exemptions below are not active AAMAS requirements. Retained for provenance.

Source basis: ARR CFP, EMNLP 2026 official CFP, and structural analysis of representative EMNLP 2024/2025 Best Papers.

Official definition quoted from ARR / EMNLP CFP:

> Long papers must describe **substantial, original, completed and unpublished work**. Wherever appropriate, concrete evaluation and analysis should be included.

Official sources:

- <https://2026.emnlp.org/calls/main_conference_papers/>
- <https://aclrollingreview.org/cfp>

## 1. Core Track Positioning

An EMNLP Best-Paper-calibrated long paper must be a **breakthrough-level, substantial, high-impact, completed research contribution**. It needs all of the following at once:

1. a clear, verifiable, broadly applicable innovation;
2. extremely rigorous and comprehensive empirical evaluation;
3. deep quantitative and qualitative analysis;
4. new insights that matter beyond a narrow local setup;
5. durable community-level impact.

It is explicitly not incremental work, preliminary exploration, a short-paper extension, or a theory / observation paper without thorough experimental support. A paper that fails the **substantial + high-impact + rigorous** standard is unlikely to reach Best Paper consideration and may struggle to reach Oral.

## 2. Strict Formatting Requirements

Any violation of this section is a desk-reject risk.

- **Main-body page limit**: the submission/review version is limited to **8 pages of content** for the main body. All main-paper figures, tables, equations, pseudocode, and algorithms count inside these 8 pages.
- **Excluded from the 8-page content limit**: References, the mandatory `Limitations` section, and optional `Ethical Considerations` / `Broader Impact`.
- **Supplementary appendix**: appendix material must be a separate supplementary PDF for this project. It must complement, not replace, the self-contained main body. The main paper must not rely on appendix-only evidence for headline claims.
- **Self-contained main-body rule**: every headline empirical claim in the abstract, introduction, conclusion, or main findings must be supported by evidence visible in the main body. Critical method semantics must be explained in the main body at sufficient prose/equation detail for a careful reader to follow without opening the supplement.
- **Mandatory section**: an independent section titled exactly `Limitations` must appear after Conclusion and before References. It does not count toward the 8-page limit, but it must contain no new method, experiment, result, figure, table, or analysis.
- **Template**: use the latest official ACL style files only. Do not modify `acl.sty`, margins, paper size, font sizes, spacing, or template behavior.
- **Layout**: A4 paper, two columns, Times Roman / Times New Roman 11 pt, 2.5 cm margins, vector or vector-quality figures with embedded fonts.
- **Submission route**: submit first to ARR on OpenReview, then commit to EMNLP 2026 after reviews / meta-review.
- **Anonymization**: strict two-way anonymization. No author names, affiliations, acknowledgments, project-identifying links, or identifying repository URLs in the main paper or supplement.
- **Responsible research**: complete the Responsible NLP Research Checklist honestly in the submission form and reference the relevant paper sections.
- **Policy compliance**: obey ACL Ethics Policy, AI Writing Assistance Policy, Multiple Submission Policy, no dual submission, and no thinly sliced contribution.
- **Camera-ready**: one extra content page is available at camera-ready, for a maximum of 9 content pages.

## 3. Common Traits Of 2024/2025 EMNLP Best Papers

A Best-Paper-level submission should satisfy all of the following simultaneously:

- **Substantial and high-impact contribution**: it addresses a long-standing pain point, introduces a new paradigm or important method, clearly exceeds strong baselines, and has broad generality.
- **Extremely thorough experiments**: 4-6 diverse datasets for Best-Paper trajectory, latest SOTA and multiple competitive baselines, full ablation matrix, sensitivity analysis, statistical significance, error bars or confidence intervals, error analysis, and case studies.
- **Clear novelty and new insight**: the paper should state not only that a method works, but what was learned. Strong papers often contain explicit surprise or insight statements such as `Surprisingly, we found that ...`, grounded in evidence.
- **Self-contained and reproducible**: the main paper is readable by itself; code, data, models or equivalent scripts/specifications are anonymously available.
- **Deep limitations**: limitations honestly discuss assumptions, dataset bias, compute scope, failure scenarios, potential negative impacts, and scope of claims.

Representative calibration papers used for this demand:

1. Infini-gram mini, EMNLP 2025 Best Paper.
2. Image Transcreation for cultural relevance, EMNLP 2024 Best Paper.
3. Robust speech representation learning for thousands of languages, EMNLP 2024 Best Paper.

## 4. Seven Review Dimensions

1. **Soundness**: the method is correct, rigorous, and precisely reproducible.
2. **Significance / Impact**: the contribution is truly substantial and valuable to the NLP community.
3. **Novelty**: the difference from prior work is clear, important, and not merely a rephrasing or minor engineering tweak.
4. **Empirical Results And Analysis**: experiments are comprehensive and analysis is deep, not just a table of numbers.
5. **Reproducibility**: implementation details, data, code, hyperparameters, compute, and release commitments are sufficient.
6. **Clarity And Presentation**: writing is clean, section logic is explicit, and figures/tables are final-quality.
7. **Responsible Research And Limitations**: limitations are specific and honest; checklist and ethics requirements are complete.

## 5. Best-Paper Structure And Page Allocation

The 8-page content body should follow this shape unless there is a strong reason not to:

- **Introduction (1-1.5 pages)**: broad background -> concrete gap -> **bold one- or two-sentence core contribution statement** -> roadmap. It must answer: why is this substantial and impactful?
- **Related Work / Background (0.75-1.5 pages)**: categorized prior work and precise deltas. Avoid long survey padding.
- **Method / Proposed Approach (1.5-3 pages)**: exact description with equations, pseudocode, architecture or task diagrams, implementation detail, and hyperparameters.
- **Experiments / Evaluation / Analysis / Case Study (2.5-4 pages)**: the heaviest section. It should cover datasets, baselines, main results, ablations, sensitivity, significance, error analysis, case studies, and discussion.
- **Conclusion (0.5-1 page)**: compressed contribution summary and very limited future work.
- **Limitations (0.5-2 pages, not counted)**: independent, honest, specific, no new evidence.
- **Ethical Considerations / Broader Impact (0.5-1 page, recommended)**: data privacy, misuse risk, fairness, and reproducibility commitments.

Experiments must occupy the largest share of content space for Best-Paper readiness.

## 6. Limitations Requirements

- Title exactly `Limitations`.
- Placed immediately after Conclusion and before References.
- Discuss only limitations of the work already presented in the main paper.
- Cover assumption failures, dataset bias, compute scope, failure cases, potential misuse, fairness or demographic scope where relevant.
- No new method, experiment, result, figure, table, or analysis.
- Best-Paper-calibrated limitations are concrete and often at least one page.

## 7. Novelty Requirements

A Best-Paper candidate must be substantial. Acceptable novelty patterns include:

- a new framework or paradigm;
- a method that significantly exceeds SOTA across multiple tasks or datasets;
- an analysis that reveals an important new phenomenon;
- a reproducibility or benchmark contribution with durable community value.

The introduction must contain a bold contribution statement and a precise distinction from prior work. Avoid incremental, minor-improvement, or thinly sliced framing.

## 8. Experimental Design And Reporting Standards

For Best-Paper trajectory, the experiment section should satisfy:

- 4-6 diverse datasets, including real-world or transfer settings where possible;
- latest SOTA and multiple strong competing baselines;
- complete ablations proving the necessity of every claimed-essential component;
- sensitivity analysis over critical hyperparameters or thresholds;
- multiple runs, paired statistical tests, confidence intervals, effect sizes, and error bars where appropriate;
- deep error analysis and case studies, preferably with visualized success and failure examples;
- implementation details, hyperparameter search, compute resources, model/backend details, and artifact release commitments;
- anonymous code/data/model release, or sufficiently detailed pseudocode/specification where release is impossible.

## 9. Writing Style And Fatal Errors

Writing must be formal, precise, objective, and section-logical.

- Every section should begin with a clear topic sentence.
- Abstract, introduction, contribution bullets, experiments, conclusion, and limitations must make claims at the same strength.
- Supported surprising findings should be stated explicitly.
- Future work must not be framed as completed contribution.
- Every figure/table needs a number, caption, and detailed in-text explanation.
- Avoid redundancy, hallucinated citations, undisclosed AI-generated content, vague future-work claims, anonymity breaches, dual submission, ethics-policy violations, and thin slicing.

## 10. Figure And Table Standards

- **Figure 1** should usually appear in Introduction or at the start of Method as the overall system/task schematic.
- Method + Experiments should contain most visual evidence; roughly 80%+ of figures/tables should support method understanding or empirical claims.
- Figures must be vector or vector-quality, with clear labels and embedded fonts.
- Tables should be minimal but information-dense: dataset, backbone, seed, metric, cost, and context-policy grouping must be unambiguous.
- Every figure/table must be explained in the main text.
- Do not squeeze fonts or spacing to hide content overflow.

## 11. Reproducibility And Responsible Research

- Complete the Responsible NLP Research Checklist in the ARR form.
- Reference relevant paper sections for limitations, risks, scientific artifacts, licenses, intended use, compute, hyperparameters, statistics, human annotation if any, and AI assistance.
- Provide anonymous code/data/model artifacts or enough executable detail for independent reproduction.
- Discuss potential risks, bias, fairness, and misuse concretely.

## 12. Pre-Submission Checklist

All items below must pass before claiming Best-Paper readiness:

- [ ] Main body strictly <= 8 pages of content, including all main figures/tables/equations/algorithms.
- [ ] Supplementary appendix is a separate PDF and is not mixed into the main paper PDF.
- [ ] Main paper is self-contained; headline claims do not rely on appendix-only evidence.
- [ ] Independent `Limitations` section with exact title, no new content, and specific failure modes.
- [ ] Latest official ACL template, no style modification, A4, double column, Times Roman 11 pt, 2.5 cm margins.
- [ ] Introduction contains a bold core contribution statement and impact explanation.
- [ ] Experiments occupy 2.5-4 pages and include 4-6 diverse datasets for Best-Paper trajectory.
- [ ] Strong recent SOTA baselines, full ablations, sensitivity analysis, statistical tests, confidence intervals / error bars, deep error and case analysis.
- [ ] Responsible NLP Research Checklist is complete and honest.
- [ ] Strict two-way anonymization and ARR Author Checklist compliance.
- [ ] All figures/tables are vector or vector-quality, readable, and explained in the text.
- [ ] Contribution is substantial, high-impact, and supported by surprising or durable insight.
- [ ] No dual submission, thin slicing, ethics violation, hallucinated citation, or undisclosed AI assistance.
- [ ] Full text is self-contained, logically clear, polished, and broad-committee readable.

## 13. Project Enforcement Rule

For this project, every Scientist demand audit, Reviewer full-paper review, and best-paper-targeted partial review must explicitly apply this demand file. If older notes conflict with this file, this file wins unless the user explicitly revises it later.

Current hard deadline reminder: EMNLP 2026 ARR deadline is **2026-05-25**.
