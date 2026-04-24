# R-FULL-021 — Full-paper review (P2 Empirical-NLP SAC STRICT, experiments-weighted)

## Batch metadata

| Field | Value |
|-------|--------|
| `review_run_id` | `reviewer_20260423_142849_21_f914b8` |
| `reviewer_profile` | `P2: Empirical-NLP SAC` — experiments-weighted, best-paper bar, strict on benchmark breadth / baseline recency / ablations / seed / CI |
| `target_pdf` | `d:\Codes\idea04\article\build\edo_paper.pdf` |
| `pdf_sha16` | `F914B89A4E45F1EF` |
| `target_score` | `8.5` |
| `independence_note` | Fresh full-paper read against the current PDF, `docs/demand.md`, and `prompts/reviewer_prompt.md`; this batch is a new experiments-first review of the latest manuscript state. |
| `reference_documents_consulted` | `docs/demand.md` + current PDF end-to-end |

---

## Document classification

`document_type = full_paper`

`submission_track = EMNLP Long Paper - Oral evaluation`

---

## Summary

The paper proposes EDO as a decentralized organizational framework and positions TCPB as a restricted Stage-1 instantiation. Relative to earlier states of the manuscript, the current draft is materially stronger on formalization, related-work positioning, and research hygiene: the method is better delimited, the MAD/MA-RAG/ReAgent discussion is more concrete, and the appendices now carry real formal support. But under a strict experiments-weighted EMNLP review, the decisive bottleneck is unchanged: the delivered empirical evidence is still one benchmark, one seed, no paired statistical test, no confidence intervals, and no external 2024-2025 SOTA in the main tables. The paper is no longer primarily blocked by soundness presentation; it is still blocked by empirical breadth and rigor.

---

## Desk-reject risks

| ID | Status | Evidence |
|----|--------|----------|
| DR-1 | PASS | Current build is 8-page main body compliant; `Conclusion` ends on page 8 and `Limitations` starts after it. |
| DR-2 | PASS | Exact title `Limitations` is present after `Conclusion`. |
| DR-3 | PASS | No new method/results are moved into `Limitations`; engineering detail remains in appendices. |
| DR-4 | POSSIBLE - cannot fully verify from extracted text | Template/font/margin manipulation cannot be conclusively audited from text extraction alone. |
| DR-5 | PASS | No obvious anonymization breach or reviewer-leak string is visible in current text. |
| DR-6 | PASS | Responsible NLP checklist appears present and internally consistent with the main text. |
| DR-7 | PASS | No thin-slicing / dual-submission pattern is inferable from the visible manuscript. |
| DR-8 | PASS | AI-assistance disclosure and ethics language are present. |

Net result: no confirmed desk-reject trigger.

---

## Best-paper structural compliance

Current state remains roughly:

- `2 pass`: Limitations depth; Ethical Considerations presence
- `3 partial`: experiments section lower-bound length; public artifact / release visibility; ablation-honesty discussion
- `7 fail`: multi-dataset breadth, latest SOTA in main tables, multi-seed + paired CI, quantitative error analysis, case-study block, final Figure 1 quality, external-baseline completeness

Per `docs/demand.md §11.5`, this keeps `oral_quality_score` capped low.

---

## Experiments-solidity audit

| Check | Status | Evidence |
|-------|--------|----------|
| EXP-1 multi-dataset | **fail** | Main body evidence is HotpotQA only; MuSiQue and 2Wiki are still future-work / Stage-2 agenda items. |
| EXP-2 multi-seed | **fail** | Current text still reports chain-200 `seed=42`; `seed=43/44` remain pending in the full-validation narrative. |
| EXP-3 significance test | **fail** | No paired bootstrap / sign test / paired t-test is reported for headline main-table comparisons. |
| EXP-4 effect size or CI | **fail** | No 95% CI or effect-size reporting is given for the canonical main-table method gaps. |
| EXP-5 ablation coverage | **pass** | Table 2 targets the delivered Stage-1 mechanism knobs (`peer_update_enabled`, `decomposer_force_forward_enabled`) plus evidence-window size. |
| EXP-6 baseline recency | **fail** | Main result tables still contain no external 2024-2025 SOTA systems; `MA-RAG` / `ReAgent` are cited in related work but not benchmarked. |
| EXP-7 sensitivity sweep | **partial** | Text mentions `±2x` sweeps and route-overlap behavior, but there is no reviewer-visible sensitivity block with main-table weight. |
| EXP-8 error analysis | **fail** | No quantitative named failure-mode taxonomy appears in the main empirical section. |

### Experiments-solidity score

`experiments_solidity_score = 1 / 8`

### Caps implied by audit

```text
EXP-1 fail  -> cap D4 at 6
EXP-2 fail  -> cap D4 at 5 and cap S5 at 4
EXP-3 fail  -> cap D4 at 6 and cap S5 at 5
EXP-6 fail  -> cap D4 at 5 and cap S6 at 4
exp_solidity_score <= 3 -> cap overall at 4.5
```

### Fresh experiments-weighted conclusion

This manuscript's empirical bottleneck is now extremely concentrated:

- `D1 / D5 / D7` are no longer the main weakness classes.
- `D3` is no longer catastrophic because the overlap-risk discussion is more concrete and the 2025 related-work hole is partly closed.
- `D4` remains the sole decisive blocker under a P2 reading.

---

## Novelty delta audit

| Prior work | Year | Claimed difference in paper | Concrete? | Overlap risk? |
|-----------|------|-----------------------------|-----------|---------------|
| Multi-Agent Debate | 2024 | Current-turn critique aggregation vs accepted-value update on delegation edges across episodes | yes | partial |
| ChatEval | 2024 | Meta-review aggregation vs recursive upstream audit object | yes | no |
| AutoGen | 2024 | Central manager / globally controlled speaker selection vs local-visibility decentralized routing | yes | no |
| MetaGPT | 2024 | Fixed software-pipeline roles vs local-organization framing with socially formed personas | partial | partial |
| MA-RAG | 2025 | Fixed specialist retrieval/synthesis stack vs local persona-update routing | yes | no |
| ReAgent | 2025 | State-triggered role rollback vs accepted-value peer calibration | yes | no |

### D3 judgment under this batch

The novelty position is better than in earlier weaker drafts because:

1. The manuscript now names recent 2025 systems (`MA-RAG`, `ReAgent`) rather than leaving the reviewer to infer the missing frontier.
2. The MAD overlap is now addressed in mechanistic language instead of only rhetorical framing.
3. The appendices now formalize `H3`, the Stage-1 extractor for `ϕ(z)`, and the R2 audit lower-bound story.

However, the submission still does **not** empirically differentiate itself from those nearest systems, and the delivered evidence remains a restricted Stage-1 prototype rather than the full claimed framework. Under a strict SAC reading, this remains:

`D3 = 5.5`

That is: stronger than a framing-only `5.0`, but still below the band where novelty is empirically or formally undeniable.

---

## Scores

| Dimension | Score | Rationale |
|----------|-------|-----------|
| D1 Soundness | **7.0** | Current paper is now operationally specified well enough that a careful reader can recover the delivered Stage-1 system without re-designing it. |
| D2 Significance | **4.5** | The research direction is interesting, but the delivered evidence is still too narrow to establish broader NLP impact. |
| D3 Novelty | **5.5** | Related-work positioning and mechanistic delta are better, but the contribution remains only partially distinguished in delivered empirical terms. |
| D4 Empirical results | **4.0** | Single benchmark, single seed, no paired significance, no CI, no external SOTA in main tables. |
| D5 Reproducibility | **6.5** | Stronger than before: prompt templates, formal supplements, and checklist details are reviewer-visible, but still not full regeneration-grade. |
| D6 Clarity | **6.0** | Readable and much cleaner, but Figure 1 is still a placeholder and the experiments section remains underweight. |
| D7 Responsible research / Limitations | **8.0** | Limitations and ethics are specific, honest, and structurally well handled. |

### Secondary scores

| Score | Value |
|------|-------|
| S1 Executability | **7.0** |
| S2 Falsifiability | **5.5** |
| S3 Empirical plan | **5.5** |
| S4 Technical clarity | **6.5** |
| S5 Statistical rigor | **3.0** |
| S6 Baseline quality | **2.0** |
| S7 Ablation completeness | **4.5** |
| S8 Writing and figures | **5.5** |
| Oral quality score | **2.5** |

---

## Score calculation

```text
weighted_sum
= 0.25*7.0 + 0.18*4.5 + 0.15*5.5 + 0.18*4.0 + 0.10*6.5 + 0.07*6.0 + 0.07*8.0
= 1.750 + 0.810 + 0.825 + 0.720 + 0.650 + 0.420 + 0.560
= 5.735

Caps triggered:
- D4 < 5                 -> cap overall at D4 + 0.5 = 4.5
- oral_quality < 5       -> cap overall at 5.5
- exp_solidity <= 3      -> cap overall at 4.5
- S6 < 5                 -> cap overall at 6.0
- S7 < 5                 -> cap overall at 6.0

Final overall = 4.5
```

`verdict = weak_reject`

`oral_eligible = false`

`confidence = 4 / 5`

---

## Top strengths

1. The paper is materially better formalized than earlier prototype-heavy drafts.
2. The delivered-vs-future boundary is now explicit and largely honest.
3. Limitations and Ethical Considerations are reviewer-visible strengths rather than liabilities.
4. Related-work coverage is more timely and concrete than before.

## Top weaknesses

1. **Single-benchmark evidence** remains the dominant issue: HotpotQA only.
2. **Single-seed reporting** is still unacceptable for oral / best-paper ambitions.
3. **No paired significance / no confidence intervals** means headline gaps are not statistically grounded.
4. **No external 2024-2025 SOTA in main result tables** keeps baseline quality very low.
5. **Table 2 ablations are on `glm-4-flash` and mostly null-effect**, so they do not rescue the canonical backbone claim.
6. **No quantitative error analysis** means the experiments section still falls short of top-tier standards.
7. **Figure 1 remains a placeholder**, which is still a real presentation liability.

---

## Core method problems

1. The framework is better delimited, but still validated mainly as a restricted prototype narrative rather than as a completed full method.
2. The strongest mechanisms (`split`, recursive audit, vector-belief routing) remain only partially delivered empirically.

## Experimental design problems

1. One benchmark only.
2. One seed only.
3. No paired significance testing.
4. No confidence intervals.
5. No external SOTA in main tables.
6. No quantitative failure taxonomy.

## Implementation / reproducibility gaps

1. Main claims still rely on partially in-progress rerun status for the broader full-validation story.
2. Regeneration-grade table / figure reproduction is promised clearly but not yet maximally reviewer-visible.

## Overclaims / risky framing

1. The paper still asks the reviewer to buy an organizational-emergence framing without matching multi-dataset evidence.
2. Cost-normalized signals are interesting, but they do not substitute for absolute-performance breadth and statistical proof.

---

## Missing or weak experiments

1. Add at least one second benchmark in the main body, ideally `MuSiQue`.
2. Finish `seed=43/44` and report paired-bootstrap CI or equivalent.
3. Put at least one external 2025 system into the main comparison table.
4. Re-run the mechanism ablation on the canonical `gpt-4.1-mini` backbone.
5. Add a quantitative error-analysis block with named failure modes.

## Statistical-significance concerns

1. No paired statistical test for the headline method gaps.
2. No 95% CI for the main result table.
3. Current full-validation narrative is still partly "in progress".

## Baseline-completeness concerns

1. `MA-RAG` and `ReAgent` are now cited, but still absent from the actual result tables.
2. The paper cannot claim strong empirical positioning while only comparing internal baselines.

---

## Limitations section assessment

| Field | Value |
|-------|-------|
| section_present | true |
| section_title_exact | true |
| contains_no_new_content | true |
| honesty_score_1_to_5 | **5** |
| specific_failure_modes_listed | true |

Issues:

- None major; this section is now a strength rather than a weakness.

## Responsible NLP checklist assessment

| Field | Value |
|-------|-------|
| appears_complete | true |

Issues:

- No major checklist inconsistency observed from the current text.

---

## What to fix for 8+

1. Put `MuSiQue` into the main results, not only future work.
2. Finish three-seed evaluation and report paired CI / statistical tests.
3. Add at least one external 2025 SOTA baseline to the main table.
4. Re-run Table 2 ablations on `gpt-4.1-mini`.
5. Add quantitative error analysis with named failure modes.
6. Replace the Figure 1 placeholder with the final vector figure.

## What to fix for oral

1. Everything in "fix for 8+".
2. Show multi-dataset gains that are not confined to one benchmark.
3. Demonstrate that at least one delivered mechanism yields a statistically supported win.
4. Provide a much stronger experiments section with broader tables and sharper conclusions.

## Recommended next actions

1. Treat `D4` as the sole critical blocker and prioritize experiment closure over further wording polish.
2. Close the `seed=43/44` + paired-CI chain before opening another experiments-heavy full review.
3. Land at least one external SOTA comparison before strengthening introduction / conclusion claims.
4. Use a non-LLM quantitative error-analysis pass from existing logs to partially close `EXP-8`.

---

## Final judgment

This is a more serious and better-specified paper than the earlier prototype-heavy states of the project, and the current draft is no longer mainly blocked by formalization hygiene. But under a strict experiments-weighted EMNLP best-paper review it is still **not empirically ready**. The manuscript's center of gravity has shifted: the main weakness is now clearly **insufficient experimental breadth and rigor**, not merely method exposition. My assessment is therefore:

- `overall = 4.5`
- `verdict = weak_reject`
- `estimated_score_after_fixes = 6.1 – 6.5`
- `estimated_score_after_best-real experimental closure = 6.8+`, but still not oral without much broader evidence
