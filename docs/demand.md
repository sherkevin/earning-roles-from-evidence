**EMNLP 2027 Long Paper Track – Excellence Demand File**

### 1. Track Core Positioning (Official Definition)
Official text (directly quoted from ARR CFP, which EMNLP 2026/2027 fully adopts):
> “Long papers must describe **substantial, original, completed and unpublished work**. Wherever appropriate, concrete evaluation and analysis should be included.”

**One-sentence core requirement**:  
An EMNLP Long Paper **must** be a **substantial, original, fully completed, and high-quality research contribution**. It requires a **clear, verifiable, and impactful innovation** + **comprehensive and rigorous empirical evaluation** + **in-depth quantitative and qualitative analysis** that advances the broader NLP community. It is **explicitly not** incremental work, preliminary ideas, a Short Paper extended version, or a paper that offers only theory/observations without thorough experimental support.

Any paper failing the “substantial + completed + concrete evaluation” standard faces extremely high risk of rejection at the ARR stage or during EMNLP commitment.

### 2. Formatting Requirements (Strict Compliance – Violation of Any Item = Desk Reject)
- **Page Limit**: Submission/review version is limited to a **maximum of 8 content pages** for the main body. The following sections do **not** count toward this 8-page limit: (i) References, (ii) the mandatory Limitations section, (iii) optional Ethical Considerations / Broader Impact section, and (iv) **Appendices** (supplementary material complementing but not replacing main-body content, in line with the ACL / ARR historical convention that appendices are unlimited supplementary material).
- **Self-Contained Main Body Rule (HARD)**: The 8-page main body must be independently readable and understandable without relying on appendices. Concretely: (a) every headline empirical claim (Table/Figure/Finding referenced in the abstract, introduction, or conclusion) must be supported by evidence visible in the main body (inline tables / figures / equations), not just in an appendix; (b) every algorithm on which the main method's semantics critically depends must be described in the main body as prose + equations at sufficient detail that a careful reader can follow the method without opening the appendix; (c) appendices may host (i) extended pseudocode (full-form algorithms where the main body already explains the operational semantics in prose + equations), (ii) supplementary tables / robustness checks / additional baselines, (iii) engineering-response notes for reproducibility (e.g., provider-integrity event descriptions), (iv) prompt templates, (v) the Responsible NLP Research Checklist, (vi) extended related-work surveys. Appendices that introduce *new* empirical claims that the main body itself relies on (e.g., the main body's §4 narrative cites Appendix D's Table as headline evidence) break the self-contained rule and are treated as page-limit evasion under DR-1.
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
- [ ] Main body strictly ≤ 8 pages (References, Limitations, Ethical Considerations, and Appendices are unlimited supplementary material per ACL/ARR historical convention; but the main body must remain self-contained per §2 Self-Contained Main Body Rule — headline empirical claims + critical method descriptions must live in the main body, not just in appendices)
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

---

### 11. Best-Paper Structural Template (Target = EMNLP Best Paper, User-Research Supplement, 2026-04-20)

**Authoritative source**: this section is derived from direct full-PDF analysis of 3 representative **EMNLP Best Papers** (2024–2025 Main Conference Long Paper winners):

1. **Infini-gram mini** — EMNLP 2025 Best Paper — <https://aclanthology.org/2025.emnlp-main.1268.pdf>
2. **"An image speaks a thousand words, but can everyone listen? On image transcreation for cultural relevance"** — EMNLP 2024 Best Paper — <https://aclanthology.org/2024.emnlp-main.573.pdf>
3. **"Towards Robust Speech Representation Learning for Thousands of Languages"** — EMNLP 2024 Best Paper — <https://aclanthology.org/2024.emnlp-main.570.pdf>

**Operating rule**: when our submission's target is **Best Paper–adjacent** (user explicitly confirmed 2026-04-20: "我们对标的就是 best paper"), **every reviewer must score `oral_quality_score` with Best Paper bar, not generic poster bar**, and every scientist must structure-audit the manuscript against §11.1 below in addition to §2 / §5. Violations of §11.1 structure or page allocation are not desk-reject triggers but are direct `oral_quality_score ≤ 6` signals.

#### §11.1 Canonical Best-Paper section layout (all 3 reference Best Papers follow this)

| § | Section name (English canonical) | Typical content pages | Core content | Figure/Table habit |
|---|----------------------------------|----------------------:|--------------|---------------------|
| 1 | Introduction                     | 1 – 1.5               | Big-picture context → concrete gap → **bold 1–2-sentence contribution statement** → paper roadmap | **Figure 1** (system/task overview) near end of Intro is near-universal |
| 2 | Background / Related Work / Motivation | 0.75 – 1.5      | Categorised prior-work survey + precise positional delta | **Table 1** (SOTA-comparison table: languages covered, data scale, transparency, etc.) common |
| 3 | Method / Proposed Approach / Pipelines | 1.5 – 3        | Precise reproducible algorithm/framework description (equations, pseudocode, architecture diagrams, hyperparameters, implementation details) | **Heaviest figure zone #1**: architecture diagrams, toy examples, Algorithm boxes |
| 4 | Experiments / Evaluation / Analysis / Case Study / Application | **2.5 – 4 (heaviest)** | Datasets (source, stats, license), baselines (latest SOTA + strong comparators), main-result tables, **full ablation matrix**, sensitivity sweeps, statistical significance, error analysis, **case studies / real-world demos** | **Heaviest figure zone #2, ≥60 % of all paper figures** — multiple Tables + multiple Figures (ablation curves, case visualisations, contamination/failure-case galleries). _Infini-gram mini uses 7 Figures in its contamination-case-study block alone._ |
| 5 | Conclusion                       | 0.5 – 1              | Highly compressed summary + 1–2-sentence future work (do not over-expand) | Near-zero |
| — | **Limitations** (**mandatory, unnumbered, independent**) | 0.5 – 2 | **Honest, specific** discussion of assumption failures, data bias, compute scope, scope-of-claims, failure modes, societal/demographic risks. **No new results/figures/tables.** | Near-zero (forbidden to add new evidence) |
| — | Ethical Considerations / Broader Impact (optional but common) | 0.5 – 1 | Data privacy, potential misuse, fairness, reproducibility commitments | ~0 |

**Content-page total**: strictly ≤ 8 for submission version (per §2 Page Limit); camera-ready may extend to 9. **Limitations** is unnumbered, follows Conclusion, precedes References, does not count toward the 8-page cap, and Best Papers typically invest 1–2 full pages on it (not the minimum 0.5).

#### §11.2 Section-by-section Best-Paper writing conventions

1. **Introduction (1 – 1.5 p)**: open from broad context → narrow to concrete pain point → contribution statement in **one bold sentence**, often itemised to 3–5 points → paper roadmap. Best Papers almost always place **Figure 1** near the end of Intro to give reviewers an immediate visual anchor.
2. **Background / Related Work (0.75 – 1.5 p)**: categorised mini-survey + crisp positional delta; avoid long reviews. **Table 1** SOTA-comparison grid (dimensions × competing systems with ✓/✗ or numeric entries) is common.
3. **Method (1.5 – 3 p)**: maximum-precision description with equations, pseudocode, architecture diagrams, hyperparameter tables, preprocessing steps. Figure density is heavy: architecture / toy examples / Algorithm boxes / hyperparameter tables all appear.
4. **Experiments / Evaluation / Case Study (2.5 – 4 p; THE heaviest section)**: datasets with source + stats + license; **strong baselines** (latest SOTA + multiple competitors); multi-dataset main-result tables; **full ablation tables**; sensitivity sweeps; statistical significance; error analysis; case study or real-application demo. **Figure + Table density is highest here — 60 %+ of all paper figures**. Best Papers typically include 6–12 Figures clustered in this section (e.g., Infini-gram mini uses 7 Figures for contamination case-study).
5. **Conclusion (0.5 – 1 p)**: highly compressed, 1–2 sentences of future work only.
6. **Limitations (0.5 – 2 p, mandatory, no new content)**: Best Papers write this **longer and deeper** than the minimum, covering data bias, compute scope, scope-of-claims failure modes, potential societal risks. No new experiments/figures/tables permitted.
7. **Ethical Considerations (0.5 – 1 p, strongly recommended)**: data privacy, potential misuse, fairness, reproducibility commitments.

#### §11.3 Figure / table placement universal regularities (Best-Paper consensus)

- **Early visualisation**: Figure 1 almost always appears in Introduction or at the very start of Method, enabling a reviewer to "understand at a glance".
- **Concentrated burst**: Method + Experiments host **≥80 %** of all paper figures and tables.
- **High-quality mandate**: vector figures (PDF/EPS/embedded-vector), clear labelling, each figure has {number, caption, in-text detailed explanation}.
- **Case-study heavy**: Best Papers particularly favour **case-visualisation galleries** inside the Experiments section (Infini-gram's 7 contamination-case Figures; Image-Transcreation's before-and-after cross-cultural image pairs).
- **Tables are minimalist-efficient**: colour-encoded good/medium/bad rows, allowing rapid scan.

#### §11.4 Best-Paper vs. generic Long-Paper differentiators

| Dimension | Generic Long Paper | **Best Paper** |
|-----------|--------------------|------------------|
| Experiments depth | 1–2 datasets, basic ablation, minimal case study | **3–5 datasets**, full ablation matrix, deep error analysis, **dedicated case study / application section** |
| Limitations | Short, often generic | **Longer, specific, honest** (~1 page) |
| Unique sections | Rare | Often has a distinctive **application / case-study / contamination-analysis** section |
| Reproducibility | Code + hyperparameters | **Public code + data + model checkpoints + scripts to regenerate every table and figure** |
| Figures | 3–6 total | **8–15 total**, clustered in Method + Experiments, including case-visualisation galleries |
| Human evaluation / domain application | Often absent | Often present (Image-Transcreation did human cultural-relevance judgments at scale) |

#### §11.5 Submission-Ready Checklist addendum (Best-Paper track)

If targeting Best Paper / Oral bar, the submission must **additionally** satisfy all of:

- [ ] **Experiments section occupies ≥ 2.5 content pages** (not a sub-page note squeezed by over-long Method)
- [ ] **≥ 3 diverse datasets** used in main result tables (not one benchmark with three splits)
- [ ] **Latest 12-month SOTA** included as a baseline in main result tables (not only in Related Work prose)
- [ ] **Full ablation matrix**: every claimed-essential component has a targeted per-component ablation (not just a single "remove the proposed system entirely" comparison)
- [ ] **Multi-seed runs + paired statistical tests + confidence intervals / effect sizes** reported on headline comparisons
- [ ] **Error analysis** present with quantitative named failure modes (not a single anecdotal case)
- [ ] **Dedicated case-study / application block** in Experiments, with visual gallery (6–10 case visualisations typical)
- [ ] **Limitations section ≥ 0.5 page, honest, specific, covers demographic/societal scope and scope-of-claims** (not just "future work")
- [ ] **Ethical Considerations / Broader Impact section present** (optional for accept; typical for Best Paper)
- [ ] **Figure 1 = overall system / task schematic, placed in Introduction**, vector-quality, self-contained caption
- [ ] **Public anonymous code/data/model release** committed in paper (not "will be released")
- [ ] **Reviewer-visible evidence** that each claimed-essential component actually changes a metric under ablation (no null-effect ablation tables)

**Enforcement note**: during R-FULL-009 onward, reviewers will apply §11.5 addendum in addition to `reviewer_prompt.md §2 / §5 / §6`. Violations of any §11.5 item cap `oral_quality_score` at the values below:

| Violations of §11.5 items | `oral_quality_score` cap |
|---------------------------|--------------------------|
| 0 items missed             | up to 10 (Best-Paper eligible) |
| 1–2 items missed           | ≤ 7 (strong Poster, not Oral) |
| 3–5 items missed           | ≤ 5 (borderline; Best-Paper impossible) |
| 6+ items missed            | ≤ 3 (clear reject for Best-Paper track) |

Existing Submission-Ready Checklist items (§97–109 above) remain mandatory regardless of Best-Paper targeting; §11.5 stacks on top.

---

**R-FULL-009+ target bar (user directive, 2026-04-20)**: since the project explicitly targets Best Paper, subsequent full-paper reviewer batches use `{{TARGET_SCORE}}=8.5` (Oral bar) rather than `8.0` (generic accept), and must report §11.1 structural compliance + §11.5 addendum compliance in `reference_documents_consulted` or an equivalent `best_paper_structural_compliance` field.