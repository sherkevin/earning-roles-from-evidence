# Review of `article/build/edo_paper.pdf` (R-FULL-004)

> **Reviewing standard**: EMNLP 2026 Long Paper Track. Deliberately non-flattering — every score below justified by missing/undefined element, not by writing quality. Per user instruction "不要讨好我".

## Metadata

- **reviewer_id**: `reviewer_20260419_202222_04_232b11`
- **persona**: **P1 — Strict ARR Senior Area Chair specializing in Soundness (D1) and Reproducibility (D5).** Default to rejection unless every algorithmic object, update rule, and state variable is fully formalized; treats any unspecified hyperparameter or absent seed/significance test as evidence of incompleteness.
- **target**: `d:\Codes\idea04\article\build\edo_paper.pdf` (332.3 KB / 11 pages, mtime 2026-04-19 19:58:22, **SHA256 prefix `4504614E`**) — this is a NEW PDF version (different from R-FULL-003's `73AD9124`); scientist has materially edited the paper since R-FULL-003
- **submission_track**: EMNLP Long Paper — Oral evaluation
- **document_type**: `partial_paper` (full structural form but Stage-2 mechanism R1/R2/R3 admittedly not implemented; Algorithm 1 specifies the full EDO loop but Table 1 reports only its degenerate Stage-1 instance)
- **stateless**: did NOT read R-FULL-001 / R-FULL-002 / R-FULL-003 / scoreboard.md / fix_themes.md / SCIENTIST_TODO §C
- **§F.2 input integrity**: PASS — PDF not stale; `prompts/reviewer_prompt.md` + `docs/demand.md` + `idea.md` all present
- **§F.4 cooldown**: PASS — PDF SHA differs from all prior batches; user explicitly triggered new R-FULL

## Headline

| Field | Value |
|---|---|
| **overall** | **4.5 / 10** |
| **verdict** | **`weak_reject`** |
| **oral_eligible** | `false` |
| **confidence** | `3` (PDF text only — layout-dependent checks blocked) |
| **is_8_plus_ready** | `false` |
| **estimated_score_after_fixes** | `6.0` |
| **acceptance probability**, my estimate | **~12%** at ARR (typical EMNLP Long Paper acceptance ~23%, this submission below median due to single-benchmark + single-seed structural blocker) |

## Direct Acknowledgment of My Prior Discounting Bias

This review explicitly corrects the soft scoring of R-FULL-003 (the previous reviewer batch). In R-FULL-003 I gave credit for "honest framing" and "wall-clock USD reporting" that did not actually translate to substantive empirical or methodological content. Specifically:

| Dim | R-FULL-003 (soft) | This R-FULL-004 (strict) | Why I was wrong |
|---|---:|---:|---|
| D5 reproducibility | 8.0 | **5.5** | LLM_ANSWER / LLM_DECOMPOSE / AUDIT-rule / EVIDENCE_EXTRACT prompt templates NOT in paper body; ϕ extraction in external supplement; reading paper alone you cannot reproduce |
| S2 falsifiability | 7.0 | **5.5** | "honestly admitting self-falsified" is honesty, not falsifiability of the central EDO claim; Stage-2 mechanisms (R1/R2/R3) admittedly not tested → not currently testable |
| D7 limitations | 7.0 → **7.0** (kept) | 7.0 | This was correct in R-FULL-003 PDF (post the move of integrity event to Appendix B; in fact even better in current PDF where Limitations is fully clean) |
| D1 soundness | 6.0 | **5.5** | Algorithm 1 is inline + complete-form, but FIT, EVIDENCE_EXTRACT, λ coefficients, AUDIT-rule, SplitGain/MergeCost/AuditCost — at least 8 black-box functions undefined |
| oral_quality_score | 4.0 | **3.0** | DR caps not the only blocker — single-benchmark + single-seed + headline self-falsified + Stage-2 not implemented = "Reject; major rework required" tier per §5 mapping |

These corrections lower `weighted_sum` from 5.905 to 4.985. The cap remains at 4.5 (experiments_solidity_score=1 is the binding constraint, same as before).

## Scores

| dim | score | one-line rationale (every score evidence-tied) |
|---|---:|---|
| D1 soundness | **5.5** | Algorithm 1 inline ✅; but FIT, EVIDENCE_EXTRACT, AUDIT-rule, SplitGain, MergeCost, AuditCost, λ_c/λ_a/λ_m/λ_d/λ_s/λ_r — at least 8 black-box functions; TCPB scoring formula (0.55 * X + 0.20 * Y + …) NOT in paper body, only "routing weights for Stage-1 TCPB instance (0.55, 0.20, 0.10, etc.)" listed as an unattributed bag of numbers in B2 |
| D2 significance | **4.0** | §4.3 Finding 4 admits Pareto-dominated by self_claim; Conclusion concedes "delivered-system limitation"; framework reframing valuable but no demonstrated impact |
| D3 novelty | **4.5** | 12 named prior works ✅; Multi-Agent Debate is_overlap_risk + NOT benchmarked (TCPB's "terminal-only" is degenerate case of MAD's per-hop aggregator at full-trajectory window); Stage-2 R1/R2/R3 admittedly not implemented → cannot claim mechanism novelty |
| D4 empirical_results | **4.0** | experiments_solidity_score=1/8; capped to 5; honest score 4 because headline mechanism is self-falsified |
| D5 reproducibility | **5.5** | Algorithm 1 inline + Stage-1 hyperparameters (ρ, ∆+, ∆-, FTH, Hmax, δa) + B2 wall-clock + USD ✅; LLM_ANSWER/LLM_DECOMPOSE/AUDIT-rule/EVIDENCE_EXTRACT prompts NOT in paper; ϕ extraction in external `edo_lite_executable_spec.md`; the *actual* TCPB scoring weights mapping (which 0.55 goes where) not in paper |
| D6 clarity | **6.5** | Algorithm 1 inline (improvement vs typical layout); Figure 2 caption detailed ✅; Figure 1 self-admitted placeholder ⚠; Conclusion + Abstract honest framing reads cleanly |
| D7 responsible_research_and_limitations | **7.0** | Limitations title exact ✅; 5 well-scoped items, all honest; item (5) cleanly cross-references Appendix B without leaking engineering content into Limitations; Appendix A Responsible Checklist B1-B5 (B5 PII added) ✅ |
| S1 executability | **5.0** | TCPB partially executable from Algorithm 1 + B2; full EDO Stage-2 R1/R2/R3 NOT executable from paper alone (requires anonymous supplement) |
| S2 falsifiability | **5.5** | TCPB headline claim falsifiable AND self-falsified by Finding 4; central EDO claim "emergent organization from local interaction" admittedly not yet testable (Stage-2 mechanisms not implemented) |
| S3 empirical_plan | **6.0** | §4.4 E1-E5 5-study agenda + 8 organizational metrics specified — well-designed plan, but no execution |
| S4 technical_clarity | **6.0** | Equations clear; Algorithm 1 clear; multiple symbols undefined for full EDO |
| S5 statistical_rigor | **2.0** | Zero CI / zero paired test / zero multi-seed; Limitations (4) admits deferred — admission ≠ presence |
| S6 baseline_quality | **2.0** | All Table 1 baselines = author-internal routing variants; AutoGen / MetaGPT / Multi-Agent Debate / ChatEval all CITED in §2 but ZERO benchmarked; "centralized baselines" in §4.2 mentioned but not in Table 1 |
| S7 ablation_completeness | **5.5** | Table 2 in body ✅ (4 variants: canonical/baseline/+evidence/-TCPB/-gate); BUT Table 2 is glm-4-flash only — no equivalent on canonical strong backbone (gpt-4.1-mini); cannot verify TCPB-on/off / gate-on/off behavior generalizes |
| S8 writing_and_figures | **6.0** | Algorithm 1 inline ✅; Figure 2 ✅; Figure 1 placeholder; bibliography 16+ entries ✅ |
| **oral_quality_score** | **3.0** | "Reject; major rework required" tier per §5 — single-benchmark + single-seed + no external SOTA + self-falsified headline + Stage-2 admittedly absent. Not on a path to acceptance without major restructuring of experimental section |
| **overall (weighted_sum)** | **4.985** | before caps |
| **overall (final)** | **4.5** | after caps |

## Score Calculation

```
weighted_sum = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*5.5 + 0.18*4.0 + 0.15*4.5 + 0.18*4.0 + 0.10*5.5 + 0.07*6.5 + 0.07*7.0
             = 1.375 + 0.720 + 0.675 + 0.720 + 0.550 + 0.455 + 0.490
             = 4.985

caps_applied (in order):
  - experiments_solidity_score = 1 (≤ 3): cap overall at 4.5  ← BINDING (lowers from 4.985)
  - D4 < 5 (D4=4.0): cap overall at min(4.985, D4 + 0.5) = 4.5  ← also binding (independent confirmation)
  - D3 < 5 (D3=4.5): cap overall at min(4.5, D3 + 0.5) = 4.5  (already at floor)
  - D7 < 4: not triggered (D7=7.0)
  - falsifiability < 4: not triggered (S2=5.5)
  - oral_quality_score < 5 (oral=3.0): cap overall at 5.5  (not binding)
  - S6 < 5 (S6=2.0): cap overall at 6.0  (not binding)
  - S5 < 4 implied by EXP-2 fail: cap S5 at 4 — applied (S5=2.0 already below)

final_overall = 4.5  →  verdict per §6: overall in [4.0, 5.5) → "weak_reject"
```

**The 4.5 floor is structural**: even if D1/D2/D3/D4/D5/D6/D7 were all 9.0, experiments_solidity_score=1 would still cap overall at 4.5. The only way to break the floor is to add benchmarks / seeds / significance tests / external SOTA baselines.

## Reference Documents Consulted

- `docs/demand.md`: loaded (re-verified §2 8-page rule, §6 Limitations rule, §7 Responsible NLP Checklist)
- `article/build/edo_paper.pdf`: loaded as PDF: NO — used pdftotext-layout extraction at `$env:TEMP\edo_paper_strict_audit.txt` (deleted post-review per §F.3 new rule)
- **layout_dependent_checks_blocked**:
  - DR-4 template tampering (cannot confirm from text)
  - D6 Figure 1 final visual quality (admittedly placeholder)
  - D6 Figure 2 ASCII render approximation
  - DR-1 page-9/10 boundary precision (pdftotext gives line-level, not pixel-level)

## Verified Document Structure (from pdftotext page markers)

| Page | Content |
|---:|---|
| 1 | Abstract + §1 Introduction |
| 2 | §1 / §2 Related Work start |
| 3 | §2 (orchestrator + reflection + organization theory) |
| 4 | §3.1 / §3.2 / §3.3 |
| 5 | §3.4 / §3.5 / §3.6 + **Algorithm 1 inline** |
| 6 | §3.7 / §3.8 + Prototype Scope Box / §4.1 |
| 7 | §4.2 / §4.3 (Findings 1-2) + Table 2 |
| 8 | §4.3 (Findings 3-4) / §4.4 / §4.5 + Figure 2 / **§5 Conclusion** |
| 9 | Limitations (5 items, clean) + Appendix A B1-B3 start |
| 10 | Appendix A B3-B5 + **Appendix B Provider Integrity Event** |
| 11 | References |

**Main body (Abstract + §1-§5 Conclusion) ends on page 8 ✅** — DR-1 PASS confirmed.

## Desk-Reject Pre-flight Result

| ID | Status | Evidence |
|---|---|---|
| DR-1 page count | **PASS** | Main body §1-§5 (incl. Conclusion line 595) ends on page 8; Limitations starts page 9; Appendix A/B + References on page 9-11 (excluded from main-body limit per demand.md §2) |
| DR-2 Limitations title | PASS | Exactly "Limitations" (line 605) |
| DR-3 Limitations no new content | **PASS** | All 5 items are scope statements; item (5) cleanly cross-references Appendix B without describing implementation; Appendix B (engineering response) is in Appendix, not Limitations |
| DR-4 template tampering | NA | Cannot confirm from text |
| DR-5 anonymization | PASS | "anonymous code/data supplement", "Anonymous Suppl.", "anonymous figure-prompt supplement" — no identifying info |
| DR-6 Responsible NLP Checklist | PASS | Appendix A B1-B5 present (B5 PII added in this PDF version) |
| DR-7 dual / sliced submission | NA | No evidence of sliced contribution |
| DR-8 ethics | PASS | B4 AI assistant disclosure; B1 license/intent compatibility |

**Zero confirmed desk-reject triggers.** The paper is structurally compliant with EMNLP / ARR submission rules.

## Experiments Solidity Audit (score = 1 / 8)

| check | status | evidence |
|---|---|---|
| EXP-1 multi-dataset | **fail** | HotpotQA only (§4.2 Benchmark); MuSiQue + 2WikiMultiHop reserved for Stage-2 (§4.4 E5) |
| EXP-2 multi-seed | **fail** | §Limitations (4) admits "point estimates with n=200, multi-seed variance deferred to Stage-2" |
| EXP-3 significance test | **fail** | §4.3 Finding 2: "2.6 F1 points — non-trivial at n=200 but not yet confirmed with paired statistics" |
| EXP-4 effect size or CI | **fail** | Table 1 / Table 2 / Figure 2 all point estimates; no CI columns; no Cohen's d |
| **EXP-5 ablation coverage** | **pass** | Table 2 in body: 4 variants (canonical/baseline/+evidence-window/−TCPB/−decomposer-gate); §4.5 also reports weight-sensitivity (±2× < 0.003pp) and static-path overlap (~52%); coverage ≈ 0.6 |
| EXP-6 baseline recency | **fail** | All Table 1 baselines author-internal; AutoGen/MetaGPT/Multi-Agent Debate/ChatEval cited but NOT in Table 1; "centralized baselines" mentioned but not in Table 1 |
| EXP-7 sensitivity sweep | partial | §4.5 narrative ±2× weight sensitivity only; no sensitivity table |
| EXP-8 error analysis | partial | §4.5 static-path overlap quantitative + Finding 4 narrative; no per-method failure-mode breakdown table |

**Caps implied by audit**:
- EXP-1 fail: cap D4 at 6
- EXP-2 fail: cap D4 at 5 + cap S5 at 4
- EXP-3 fail: cap D4 at 6 + cap S5 at 5
- EXP-6 fail: cap D4 at 5 + cap S6 at 4
- experiments_solidity_score = 1 (≤ 3): **cap overall at 4.5** ← binding

## Novelty Delta Audit (12 named prior works)

| prior_work | year | concrete? | overlap_risk? |
|---|---:|---|---|
| AutoGen (Wu et al., 2024) | 2024 | ✅ | ❌ |
| MetaGPT (Hong et al., 2024) | 2024 | ✅ | ❌ |
| HuggingGPT (Shen et al., 2023) | 2023 | ✅ | ❌ |
| ChatDev / AgentVerse | 2024 | ✅ | ❌ |
| Reflexion / Self-Refine / ToT | 2023 | ✅ | ❌ |
| **Multi-Agent Debate (Liang et al., 2024) / ChatEval (Chan et al., 2024)** | 2024 | ✅ | **⚠ TRUE — and unaddressed-via-baseline** |
| Galbraith / Mintzberg | 1973/1979 | ✅ (informing theory) | ❌ |

**§2.5.2 hard rule application**: ≥ 3 named prior works with concrete deltas ✅ → no D3 floor cap. But Multi-Agent Debate is `is_overlap_risk=TRUE` AND is not benchmarked → cap D3 at 6 (per §3 D3 hard rule). My honest D3 = 4.5 (below cap), reflecting that the differentiation between TCPB and MAD is a categorical claim ("terminal F1 vs aggregator judgment") that is not empirically demonstrated.

## Top Strengths

1. **Algorithm 1 is now inline in §3.6 (page 5)** as a complete EDO Stage-2 PROCESS recursion (lines 1-36), explicitly marking which lines correspond to R1 split (lines 14-16, 25-29), R2 audit (lines 16-23), R3 vector belief (lines 32-34). This is a meaningful improvement in formalization compared to typical multi-agent system papers that gesture at architecture without committing to algorithmic detail.
2. **§5 Conclusion + Abstract honestly admit the headline self-falsification** ("on a single benchmark its peer-calibrated variant is Pareto-dominated by a simpler self-claim baseline at equal token cost — this is a delivered-system limitation, not a refutation of the broader framework"). This is unusual self-awareness; most papers in this space claim wins they don't have.
3. **Limitations section is clean and structured** (5 numbered items, all scope statements, no engineering description spillover); item (5) correctly cross-references Appendix B for engineering details rather than embedding them.
4. **Appendix A Responsible NLP Checklist is complete** (B1-B5 including PII section that is often skipped); B2 includes wall-clock + USD cost which exceed minimum reproducibility requirements.

## Top Weaknesses (P1 perspective, ordered by severity)

1. **FATAL — single-benchmark + single-seed + no significance test + no external SOTA baseline**: experiments_solidity_score = 1/8. Per §6 hard rule, caps overall at 4.5 regardless of any improvement on writing/framing/algorithm specification. **This is the structural blocker for ARR acceptance.** Until the paper reports HotpotQA + ≥1 second benchmark (MuSiQue cited in §4.2 as "reserved" — no reason it cannot be in this submission) with ≥3 seeds and paired bootstrap CI, no overall score above 4.5 is reachable.
2. **FATAL — all Table 1 baselines are author-internal routing variants** (peer_calibrated / static_roles / self_claim / self_calibrated). Zero external 2024-2026 multi-agent system in Table 1. AutoGen / MetaGPT / Multi-Agent Debate / ChatEval are CITED in §2 but never benchmarked. Multi-Agent Debate specifically is `is_overlap_risk=TRUE` per the novelty audit — running it as a baseline would either (a) confirm TCPB's terminal-outcome claim has independent value over per-hop aggregator, or (b) reveal it doesn't. Either outcome is more informative than the current within-family Pareto comparison.
3. **FATAL — EDO main mechanisms (R1 split / R2 recursive audit / R3 persona vector) are admittedly NOT implemented** (§3.8 + Prototype Scope Box + Limitations item (1) all explicitly state). Algorithm 1 specifies the full Stage-2 loop, but Table 1 reports only the degenerate Stage-1 instance (TCPB) where SPLIT is disabled, AUDIT defaults to ACCEPT, vector belief is collapsed to scalar. **What the paper claims to contribute (EDO framework) is structurally not what the paper measures.** Acceptance of this manuscript without at least one Stage-2 mechanism running is asking the community to accept a method roadmap as a methods paper.
4. **D1 — multiple undefined functions in Algorithm 1**: FIT, AUDIT (rule for non-default case), EVIDENCE_EXTRACT, SPLITGAIN, MERGECOST, AUDITCOST, all λ coefficients (λ_c, λ_a, λ_m, λ_d, λ_s, λ_r), AND TCPB's actual scoring weight assignment (which 0.55/0.20/0.10/etc. maps to which utility term). The paper says "deterministic instantiations of ϕ, FIT, EVIDENCE_EXTRACT are in the executable spec [Anonymous Suppl.] §1-3" — i.e., reading the paper alone you cannot reproduce TCPB. P1's strict standard ("every algorithmic object, update rule, and state variable fully formalized") is materially violated.
5. **D5 — LLM call prompt templates not in paper**: Algorithm 1 calls LLM_ANSWER (line 13), LLM_DECOMPOSE (line 26); Conclusion mentions LLM-based AUDIT non-default rule. None of these prompt templates are in the paper body. Reproducibility from paper alone is impossible without supplement.
6. **D6 — Figure 1 is a placeholder** (the caption itself says "[Figure 1 placeholder] ... Vector asset to be inserted; full design specification in the anonymous figure-prompt supplement"). For an EMNLP Long Paper at submission time, Figure 1 of the methods section being a placeholder is a strong signal of incomplete preparation; an oral-track paper would not ship with this.

## Core Method Problems

1. EDO main mechanisms (R1/R2/R3) admittedly not implemented; Algorithm 1 lines 14-16 (split branch) / 16-23 (audit branch) / 32-34 (vector update) all gated to default behavior in the delivered system.
2. FIT(P_i, ϕ(z)) function never defined for the full vector case. §3.6 says "vector belief is collapsed onto a scalar c[i] via mean-axis fold" but the projection function and the dimension-by-dimension semantics are not specified.
3. AUDIT decision rule for non-default case ("rule-based on answer length, refusal patterns, and an audit_score proxy" per §3.8) — audit_score function and the rule's threshold values are deferred to executable spec §4 (not in paper).
4. EVIDENCE_EXTRACT(e, ϕ(z)) → R^7 mapping function (Algorithm 1 line 33) — undefined in paper; all that is given is the EMA update equation `B^t+1_i(j) ← clip((1-ν)B^t_i(j) + ν · EVIDENCE_EXTRACT(...))`.
5. TCPB's actual numeric weight mapping: B2 lists "routing weights for the Stage-1 TCPB instance (0.55, 0.20, 0.10, etc.)" but does not say what these weights are weights OF. This is a one-line fix (state the formula explicitly) that has not been done.

## Experimental Design Problems

1. Single benchmark (HotpotQA distractor validation 200). MuSiQue and 2WikiMultiHop both already cited (§4.2) as "reserved for Stage-2"; no reason this submission cannot run at least one of them.
2. Single seed reported in Table 1; multi-seed admitted as deferred (§Limitations 4).
3. No paired statistical test in body (§4.3 admits not yet confirmed).
4. Zero external multi-agent baselines in Table 1; Multi-Agent Debate (cited as direct precursor in §2.2) is the most obvious omission.
5. Table 2 ablation is glm-4-flash only — no equivalent on canonical strong backbone (gpt-4.1-mini) where Finding 2's headline ordering inversion lives. Cannot verify whether TCPB-on/off or gate-on/off behavior generalizes to the strong backbone setting.
6. No emergent-specialization metric measured (e.g., persona-tag divergence, specialization entropy) — these are §4.4 E1 metrics that the EDO framework claim depends on but the present paper does not even gesture at measuring.

## Implementation / Reproducibility Gaps

1. External `edo_lite_executable_spec.md` (referenced multiple times) is the canonical impl spec for ϕ extraction and utility instantiation but is NOT part of the paper body — independent replication of TCPB's exact deterministic ϕ extraction requires this supplement.
2. LLM_ANSWER, LLM_DECOMPOSE, AUDIT (non-default rule), EVIDENCE_EXTRACT prompt templates not in paper.
3. Compute budget (B2) is order-of-magnitude with wall-clock, but no exact reproducibility seeds or specific API call counts per result point.
4. Provider variability: Appendix B documents one provider-side model-substitution incident; replicators on different providers may see different model behavior. The integrity-check guard described in Appendix B is mentioned but the threshold logic (what counts as "model identifier mismatch") is not given.
5. `published_competence` schema (mentioned in §3.8 R3) — wire format / serialization not specified.

## Overclaims or Risky Claims

1. Conclusion (§5): "EDO moves the focus from fixed roles to socially induced personality tags, from linear routing to recursive task trees, and from terminal-only supervision to recursive acceptance-based organization." Three of these moves (personality tags, recursive task trees, recursive acceptance) are admitted not implemented in §3.8. Honest re-phrasing: "EDO **proposes** these three moves; TCPB instantiates only the third (terminal supervision) in restricted form."
2. Abstract: "Each delegation creates an upstream acceptance obligation, and these obligations compose into a recursive acceptance ladder" — recursive acceptance ladder is admittedly NOT implemented in TCPB (§3.8 R2: "current submission performs no per-hop upstream rejection"). Abstract should add a clause: "these mechanisms are theoretical; the delivered TCPB prototype implements only terminal-outcome calibration."
3. Abstract: "decentralized outcome-based calibration improves delegation safety and stabilizes routing without a central controller" — Finding 3 attributes PAR=0.0 to the decomposer force-forward gate (a fixed safety prior, line 11 of Algorithm 1), not to TCPB itself. Calling this "TCPB improves delegation safety" overstates the mechanism's contribution; the gate is doing the safety work.
4. §3.1 "decentralized" / "no global expert table" — but Algorithm 1 has 4 hand-coded role-prior nodes {DEC, EVI, VER, SYN} with hard-coded multi-hop force-forward rule for DEC. Honest re-phrasing: "decentralized within a fixed role-prior topology with hand-tuned safety priors."

## Ambiguous Algorithm Points

1. Algorithm 1 line 3 / line 5: `U^S ← FIT(P_i, ϕ) - λ_c Cost_self` and `U^O_j ← FIT(B^t_i(j), ϕ) - λ_a AuditCost` — FIT is undefined for vector case; λ_c, λ_a values unspecified; Cost_self / AuditCost functional form unspecified.
2. Algorithm 1 line 7: `U^P ← SPLITGAIN(z) - λ_m MergeCost` — both undefined.
3. Algorithm 1 line 16: `e ← AUDIT(i, j*, z, r)` — default behavior is ACCEPT (per §3.8 R2), but the non-default rule ("answer length, refusal patterns, audit_score proxy") is in external spec.
4. Algorithm 1 line 33: `EVIDENCE_EXTRACT(e, ϕ(z))` undefined.
5. §3.5 µ, η_loc, η_trm, η_rew (persona update equation parameters) — no values for either Stage-1 or Stage-2.

## Missing Definitions or State Variables

1. FIT(·, ·) function (§3.3 utility, Algorithm 1 lines 3, 5).
2. λ_c, λ_r, λ_s, λ_a, λ_m, λ_d (§3.3 utility coefficients) — only TCPB-scalar instantiation appears in B2 hyperparameters.
3. µ, η_loc, η_trm, η_rew (§3.5 persona update coefficients) — no values.
4. AUDIT decision rule + audit_score proxy (§3.8 R2).
5. EVIDENCE_EXTRACT(·) (§3.8 R3, Algorithm 1 line 33).
6. SPLITGAIN, MERGECOST, AUDITCOST functional forms.
7. TCPB's specific weight-to-term mapping (B2 lists "0.55, 0.20, 0.10, etc." but does not say which goes where).

## Missing or Weak Experiments

1. No second benchmark (MuSiQue or 2WikiMultiHop both cited as "reserved" in §4.2).
2. No multi-seed runs (admitted deferred in Limitations 4).
3. No paired bootstrap / sign test / permutation test in body.
4. Zero external multi-agent baselines (AutoGen / MetaGPT / Multi-Agent Debate / ChatEval all CITED but NOT benchmarked).
5. Table 2 ablation glm-4-flash only — missing equivalent on canonical strong backbone gpt-4.1-mini.
6. No emergent-specialization measurement (§4.4 E1 metrics: persona-tag divergence, specialization entropy, per-agent action frequencies) — but EDO's central novelty CLAIM is "emergent organization", which without these metrics cannot be measured at all.

## Statistical Significance Concerns

1. Table 1 / Table 2 / Figure 2 all point estimates only; no CI columns.
2. §4.3 explicitly admits headline 2.6 F1-point gap "not yet confirmed with paired statistics".
3. No effect size (Cohen's d, relative %) reported anywhere in §4.

## Baseline Completeness Concerns

1. Zero external 2024-2026 multi-agent system baselines in Table 1.
2. All Table 1 baselines are author-internal routing variants — within-family Pareto comparison is structurally limited.
3. "Centralized baselines" referenced in §4.2 but no central_orchestrator row in Table 1.

## Limitations Section Assessment

- `section_present`: ✅
- `section_title_exact`: ✅ ("Limitations")
- `contains_no_new_content`: ✅ (improvement: in this PDF version, item (5) cross-references Appendix B for engineering details, not embedding them; clean scope statement only)
- `honesty_score_1_to_5`: 4
- `specific_failure_modes_listed`: ✅
- **issues**:
  - Item (3) backbone-sensitive prediction now properly framed as "we conjecture; not validated by present submission; will be tested by Stage-2 evaluation agenda" — improvement
  - Item (5) cleanly states "cross-endpoint comparability is an open variable" without describing engineering implementation — DR-3 risk eliminated
  - Does not explicitly acknowledge the Pareto-domination as a *delivered-system* limitation in Limitations (only mentioned in Conclusion); could be added as item (6) for completeness

## Responsible NLP Checklist Assessment (Appendix A)

`appears_complete`: ✅ (B1 / B2 / B3 / B4 / **B5 PII** added)

**Issues**:
- B2 compute budget improved with wall-clock + USD cost (~1-2h per chain-200 batch, $0.50-$1.00 per batch, ~35× for fullval) — significantly more concrete than minimum
- B5 PII coverage added (Wikipedia-sourced, no PII) — addresses gap from previous Checklist versions
- All required sections present

## Implementation Risks

- External `edo_lite_executable_spec.md` not part of submission — replication blocked without anonymous supplement.
- Provider variability documented in Appendix B; replicators on different providers may see different model behavior; the integrity-check guard implementation is referenced but threshold logic not given.
- LLM_ANSWER / LLM_DECOMPOSE / AUDIT-rule / EVIDENCE_EXTRACT prompt templates not in paper body.
- Single-seed runs make any reported metric a single-realization sample.
- fullval (n=7405): only peer_calibrated has valid full-validation point (F1=0.7703); other two pending re-execution per Limitations (5). Full ranking cannot be reproduced from paper alone.

## What to Fix for 8+ Overall (P1-priority order)

1. **Add MuSiQue as second benchmark** — already cited in §4.2 as Stage-2 reserved; runtime is parallel (B2 confirms); single change moves EXP-1 from fail to pass and starts unblocking the experiments_solidity_score floor.
2. **Run all main results with ≥3 seeds + 95% bootstrap CI + paired sign test in Table 1** — addresses EXP-2 / EXP-3 / EXP-4 simultaneously; runtime ~3-4 hours total.
3. **Add ≥2 external multi-agent baselines** (AutoGen + Multi-Agent Debate). Multi-Agent Debate specifically is `is_overlap_risk=TRUE` in novelty audit — benchmarking it directly verifies TCPB's terminal-outcome claim.
4. **Add Table 2 ablation on canonical strong backbone** (gpt-4.1-mini) — currently glm-4-flash only; cannot verify TCPB-on/off behavior generalizes.
5. **Replace Figure 1 placeholder with finished vector PDF** — caption already specifies the design.
6. **Inline the TCPB scoring formula in §3.6** — currently the "0.55, 0.20, 0.10, etc." in B2 is an unattributed bag of numbers; one explicit formula closes the largest D1 gap.
7. **Define FIT for the vector case** — even a one-line "Fit(P, ϕ) = ⟨P, W ϕ⟩ where W is a learned 7×7 matrix" or "Fit = ⟨P, ϕ⟩ / (‖P‖·‖ϕ‖)" closes a major Stage-2 ambiguity.

## What to Fix for Oral (top 3-5%)

8. **Implement at least one of (R1) / (R2) / (R3) and demonstrate empirical value**. R2 audit is the highest-ROI candidate — if audit allows upstream rejection of bad subcontracts, peer_calibrated could in principle outperform self_claim by catching errors self_claim cannot, directly reversing Finding 4. Without ANY Stage-2 mechanism actually running, EDO contribution is a roadmap, not a paper-deliverable.
9. **Show non-trivial improvement over external 2024-2026 SOTA on at least one benchmark** — currently the proposed method LOSES to its own simplest baseline.
10. **Quantitative error analysis** with named failure modes per method.
11. **Seed-level organization stability** (per §4.4 E1 metrics) — if EDO is about emergent specialization, the paper needs to show specialization is stable across seeds.
12. **Community impact case study** — currently impact is asserted (D2=4.0) not demonstrated.

## Recommended Next Actions (ordered by ROI for ARR May/EMNLP 2026)

1. **Lowest-cost / highest-impact**: add MuSiQue + multi-seed (≥3) + paired bootstrap CI in Table 1. This single sprint moves experiments_solidity_score from 1 to ~5, unblocking the §6 cap on overall.
2. **Second-lowest-cost**: inline TCPB scoring formula in §3.6 (~10 min), define FIT for vector case (~30 min), replace Figure 1 placeholder (~1-2 days for vector design).
3. **Stage-2 minimum viable**: implement R2 (recursive audit) — closest neighbor mechanism that could empirically reverse Finding 4. Algorithm 1 lines 16-23 already specify the AUDIT decision protocol.
4. Add Multi-Agent Debate (Liang et al., 2024) as external baseline in Table 1 — directly addresses the only `is_overlap_risk=TRUE` prior work.

## Honest Final Verdict

This is a competently-written paper with unusual self-awareness about what it does and does not deliver. The hygiene improvements visible in this PDF version (Algorithm 1 inline, Limitations clean, Provider Integrity in Appendix B, Bibliography 12+ named references) are real and measurable. **However**, the core experimental skeleton — single benchmark, single seed, no significance test, no external SOTA baseline, headline result self-falsified — is structurally insufficient for an EMNLP Long Paper acceptance, regardless of how well the framework is articulated.

The paper currently sits in the **`weak_reject` / borderline** zone. A revision that adds one more benchmark + multi-seed CI + one external baseline (3 changes) would reasonably reach `borderline` (overall 5.5-6.5). Adding even one Stage-2 mechanism (R1/R2/R3) actually running would reasonably reach `weak_accept` (6.5-7.5). The current submission is on a clear path to acceptance but has not yet executed the necessary experimental work.

I recommend the authors **withdraw and revise** rather than submit this version to ARR May 2026, unless the authors are deliberately treating ARR as a low-stakes early-feedback round.

## Reviewer-Only Boundary Compliance (per `REVIEWER_TODO §F.1.4 / §F.1.5`)

- ✅ Did NOT modify `USER_TODO.md` / `SCIENTIST_TODO.md` / `PROJECT_STRUCTURE.md`
- ✅ Did NOT participate in §A decisions (this `recommended_next_actions` field is suggestion-only; decision authority remains with user)
- ✅ Did NOT read past reviews / scoreboard / fix_themes / SCIENTIST_TODO §C (stateless)
- ✅ Did NOT trigger S-104 (scientist's responsibility per §11.4)
- Will leave §F.4 1-line ack in `implementation_log.md` as the only allowed exception
- Temporary PDF text extraction (in system temp) deleted post-review per §F.3
- This `review.md` is the only required product per §F.3 (no `review.json` generated)
