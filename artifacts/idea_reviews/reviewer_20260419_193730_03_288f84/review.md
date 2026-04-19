# Review of `article/build/edo_paper.pdf` (R-FULL-003)

## Metadata

- **reviewer_id**: `reviewer_20260419_193730_03_288f84`
- **reviewer_profile**: P2 Empirical-NLP SAC focused on Empirical Results (D4), Baseline Quality (S6), Ablation Completeness (S7), and Statistical Rigor (S5). Demands ≥3 diverse datasets, latest published SOTA, full ablation matrix, multi-seed runs with paired significance tests, and honest error analysis; flags single-benchmark / single-seed papers as borderline-reject by construction.
- **model**: human/agent (Cursor session, no remote LLM call)
- **target**: `article/build/edo_paper.pdf` (347.8 KB / 11 pages, mtime 2026-04-19 19:28:22, SHA256 prefix 73AD9124)
- **submission_track**: EMNLP Long Paper — Oral evaluation
- **document_type**: `partial_paper` (full structural form but admittedly degenerate-instance experimental delivery; per §10 reviewer rules, treated as partial paper for scoring)
- **stateless**: did NOT read R-FULL-001 / R-FULL-002 / scoreboard.md / fix_themes.md / SCIENTIST_TODO §C
- **F.2 input integrity**: PASS — PDF not stale (TEX 19:28:02 < PDF 19:28:22), all 3 authoritative inputs present
- **F.4 cooldown**: PASS — PDF SHA differs from previous batches (different size/mtime); user explicitly triggered new batch

## Headline

| Field | Value |
|---|---|
| **overall** | **4.5 / 10** |
| **verdict** | **`weak_reject`** |
| **oral_eligible** | `false` |
| **confidence** | `3` (PDF text only — layout-dependent checks blocked) |
| **is_8_plus_ready** | `false` |
| **estimated_score_after_fixes** | `6.5` |

## Scores

| dim | score | one-line rationale |
|---|---:|---|
| D1 soundness | 6.0 | Algorithm 1 is now the full EDO Stage-2 spec (R1+R2+R3 integrated PROCESS recursion); Fit / EVIDENCE_EXTRACT / λ_a still undefined |
| D2 significance | 5.0 | Reframing valuable; honest admission Pareto-dominated by self_claim limits practical significance |
| D3 novelty | 5.5 | 12 named prior works with concrete deltas; Multi-Agent Debate is_overlap_risk partially-addressed-not-benchmarked |
| D4 empirical_results | 5.0 | Single benchmark + single seed + no significance test; experiments_solidity_score = 1/8 |
| D5 reproducibility | 8.0 | Algorithm 1 EDO Stage-2 spec + B2 wall-clock + USD cost + all hyperparameters + anonymous code supplement |
| D6 clarity | 7.0 | Algorithm 1 page-11 full-page float (reading discontinuity); Figure 1 placeholder; otherwise crisp |
| D7 limitations | 7.0 | 5 honest scope limits; item (5) Provider integrity event borders DR-3 (engineering description in Limitations) |
| S1 executability | 6.5 | TCPB Stage-1 reproducible from Algorithm 1 step 13/16 default; Stage-2 R1/R2/R3 reproducible if you can implement LLM_DECOMPOSE / AUDIT |
| S2 falsifiability | 7.0 | Honest acknowledgment of self-falsification in Conclusion + Abstract + Limitations (1) + (3) backbone-sensitive conjecture marked unvalidated |
| S3 empirical_plan | 7.0 | §4.4 E1-E5 5-study agenda + 8 organizational metrics specified |
| S4 technical_clarity | 6.5 | Equations clear; multiple symbols undefined for full EDO |
| S5 statistical_rigor | 3.0 | No CI / no paired test / no multi-seed (Limitations 4 admits deferred) |
| S6 baseline_quality | 3.0 | All baselines author-internal (peer/static/self_claim/self_calibrated); AutoGen/MetaGPT/MAD/ChatEval cited but not benchmarked |
| S7 ablation_completeness | 6.0 | Table 2 in body: 4 variants (canonical/baseline/+evidence/-TCPB/-gate) |
| S8 writing_and_figures | 6.0 | Algorithm 1 + Figure 2 ✓; Figure 1 placeholder; Algorithm 1 isolated on page 11 (layout pressure signal) |
| **oral_quality_score** | **4.0** | "Weak reject; clear path to acceptance after major revision" — single-benchmark / single-seed papers are borderline-reject by construction per P2 default |
| **overall (weighted_sum)** | **5.905** | before caps |
| **overall (final)** | **4.5** | after caps |

## Score Calculation

```
weighted_sum = 0.25*D1 + 0.18*D2 + 0.15*D3 + 0.18*D4 + 0.10*D5 + 0.07*D6 + 0.07*D7
             = 0.25*6.0 + 0.18*5.0 + 0.15*5.5 + 0.18*5.0 + 0.10*8.0 + 0.07*7.0 + 0.07*7.0
             = 1.500 + 0.900 + 0.825 + 0.900 + 0.800 + 0.490 + 0.490
             = 5.905

caps_triggered:
  - experiments_solidity_score = 1 (only EXP-5 strict pass): cap overall to 4.5
    (per §6 hard rule: results-not-solid floor)
  - D4 < 7 (D4=5.0): cap overall to 7.0 — not binding (already 4.5)
  - oral_quality_score < 5 (oral=4.0): cap overall to 5.5 — not binding (already 4.5)
  - S6 < 5 (S6=3.0): cap overall to 6.0 — not binding (already 4.5)
  - S5 < 4 implied by EXP-2 fail: cap S5 at 4 — applied (S5=3.0 already below cap)
  - S6 < 4 implied by EXP-6 fail: cap S6 at 4 — applied (S6=3.0 already below cap)

final_overall = 4.5  →  verdict mapping per §6:
  overall in [4.0, 5.5)  →  "weak_reject"
```

**Note on cap mechanics**: The §6 experiments_solidity floor (cap at 4.5 when score ≤ 3) is by design — it prevents `overall` from rewarding well-written / well-framed but empirically thin papers. `weighted_sum=5.905` reflects honest improvements on D5 / D6 / D7 / S2 / S3 vs. typical Stage-1 manuscripts; however EXP-1/2/3/4/6 all still fail.

## Reference Documents Consulted

- `docs/demand.md` loaded: `true`
- `article/build/edo_paper.pdf` loaded as PDF: `false` — used pdftotext extraction (temporary file in system temp, deleted post-review per §F.3 new rule)
- **layout_dependent_checks_blocked**:
  - DR-1 precise main-body page boundary (§5 Conclusion appears to bleed onto page 9 per pdftotext layout)
  - DR-4 template tampering (cannot confirm from text)
  - D6 Figure 1 quality (admittedly a placeholder per its own caption)
  - D6 Figure 2 visual quality (ASCII render is approximate)
  - D6 Algorithm 1 page-11 float positioning (full-page float on last page is layout-pressure signal)

## Document Type Justification

This is structurally a `full_paper` (Abstract + 5 sections + Limitations + Appendix A Responsible Checklist + References + Algorithm 1 float) but methodologically a **`partial_paper`**:

- §3.6: "Algorithm 1 specifies the full EDO Stage-2 execution loop... The reported empirical results in Table 1 come from the **degenerate Stage-1 instance** of this loop, which we call... TCPB: SPLIT is disabled, AUDIT defaults to ACCEPT on every return, and the vector belief Bit(j) is collapsed onto a scalar c[i]"
- Prototype Scope Box: explicitly enumerates 5 substitutions from full EDO
- §3.8 R1/R2/R3: "current submission contains zero split events" / "current submission performs no per-hop upstream rejection" / "is not updated per hop"
- Per reviewer rule §10 "method-design / idea note vs full 8-page paper": EDO main mechanisms are method-design without empirical evaluation. The submission is a hybrid: full paper structure + partial-paper experimental scope.

Treating as `partial_paper` does NOT trigger the "any score ≥ 7 forbidden" reviewer hard rule because the paper has full 8-page main body + complete bibliography + Algorithm 1 + Table 1/2 + Figure 2 — only the experimental delivery (not the structure) is partial.

## Summary

EDO reframes decentralized multi-agent routing as 'organizational emergence' under local interaction. The full method (recursive split + audit + persona vector) is admittedly NOT implemented — Algorithm 1 specifies the full EDO Stage-2 execution loop, but Table 1 reports only the degenerate Stage-1 instance (TCPB: SPLIT disabled, AUDIT defaults to ACCEPT, vector belief collapsed to scalar). On a single benchmark (HotpotQA n=200, single seed), the proposed peer-calibrated TCPB (F1=0.7381) is admittedly Pareto-dominated by the simplest baseline self_claim (F1=0.7641) at equal token cost (6,414/sample) — the paper frames this as "delivered-system limitation, not a refutation of the broader framework". Bibliography contains 12 named recent prior works with concrete mechanistic deltas; closest neighbor Multi-Agent Debate (Liang et al., 2024) is is_overlap_risk=TRUE but only partially-addressed-in-§2.2-and-not-benchmarked.

## Top Strengths

1. **Algorithm 1 is now the full EDO Stage-2 specification** (PROCESS recursion integrating R1 split + R2 audit + R3 vector-belief routing in 22+ lines with bounded recursion `dmax=3, nmax=12`). Treating Table 1's TCPB as a *degenerate special case* of Algorithm 1 (SPLIT disabled, AUDIT defaults to ACCEPT, vector→scalar fold) is a clean framing that lets a re-implementer recover both the delivered system AND the proposed Stage-2 system from a single algorithm box.
2. **Honest scoping is unusually disciplined**: Abstract, §3.6, §3.7, §3.8 R1/R2/R3, Prototype Scope Box, §Limitations (1)/(2)/(3)/(4)/(5), and Conclusion all consistently mark Stage-2 as proposed-but-not-delivered. Conclusion explicitly says: "We honestly report that on a single benchmark its peer-calibrated variant is Pareto-dominated by a simpler self-claim baseline at equal token cost — this is a delivered-system limitation, not a refutation of the broader framework."
3. **Related Work (§2.1-§2.3) names 12 specific prior systems** (AutoGen / MetaGPT / HuggingGPT / ChatDev / AgentVerse / Reflexion / ToT / Self-Refine / Multi-Agent Debate / ChatEval / Galbraith / Mintzberg) and articulates concrete mechanistic deltas for each — far above the typical "orchestrator-based frameworks" generic referencing.
4. **Reproducibility infrastructure is thorough**: B2 includes wall-clock estimate (~1-2 hours per chain-200 batch), USD cost ($0.50-$1.00 per chain-200 batch, ~35× for fullval), all hyperparameters for both Stage-1 and Stage-2 (ν=0.2, kmax=3, dmax=3, nmax=12), anonymous code/data supplement reference, and integrity-check provenance for the provider drift event.

## Top Weaknesses (ordered by severity, P2 perspective)

1. **FATAL** — `experiments_solidity_score = 1/8`: only EXP-5 (ablation) passes. Single benchmark (HotpotQA only); single seed (no multi-seed); no paired statistical test; no CI / no effect size; baselines all author-internal (no external SOTA from past 24 months). Per §6 hard rule, this caps `overall` at 4.5 regardless of how strong other dimensions are. **This is the structural blocker** for an EMNLP Long Paper acceptance.
2. **FATAL** — All Table 1 baselines are author-internal routing variants (`fixed_peer_calibrated` / `fixed_static_roles` / `fixed_self_claim` / `fixed_self_calibrated`). Zero external 2024-2026 multi-agent system in Table 1. AutoGen / MetaGPT / Multi-Agent Debate / ChatEval are CITED in §2 but never benchmarked. Multi-Agent Debate is `is_overlap_risk=TRUE` per §2.5.2 audit (TCPB's "terminal-outcome only" is essentially a degenerate case of MAD's "per-hop critique aggregator with aggregator window = full trajectory") — benchmarking it would be the most direct way to verify the only real mechanistic claim.
3. **FATAL** — Headline empirical claim is admittedly self-falsified: §4.3 Finding 4 + Conclusion both admit `peer_calibrated F1=0.7381 < self_claim F1=0.7641` at equal token cost. The paper's framing pivots from "TCPB wins" to "EDO framework explains *when* delegation overhead pays off — and Stage-1 evidence reveals backbone-sensitive threshold effects that motivate the full theory." This pivot is theoretical, not demonstrated. Per P2 standard, framework-only claims without empirical support are at most weak_accept.
4. **Stage-2 mechanisms (R1 split / R2 audit / R3 persona vector) are admittedly NOT implemented** — Algorithm 1 specifies them but §3.6 + §3.8 + Prototype Scope Box + Limitations (1) all explicitly say the delivered system runs only the degenerate Stage-1 instance. EDO's claimed contribution is structurally evaluable only as a research roadmap, not as a paper deliverable.
5. **Figure 1 is a placeholder** (caption explicitly says '[Figure 1 placeholder] Vector asset to be inserted; full design specification in the anonymous figure-prompt supplement'). For an EMNLP Long Paper, Figure 1 of the methods section being a placeholder is a strong signal of incomplete preparation.
6. **DR-3 POSSIBLE — Limitations item (5) contains engineering description**: Limitations item (5) describes the fail-fast integrity check implementation ("compares the model identifier echoed back in each response against the requested identifier and raises an explicit error on mismatch") and the endpoint-switch decision ("the upstream API endpoint serving the strong backbone was switched to a different OpenAI-compatible provider channel with this guard enabled in pre-send mode"). Per demand.md §6, Limitations should contain only scope/honesty discussion, not new engineering content. Borderline POSSIBLE violation; reviewer recommends moving the implementation detail to a separate Appendix B (or to §3.x runtime description) and keeping Limitations (5) to a one-sentence cross-endpoint-comparability scope statement.

## Desk-Reject Risks

| ID | Status | Evidence |
|---|---|---|
| DR-1 | POSSIBLE | pdftotext suggests §5 Conclusion bleeds onto page 9 (lines 582-616). Per demand.md §2 strict reading, Conclusion counts toward 8-page main body. Needs scientist verification on rendered PDF page boundaries. |
| DR-2 | PASS | "Limitations" title exact (line 617) |
| DR-3 | **POSSIBLE** | Limitations item (5) contains engineering implementation description (fail-fast integrity guard + endpoint switch) — borderline new content per demand.md §6 strict reading |
| DR-4 | NA | Cannot confirm template tampering from text only |
| DR-5 | PASS | Anonymization explicit: "anonymous code/data supplement", "Anonymous Suppl.", "anonymous figure-prompt supplement" |
| DR-6 | PASS | Appendix A Responsible NLP Checklist B1-B4 present |
| DR-7 | NA | Not applicable |
| DR-8 | PASS | B4 discloses AI-assistant use; B1 discloses license/intent; citations resolve to plausible real papers |

## Experiments Solidity Audit (score = 1 / 8)

| check | status | evidence |
|---|---|---|
| EXP-1 multi-dataset | **fail** | HotpotQA only (§4.2); MuSiQue and 2WikiMultiHop reserved for Stage-2 (§4.4 E5) |
| EXP-2 multi-seed | **fail** | §Limitations (4) admits "point estimates with n=200, multi-seed deferred to Stage-2" |
| EXP-3 significance test | **fail** | §4.3: "2.6 F1 points — non-trivial at n=200 but **not yet confirmed with paired statistics**" |
| EXP-4 effect size or CI | **fail** | Table 1 / Table 2 / Figure 2 all point estimates; no CI columns; no Cohen's d |
| **EXP-5 ablation coverage** | **pass** | Table 2 in body: 4 variants (canonical anchor / refreshed baseline / +evidence-window / −TCPB / −decomposer-gate); §4.5 also reports weight-sensitivity (±2× < 0.003pp) and static-path overlap (~52%); coverage_ratio ≈ 0.60 |
| EXP-6 baseline recency | **fail** | All baselines author-internal; AutoGen / MetaGPT / Multi-Agent Debate / ChatEval cited but not in Table 1 baseline list |
| EXP-7 sensitivity sweep | partial | §4.5 narrative ±2× weight sensitivity only; no sensitivity table in body |
| EXP-8 error analysis | partial | §4.5 static-path overlap quantitative + Finding 4 narrative; no per-method failure-mode breakdown table |

**Caps implied by audit**:
- EXP-1 fail (single benchmark): cap D4 at 6
- EXP-2 fail (single seed): cap D4 at 5 AND cap S5 at 4
- EXP-3 fail (no significance test): cap D4 at 6 AND cap S5 at 5
- EXP-6 fail (no recent SOTA, all author-internal): cap D4 at 5 AND cap S6 at 4
- experiments_solidity_score = 1 (≤ 3): **cap overall at 4.5** ← the binding constraint

## Novelty Delta Audit

12 named prior works, 1 with `is_overlap_risk=TRUE`:

| prior_work | year | concrete? | overlap_risk? |
|---|---:|---|---|
| AutoGen (Wu et al., 2024) | 2024 | ✅ | ❌ |
| MetaGPT (Hong et al., 2024) | 2024 | ✅ | ❌ |
| HuggingGPT (Shen et al., 2023) | 2023 | ✅ | ❌ |
| ChatDev / AgentVerse | 2024 | ✅ | ❌ |
| Reflexion / Self-Refine / ToT | 2023 | ✅ | ❌ |
| **Multi-Agent Debate (Liang et al., 2024) / ChatEval (Chan et al., 2024)** | 2024 | ✅ | **⚠ TRUE** |
| Galbraith / Mintzberg | 1973 / 1979 | ✅ (informing theory) | ❌ |

**Multi-Agent Debate overlap detail**: §2.2 says "Multi-Agent Debate (Liang et al., 2024; Du et al., 2024) and ChatEval (Chan et al., 2024) replace self-critique with explicit per-hop peer critique that a meta-reviewer aggregates. All these approaches assume that agents (or the aggregating reviewer) are at least moderately reliable judges of competence within a single turn." TCPB's "terminal-outcome only, no per-hop critique" is mechanistically a degenerate case of MAD's "per-hop critique aggregator with aggregator window = full trajectory". §2.2 partially addresses this overlap by claiming TCPB's use of *gold answer* (terminal F1) instead of *aggregator judgment* is a categorically different signal. But MAD is NOT in Table 1 baseline list, so this differentiation is asserted, not benchmarked. Per §2.5.2 hard rule: ≥3 named prior works with concrete deltas → no D3 cap. But the unaddressed-via-baseline overlap is the highest-priority experimental fix.

## Limitations Section Assessment

- `section_present`: ✅
- `section_title_exact`: ✅ ("Limitations")
- `contains_no_new_content`: **POSSIBLE VIOLATION** — item (5) Provider-side data-integrity event contains engineering implementation description (fail-fast integrity check, pre-send mode, endpoint switch) that arguably constitutes new content
- `honesty_score_1_to_5`: 4
- `specific_failure_modes_listed`: ✅
- **issues**:
  - Item (5) borderline DR-3 violation — engineering description of guard implementation should move to a separate Appendix or §3.x runtime section; Limitations (5) should be ≤ 1 sentence stating "cross-endpoint comparability is an open variable" only
  - No demographic / societal risks discussed (low risk for reading-comprehension scope, but should be stated explicitly per demand.md §6)
  - Item (3) backbone-sensitive prediction is now properly framed as "we conjecture; not validated by present submission; will be tested by Stage-2" — improvement noted

## Responsible NLP Checklist Assessment (Appendix A)

`appears_complete`: ✅ (B1 Scientific artifacts / B2 Computational experiments / B3 Human subjects / B4 AI assistants)

**Issues**:
- B2 compute budget is now order-of-magnitude PLUS wall-clock estimate (1-2 hours per chain-200 batch) PLUS USD cost ($0.50-$1.00 per chain-200 batch, ~35× for fullval) — significantly more concrete than minimum
- B3 "Not applicable" now properly states "no human evaluation of model outputs was conducted" — improvement noted
- Missing B5+ sections per latest ARR Responsible NLP Research Checklist (only B1-B4 present); B5 "Use of data containing PII" should be addressed even if "not applicable" (HotpotQA is Wikipedia-sourced, no PII)

## What to Fix for 8+ Overall (P2-priority order)

1. **Add MuSiQue as second benchmark** — already cited in §4.2/§4.4 E5 as Stage-2 reserved. Single change moves EXP-1 from fail to pass and unblocks D4 from the experiments_solidity_score floor. Lowest-cost / highest-impact for any 8+ aspiration.
2. **Multi-seed (≥3) + 95% bootstrap CIs + paired sign test in Table 1** — addresses EXP-2 / EXP-3 / EXP-4 simultaneously. The runtime is parallel (B2 confirms ~1-2h per chain-200 batch); 3 seeds × 3 methods = 9 runs ≈ 3-4 hours.
3. **Add ≥2 external multi-agent baselines (AutoGen + Multi-Agent Debate)** in Table 1. Multi-Agent Debate specifically is the only `is_overlap_risk=TRUE` prior work in the novelty audit; benchmarking it directly verifies TCPB's terminal-outcome advantage over per-hop critique aggregator. Without this comparison, the central novelty claim is asserted, not measured.
4. **Add equivalent Table 2 ablation on the gpt-4.1-mini canonical backbone** — currently Table 2 is glm-4-flash only. Cannot verify whether TCPB-on/off + gate-on/off behavior generalizes to the strong backbone where Finding 2's ordering inversion lives.
5. **Replace Figure 1 placeholder with finished vector PDF** — caption already specifies design (top: full sparse-graph + recursive audit ladder + 3-action policy; bottom: 4-node chain TCPB).
6. **Move Limitations item (5) engineering description into a separate Appendix B / §3.x** — Limitations (5) should be ≤ 1 sentence on cross-endpoint comparability; the fail-fast guard implementation belongs elsewhere to remove DR-3 POSSIBLE violation.

## What to Fix for Oral (top 3-5%)

7. **Implement at least one of (R1) split / (R2) audit / (R3) persona vector** and demonstrate empirical value. Without ANY Stage-2 mechanism running, the EDO contribution is a roadmap, not a paper-deliverable. **R2 audit is the highest-information experiment** — if audit allows upstream rejection of bad subcontracts, peer_calibrated could in principle outperform self_claim by catching errors self_claim cannot, directly reversing Finding 4.
8. **Show non-trivial improvement over an external 2024-2026 SOTA** — currently the proposed method LOSES to its own simplest variant. Even a tied result against Multi-Agent Debate would be substantially more credible than the current within-family Pareto comparison.
9. **Quantitative error analysis** with named failure modes per method (e.g., "X% of TCPB errors are extraction failures at evidence_seeker, Y% are aggregation failures at synthesizer") — current §4.5 static-path overlap and Finding 4 narrative are interpretive, not quantitative breakdowns.
10. **Seed-level organization stability** per §4.4 metric list — if EDO is about emergent specialization, the paper needs to show specialization is stable across seeds.
11. **Address Appendix A page-pressure** — currently Algorithm 1 is rendered as a full-page float on page 11, indicating layout pressure. Either trim §3.6/§3.7 narrative to fit Algorithm 1 inline, or split Algorithm 1 into Algorithm 1a (TCPB Stage-1 degenerate, in-line in §3.6) and Algorithm 1b (full EDO Stage-2, in Appendix).
12. **Community-impact case study** — currently impact is asserted (D2=5.0) not demonstrated.

## Recommended Next Actions (ordered by ROI)

1. **Lowest-cost / highest-impact**: add MuSiQue + multi-seed (≥3) + paired bootstrap CI in Table 1. This single sprint moves experiments_solidity_score from 1 to ~5, unblocking the §6 cap on overall.
2. **Second-lowest-cost**: move Limitations item (5) engineering description out of Limitations (DR-3 POSSIBLE fix, ~10 min writing).
3. **Stage-2 minimum viable**: implement R2 (recursive audit) — closest neighbor mechanism that could empirically reverse Finding 4. Algorithm 1 lines 16-23 already specify the AUDIT decision protocol.
4. **Add Multi-Agent Debate (Liang et al., 2024) as external baseline in Table 1** — directly addresses the only `is_overlap_risk=TRUE` prior work in the novelty audit.

## Implementation Risks

- External `edo_lite_executable_spec.md` is canonical impl spec for ϕ(z) extraction and utility instantiation — referenced 4+ times but not in paper body. Independent replication of TCPB's exact deterministic ϕ(z) extraction requires this supplement.
- Provider variability documented in Limitations (5); replicators on different providers may see different model behavior. The integrity-check guard described in Limitations (5) is mentioned but its exact threshold logic is not given.
- LLM_ANSWER, LLM_CONTRIBUTE, LLM_DECOMPOSE, AUDIT (when not default), EVIDENCE_EXTRACT prompt templates not in paper body — these substantially affect F1 and Stage-2 mechanism behavior.
- Single-seed runs make any reported metric a single-realization sample.
- fullval (n=7405): only peer_calibrated has valid full-validation point (F1=0.7703 reported); other two pending re-execution per Limitations (5). Full ranking cannot be reproduced from paper alone.

## Rule Source Disagreements

None observed. The reviewer prompt rubric is consistent with `docs/demand.md` as I have read it: 8-page main body (DR-1 ↔ demand.md §2), exact 'Limitations' title (DR-2 ↔ demand.md §2), no new content in Limitations (DR-3 ↔ demand.md §6), Responsible NLP Checklist (DR-6 ↔ demand.md §7), AI-assistance disclosure (DR-8 ↔ demand.md §6 + B4).

## Reviewer-Only Boundary Compliance (per `REVIEWER_TODO §F.1.4 / §F.1.5`)

- ✅ Did NOT modify `USER_TODO.md` / `SCIENTIST_TODO.md` / `PROJECT_STRUCTURE.md`
- ✅ Did NOT participate in §A decisions (this `recommended_next_actions` field is suggestion-only; decision authority remains with user)
- ✅ Did NOT read past reviews / scoreboard / fix_themes / SCIENTIST_TODO §C (stateless)
- ✅ Did NOT trigger S-104 (scientist's responsibility per §11.4)
- Will leave §F.4 1-line ack in `implementation_log.md` as the only allowed exception
- Temporary PDF text extraction (in system temp) deleted post-review per new §F.3
- This `review.md` is the only required product per new §F.3 (no `review.json` generated)
