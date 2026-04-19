# Review of `article/build/edo_paper.pdf` (R-FULL-002)

- reviewer_id: `reviewer_20260419_185701_02_12b911`
- reviewer_profile: P3 (Adversarial Novelty SAC — Novelty + Significance focus)
- model: human/agent (Cursor session, no remote LLM call)
- target: `article/build/edo_paper.pdf` (348.4 KB / 11 pages, pdftotext extraction at `_edo_paper_text_for_review_v2.txt`)
- document_type: `full_paper`
- verdict: **`weak_reject`**
- confidence: `3` (PDF text only — layout-dependent checks blocked)
- is_8_plus_ready: `false`
- oral_eligible: `false`
- estimated_score_after_fixes: `6.5`

## Scores

| dim | score | notes |
|---|---:|---|
| D1 soundness | 6.0 | Algorithm 1 fully specified for TCPB; full EDO Fit / λ / η / ν undefined |
| D2 significance | 5.0 | Reframing valuable; Finding 1 admits backbone dominates |
| D3 novelty | 5.5 | 12 named prior works + concrete deltas; Multi-Agent Debate is_overlap_risk |
| D4 empirical_results | 5.0 | Single benchmark + single seed + no significance test (Limitations admits) |
| D5 reproducibility | 7.5 | Algorithm 1 + Appendix B Checklist + anonymous code supplement |
| D6 clarity | 7.5 | Algorithm 1 + Figure 2 + Prototype Scope Box; Figure 1 placeholder only |
| D7 limitations | 7.5 | 4 concrete scope limits + Appendix B + 'Limitations' title exact |
| S1 executability | 6.0 | TCPB executable from Alg 1; full EDO needs supplement |
| S2 falsifiability | 6.0 | Headline claim falsifiable AND already falsified by Finding 4 (intellectually honest) |
| S3 empirical_plan | 6.5 | §4.4 E1-E5 well-designed Stage-2 agenda |
| S4 technical_clarity | 6.5 | Equations clear; multiple symbols undefined for full EDO |
| S5 statistical_rigor | 3.0 | No CI / no paired test / no multi-seed (admits deferred) |
| S6 baseline_quality | 3.0 | All baselines author-internal; AutoGen/MetaGPT/MAD cited but not benchmarked |
| S7 ablation_completeness | 6.0 | Table 2 ablation in body (improvement vs prior) |
| S8 writing_and_figures | 6.5 | Algorithm 1 + Figure 2 ✓; Figure 1 placeholder ⚠ |
| **oral_quality_score** | **4.0** | "Weak reject; clear path to acceptance after major revision" |
| **overall** | **4.5** | weighted_sum=5.925; capped by experiments_solidity_score=1/8 |

## Score Calculation

```
weighted_sum = 0.25*6.0 + 0.18*5.0 + 0.15*5.5 + 0.18*5.0 + 0.10*7.5 + 0.07*7.5 + 0.07*7.5
             = 1.500 + 0.900 + 0.825 + 0.900 + 0.750 + 0.525 + 0.525
             = 5.925

caps_triggered:
  - experiments_solidity_score = 1 (only EXP-5 strict pass): cap overall to 4.5
    (per §6 hard rule: results-not-solid floor)
  - D4<7 cap to 7.0: not binding
  - oral_quality_score<5 cap to 5.5: not binding (already 4.5)
  - S6<5 cap to 6.0: not binding (already 4.5)

final_overall = 4.5  →  verdict = weak_reject  (overall in [4.0, 5.5))
```

**Note**: `weighted_sum=5.925` is +1.07 (+22%) higher than would be achieved with the rubric on a less-developed manuscript (e.g., a manuscript without Algorithm 1, without Table 2 ablation, without 12-name bibliography). However, the §6 experiments_solidity floor caps `overall` at 4.5 because EXP-1/2/3/4/6 still fail. This is by design — the rubric prevents `overall` from rewarding well-written but empirically thin papers.

## Reference Documents Consulted

- `docs/demand.md` loaded: `true`
- `article/build/edo_paper.pdf` loaded as PDF: `false` — used pdftotext extraction
- Layout-dependent checks blocked:
  - DR-1 precise main-body page boundary (§5 Conclusion appears to bleed to page 9)
  - DR-1 Appendix A page placement (Appendix A is engineering provenance, NEITHER Limitations NOR References NOR Ethical Considerations — strict reading of demand.md §2 may count it toward 8-page main body)
  - DR-4 template tampering (cannot confirm from text)
  - D6 Figure 1 quality (admittedly a placeholder per its own caption)
  - D6 Figure 2 visual quality

## Summary

EDO reframes decentralized multi-agent routing as 'organizational emergence' under local interaction. The full method (recursive split + audit + persona vector) is admitted not implemented; the delivered system is the Stage-1 TCPB prototype evaluated on a single benchmark (HotpotQA n=200, single seed, no significance tests, baselines = 4 author-internal routing variants). The paper is unusually honest: it explicitly admits via §4.3 Finding 4 that the proposed method (peer_calibrated F1=0.7381) is Pareto-dominated by the simplest baseline (self_claim F1=0.7641) at equal token cost, and §Limitations enumerates 4 concrete scope limits. Algorithm 1 box, Table 2 ablation, Figure 2 backbone-sensitivity chart, and 12 named prior works in Related Work are all rendered in the PDF. Headline empirical claim remains under-supported; the submission's value lives in the framework + roadmap, not in measured wins.

## Top Strengths

1. **Unusually honest scoping**: §3.6 (TCPB), §3.7 (separation rationale), §3.8 (Stage-2 R1/R2/R3 boundaries), Prototype Scope Box, and §Limitations (4 concrete scope limits) form a self-consistent honesty boundary. Reviewers rarely see this level of self-awareness about what is/isn't delivered.
2. **Algorithm 1 fully specified**: TCPB execution loop with all hyperparameters (Hmax=4, FTH=0.5, ∆+=+0.06, ∆-=-0.10, ρ=0.5, δa=0.02) — TCPB-only is reproducible from the paper alone.
3. **12 named prior works in Related Work** with concrete mechanistic deltas (AutoGen / MetaGPT / HuggingGPT / ChatDev / AgentVerse / Reflexion / ToT / Self-Refine / Multi-Agent Debate / ChatEval / Galbraith / Mintzberg) — far exceeds typical 'orchestrator-based frameworks' generic referencing.
4. **Table 2 mechanism ablations** (TCPB on/off, gate on/off, evidence window) are IN paper body, not externalized — directly supports the claim that TCPB and gate contributions are isolable.

## Top Weaknesses (ordered by severity)

1. **FATAL** — Headline empirical claim self-falsified: §4.3 Finding 4 admits 'peer_calibrated uses the same token budget as self_claim (both 6,414/sample) but achieves lower F1' — proposed TCPB Pareto-dominated by simplest baseline. Paper acknowledges the pivot but the empirical pivot is theoretical, not demonstrated.
2. **FATAL** — Single-benchmark / single-seed / no-significance-test configuration: experiments_solidity_score = 1/8 (only EXP-5 ablation passes). Per §6 hard rule this caps overall at 4.5 regardless of how strong other dimensions are.
3. **FATAL** — All Table 1 baselines are author-internal routing variants — zero external multi-agent system from 2024-2026 (AutoGen / MetaGPT / Multi-Agent Debate / ChatEval are CITED but NOT benchmarked). Closest neighbor Multi-Agent Debate is is_overlap_risk=TRUE; benchmarking it would be the most direct way to verify TCPB's terminal-outcome advantage over per-hop critique aggregator.
4. Stage-2 mechanisms (split / recursive audit / persona vector) — i.e. the actual EDO theoretical contribution — are explicitly NOT IMPLEMENTED (§3.8 R1/R2/R3). Per ARR's 'completed work' clause, an EDO claim cannot be evaluated from this submission; only TCPB can.
5. Figure 1 is a placeholder (caption explicitly says '[Figure 1 placeholder] Vector asset to be inserted'); D6 cannot verify final figure quality.
6. Page-limit risk: §5 Conclusion appears to bleed to page 9 per pdftotext layout, AND Appendix A 'Provider-side data integrity event' is on page 9 but is NEITHER Limitations NOR References NOR Ethical Considerations — strict reading of demand.md §2 may count Appendix A toward 8-page main body.

## Desk-Reject Risks

- **DR-1 (POSSIBLE)** — main body 8-page limit: §5 Conclusion bleeds + Appendix A NOT on excluded list per strict demand.md §2 reading
- **DR-2: PASS** — 'Limitations' title exact
- **DR-3: PASS** — Limitations contains no new methods/tables/figures
- **DR-4** — cannot confirm from text only
- **DR-5: PASS** — anonymization explicit and consistent ('anonymous code supplement', 'Anonymous Suppl.')
- **DR-6: PASS** — Appendix B Responsible NLP Checklist B1-B4 present
- **DR-7: NA**
- **DR-8: PASS** — B4 discloses AI-assistant use; B1 discloses license/intent; citations resolve to plausible real papers

## Experiments Solidity Audit (score = 1 / 8)

| check | status | evidence |
|---|---|---|
| EXP-1 multi-dataset | fail | HotpotQA only; MuSiQue / 2WikiMultiHop reserved for Stage-2 (§4.4 E5) |
| EXP-2 multi-seed | fail | §Limitations (4) admits 'point estimates with n=200, multi-seed deferred' |
| EXP-3 significance test | fail | §4.3: '2.6 F1 points — non-trivial at n=200 but not yet confirmed with paired statistics' |
| EXP-4 effect size or CI | fail | Table 1/2 point estimates only; no CI columns |
| **EXP-5 ablation coverage** | **pass** | Table 2 in body: 4 variants (canonical/baseline/+evidence/−TCPB/−gate); coverage_ratio=0.60 |
| EXP-6 baseline recency | fail | All Table 1 baselines author-internal; AutoGen/MetaGPT/MAD/ChatEval cited but not benchmarked |
| EXP-7 sensitivity sweep | partial | §4.5 narrative ±2× weight sensitivity; no sensitivity table |
| EXP-8 error analysis | partial | §4.5 static-path overlap quantitative; rest interpretive |

## Novelty Delta Audit (12 named prior works; 1 is_overlap_risk)

| prior_work | year | concrete? | overlap_risk? |
|---|---:|---|---|
| AutoGen (Wu et al., 2024) | 2024 | ✅ | ❌ |
| MetaGPT (Hong et al., 2024) | 2024 | ✅ | ❌ |
| HuggingGPT (Shen et al., 2023) | 2023 | ✅ | ❌ |
| ChatDev / AgentVerse | 2024 | ✅ | ❌ |
| Reflexion / Self-Refine / ToT | 2023 | ✅ | ❌ |
| **Multi-Agent Debate (Liang et al., 2024) / ChatEval (Chan et al., 2024)** | 2024 | ✅ | **⚠ TRUE** — TCPB's 'terminal-outcome only' is essentially a degenerate case of MAD's per-hop critique aggregator with aggregator window = full trajectory. Partially addressed in §2.2 but Multi-Agent Debate is NOT in Table 1 baseline list. |
| Galbraith / Mintzberg | 1973–1979 | ✅ (informing theory, not NLP system) | ❌ |

**Per §2.5.2 hard rule**: ≥3 named prior works with concrete deltas → no D3 cap. But the one is_overlap_risk=TRUE prior (Multi-Agent Debate) is partially-addressed-in-text, not benchmarked — minor cap risk.

## Limitations Section Assessment

- section_present: ✅
- section_title_exact: ✅ ('Limitations')
- contains_no_new_content: ✅
- honesty: 4/5
- specific_failure_modes_listed: ✅
- issues:
  - Does not acknowledge Finding 4 self-falsification as a delivered-system limitation (only frames it as future-Stage-2 motivation)
  - No demographic/societal risks discussed (low risk for this scope, but should be stated)
  - Limitation (3) backbone-sensitive prediction reads as 'confirmed' rather than 'we conjecture; Stage-2 will test'

## Responsible NLP Checklist Assessment

Appendix B includes B1 (Scientific artifacts) / B2 (Computational experiments) / B3 (Human subjects) / B4 (AI assistants).

Issues:
- B2 compute budget is order-of-magnitude only (≤10⁴ API calls); missing wall-clock + USD cost
- B3 'Not applicable' should also state 'no human evaluation of model outputs'
- Missing B5+ sections per latest ARR Checklist (only B1-B4 present)

## What to Fix for 8+ Overall

1. **Add MuSiQue as second benchmark** — already cited in §4.2/§4.4 E5; lowest-cost path to EXP-1 pass and unblocks D4 from experiments_solidity floor.
2. **Multi-seed (≥3) + 95% bootstrap CIs + paired sign test in Table 1** — addresses EXP-2/3/4 simultaneously.
3. **Add ≥2 external multi-agent baselines (AutoGen + Multi-Agent Debate)** — Multi-Agent Debate is is_overlap_risk=TRUE; benchmarking it directly verifies TCPB's terminal-outcome advantage over per-hop critique aggregator.
4. **Add equivalent Table 2 ablation on gpt-4.1-mini canonical backbone** — currently glm-4-flash only; cannot verify TCPB-on/off generalizes to strong backbone where Finding 2 inversion lives.
5. **Replace Figure 1 placeholder with finished vector PDF** — caption already specifies design; just needs rendering.
6. **Re-phrase Conclusion + Abstract** to honestly attribute Stage-2 mechanisms as 'proposed' rather than 'delivered' (3 overclaim items, ~30 min writing).

## What to Fix for Oral (top 3-5%)

7. **Implement at least one of (R1) split / (R2) audit / (R3) persona vector** and demonstrate empirical value. Without ANY Stage-2 mechanism running, EDO contribution is a roadmap, not a paper-deliverable. **R2 audit recommended** as the closest neighbor mechanism that could empirically reverse Finding 4.
8. **Show non-trivial improvement over external 2024-2026 SOTA** — currently proposed method LOSES to its own simplest variant.
9. **Quantitative error analysis** with named failure modes per method.
10. **Seed-level organization stability** per §4.4 metric list.
11. **Address Appendix A page-limit risk** — move Provider-side data integrity content into Limitations or Ethical Considerations (both excluded from page count).
12. **Community-impact case study** — currently impact is asserted (D2=5.0) not demonstrated.

## Recommended Next Actions (ordered by ROI)

1. **Lowest-cost / highest-impact**: add MuSiQue + multi-seed + paired bootstrap CI in Table 1. This single sprint moves experiments_solidity_score from 1 to ~5, unblocking the §6 cap on overall.
2. **Second-lowest-cost**: re-phrase Abstract + Conclusion to honestly attribute Stage-2 mechanisms as 'proposed' (~30 min writing).
3. **Stage-2 minimum viable**: implement R2 (recursive audit) — closest neighbor mechanism that could empirically reverse Finding 4. If audit allows upstream rejection of bad subcontracts, peer_calibrated could in principle outperform self_claim by catching errors self_claim cannot. **This is the highest-information experiment** for EDO's claimed advantage.
4. Add Multi-Agent Debate (Liang et al., 2024) as external baseline in Table 1 — directly addresses the only is_overlap_risk=TRUE prior work.

## Implementation Risks

- External `edo_lite_executable_spec.md` is canonical impl spec for ϕ(z) extraction and utility instantiation — referenced 4+ times but not in paper body
- Provider variability: Appendix A documents one provider-side model-substitution incident; replicators on different providers may see different model behavior
- Single-seed runs make any reported metric a single-realization sample
- fullval (n=7405): only peer_calibrated has valid full-validation point (F1=0.7703); other two pending re-execution per Appendix A — full ranking cannot be reproduced from paper alone

## Rule Source Disagreements

Minor ambiguity (NOT a disagreement): demand.md §2 says 'main body only; references, Limitations, and Ethical Considerations do not count toward this limit'. Appendix A 'Provider-side data integrity event' is NEITHER Limitations NOR References NOR Ethical Considerations. Strict reading: Appendix A counts toward the 8-page main-body limit. Permissive reading: 'Appendix' is a catch-all category that does not count. Reviewer applied strict reading (DR-1 POSSIBLE). Authors should clarify with PC chairs OR move integrity content into Limitations / Ethical Considerations to be safe.
