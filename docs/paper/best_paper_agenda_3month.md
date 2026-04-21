# Best-Paper 2–3 Month Agenda — EDO paper toward EMNLP / NeurIPS / ACL Oral + Best Paper

> **Status**: ACTIVATED 2026-04-21 R56, per user decision `U-023-decide = (b)` ("延期 2-3 个月冲击最佳论文"). Sprint ARR May 25 deadline deprecated.
>
> **Target bar**: overall ≥ 8.5, oral_quality_score ≥ 8.5 (top 3–5% of EMNLP/NeurIPS/ACL). Fallback bar if T-Best-3 (S-191) fails empirically: overall 7.0–7.5 comfortable Oral border.
>
> **Target timeline**: Month 1 = 2026-05-01 to 2026-05-31 (Stage-2 mechanism real impl + convergence/info-bound theorems). Month 2 = 2026-06-01 to 2026-06-30 (3+ diverse datasets × external SOTA full head-to-head + entropy theorem + MuSiQue + 2WikiMultiHop). Month 3 = 2026-07-01 to 2026-07-31 (case-study gallery + T-Best-3 provable advantage paper + final rebuttal-ready polish).
>
> **Target venue**: TBD by user (`U-EXEC-009` dispatched — options include EMNLP 2027 ARR December cycle / NeurIPS 2027 (not LLM-friendly?) / ACL 2027 / NAACL 2027 / COLM 2027).
>
> **Maintainer**: scientist (single editor). Refresh trigger: end of each Month's milestone.

---

## 0. Executive summary

Based on `docs/paper/theoretical_depth_audit.md` + `docs/paper/best_paper_structural_audit.md` + 17 R-FULL batches of reviewer feedback:

- **Current state (R55, post-S-173)**: overall 4.5 weak_reject. §11.5 7 hard + 3 partial + 2 pass. D1 = 6.5 under P4/P1 (Symbol Glossary + Appendix F theorems). D4 = 3.5–4.0 binding cap on overall.
- **Sprint fix path (ARR May 25)**: abandoned. Would have reached overall 6.0–6.5 borderline.
- **Best-Paper path (this doc)**: target 7.0–7.5 Oral border minimum; 8.5 Best Paper requires T-Best-3 novel-mechanism breakthrough.

---

## 1. Month 1 (2026-05-01 to 2026-05-31) — "Stage-2 mechanisms real, not theoretical"

### Milestone M1: Activate at least one of R1 / R2 / R3 in code + empirical win on ≥ 2 datasets

#### Engineer tickets

- **E-021 R1 split branch impl** (Medium): engineer activates `workspace/idea04_core/methods.py::edo_stage2_chain` with `SPLIT` gate weight lifted from $-\infty$ to learned threshold; `Decompose` LLM call wired into task-tree state. Builds on R1 split design in §3.9 H1 hypothesis. Expected effort: 5 days. Blocked on U-EXEC-008 quota recharge + engineer cycle.

- **E-022 R2 audit protocol impl** (High, critical for S-189/S-191): `workspace/idea04_core/audit_runtime.py` 4-class decision protocol (accept / reject+redo / reject+reroute / reject+resplit) landed earlier in scripts but not wired into `Runner.run()`. E-022 wires it in, with `AUDIT` decision threshold as a learned parameter. Expected effort: 5 days.

- **E-023 R3 vector belief update impl** (Medium, drives S-190): 7-axis belief vector $B_i^t(j) \in [0,1]^{7}$ updated via EMA per Algorithm 1 line 22–24 (not projected to scalar `c[i]` as in TCPB). Expected effort: 3 days.

- **E-024 Case-study extraction pipeline** (Medium, drives §4.x case-study gallery): scripted extraction of "TCPB audit correction vs self-claim false-accept" style trace pairs; output = 10 side-by-side visualisations. Expected effort: 3 days.

- **E-025 MuSiQue + 2WikiMultiHop fullval pipelines** (High, covers §11.5 #2 3+ datasets): adapts `run_e017_fullval_seed.py` for MuSiQue (already prep-seeded per `scripts/prep_musique_seed.py`) and 2WikiMultiHop. Expected effort: 5 days each = 10 days.

- **E-026 MAD / AutoGen / ChatEval / MA-RAG / ReAgent full head-to-head** (High, closes §11.5 #3 external SOTA): full fullval reproduce not smoke. Expected effort: 5 days.

#### Scientist tickets

- **S-189 (Active)** R2 audit Ω(H) information-theoretic lower bound — complete Month 1 (Appendix F.5 + main-body §3.4 cross-ref). Effort: 1 week derivation + review.

- **S-192** (new, Month 1) Update `theoretical_depth_audit.md` + `best_paper_structural_audit.md` to track Best-Paper path status. Effort: 2 days.

#### User decisions / todos

- **U-EXEC-008** (still pending): recharge newapi ≈ $300 (now also needs E-021..E-026 budget ≈ $400 = **recharge ≈ $700–1000** for full Month-1 budget).

- **U-EXEC-009** (new, dispatched): **decide target venue** (EMNLP 2027 / NeurIPS 2027 / ACL 2027 / NAACL 2027 / COLM 2027). Affects paper format (10-page vs 8-page body), bib style, submission deadline (each cycle differs). Recommend **COLM 2027** (NLP-friendly, accepts ≥ 15-page format, paper-quality > venue) OR **NAACL 2027** (ARR cycle matches our sprint).

### Month 1 deliverables

- edo_paper.tex with at least one of R1/R2/R3 activated in §4 Experiments table
- ≥ 2 datasets in main results tables (HotpotQA + MuSiQue confirmed; 2WikiMultiHop aspirational)
- S-189 theorem in Appendix F.5
- Engineer E-021/E-022/E-023 merged

---

## 2. Month 2 (2026-06-01 to 2026-06-30) — "3+ diverse datasets + external SOTA full head-to-head"

### Milestone M2: 3+ diverse benchmarks + AutoGen/ChatEval/MAD/MA-RAG/ReAgent in main results Table 1

#### Engineer tickets

- **E-027** Non-QA task family exploration — e.g. arithmetic reasoning (GSM8K), code execution (MBPP), or multi-step agentic task (WebShop). Activates §11.4 "Best Papers often have dedicated application / case-study section" expectation. Effort: 5 days.

- **E-028** Cross-benchmark scaling study — for each of HotpotQA / MuSiQue / 2WikiMultiHop / (chosen non-QA), report effect of Stage-2 R1/R2/R3 individually + combined. Yields 4 × 4 = 16 ablation cells. Effort: 5 days.

- **E-029** Paired-bootstrap CI + effect-size across all benchmarks (re-use `scripts/paired_bootstrap_ci.py`). Effort: 1 day.

#### Scientist tickets

- **S-190 (Active)** Emergent-specialization entropy theorem — complete Month 2. Requires R3 vector belief impl done (E-023) + Lyapunov derivation + empirical axis-specialization entropy curves from multi-seed runs. Effort: 2 weeks.

- **S-193** (new, Month 2) Case-study gallery Section §4.x writing — 6–10 visualisations with captions. Builds on E-024 + E-028.

- **S-194** (new, Month 2) Figure 2 + Figure 3 + Figure 4 rebuild with full 3+ datasets data.

### Month 2 deliverables

- Main result Table 1 = 3+ datasets × 5+ methods (our TCPB, our EDO Stage-2, MAD, AutoGen GroupChat, MA-RAG, ReAgent, ChatEval)
- §4.x Case Study section with 6–10 figures
- Appendix F.6 emergent-specialization entropy theorem

---

## 3. Month 3 (2026-07-01 to 2026-07-31) — "T-Best-3 novel mechanism paper, final polish"

### Milestone M3: Ship S-191 T-Best-3 + final rebuttal-ready polish

#### Scientist tickets (highest-impact single-person work)

- **S-191 (CRITICAL, Active) — Original novel mechanism with provable advantage vs MAD / AutoGen / MA-RAG**: 
  * Derivation: R2 recursive audit is provably more sample-efficient than MAD debate for credit-assignment in H-hop QA by factor Ω(H), provided audit decisions are ≥ 1/2+ε accurate.
  * Empirical verification: hold 4 external systems fixed, swap R2 audit into each, measure sample-efficiency on paired-multi-seed multi-hop tasks.
  * Output: main body §3.10 "Mechanism-level advantage theorem" + Appendix F.7 proof + §4.x Table 6 empirical verification.
  * **This is the single highest-risk / highest-reward ticket in the entire project.** If T-Best-3 proves + empirically verifies cleanly, overall lifts to 8.0–8.5 band. If it fails (e.g. empirical effect is only Ω(log H) not Ω(H), or the theorem requires stronger assumptions), fallback is "quantifiably compared and ruled out" which still clears Oral border 7.0–7.5.
  * Effort: 3–4 weeks writing + simulation validation.

- **S-195** (new, Month 3) Final figure redesigns: Figure 1 vector + any remaining placeholders closed.

- **S-196** (new, Month 3) Responsible NLP Checklist + Ethical Considerations full rewrite to Best-Paper depth (currently 5-paragraph but can expand to 1-page Best-Paper typical).

- **S-197** (new, Month 3) Rebuttal-ready polish: re-run all reviewer-visible checks (DR-1/DR-2/DR-3/DR-4/DR-5/DR-6/DR-7/DR-8 + §11.5 12-item), + overfull/underfull hbox cleanup (expected 0 overfull post-compression + 0 underfull ≥ 10pt).

#### User decisions / todos

- **U-EXEC-010** (new, Month 3): final pre-submission LaTeX check — user reads full pdf + checks anonymization + gives green-light for submission.

- **U-EXEC-011** (new, Month 3): submission itself (OpenReview / target-venue upload).

### Month 3 deliverables

- §3.10 + Appendix F.7 T-Best-3 theorem + proof
- §4.x Table 6 empirical verification
- Final rebuttal-ready PDF at ≥ 7.0 overall projected
- Submission to target venue via OpenReview

---

## 4. Risk register

| Risk | Mitigation |
|---|---|
| U-EXEC-008 recharge delayed → Month 1 slips | Scientist does S-189 theorem derivation (non-quota) first; engineer preps MuSiQue data-only prep (already done). |
| E-022 R2 audit impl hits integration bug | Fall back to R1 split or R3 vector belief as Month-1 win. |
| T-Best-3 (S-191) fails empirically | Rename "provable advantage" → "empirical advantage with complexity bound"; drop Best Paper 8.5 target, keep Oral 7.0–7.5. |
| Target venue unclear (U-EXEC-009 pending) | Default to NAACL 2027 ARR December cycle. |
| User pulls timeline short (e.g. reverses back to May 25) | Revert S-189/S-190/S-191 to blocked; re-activate ARR sprint path per R46 U-023 (a). |

---

## 5. 17-batch reviewer evidence that Best-Paper is reachable

Weighted_pre_cap trajectory:
```
5.925 → 5.905 → 4.985 → 4.910 → 4.560 → 4.725 → 5.105 → 4.940 → 4.765
→ 4.975 → 3.500 → 5.240 → 5.100 → 5.495 → 5.580 → 5.490 → 5.350
```

- Last 3 batches ≥ 5.3 under strictest personas (R-FULL-015 P4 / R-FULL-016 P1 Strict ARR / R-FULL-017 P5 BPC)
- D1 4.5 sub-5 cap CLOSED under P1 Strict via S-163/S-164/S-173
- D4 ≈ 3.5–4.0 binding cap until experiments_solidity ≥ 4/8 (= 4 of 8 EXP checks pass)
- Currently EXP-7 partial pass only; need EXP-1/2/3/4/6 to pass (multi-dataset / multi-seed / paired test / CI / external SOTA)

All Best-Paper fix items are either Month-1 blocked-on-quota-and-engineer-time or Month-3 scientist-solo-high-risk. Roughly linear progress expected.

---

## 6. Maintenance

**Refresh trigger**:
- End of Month 1 / Month 2 / Month 3 milestones — update §1/§2/§3 status with actuals.
- Any new reviewer batch R-FULL-018+ — update §5 trajectory line.
- Any user decision that changes venue / timeline / U-023 stance.

**Owned by**: scientist (single editor).

**Related files**:
- `docs/paper/theoretical_depth_audit.md` — source of T-1..T-6 sprint-scope + T-Best-1..T-Best-3 Best-Paper-track.
- `docs/paper/best_paper_structural_audit.md` — §11.5 12-item checklist tracking.
- `docs/paper/benchmark_inventory.md` — datasets + backbone + baselines authority.
- `docs/paper/sota_baseline_survey_2026.md` — external baseline survey (U-022 Tier-1).
- `docs/coordination/SCIENTIST_TODO.md §B.5` — S-189/S-190/S-191 (active post-U-023=(b)) + S-192/S-193/S-194/S-195/S-196/S-197.
- `docs/coordination/USER_TODO.md §A` — U-023 (approved_b R56) + U-EXEC-008/009/010/011.
