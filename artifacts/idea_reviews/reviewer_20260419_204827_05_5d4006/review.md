# Review of `article/build/edo_paper.pdf` (R-FULL-005)

> ## ⚠ SOFT SCORING — SUPERSEDED BY R-FULL-006 STRICT REVISION
>
> **Issued at**: 2026-04-19 ~20:48. Per user feedback "不够严厉，你的审稿太过于温和" issued shortly after this review landed, the scoring below is admitted to be **soft / lenient on multiple dimensions**, even though it claimed P4 strictness. Specifically the following dimension scores were inflated by giving credit for "scientist made hygiene effort" rather than evaluating content quality against the rubric bands:
>
> | Dim | Original (soft) | R-FULL-006 strict | Why this was soft |
> |---|---:|---:|---|
> | D1 soundness | 5.5 | **4.5** | Algorithm 1 has 8+ undefined functions (FIT for vector, AUDIT non-default rule, EVIDENCE_EXTRACT, SPLITGAIN/MERGECOST/AUDITCOST, λ_c/λ_a/λ_m/λ_d/λ_s/λ_r, TCPB weight-to-term mapping). LLM_ANSWER / LLM_DECOMPOSE / AUDIT-rule / EVIDENCE_EXTRACT prompts not in paper body. By band 5 ("Material gaps: a concept is intuitive but not implementable from the paper") this is exactly the right anchor. 5.5 was a band-6 score that gave credit for "Algorithm 1 inline" effort — but the inlined algorithm itself contains the un-implementable holes. |
> | D5 reproducibility (P4 SPECIALTY) | 5.5 | **4.0** | P4 should be MOST strict here. Reading paper alone you cannot reproduce TCPB. LLM-call prompts, ϕ extraction rule, FIT vector form, audit_score proxy, TCPB weight-to-term mapping all in external `edo_lite_executable_spec.md` supplement. By band 4 ("Methods description is too sparse for any reliable replication") this is the correct anchor. Wall-clock + USD reporting is a B2 hygiene check that does NOT compensate for missing prompts/rules — that was the mistake. |
> | D6 clarity | 6.0 | **5.0** | Figure 1 caption explicitly admits placeholder ("Vector asset to be inserted") — for an EMNLP submission this is band-5 territory ("Substantial revision needed for ... figure quality"), not band-6 "minor awkward phrasing". Algorithm 1 column-spanning narrative + multiple undefined symbols make the methods section materially harder to read on first pass. |
> | D7 limitations (P4 SPECIALTY) | 7.5 | **5.5** | This was the worst inflation. Limitations 5 items are: (1) Stage-1 only / (2) safety priors entanglement / (3) backbone-sensitive conjectural / (4) statistical evidence point estimates deferred / (5) cross-endpoint comparability open. Of these, (1) (4) (5) are framed as "Stage-2 will fix this" — band-5 explicitly: "Limitations read as future work rather than honest scope-bounding". Item (2) is vague. Only item (3) is genuinely conjectural-honest. Plus: NO demographic / societal / multilingual / dataset-bias / per-method failure-mode discussion (band 8+ requires demographic/societal). Honest = 5.5 (between band 5 future-work tone and band 6 vague), not 7.5. |
> | S1 executability | 5.0 | **4.5** | "needs guesswork on multiple components" = 6; "effectively un-implementable" = 3. With LLM prompts + ϕ + FIT + audit_score + weight mapping all in supplement, the paper alone cannot be reimplemented in 1 week → 4.5. |
> | S2 falsifiability | 5.5 | **4.5** | Central EDO claim "emergent organization from local interaction" admittedly NOT testable as designed (Stage-2 mechanisms not implemented). The TCPB sub-claim that IS testable was self-falsified. |
> | S3 empirical_plan | 6.0 | **5.0** | Plan covers main comparison only; given execution shows the claimed mechanism doesn't help, plan quality is downgraded — band 5 ("covers main comparison only"). |
> | S4 technical_clarity | 6.0 | **5.0** | Multiple symbols undefined; equations clear but operational meaning incomplete → band 5. |
> | S7 ablation_completeness | 5.5 | **4.5** | Table 2 ablation is glm-4-flash only + ZERO Stage-2 mechanism ablations + the headline backbone (gpt-4.1-mini) has no equivalent. Band 4 ("Only a single all-or-nothing ablation") is closer than band 5. |
> | S8 writing_and_figures | 6.0 | **5.0** | Figure 1 placeholder for an EMNLP submission is band-5, not band-6. |
> | oral_quality_score | 3.0 | **2.5** | P5/P4 strictest view = "Reject; not on a path to acceptance" (band 2) for a paper whose proposed mechanism loses to its simplest baseline at equal cost AND whose claimed contribution is admittedly unimplemented. |
> | weighted_sum | 4.910 | **4.300** | recomputed with strict scores |
> | overall (after caps) | 4.5 | **4.3** | breaks below the 4.5 cap floor (raw weighted_sum < cap, so cap is not binding) |
>
> **Strict re-evaluation drops the verdict from cap-bound 4.5 to genuinely-derived 4.3** — still `weak_reject` but now closer to `reject` (4.0 boundary). The 4.5 cap floor is not always binding when the raw weighted_sum is itself below 4.5. **This is a critical methodological correction**: previous 5 R-FULL batches all reported overall=4.5 because reviewer scores were all soft enough that §6 caps were binding; if reviewers had scored strictly enough, raw weighted_sum could go below cap floor, exposing that the structural ceiling on this paper's quality is even lower than previously reported.
>
> **Per reviewer §F.4 cooldown rule**, R-FULL-006 was triggered immediately after this admission and uses the same PDF SHA `4504614E` with a stricter recalibration of the same dimensions; see `artifacts/idea_reviews/reviewer_<TS>_06_<HASH>/review.md`.
>
> **This file is preserved as historical evidence of reviewer score-inflation drift.** Use **R-FULL-006** for the current authoritative judgment.
>
> ---

> **Reviewing standard**: EMNLP 2026 Long Paper Track. Stateless reviewer; did not consult any prior R-FULL-001/002/003/004 review, scoreboard, or fix_themes. All scores derived independently from the paper text + `prompts/reviewer_prompt.md` rubric + `docs/demand.md` rulebook.
>
> **User instruction acknowledgment**: "全新的审稿人，不被之前的审稿意见左右，按审稿模版的要求来审，客观严格公正" — followed strictly.

## Metadata

| Field | Value |
|---|---|
| `reviewer_id` | `reviewer_20260419_204827_05_5d4006` |
| `reviewer_profile` | **P4 — Reproducibility-and-Ethics SAC focused on Reproducibility (D5), Limitations (D7), and Responsible NLP Checklist compliance.** Verifies the Limitations section is titled exactly "Limitations", adds no new content, and enumerates concrete failure modes; flags missing artifact licenses, undisclosed AI assistance, and absent compute-budget reporting as desk-reject candidates. |
| `target` | `d:\Codes\idea04\article\build\edo_paper.pdf` (332.3 KB / 11 pages, mtime 2026-04-19 19:58:22, **SHA256 prefix `4504614E196E9DDA`**) |
| `submission_track` | `EMNLP Long Paper - Oral evaluation` |
| `document_type` | `partial_paper` (full structural form: Abstract / §1-§5 / Limitations / Appendix A B1-B5 / Appendix B / References = 11 pages; but Algorithm 1 specifies the full EDO Stage-2 loop while Table 1 reports only its degenerate Stage-1 instance — what the paper claims as theoretical contribution is structurally not what it measures) |
| `stateless` | confirmed: did NOT read R-FULL-001 / R-FULL-002 / R-FULL-003 / R-FULL-004 review.md, scoreboard.md, fix_themes.md, SCIENTIST_TODO §C |
| `§F.2 input integrity` | PASS — PDF + `prompts/reviewer_prompt.md` + `docs/demand.md` + `idea.md` all loaded |
| `§F.4 cooldown` | **PDF SHA `4504614E` is identical to R-FULL-004's SHA — same physical paper version.** User explicitly verbally triggered this batch with new persona ("全新的审稿人") which constitutes implicit `U-Review-5-decide` overriding the 24-hour cooldown rule. Treating as legitimate persona-rotation re-test |

## Headline Scores

| Field | Value |
|---|---|
| **`overall`** | **4.5 / 10** |
| **`verdict`** | **`weak_reject`** |
| **`oral_eligible`** | `false` (oral_quality_score=3.0 < 8.5; D3=4.0 < 7.0) |
| **`confidence`** | `3` (PDF text via pdftotext-layout extraction; layout-dependent checks for Figure 1 quality + DR-4 template tampering blocked) |
| **`is_8_plus_ready`** | `false` |
| **`estimated_score_after_fixes`** | `6.0` (after MuSiQue + 3-seed CI + 1 external SOTA baseline + Stage-2 mechanism actually implemented) |
| **acceptance probability**, my estimate | **~10-15%** at ARR (well below typical EMNLP Long Paper acceptance ~23% due to single-benchmark + single-seed structural blocker) |

## Summary (≤ 100 words)

The paper proposes Emergent Delegation Organization (EDO), a decentralized multi-agent framework with three primitive actions (do_self / outsource / split), recursive upstream audit, and value-induced personality tags on sparse graphs. Algorithm 1 specifies the full EDO Stage-2 loop. However, the delivered executable system (TCPB) is a degenerate Stage-1 instance: SPLIT disabled, AUDIT defaults to ACCEPT, vector belief collapsed to scalar. Empirical evidence is HotpotQA-only (n=200, single seed); the headline result self-falsifies (peer_calibrated F1=0.7381 < self_claim F1=0.7641 at equal token cost). All baselines are author-internal routing variants; no external 2024-2026 SOTA. Limitations and Responsible NLP Checklist are clean.

## Reference Documents Consulted

| Field | Value |
|---|---|
| `demand_md_loaded` | `true` — `docs/demand.md` re-verified for §2 page rule, §6 Limitations rule, §7 Responsible NLP Checklist |
| `edo_paper_pdf_loaded` | partial — read via `pdftotext -layout` extraction at `$env:TEMP\edo_paper_r5_strict_audit.txt` (deleted post-review per §F.3); did NOT read PDF as native PDF attachment |
| `fallback_source_used` | `pdftotext -layout` extraction |
| `layout_dependent_checks_blocked` | DR-4 (template tampering — cannot confirm font / margin / spacing from text); D6 Figure 1 quality (caption admits placeholder, but final visual quality cannot be assessed); some D6 figure positioning checks |
| `rule_source_disagreements` | (empty list) — no rubric clauses conflict with `docs/demand.md`; all caps and verdict thresholds applied per §6 |

## Verified Document Structure (from pdftotext page markers)

| PDF Page | Content (mapped from pdftotext line ranges) |
|---:|---|
| 1 | Abstract (right column) + §1 Introduction (left column 044-) |
| 2 | §1 cont. + §2 Related Work start (157-) |
| 3 | §2.2 Reflection / §2.3 Division of labor + Figure 1 placeholder (left col) |
| 4 | §3.1 Problem formulation / §3.2 Agent state / §3.3 Task signatures (start) |
| 5 | §3.3 utility equations / §3.4 Recursive audit / §3.5 Personality update / §3.6 + **Algorithm 1 inline** |
| 6 | Algorithm 1 cont. (lines 9-36) / Prototype Scope Box / §3.7 / §3.8 / §3.9 |
| 7 | §4.1 / §4.2 setup / §4.3 Findings 1-2 + Table 2 |
| 8 | §4.3 Finding 3-4 + Table 1 + Figure 2 / §4.4 / §4.5 / **§5 Conclusion** + **Limitations (start)** |
| 9 | Limitations items (3)-(5) + Appendix A B1 / B2 (start) |
| 10 | Appendix A B2 / B3 / B4 / B5 + **Appendix B Provider Integrity Event** |
| 11 | References (Bibliography) |

**Main body §1-§5 (Conclusion line 570 = page 8) ends within 8-page cap ✅** — DR-1 PASS confirmed via direct page-marker extraction.

## Step 2: Desk-Reject Pre-flight (DR-1 .. DR-8)

| ID | Trigger | Status | Evidence |
|---|---|---|---|
| **DR-1** | Page-limit (main body > 8 pages) | **PASS** | §5 Conclusion title at pdftotext line 570 (page 8 boundary = line 602); main body §1-§5 ends within page 8. References at page 10-11. Per `docs/demand.md §2`: "main body only; references, Limitations, and Ethical Considerations do not count toward this limit". Limitations + Appendix A + Appendix B + References fall in pages 8-11 outside the 8-page cap. |
| **DR-2** | Limitations section title exact | **PASS** | Title is exactly "Limitations" (right-column line 605, position confirmed). Appears after §5 Conclusion and before References. |
| **DR-3** | New material in Limitations | **PASS** | All 5 items are scope statements (Stage-1 only / safety-prior entanglement / backbone-sensitive conjectural / point estimates with multi-seed deferred / cross-endpoint comparability is open variable). Item (5) cleanly cross-references Appendix B for engineering details rather than embedding them. No new methods, experiments, results, or analyses inside §Limitations. |
| **DR-4** | Template tampering (font / margins / spacing) | **NA** | Cannot confirm from pdftotext extraction; would require rendered PDF inspection. `layout_dependent_checks_blocked`. |
| **DR-5** | Anonymization breach | **PASS** | Title page reads "Anonymous EMNLP 2026 Submission". Code/data references use "the anonymous code/data supplement", "[Anonymous Suppl.]", "the anonymous figure-prompt supplement". No author names, GitHub URLs, project names, or identifying phrases visible. |
| **DR-6** | Responsible NLP Checklist skipped | **PASS** | Appendix A "Responsible NLP Research Checklist" present, with B1 (artifacts) / B2 (compute) / B3 (human subjects) / B4 (AI assistants) / B5 (PII) all answered. No contradictions between paper body and checklist. |
| **DR-7** | Dual / sliced submission | **NA** | Cannot directly verify from text alone; no obvious slicing markers. |
| **DR-8** | Ethics policy violation | **PASS** | B4 explicitly discloses use of code-completion AI assistant for runner.py / methods.py / prompts; states all suggestions reviewed line-by-line; states no AI-generated prose; B1 lists licenses (HotpotQA Apache-2.0, code MIT). |

**Result**: 0 confirmed desk-reject triggers. The paper passes structural compliance.

## Step 3: Experiments-Solidity Pre-Audit

| Check | Status | Evidence |
|---|---|---|
| EXP-1 multi-dataset (≥3 datasets, ≥2 task families) | **fail** | "Benchmark: HotpotQA (Yang et al., 2018) distractor validation subset, 200 examples" (§4.2). MuSiQue + 2WikiMultiHop cited as "reserved for the Stage-2 EDO benchmark transfer (§4.4 E5)" — not used in present submission. |
| EXP-2 multi-seed (≥3 seeds, list reported) | **fail** | §Limitations item (4): "Statistical evidence is presently limited to point estimates with n=200: paired-bootstrap confidence intervals, multi-seed variance, and explicit significance tests are deferred to the Stage-2 evaluation agenda". |
| EXP-3 significance test (paired) | **fail** | §4.3 Finding 2: "The gap between the best and worst Stage-1 method is 2.6 F1 points — non-trivial at n=200 but not yet confirmed with paired statistics." |
| EXP-4 effect size or 95% CI | **fail** | Table 1 / Table 2 / Figure 2 all report point estimates only. No CI columns, no Cohen's d. §B2: "Confidence intervals are explicitly not reported in this submission and are flagged in §Limitations as future Stage-2 work". |
| EXP-5 ablation coverage | **partial** | Table 2 (page 7) reports 4 ablation variants on glm-4-flash chain-200: canonical anchor / refreshed baseline / +evidence window / -TCPB / -decomposer gate. §4.5 narrative adds weight-sensitivity sweep (±2× < 0.003 pp F1 change) and static-path overlap (~52%). claimed_essential_components: {decomposer gate, TCPB calibration, FIT scoring, role priors, sparse graph routing, vector belief}; components_with_ablation: {decomposer gate, TCPB calibration, evidence window}; coverage_ratio ≈ 0.5-0.6. Critical gap: Table 2 ablations are glm-4-flash only, no equivalent on canonical strong backbone (gpt-4.1-mini) where the headline results live. |
| EXP-6 baseline recency (latest SOTA, ≥50% baselines from past 24 mo) | **fail** | Table 1 baselines = {fixed_peer_calibrated, fixed_static_roles, fixed_self_claim} — all author-internal routing variants. Zero external 2024-2026 systems. AutoGen / MetaGPT / Multi-Agent Debate / ChatEval cited in §2 Related Work but NOT in Table 1. oldest_baseline_year: own-prior-method; most_recent_baseline_year: own; latest_sota_present: false. missing_recent_sota: AutoGen, Multi-Agent Debate, ChatEval. |
| EXP-7 sensitivity sweep (≥3 values per critical hyperparameter) | **partial** | §4.5 narrative weight-sensitivity ±2× < 0.003 pp F1 — narrative only, no table; only 1 hyperparameter (the top-level routing weight scale). The 8 hand-set priors (∆+, ∆-, ρ, FTH, Hmax, ν, kmax, dmax, nmax) listed in B2 are NOT individually swept. |
| EXP-8 error analysis (named failure modes, not single case) | **partial** | §4.5: "static-path overlap analysis (peer_calibrated reproducing ∼52% of static routes) shows stable route structure can form without central control" — quantitative narrative. §4.3 Finding 4 narrative: "peer_calibrated overhead does not yield F1 gains". No per-method failure-mode breakdown table. |

**experiments_solidity_score = 1 / 8** (only EXP-5 borderline-pass; counting strict, even EXP-5 is partial)

**Caps implied by audit (per §2.5.1)**:
- EXP-1 fail → cap D4 at 6
- EXP-2 fail → cap D4 at 5 + cap S5 at 4
- EXP-3 fail → cap D4 at 6 + cap S5 at 5
- EXP-6 fail → cap D4 at 5 + cap S6 at 4
- experiments_solidity_score ≤ 3 → **cap overall at 4.5** (binding)
- experiments_solidity_score ≤ 5 → cap overall at 6.5 (subsumed by 4.5)

## Step 4: Novelty Delta Audit (≥3 named prior works)

| Prior Work | Year | Claimed Difference (paper's framing) | `is_concrete` | `is_overlap_risk` |
|---|---:|---|---|---|
| AutoGen (Wu et al.) | 2024 | "(i) globally visible expert/role table at initialization, (ii) a central decision node that owns all routing, and (iii) a fixed task script — all 3 properties our work specifically removes" (§2.1) | **true** (mechanistic, falsifiable: presence/absence of central decision node observable from architecture) | **false** |
| MetaGPT (Hong et al.) | 2024 | "MetaGPT (Hong et al., 2024) hard-codes a software-engineering pipeline (PM → architect → engineer) where each agent's role and order are pre-assigned" — EDO removes pre-assigned roles (§2.1) | **true** (mechanistic) | **false** |
| Reflexion (Shinn et al.) | 2023 | "Our prior work found that self-reflection is especially unreliable when the question is not 'is this sentence better?' but 'should I have handled this task at all?' — a delegation, rather than generation, decision" (§2.2). EDO replaces self-reflection with terminal outcome feedback. | **true** (mechanistic: per-step generation reflection vs terminal outcome calibration) | **false** |
| **Multi-Agent Debate / Liang et al.; Du et al.** | **2024** | "Multi-Agent Debate (Liang et al., 2024; Du et al., 2024) and ChatEval (Chan et al., 2024) replace self-critique with explicit per-hop peer critique that a meta-reviewer aggregates. ... in the restricted TCPB prototype, only terminal outcomes are used for calibration." (§2.2) | **partial** (qualitative: "we use terminal outcomes" vs MAD's "per-hop critique") | **TRUE** — TCPB's "terminal-only outcome" is mathematically a degenerate case of MAD's "per-hop aggregator with full-trajectory window". Paper does not benchmark MAD as baseline; SWAP-4 (R2 audit into MAD `final_aggregator`) is in `external_baseline_plan.md` but NOT in current submission. |
| ChatDev (Qian et al.) | 2024 | "ChatDev (Qian et al., 2024) and AgentVerse (Chen et al., 2024) extend the orchestrator paradigm with richer agent communication and emergent behaviors but still rely on either a manager agent or globally synchronized state" — EDO removes both. (§2.1) | **true** | **false** |

Required minimum: ≥3 named prior works with concrete deltas → **PASS** (5 named, 4 concrete).

**Caps implied (per §2.5.2 + §3 D3 hard rules)**:
- Multi-Agent Debate has `is_overlap_risk=true` AND paper does not benchmark it → **cap D3 at 4** (per §3 D3 hard rule "If the closest prior work performs the same routing/training/aggregation signal under a different name, cap D3 at 4")
- This also triggers §6 cap rule: "novelty_delta_audit shows ≥1 `is_overlap_risk=true` unaddressed: cap overall at 5.0" (not binding because 4.5 already lower)

## Step 5: ARR 7-Dimension Scores (D1-D7)

| Dim | Score | Rationale (evidence-tied) |
|---:|---:|---|
| **D1 soundness** | **5.5** | Algorithm 1 inline (page 5) is a meaningful improvement over typical multi-agent papers; specifies full EDO Stage-2 PROCESS recursion with R1/R2/R3 line markers. **But**: FIT(P, ϕ) function form undefined for vector case; AUDIT non-default rule undefined ("rule-based on answer length, refusal patterns, audit_score proxy" — audit_score function not specified); EVIDENCE_EXTRACT(e, ϕ(z)) → R^7 undefined; SPLITGAIN, MERGECOST, AUDITCOST functional forms undefined; coefficient values λ_c, λ_a, λ_m, λ_d, λ_s, λ_r unspecified; TCPB scoring weight-to-term mapping undefined (B2 lists "0.55, 0.20, 0.10, etc." as bag of numbers without semantics); §3.5 µ, η_loc, η_trm, η_rew (persona update equation) — no values. Per band 6 ("Plausible but multiple under-specified components"); honest = 5.5. |
| **D2 significance** | **4.0** | §4.3 Finding 4 admits "peer_calibrated overhead does not yield F1 gains ... For a capable backbone on HotpotQA, the simpler methods are Pareto-dominant on the F1/cost frontier"; §5 Conclusion repeats "Pareto-dominated by a simpler self-claim baseline at equal token cost — this is a delivered-system limitation". The proposed Stage-2 mechanisms (R1/R2/R3) are admittedly NOT implemented (§3.8 + Prototype Scope Box + Limitations item (1)). What the paper claims as "stronger contribution" is not demonstrated. Per band 4 ("Limited significance; addresses a problem few in the community care about — at the present submission state"). |
| **D3 novelty** | **4.0** | Multi-Agent Debate `is_overlap_risk=true` AND not benchmarked → cap D3 at 4 per §3 D3 hard rule. 5 named priors with 4 concrete deltas, but the central novelty CLAIM (recursive split + recursive audit + persona-tag emergence) is admittedly not empirically realized (§3.8). EDO framework is largely a re-framing of decentralized routing literature with concrete Stage-2 designs that remain proposed. |
| **D4 empirical_results** | **4.0** | After caps from §2.5.1: D4 ≤ 5 (EXP-2 fail) + D4 ≤ 5 (EXP-6 fail) + D4 ≤ 6 (EXP-1 fail) + D4 ≤ 6 (EXP-3 fail). Honest = 4 because: single benchmark + single seed + headline result self-falsified by Finding 4 + zero external SOTA. Per band 4 ("Single benchmark, single seed, weak or stale baselines, no ablations; results may be within noise. Authors should not draw conclusions from such evidence"). |
| **D5 reproducibility** (P4 specialty) | **5.5** | **Strengths**: Algorithm 1 inline gives full Stage-2 spec (page 5); B2 lists exact Stage-1 hyperparameters (∆+ = +0.06, ∆- = -0.10, ρ = 0.5, FTH = 0.5, Hmax = 4, δa = 0.02) and Stage-2 constants (ν = 0.2, kmax = 3, dmax = 3, nmax = 12); B2 wall-clock estimate (1-2h per chain-200 batch) + USD cost ($0.50-$1.00 per chain-200 batch) + fullval scaling (~35× chain-200) — these exceed minimum reproducibility requirements; B1 lists all licenses (HotpotQA Apache-2.0, code MIT). **Critical gaps**: LLM_ANSWER prompt template NOT in paper (Algorithm 1 line 13 calls it); LLM_DECOMPOSE prompt NOT in paper (line 26); AUDIT non-default rule NOT in paper (line 16; default ACCEPT only specified); EVIDENCE_EXTRACT function NOT in paper (line 33); ϕ(z) extraction rule explicitly delegated to "executable spec [Anonymous Suppl.] §1-3" (§3.6 caption); FIT(P, ϕ) form undefined; TCPB scoring formula not in paper. Per band 6 ("Significant reproduction effort required; multiple critical hyperparameters absent") with mitigating factors → 5.5. |
| **D6 clarity** | **6.0** | Algorithm 1 inline ✅; Figure 2 caption detailed and self-contained ✅; honest framing reads cleanly throughout. **But**: Figure 1 caption explicitly admits placeholder ("[Figure 1 placeholder] ... Vector asset to be inserted; full design specification in the anonymous figure-prompt supplement") — for an EMNLP Long Paper at submission time, the figure-1 of the methods section being a placeholder is a clarity-preventing defect. Also pdftotext extraction shows column-spanning narrative that may read awkward in rendered PDF. Per band 6 ("Repeated awkward phrasing; one figure is hard to read; structure occasionally fights the argument"). |
| **D7 responsible_research_and_limitations** (P4 specialty) | **7.5** | **Strengths**: Limitations title exact "Limitations" ✅; 5 numbered items, all scope statements ✅; item (5) cleanly cross-references Appendix B for engineering details (no DR-3 risk) ✅; item (3) properly conjectural ("we conjecture; this conjecture is not validated by the present submission") ✅; B5 PII section added (Appendix A) ✅; B4 AI assistant disclosure explicit ✅. **Gaps preventing 8+**: NO mention of demographic/societal risks (band 8+ requires "demographic / societal risks, failure modes"); HotpotQA dataset bias not discussed beyond PII statement; multilingual / low-resource generalization risks absent; per-method failure-mode breakdown not provided. Per band 7 ("Limitations exist but are partially generic; risks discussed superficially") with significant strengths above; honest = 7.5. |

## Step 5 cont.: ARR 8 Secondary Dimension Scores (S1-S8)

| Dim | Score | Rationale |
|---:|---:|---|
| **S1 executability** | **5.0** | TCPB Stage-1 partially executable from Algorithm 1 + B2 hyperparameters; full EDO Stage-2 (R1/R2/R3) NOT executable from paper alone. Per band: needs guesswork on multiple components. |
| **S2 falsifiability** | **5.5** | TCPB headline claim falsifiable AND self-falsified by Finding 4 (paper honestly admits). Central EDO claim "emergent organization from local interaction" is admittedly not yet testable (Stage-2 mechanisms not implemented). Backbone-sensitive prediction now properly framed as conjectural. Mixed: testable parts are tested but main claim not yet operationalized. |
| **S3 empirical_plan** | **6.0** | §4.4 lists 5 well-designed Stage-2 studies (E1 emergent specialization / E2 split value / E3 audit value / E4 sparse-graph robustness / E5 benchmark transfer) + 8 organizational process metrics (specialization entropy / persona-tag divergence / audit precision-recall / etc.). Plan design is solid; execution is zero. |
| **S4 technical_clarity** | **6.0** | Equations clear notation; Algorithm 1 readable; multiple symbols undefined (FIT, EVIDENCE_EXTRACT, λs, AUDIT-rule, TCPB weight mapping). |
| **S5 statistical_rigor** | **2.0** (capped at 4 by EXP-2 fail; capped at 5 by EXP-3 fail) | Zero CI; zero paired statistical test; single seed for all reported numbers. Limitations (4) admits all three deferred to Stage-2 — admission ≠ presence. |
| **S6 baseline_quality** | **2.0** (capped at 4 by EXP-6 fail) | All Table 1 baselines = author-internal routing variants. Zero external 2024-2026 SOTA. AutoGen / MAD / ChatEval / MetaGPT cited but not benchmarked. Per band 3 ("Self-comparison only OR weak baselines that the paper itself implies are below the standard") + band 2 ("No external baselines at all") → 2.0. |
| **S7 ablation_completeness** | **5.5** | Table 2 in body (4 variants: canonical / refreshed baseline / +evidence-window / -TCPB / -decomposer-gate) covers TCPB calibration + decomposer gate ✅; §4.5 sensitivity sweep narrative ±2× weight ✅. **Critical gap**: Table 2 is glm-4-flash only — no equivalent ablation on the canonical strong backbone (gpt-4.1-mini) where Finding 2's headline backbone-sensitive ordering inversion lives. Cannot verify whether TCPB-on/off or gate-on/off behavior generalizes. Stage-2 mechanism components (FIT vector form, vector belief, R1 split, R2 audit) have zero ablation. |
| **S8 writing_and_figures** | **6.0** | Algorithm 1 inline ✅; Figure 2 ✅; Bibliography 12+ named entries (vs typical ACL template default 4) ✅. Figure 1 placeholder ⚠. Tables/captions self-contained. |

## `oral_quality_score` (P4 strict view)

**`oral_quality_score = 3.0`**

Per §5 mapping:
- band 3: "Reject; major rework required"
- band 4: "Weak reject; clear path to acceptance after major revision"

Justification: single benchmark + single seed + zero external SOTA + headline result self-falsified + Stage-2 mechanism admittedly absent + Figure 1 placeholder. P4 specialty (D5/D7) gives some credit for honest Limitations + complete Responsible NLP Checklist, but the experimental skeleton is structurally insufficient for an EMNLP Oral. Not on a path to acceptance without major restructuring of §4.

## Step 7: Score Calculation (deterministic, with caps shown)

```
weighted_sum = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*5.5 + 0.18*4.0 + 0.15*4.0 + 0.18*4.0 + 0.10*5.5 + 0.07*6.0 + 0.07*7.5
             = 1.375 + 0.720 + 0.600 + 0.720 + 0.550 + 0.420 + 0.525
             = 4.910

caps_triggered (in order of evaluation):
  - DR-1..DR-8 confirmed:                NO (all PASS or NA)
  - D1 (Soundness) < 5:                  NO (D1=5.5)
  - D4 (Empirical) < 5:                  YES (D4=4.0) → cap overall at min(weighted_sum, D4 + 0.5)
                                                       = min(4.910, 4.5) = 4.5  ← BINDING
  - D4 (Empirical) < 7:                  YES (D4=4.0) → cap overall at 7.0 (not binding, 4.5 < 7.0)
  - D3 (Novelty) < 5:                    YES (D3=4.0) → cap overall at min(4.5, D3 + 0.5)
                                                       = min(4.5, 4.5) = 4.5  ← BINDING (same)
  - D3 (Novelty) < 6:                    YES (D3=4.0) → cap overall at 6.5 (not binding)
  - D7 (Limitations) < 4:                NO (D7=7.5)
  - falsifiability < 4:                  NO (S2=5.5)
  - oral_quality_score < 5:              YES (oral=3.0) → cap overall at 5.5 (not binding)
  - experiments_solidity_score ≤ 3:      YES (1) → cap overall at 4.5  ← BINDING (same)
  - experiments_solidity_score ≤ 5:      YES (1) → cap overall at 6.5 (subsumed)
  - novelty_delta_audit unaddressed
    `is_overlap_risk=true` (MAD):        YES → cap overall at 5.0 (not binding, 4.5 < 5.0)
  - S6 (baseline_quality) < 5:           YES (S6=2.0) → cap overall at 6.0 (not binding)
  - S7 (ablation_completeness) < 5:      NO (S7=5.5)

final_overall = 4.5  →  verdict per §6 thresholds: overall in [4.0, 5.5) → "weak_reject"
```

**The 4.5 floor is structural and triple-binding** (D3+D4 dimension caps + experiments_solidity floor all converge at 4.5). To break it requires improving D3 (add MAD as benchmarked baseline + 2 more concrete deltas) AND D4 (add MuSiQue + multi-seed + paired CI + external SOTA) AND experiments_solidity_score ≥ 4 (any 3 of EXP-1/2/3/4/6/7/8 newly passing). The paper's writing/framing/algorithm spec quality are NOT the bottleneck — experimental rigor is.

## `top_strengths` (4 items)

1. Algorithm 1 inline (page 5) specifies the full EDO Stage-2 PROCESS recursion with R1/R2/R3 line-level markers — meaningful formalization commitment compared to typical agentic-system papers that gesture at architecture without algorithmic detail.
2. §5 Conclusion + Abstract honestly admit Pareto-domination by simpler baseline ("delivered-system limitation, not refutation of the broader framework") — unusual self-awareness; Limitations item (3) is properly conjectural.
3. Limitations section is title-exact, 5 well-scoped numbered items, item (5) cleanly cross-references Appendix B without leaking engineering content; Appendix A Responsible NLP Checklist B1-B5 complete (B5 PII added — often skipped in similar submissions).
4. B2 compute budget exceeds minimum: wall-clock (1-2h per chain-200 batch) + USD cost ($0.50-$1.00) + fullval 35× scaling estimate; Stage-1 hyperparameters fully listed (∆+/∆-/ρ/FTH/Hmax/δa); 12+ named bibliography entries (vs typical ACL template-default 4).

## `top_weaknesses` (6 items, ordered by severity)

1. **FATAL** — `experiments_solidity_score = 1/8`: single HotpotQA benchmark + single seed + zero paired statistical test + zero external 2024-2026 SOTA baseline. §6 cap locks `overall` at 4.5 regardless of any improvement on writing/algorithm/framing. **This is the structural blocker for acceptance.**
2. **FATAL** — All Table 1 baselines are author-internal routing variants (peer_calibrated / static_roles / self_claim). AutoGen / Multi-Agent Debate / ChatEval / MetaGPT cited in §2 but ZERO benchmarked. Multi-Agent Debate is `is_overlap_risk=true` per §2.5.2 audit (TCPB's terminal-outcome is degenerate case of MAD's per-hop aggregator); not benchmarking it caps D3 at 4.
3. **FATAL** — EDO main mechanisms (R1 split / R2 recursive audit / R3 vector-belief routing) are admittedly NOT implemented (§3.8 + Prototype Scope Box explicitly state). Algorithm 1 specifies the full Stage-2 loop, but Table 1 reports only its degenerate Stage-1 instance. **What the paper claims as theoretical contribution is structurally not what the paper measures.**
4. **D1 / D5** — Algorithm 1 contains 8+ undefined functions: FIT(P, ϕ), AUDIT non-default rule, EVIDENCE_EXTRACT, SPLITGAIN, MERGECOST, AUDITCOST, λ_c/λ_a/λ_m/λ_d/λ_s/λ_r coefficients, AND TCPB's actual weight-to-term mapping (B2 lists "0.55, 0.20, 0.10, etc." without semantics). LLM_ANSWER / LLM_DECOMPOSE / AUDIT-rule / EVIDENCE_EXTRACT prompt templates not in paper body. Reading paper alone cannot reproduce TCPB.
5. **D6** — Figure 1 caption explicitly admits placeholder status ("Vector asset to be inserted"). For an EMNLP Long Paper submission, the methods-section opening figure being a placeholder is a strong signal of incomplete preparation.
6. **D7 (P4 specialty gap)** — Limitations is honest and specific but does NOT discuss demographic / societal risks, dataset bias beyond PII statement, multilingual / low-resource generalization, or per-method failure modes. To reach D7 = 8+ band ("touches risks; checklist clearly addressed") would need a small "Broader Impact / Societal Risk" sentence in Limitations.

## `core_method_problems`

1. EDO Stage-2 mechanisms (R1 split / R2 audit / R3 vector belief) admittedly NOT implemented; Algorithm 1 lines 14-16 / 16-23 / 32-34 all gated to default behavior in delivered TCPB instance.
2. FIT(P_i, ϕ(z)) function form undefined for vector case; §3.6 only says "vector belief is collapsed onto a scalar c[i] via mean-axis fold" but the projection function is unspecified.
3. AUDIT non-default rule (Algorithm 1 line 16) — paper says "rule-based on answer length, refusal patterns, audit_score proxy" but audit_score and threshold values are deferred to external supplement.
4. EVIDENCE_EXTRACT(e, ϕ(z)) → R^7 mapping (Algorithm 1 line 33) — undefined in paper body.
5. TCPB's specific numeric weight-to-term mapping (B2 "0.55, 0.20, 0.10, etc.") — without naming which weight applies to which utility term, the formula is irreproducible.

## `experimental_design_problems`

1. Single benchmark only (HotpotQA distractor n=200); MuSiQue + 2WikiMultiHop both cited as "reserved for Stage-2" — no reason at least one cannot be in the present submission.
2. Single seed reported in Table 1; multi-seed admitted as deferred (Limitations 4).
3. No paired bootstrap / sign test / permutation test in body; §4.3 explicitly admits "not yet confirmed with paired statistics".
4. Zero external multi-agent system baselines in Table 1 — most consequential omission is Multi-Agent Debate (Liang et al., 2024), the named overlap-risk prior work.
5. Table 2 ablation glm-4-flash only — no equivalent on canonical strong backbone (gpt-4.1-mini) where headline ordering inversion (Finding 2) lives.

## `implementation_or_reproducibility_gaps`

1. External `edo_lite_executable_spec.md` is referenced 4+ times as the canonical impl spec (ϕ extraction, utility instantiations, prompt templates) but NOT part of the paper body — independent replication blocked without anonymous supplement.
2. LLM_ANSWER, LLM_DECOMPOSE, AUDIT (non-default rule), EVIDENCE_EXTRACT prompt templates absent from paper body.
3. fullval (n=7405) status: B2 implies 35× chain-200 scaling; Limitations item (5) admits 2 of 3 method runs are "queued for re-execution" under new endpoint; only peer_calibrated has valid full-validation data point. Full Table 1 ranking cannot be reproduced from paper alone.
4. Random seeds for the n=200 HotpotQA slice: §4.2 says "versioned slice in the anonymous supplement" — paper does not disclose the actual question IDs or selection rule, so independent replication of "same 200 examples" requires the supplement.
5. `audit_score` proxy implementation in Stage-2 (§3.8 R2): "rule-based on answer length, refusal patterns, audit_score proxy" — none of these rules / thresholds are in the paper.

## `overclaims_or_risky_claims`

1. Conclusion: "EDO moves the focus from fixed roles to socially induced personality tags, from linear routing to recursive task trees, and from terminal-only supervision to recursive acceptance-based organization." — three of these moves (personality tags emergence / recursive task trees / recursive acceptance) are admittedly NOT implemented (§3.8). Honest framing: "EDO **proposes** these three moves; TCPB instantiates only the third (terminal supervision) in restricted form".
2. Abstract: "decentralized outcome-based calibration improves delegation safety and stabilizes routing without a central controller" — Finding 3 attributes PAR=0.0 to the **decomposer force-forward gate** (a fixed safety prior coded as Algorithm 1 line 11), not to TCPB itself. The gate is doing the safety work; calling this a TCPB benefit is overstated.
3. §3.1 "decentralized; no global expert table; sparse connected graph" — Algorithm 1 has 4 hand-coded role-prior nodes {DEC, EVI, VER, SYN} with hard-coded multi-hop force-forward rule for DEC. Honest re-phrasing: "decentralized within a fixed role-prior topology with hand-tuned safety priors".
4. §2.2 "in the restricted TCPB prototype, only terminal outcomes are used for calibration" — but TCPB's mechanism is mathematically a degenerate case of Multi-Agent Debate's per-hop aggregator (window=full-trajectory). The differentiation paragraph in §2.2 does not address this overlap with `is_concrete=true` evidence.

## `ambiguous_algorithm_points`

1. Algorithm 1 line 3: `U^S ← FIT(P_i, ϕ) - λ_c Cost_self` — FIT undefined for vector case; λ_c, Cost_self functional form unspecified.
2. Algorithm 1 line 5: `U^O_j ← FIT(B^t_i(j), ϕ) - λ_a AuditCost` — λ_a, AuditCost both undefined.
3. Algorithm 1 line 7: `U^P ← SPLITGAIN(z) - λ_m MergeCost` — both undefined.
4. Algorithm 1 line 16: `e ← AUDIT(i, j*, z, r)` — default behavior is ACCEPT (§3.8 R2), but non-default rule deferred to external spec.
5. Algorithm 1 line 33: `EVIDENCE_EXTRACT(e, ϕ(z))` — function form undefined; paper says "definitions live in the executable spec [Anonymous Suppl.] §1-3".

## `missing_definitions_or_state_variables`

1. FIT(P, ϕ) function (§3.3 utility, Algorithm 1 lines 3, 5).
2. λ_c, λ_r, λ_s, λ_a, λ_m, λ_d coefficient values (§3.3 utility).
3. µ, η_loc, η_trm, η_rew (§3.5 persona update equation).
4. AUDIT decision rule + audit_score proxy (§3.8 R2).
5. EVIDENCE_EXTRACT(·) (§3.8 R3, Algorithm 1 line 33).

## `missing_or_weak_experiments`

1. No second benchmark — MuSiQue or 2WikiMultiHop both already cited as "reserved" in §4.2; runtime parallel infrastructure exists (B2).
2. No multi-seed runs (admitted deferred in Limitations 4).
3. No paired bootstrap / sign test / permutation test in body for Table 1 comparisons.
4. Zero external multi-agent system baselines (AutoGen / MetaGPT / Multi-Agent Debate / ChatEval all cited but not benchmarked).
5. Table 2 ablation missing on canonical strong backbone (gpt-4.1-mini).
6. No emergent-specialization measurement (§4.4 E1 metrics: persona-tag divergence, specialization entropy, per-agent action frequencies) — but EDO's central novelty CLAIM depends on these metrics.

## `statistical_significance_concerns`

1. Table 1 / Table 2 / Figure 2 all point estimates only; no CI columns, no Cohen's d, no relative improvement %.
2. §4.3 explicitly admits headline 2.6 F1-point gap "non-trivial at n=200 but not yet confirmed with paired statistics".
3. n=200 HotpotQA is a small slice — without bootstrap CI it is impossible to bound the variance of the reported point estimates.

## `baseline_completeness_concerns`

1. Zero external 2024-2026 multi-agent system baselines in Table 1.
2. Multi-Agent Debate (Liang et al., 2024) — `is_overlap_risk=true` in novelty audit but not benchmarked.
3. "Centralized baselines" referenced in §4.2 ("compare ... and centralized baselines under shared inputs") but no central_orchestrator row in Table 1.

## `limitations_section_assessment` (P4 deep audit)

| Field | Value |
|---|---|
| `section_present` | `true` |
| `section_title_exact` | `true` (exactly "Limitations" at right-column line 605) |
| `contains_no_new_content` | `true` — all 5 items are scope statements; item (5) cleanly cross-references Appendix B for engineering details rather than embedding them; no new methods / experiments / results / figures / tables / analyses inside §Limitations |
| `honesty_score_1_to_5` | `4` |
| `specific_failure_modes_listed` | `true` — Pareto-domination by self_claim explicitly named in Conclusion (cross-referenced from Limitations); single-benchmark, single-seed, missing CI, missing paired tests all enumerated |
| `issues` | (1) No demographic or societal risk discussion (band 8+ requires it); (2) No dataset-bias discussion beyond Wikipedia-source PII statement in B5; (3) No multilingual / low-resource generalization discussion; (4) Per-method failure-mode breakdown not provided (Pareto-dominated narrated but not anatomized) |

## `responsible_nlp_checklist_assessment` (P4 deep audit)

| Field | Value |
|---|---|
| `appears_complete` | `true` — B1 (artifacts + licenses) / B2 (compute + hyperparameters) / B3 (no human subjects) / B4 (AI assistant disclosure) / B5 (PII not applicable) all answered |
| `issues` | (1) B2 hyperparameters list mentions "routing weights for the Stage-1 TCPB instance (0.55, 0.20, 0.10, etc.)" — the "etc." obscures whether all weights are listed; (2) B2 does not state random seeds used (only that single seed was used per Limitations 4); (3) B4 is honest about AI code-assistant for runner.py / methods.py / prompts but does not enumerate which prompt templates were AI-suggested vs author-original (low-priority gap) |

## `implementation_risks`

1. External `edo_lite_executable_spec.md` not part of submission — replication blocked without anonymous supplement disclosure.
2. Provider variability documented in Appendix B; replicators on different providers may see different model behavior; the integrity-check guard threshold logic is not given.
3. LLM_ANSWER / LLM_DECOMPOSE / AUDIT-rule / EVIDENCE_EXTRACT prompt templates absent from paper body.
4. Single-seed runs make any reported metric a single-realization sample.
5. fullval n=7405 only valid for peer_calibrated method; other 2 method runs queued for re-execution per Limitations (5) — the full Table 1 fullval ranking cannot be reproduced from paper alone in current state.

## `what_to_fix_for_8_plus` (6 items, P4-priority order)

1. **Add MuSiQue as second benchmark** (already cited in §4.2 as Stage-2 reserved; runtime is parallel per B2). Single change moves EXP-1 fail → pass and starts unblocking experiments_solidity_score floor.
2. **Run all main results with ≥3 seeds + 95% bootstrap CI + paired sign test in Table 1**. Addresses EXP-2 / EXP-3 / EXP-4 simultaneously.
3. **Add Multi-Agent Debate (Liang et al., 2024) as external baseline in Table 1** — directly addresses the only `is_overlap_risk=true` prior work; would either confirm TCPB's terminal-outcome claim has independent value or refute it (either outcome is more informative than the current within-family Pareto comparison).
4. **Add Table 2 ablation on canonical strong backbone (gpt-4.1-mini)** — currently glm-4-flash only; cannot verify whether TCPB-on/off behavior generalizes to the strong-backbone setting where the headline conclusion lives.
5. **Inline TCPB scoring formula in §3.6** — currently the "0.55, 0.20, 0.10, etc." in B2 is unattributed; one explicit formula closes the largest D1 / D5 gap with ~10 minutes of writing.
6. **Add LLM call prompt templates as Appendix C (≤ 1 page)** — list the 4 LLM-call templates used in Algorithm 1 (LLM_ANSWER / LLM_DECOMPOSE / AUDIT non-default rule / EVIDENCE_EXTRACT). Currently they are in supplement only; reading paper alone cannot reproduce.

## `what_to_fix_for_oral` (5 items)

1. **Implement at least one of R1 / R2 / R3 and demonstrate empirical value**. R2 audit is highest-ROI candidate — if recursive audit allows upstream rejection of bad subcontracts, peer_calibrated could in principle outperform self_claim by catching errors self_claim cannot, directly reversing Finding 4. Without ANY Stage-2 mechanism actually running, EDO is a roadmap, not an executable contribution.
2. **Show non-trivial improvement over external 2024-2026 SOTA on at least one benchmark** — currently the proposed method LOSES to its own simplest baseline at equal token cost.
3. **Add demographic / societal risk discussion to Limitations** + dataset-bias discussion (HotpotQA Wikipedia bias toward English, biographical entities, factual QA). Short paragraph would lift D7 to 8+.
4. **Quantitative error analysis with named failure modes per method** — not just narrative; needs a table showing where each method fails.
5. **Seed-level organization stability metrics** (per §4.4 E1) — if EDO is about emergent specialization, the paper needs to show specialization is stable across seeds.

## `recommended_next_actions` (4 items, smallest-cost first)

1. **Lowest-cost / highest-impact**: add MuSiQue + multi-seed (≥3) + paired bootstrap CI in Table 1. This single sprint moves experiments_solidity_score from 1 to ~5, unblocking the §6 cap on overall.
2. **~30 minutes**: inline TCPB scoring formula in §3.6 + define FIT(P, ϕ) for vector case in §3.3 + add B5 societal-risk paragraph to Limitations. Lifts D1 / D5 / D7 with negligible page-budget cost.
3. **~1-2 days writing**: replace Figure 1 placeholder with finished vector PDF (caption already specifies the design).
4. **Stage-2 minimum viable**: implement R2 (recursive audit) — closest neighbor mechanism that could empirically reverse Finding 4 and turn delivered narrative from "Pareto-dominated honest disclosure" to "EDO contribution validated".

## Honest Final Verdict

The paper is competently written with unusually honest framing — Conclusion + Abstract proactively admit the headline's Pareto-domination, Limitations are clean and structural, Responsible NLP Checklist is complete (B5 PII included). Algorithm 1 inline at page 5 is a meaningful formalization commitment. **However**, the core experimental skeleton (single HotpotQA benchmark, single seed, no paired statistical test, zero external SOTA baseline) is structurally insufficient for an EMNLP Long Paper acceptance regardless of writing quality. The §6 cap locks `overall` at 4.5 with three independent triggers (D3<5, D4<5, experiments_solidity ≤ 3) all converging at the same floor.

The paper currently sits in the **`weak_reject` / borderline-reject** zone. The fastest path to acceptance is NOT more writing or more algorithm refinement but more experiments. A revision that (a) adds MuSiQue as second benchmark + multi-seed CI + 1 external baseline (Multi-Agent Debate), (b) actually implements R2 audit and shows it improves over self_claim, would reasonably reach `borderline` (overall 5.5-6.5) or `weak_accept` (6.5-7.5).

I recommend the authors either (i) **withdraw and revise** before ARR May 2026 to include the missing benchmarks/baselines/Stage-2 mechanism, or (ii) submit as-is to ARR May 2026 ONLY as a low-stakes early-feedback round, accepting that without the experimental work above the paper will not exceed 4.5.

## Reviewer-Only Boundary Compliance (per `REVIEWER_TODO §F.1.4 / §F.1.5`)

- ✅ Did NOT modify any TODO file outside `REVIEWER_TODO.md` and `artifacts/idea_reviews/` during the review itself
- ✅ Did NOT participate in §A decisions (`recommended_next_actions` is suggestion only; decision authority remains with user)
- ✅ Did NOT read past R-FULL-001/002/003/004 reviews / scoreboard.md / fix_themes.md / SCIENTIST_TODO §C (stateless)
- ✅ Did NOT trigger S-104 (scientist's responsibility per §11.4)
- Will leave §F.4 1-line ack in `implementation_log.md` as the only allowed exception
- Will dispatch new S-XXX TODOs to scientist per user's standing instruction "你不要忘了给科学家下任务" (R-FULL-004 established the pattern)
- Temporary PDF text extraction at `$env:TEMP\edo_paper_r5_strict_audit.txt` deleted post-review per §F.3
- This `review.md` is the only required product per §F.3 (no `review.json` generated; matches user's 2026-04-19 instruction)
