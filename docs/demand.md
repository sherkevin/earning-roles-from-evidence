**EMNLP 2027 Long Paper Track – Excellence Demand File**

### 1. Track Core Positioning (Official Definition)
Official text (directly quoted from ARR CFP, which EMNLP 2026/2027 fully adopts):
> “Long papers must describe **substantial, original, completed and unpublished work**. Wherever appropriate, concrete evaluation and analysis should be included.”

**One-sentence core requirement**:  
An EMNLP Long Paper **must** be a **substantial, original, fully completed, and high-quality research contribution**. It requires a **clear, verifiable, and impactful innovation** + **comprehensive and rigorous empirical evaluation** + **in-depth quantitative and qualitative analysis** that advances the broader NLP community. It is **explicitly not** incremental work, preliminary ideas, a Short Paper extended version, or a paper that offers only theory/observations without thorough experimental support.

Any paper failing the “substantial + completed + concrete evaluation” standard faces extremely high risk of rejection at the ARR stage or during EMNLP commitment.

### 2. Formatting Requirements (Strict Compliance – Violation of Any Item = Desk Reject)
- **Page Limit**: Submission/review version is limited to a **maximum of 8 content pages** (main body only; references, Limitations, and Ethical Considerations do **not** count toward this limit). All figures, tables, equations, pseudocode, and algorithm descriptions **must** fit entirely within these 8 pages.
- **Mandatory Section**: An independent section titled exactly **“Limitations”** must appear after the Conclusion and before References. This section **does not count** toward the 8-page limit but **must not** contain any new methods, experiments, results, figures, tables, or analyses. Violation = immediate desk reject.
- **Template**: Use the **official ACL Style Files** only (latest version from https://github.com/acl-org/acl-style-files or the official Overleaf ACL template). **No modifications** to acl.sty or any style files are allowed; no other conference templates permitted.
- **Exact Layout Rules** (any deviation = desk reject):
  - Paper size: strictly A4 (21 cm × 29.7 cm).
  - Margins: 2.5 cm on all sides.
  - Font: Times Roman (or Times New Roman) 11 pt, two-column format (column width 7.7 cm, gap 0.6 cm).
  - All headings, captions, references, and footnotes must follow the template’s exact font sizes and spacing.
  - Figures/tables must be vector-based (PDF/EPS), embedded fonts, and clearly legible when printed. Font squeezing or spacing tricks to fit extra content are forbidden.
- **Submission System**: Submit first via **ACL Rolling Review (ARR)** on OpenReview, then commit to EMNLP 2027 after receiving reviews and meta-review.
- **Anonymization**: Strict **two-way blind review**. No author names, affiliations, acknowledgments, project names, GitHub links, or any identifying information may appear in the main paper or supplementary materials.
- **Additional Mandatory Requirements**:
  - Complete the **Responsible NLP Research Checklist** (filled in the submission form; every item must be answered honestly and referenced by section number in the paper).
  - Comply with ACL Publication Ethics Policy, AI Writing Assistance Policy, and Multiple Submission Policy.
  - No dual submissions; no “thinly sliced” contributions.

**Camera-ready stage**: Authors receive **one extra content page** (maximum 9 pages) to address reviewer comments.

### 3. Unified Characteristics of Accepted Long Papers (Common Traits of All Oral/Spotlight Papers)
Every paper accepted at EMNLP (especially high-scoring Oral presentations) simultaneously satisfies **all** of the following:
- **Substantial and novel contribution**: Clear, important, and broadly applicable innovation—not minor tweaks.
- **Extremely high completeness**: Multi-dataset experiments (minimum 3–5 representative datasets), strong baselines (latest SOTA + multiple competitive systems), full ablation/sensitivity studies, statistical significance tests, error analysis, and case studies.
- **Rigorous empirical validation**: Fully reproducible results with clear explanations and either theoretical grounding or strong empirical evidence.
- **Self-contained**: The main text can be read and understood independently without relying on appendices.
- **Generality and impact**: Offers insights or solutions that matter to the wider NLP community, often addressing long-standing challenges or emerging issues (LLM reliability, safety, multilingual settings, low-resource scenarios, fairness, etc.).

### 4. Review Criteria – The 7 Dimensions Reviewers Weight Most Heavily (ARR Official Review Form Order)
1. **Soundness / Technical Soundness** (highest weight): Are the methods correct, reproducible, and rigorous?
2. **Significance / Impact**: Is the contribution substantial and valuable to the community?
3. **Novelty**: Are the differences from prior work clear and important?
4. **Empirical Results & Analysis**: Are experiments comprehensive? Is the analysis deep?
5. **Reproducibility**: Are implementation details sufficient? Are code/data provided anonymously?
6. **Clarity & Presentation**: Is the writing clear, logically structured, and are figures/tables of high quality?
7. **Responsible Research & Limitations**: Are limitations discussed honestly? Is the Responsible NLP Checklist complete?

### 5. Detailed Structure and Logic Requirements (Standard Flow + Suggested Page Allocation for Excellence)
- **Title & Abstract** (≈0.5 page): Abstract (200–250 words) must clearly state the problem, core contribution, key results, and impact.
- **Introduction** (1–1.5 pages): Provide background → specific research gap → **bold, explicit 1–2 sentence contribution statement** → outline of paper structure. Must explicitly answer “Why is this work substantial?”
- **Related Work** (0.75–1.5 pages): Categorize prior work and **precisely position** the current contribution (avoid lengthy surveys).
- **Method / Proposed Approach** (2–3 pages – one of the heaviest sections): Provide precise, reproducible descriptions (equations, pseudocode, architecture diagrams, hyperparameter details).
- **Experiments / Evaluation** (2.5–3.5 pages – usually the most important section): Describe datasets (source, statistics, license), baselines (SOTA + strong comparators), metrics, main results (multiple tables + figures), **full ablation studies**, sensitivity analyses, statistical tests, error analysis, case studies, and discussion.
- **Conclusion** (0.5 page): Summarize contributions + brief future work (keep short).
- **Limitations** (0.5–1+ pages, not counted in limit): Independent section; honest, specific, and in-depth discussion of all limitations of the presented work (assumptions, scope, biases, failure cases, potential risks). **No new content allowed.**
- **Optional: Ethical Considerations / Broader Impact** (strongly recommended).

### 6. Strict Guidelines for the Limitations Section (Official + High-Scoring Practice)
- Title must be exactly **“Limitations”** and placed immediately after Conclusion.
- Content discusses **only** limitations of the work already presented in the main paper.
- Excellent examples explicitly cover assumption failures, dataset biases, computational limits, potential negative societal impacts, and directions for improvement.
- Poor examples (risk low scores or rejection): overly vague statements, treating it as future work, or omitting real issues.

### 7. Responsible NLP Research Checklist – Mandatory Compliance
Must be completed item-by-item in the ARR form and referenced by section in the paper. Critical items include:
- Limitations discussion, potential risks, scientific artifact usage (citations, licenses, intended use), experimental details (parameters, compute budget, statistical tests), human annotation/participant details, and AI assistance disclosure.
- Any systematic omissions or misleading answers = desk reject.

### 8. Experimental Design & Reporting Standards (Non-Negotiable for High Scores)
- Minimum 3–5 diverse datasets.
- Strong baselines including latest SOTA.
- Complete ablation studies proving necessity of every component.
- Multiple runs + statistical significance + error bars.
- Full implementation details, hyperparameter search, and compute resource reporting.
- Reproducibility: anonymously provide code/data links or sufficiently detailed pseudocode.

### 9. Writing Style & Fatal Errors to Avoid
- Language: formal, precise, objective; frequent use of “We propose…”, “Our experiments demonstrate…”, “Results show that…”.
- Every section begins with a clear topic sentence.
- All figures/tables must have numbers, captions, and detailed inline explanations.
- Avoid: redundancy, hallucinated citations, thinly sliced contributions, undisclosed AI-generated text.

### 10. Stand-Out Paradigms (What Makes Papers Truly Excellent)
High-scoring Long Papers typically feature one or more of the following:
- A novel framework/method that significantly outperforms SOTA across multiple tasks/datasets.
- Important new insights (“Surprisingly, we found that…”).
- Extremely thorough analysis with theoretical or strong empirical grounding.
- High reproducibility (public code, data, models).
- Solutions to genuinely important emerging challenges.

**One-sentence summary of excellence**:  
It must be a **deep, broad, rigorously evidenced substantial contribution** that any reviewer would recognize as clearly worthy of acceptance.

---

**Submission-Ready Checklist (100% Completion Required – Otherwise Extremely High Desk-Reject Risk)**:
- [ ] Main content strictly ≤ 8 pages (including all figures/tables)
- [ ] Independent “Limitations” section present with exact title and no new content
- [ ] Latest official ACL template used with zero modifications
- [ ] Introduction contains a clear, bold core contribution statement
- [ ] Experiments include strong baselines, multiple datasets, full ablations, and deep error analysis
- [ ] Responsible NLP Research Checklist fully and honestly completed
- [ ] Strict two-way anonymization (no identifying information anywhere)
- [ ] All figures/tables are vector-based, clear, and print-ready
- [ ] ARR Author Checklist completed (https://aclrollingreview.org/authorchecklist)
- [ ] No dual submission, no thinly sliced work, full ethics policy compliance
- [ ] Paper is self-contained, logically clear, and free of obvious English errors
- [ ] All ARR/ACL ethics & formatting policies have been read and followed

**Final Note**: This file is based on the most current ARR + EMNLP 2026 official requirements (as of April 2026). EMNLP 2027 CFP will use the identical core rules. If any minor updates appear after CFP release, the document will be synchronized immediately.

Start writing with the official template now. Would you like:
- A ready-to-copy LaTeX skeleton with exact section ordering?
- Concrete example paragraphs for the Limitations section (excellent vs. poor)?
- Or item-by-item guidance on filling the Responsible NLP Checklist?

Just let me know and we will polish the manuscript to the highest possible standard.