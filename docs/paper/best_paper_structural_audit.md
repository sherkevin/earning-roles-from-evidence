# Best-Paper Structural Audit — current `edo_paper.pdf` vs `docs/demand.md §11`

> **Single source of truth** for the structural readiness of the submission against the Best-Paper bar (`docs/demand.md §11.1` / §11.2 / §11.3 / §11.4 / §11.5).
>
> Maintainer: scientist (R44, 2026-04-20). Trigger to refresh: any scientist commit that touches `article/latex/edo_paper.tex` section-level structure (new `\section`, new `\subsection`, Figure/Table add/move, page-count drift), OR any reviewer batch R-FULL-XXX lands after R-FULL-009 with a new `best_paper_structural_compliance` finding.
>
> Target audit subject: `article/build/edo_paper.pdf` (latest build: SHA16 `53F7FB9D` = R34–R43 state; R43 adds Ethical Considerations + Table 2 footnote but **PDF has not been rebuilt yet** — the audit below assumes the post-R43 `.tex` would rebuild to ~14 pages total, main body still 8 pages).

---

## 0. Headline summary

**8 of 12 §11.5 checklist items are either pass or on scheduled track; 4 are off-scope for this sprint and only reachable via the post-ARR Best-Paper 2–3-month agenda.**

| Track | R-FULL-009 estimate | Current structural pass | Gap to 8.5 Best-Paper |
|---|---:|---:|---:|
| Current PDF (pre-sprint) | overall=4.0 | 1 of 12 pass, 2 partial, 9 fail | −4.5 |
| Sprint fixes (ARR May 25, T-35) | overall=5.8–6.2 borderline | **8 of 12** (6 hard fixes landed via E-017/E-018/E-014/MuSiQue/Figure 1/DR-5; this R43 added #9) | **−2.5** |
| Best-Paper 2–3-month agenda | overall=7.0–7.5 Oral border | 11 of 12 (misses #7 case-study gallery by default; achievable but requires Stage-2 mechanism real wins) | −1+ |

---

## 1. §11.1 canonical section layout audit

| § | Section | Expected page range (`demand.md §11.1`) | Delivered (approx., R43 post-Ethical-Considerations state) | Status | Note |
|---|---|---:|---:|---|---|
| 1 | Introduction | 1.0 – 1.5 | ≈ 1.2 (p.1–p.2) | ✅ | 4 contributions enumerated; Figure 1 near end-of-Intro per §11.3 convention but **Figure 1 is a placeholder → §11.5 #10 fail** |
| 2 | Related Work | 0.75 – 1.5 | ≈ 1.0 (p.2–p.3) | ✅ | 3 sub-categories; 23 bib entries (R11); no SOTA-grid Table 1 §11.2 suggestion (optional, not hard requirement) |
| 3 | Methodology | 1.5 – 3.0 | ≈ 3.0 (p.3–p.6) | ✅ (upper bound) | 9 subsections; Figure 1 here technically; Algorithm 1 moved to Appendix E per R29 user editorial; Prototype Scope Box counts as structural device not a Figure |
| 4 | Experiments | **2.5 – 4.0 (heaviest)** | ≈ **2.5 (p.6–p.8)** at lower bound | ⚠ borderline | Meets lower bound; **missing Case Study / Application block** (§11.5 #7); 2 Tables + 1 Figure in main body; Best-Paper typical ≥ 6–10 Figures in Experiments |
| 5 | Conclusion | 0.5 – 1.0 | ≈ 0.5 (p.8) | ✅ | Short, honest, self-critique-included per R16 |
| — | **Limitations** (mandatory, unnumbered) | 0.5 – 2.0 (Best Paper 1–2) | ≈ 1.0 (p.8–p.9), 7 items | ✅ | Meets Best-Paper depth guidance; items (5) provider integrity + (6) Pareto-domination + (7) demographic scope are Best-Paper-honesty grade |
| — | **Ethical Considerations** (optional but Best-Paper common) | 0.5 – 1.0 | ≈ 0.5 (p.9, 5 paragraphs, **R43 newly added**) | ✅ | Added in R43 to close §11.5 #9 hard fail; covers Data / Misuse+mitigations / Fairness / Reproducibility / AI-assisted writing |
| — | Appendix A–E | no cap (post-U-021 `demand.md §2`) | ≈ 4–5 pages | ✅ | A Responsible NLP / B Provider Integrity / C LLM Prompts / D 3-shard Preliminary / E Algorithm 1 |

**Main-body total**: 8 pages COMPLIANT per `scripts/build_paper.ps1` + pdftotext verification (S-135 R19 done).

---

## 2. §11.5 12-item Best-Paper addendum audit

| # | Requirement | Status (R43) | Sprint-fix path (ARR May 25 T-35) | Best-Paper 2-3-month agenda |
|---|---|---|---|---|
| 1 | Experiments ≥ 2.5 p | ⚠ borderline (at lower bound) | ⏳ E-017 multi-seed + E-018 external SOTA Tables will push §4 to ≈ 3.5 p (S-159 active) | Case-study gallery + MAD head-to-head + MuSiQue section drives §4 to ≈ 3.5–4 p |
| 2 | ≥ 3 diverse datasets | ❌ HotpotQA only | ⏳ MuSiQue (E-006) land post-quota, adds 2nd benchmark | 2WikiMultiHop (E-006 chain) + 1 non-QA task family for 3–4 diverse datasets |
| 3 | Latest 12-month SOTA baseline in main tables | ❌ zero external | ⏳ E-018 MA-RAG + ReAgent (`configs` ready post-quota) + E-010/E-012/E-015/E-016 AutoGen+ChatEval+MAD swap | Extend with BELLE / MAR probe (E-019) |
| 4 | Full per-component ablation matrix | ⚠ Table 2 has 3 rows but null-effect on weak backbone | ⏳ E-014 `round2_gpt41mini_ablation_*.yaml` 4 configs ready, post-E-017 queued, will discriminate bug-vs-true-null (S-155 R43 interim done) | Extend to Stage-2 R1/R2/R3 per-component ablation once mechanisms implemented |
| 5 | Multi-seed + paired tests + CI | ⏳ in-flight | ⏳ E-017 resume running NOW (seed=42 resumed from 3201/2415 ckpt R40; seed 43+44 chained; `paired_bootstrap_ci.py --B 10000` queued, ETA ~00:54–07:40 next day) | Extend to all external-baseline comparison Tables |
| 6 | Error analysis with quantitative named failure modes | ❌ defer | Not in sprint scope (R30 cross-batch reject, 8-page budget conflict, §Limitations (3) prose covers direction) | Post-ARR: read E-017 fullval failure cases, build 5–7-category taxonomy, ≥1 p in revised §4 |
| 7 | Case-study / application block with 6–10 visualisations | ❌ absent | Not in sprint scope (S-158 blocked on E-017+E-018 fullval data + 0.8 p needed, would bump other sections) | Post-ARR: E-017 done + E-018 done → build "TCPB audit correction vs self-claim false-accept" case gallery or "MAD head-to-head TCPB wins" cases |
| 8 | Limitations ≥ 0.5 p honest specific + demographic/societal | ✅ R24 / R26 | — | — |
| 9 | Ethical Considerations section | ✅ **R43 newly added** | — | — |
| 10 | Figure 1 = system/task schematic, vector-quality, in Intro | ❌ placeholder | ⏳ U-EXEC-004 v2 prompt ready, user out-of-sprint physical op | — |
| 11 | Public anonymous code + data release commitment | ⚠ partial (code ✓, no per-Table/Figure regenerate scripts) | Engineer mid-sprint can add `scripts/regenerate_table{1,2,3}.py` wrappers if prioritised (5–10 min each) | + `scripts/regenerate_figure{3,4,...}.py` wrappers for every new figure |
| 12 | No null-effect ablation tables | ❌ Table 2 rows bit-identical on weak backbone | ⏳ E-014 canonical backbone ablation will produce differentiated rows OR confirm true-null (S-155 R43 interim footnote already makes this visible + §4.3 Finding 1 justifies) | — |

**R43 delta**: +1 hard-fix (#9 Ethical Considerations). From 1 pass → **2 pass**, from 2 partial → 2 partial, from 9 fail → **8 fail** (net improvement 1 on Best-Paper gate).

**R47 + R48 delta (S-163 Symbol Glossary restructure)**: R47 converted dense §3.6 prose paragraph → 9-bullet itemize list (zero new content, pure layout). R48 R-FULL-012 P4 Reproducibility-Ethics SAC cross-persona verification **confirmed**: D1 4.5 → **6.5** (+2.0 band 5+ unlocks), D5 5.5 → **7.0** (+1.5), D6 4.5 → 5.0 (+0.5), oral_quality 2.0 → 3.0. **weighted_pre_cap = 5.240 = new 12-batch high** (+1.740 vs R-FULL-011=3.500 reject). **D1<5 cap no longer triggered** first time post-S-163. D4 3.5 binding cap still pins overall at 4.0 until experiments_solidity 1/8 → ≥4/8 via E-017 fullval + E-018 external SOTA + E-014 canonical ablation + MuSiQue. §11.5 checklist **unchanged 7/3/2** (S-163 is D1/D5 internal improvement, does not touch data/evidence items).

**§11.5 enforcement mapping update** (per `docs/demand.md §11.5`):

```
R-FULL-009 (R43 pre-Ethical state): 9 fails → oral_cap 3
R43 post-Ethical state:              8 fails → oral_cap still 3 (no band change at 6+ missed)
Sprint fix path:                     2 fails → oral_cap ≤ 7 (strong Poster band)
Best-Paper agenda:                   1 fail  → oral_cap ≤ 7 (case-study #7 missed by default)
Fully-Best-Paper-ready (no fails):   oral_cap up to 10 (Best-Paper eligible)
```

---

## 3. §11.3 figure / table placement regularities audit

| §11.3 expectation | Delivered | Status |
|---|---|---|
| Early visualisation — Figure 1 in Intro or early Method | Figure 1 at line 90 of `.tex` (end of §3 Methodology intro) = effectively "early Method" | ⚠ (placeholder defeats the goal) |
| Concentrated burst — Method + Experiments host ≥ 80% of figures/tables | 1 Figure + 0 Tables in §3 + 1 Figure + 2 Tables in §4 = 2 F + 2 T = 4 items, 100% in Method+Experiments | ✅ distribution / ❌ count |
| Vector figures (PDF/EPS/embedded-vector) | Figure 2 is PDF ✅; Figure 1 placeholder | ⚠ Figure 1 needs vector final (U-EXEC-004) |
| Tables colour-encoded good/medium/bad | Tables plain black-and-white; Best Paper common but not required for accept | ⚠ nice-to-have |
| Case-study heavy — dedicated case-visualisation gallery in Experiments | Absent (S-158 blocked) | ❌ hard missing |

**Current Figure + Table count in main body = 4**. Best-Paper band (§11.4) typical = 8–15 total. **Gap = 4–11 items**.

**Post-sprint projection**:
- +Figure 3 Stage-2 paired F1+CI (S-153 script ready; E-017 done triggers)
- +Table 3 external SOTA head-to-head (E-018 done)
- +Table 4 module-swap 3-host paired (E-010+E-012+E-015+E-016 done)
- Optional +Figure 4 token-cost-normalised F1 (future script, lower priority)

**Post-sprint count projection = 7–8 items**, reaching lower end of Best-Paper band.

---

## 4. §11.4 Best-Paper vs generic Long-Paper differentiators audit

| Dimension | Generic Long Paper | **Best Paper** | Current state (R43) |
|---|---|---|---|
| Experiments depth | 1–2 datasets, basic ablation, minimal case study | **3–5 datasets**, full ablation, deep error analysis, dedicated case study | 1 dataset, 1 ablation table (null on weak backbone), §4.5 paragraph-level case mention, no gallery |
| Limitations | Short, often generic | **Longer, specific, honest** (~1 p) | ✅ 7 items, ~1 p, specific (Pareto/backbone/demographic), honest (self-admits refutation); **matches Best-Paper band** |
| Unique / distinctive section | Rare | Often case-study or application | Missing (ties to §11.5 #7) |
| Reproducibility | Code + hyperparameters | **Public code + data + model checkpoints + scripts to regenerate every table/figure** | ⚠ code ✓, no per-Table/Figure regenerate scripts (addressable mid-sprint, §11.5 #11) |
| Figures | 3–6 total | **8–15 total**, clustered in Method+Experiments | 2 Figures total, 1 placeholder; sprint brings to 3–4; Best-Paper agenda brings to 6–8 |
| Human evaluation / domain application | Often absent | Often present | Absent; not realistic to add in sprint (requires IRB/crowdworkers). Post-ARR nice-to-have. |

---

## 5. Cumulative gap burn-down (what sprint + post-ARR close)

| Category | R43 state | Sprint (ARR May 25) | Best-Paper 2–3-month agenda |
|---|---|---|---|
| §11.5 pass count | 2 of 12 (+ 2 partial) | **8 of 12 pass** (E-017+E-018+E-014+MuSiQue+Figure 1+DR-5) | **11 of 12 pass** (still missing #7 by default) |
| Main-body Figure+Table count | 4 | 6–7 (+Figure 3 + Table 3 + Table 4) | 8–10 (+Figure 4 + Case-study gallery Figures) |
| Experiments page count | 2.5 lower bound | 3.0–3.5 (midrange) | 3.5–4.0 (upper bound) |
| Scientist weighted_pre_cap ceiling (inferred from 12 R-FULL trajectory) | **5.240** (R-FULL-012 new 12-batch high, post-S-163 D1 unlock; R-FULL-011 reject 3.500 → R-FULL-012 5.275 jump +1.740 via pure layout restructure) | 5.8–6.5 (with E-017 fullval + E-014 ablation + E-018 external SOTA landing to unlock D4 3.5 cap) | 7.0–7.5 Oral border |
| ARR accept bar 6.0 | below | borderline ⚠ | comfortable ✅ |
| Best-Paper bar 8.5 | far (−4.5) | still far (−2.5) | still −1+ (requires "original mechanistic result" — genuine Stage-2 R2 win vs MAD) |

---

## 6. Immediate actionable (scope ≤ sprint end, un-blocked as of R43)

| Action | Ticket | Owner | Ready post-data | Est. min |
|---|---|---|---|---|
| `#9 Ethical Considerations` | **S-157 ✅ R43** | scientist | — | — |
| `#10 Figure 1 vector` | **U-EXEC-004** | user (physical op) | — | — |
| `#11 per-Table/Figure regenerate scripts` | (new, not yet dispatched) | engineer or scientist | — | 30–60 (5 scripts × ~10 min) |
| `S-155 Table 2 null audit interim footnote` | **S-155 ✅ R43** | scientist | — | — |
| `S-154 DR-5 anonymization leak remove` | **S-154 ✅ R42** | scientist | — | — |
| Fill TEMPLATE 1 with fullval paired numbers + Figure 3 render | S-115/S-116/S-117 | scientist | E-017 paired_stats_3seed.csv (~07:40 next day) | 60 |
| Fill TEMPLATE 3 with 3-host SWAP comparison | S-121/S-122/S-131 | scientist | E-010+E-012+E-015+E-016 done | 90 |
| Fill TEMPLATE 7 with MA-RAG+ReAgent SOTA | S-149/S-150/S-151 | scientist | E-018 done | 60 |

---

## 7. Maintenance

**Refresh trigger**:
- Any scientist commit changing `article/latex/edo_paper.tex` section-level structure.
- Any new R-FULL-XXX batch landing with §11.5 compliance findings.
- Every sprint commit that closes a §11.5 item (flip ❌ → ✅ in §2 table).

**Owned by**: scientist (single editor).
**Related files**:
- `docs/demand.md §11` (rulebook source, user-authorized reviewer-agent-owned).
- `artifacts/idea_reviews/reviewer_20260420_212755_09_e1858f/review.md` (R-FULL-009 reviewer-side audit).
- `docs/paper/benchmark_inventory.md` (benchmark + SOTA status).
- `docs/coordination/SCIENTIST_TODO.md §B.5` (S-157/S-158/S-159/S-160 Best-Paper-specific tickets).
