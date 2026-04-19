# Page Budget Audit (S-011)

> Audit date: 2026-04-19
> Source manuscript: `docs/paper/EMNLP_paper_draft.md` (EDO portion = lines 1–257; short-paper duplicate L258–365 ignored — pending U-003 merge)
> Target: EMNLP Long Paper, **strict 8 content pages** main body (Limitations + References do **not** count). See `docs/demand.md §2 / §5`.

---

## 1. Methodology

* Word count obtained via the Python script logged at the bottom of this file (separates duplicate sections by line ranges so collisions don't double-count).
* Page conversion uses an ACL 2-column 11 pt **conservative** density:
  * Pure prose: **~600 words / page**
  * Math-heavy: **~450 words / page** (equations consume ~30% extra vertical space)
  * Sections with embedded figures / tables: subtract figure footprint from the prose budget
* Figure / Algorithm footprint estimates (ACL 2-col, single-column width):
  * Algorithm 1 box (½ page target): **0.45 page**
  * Figure 1 (3-action policy schematic, single column): **0.30 page**
  * Figure 2 (backbone-sensitivity bar chart, single column): **0.30 page**
  * Main results table (`fixed_*` × {EM, F1, PAR, MHC, cost}, single column): **0.25 page**

---

## 2. Section-by-section: word count, current page estimate, target, gap

| § | Section | Words | Equations | Figs/Tables planned | Current pages (est.) | Target (demand.md §5) | Gap |
|---|---|---:|---:|:---|---:|---:|---:|
| — | Title + Abstract | 230 | 0 | none | 0.40 | 0.50 | **−0.10** (room) |
| 1 | Introduction | 779 | 0 | none | 1.30 | 1.00–1.50 | within band |
| 2 | Related Work | 303 | 0 | none | 0.50 | 0.75–1.50 | **−0.25** (room) |
| 3 | Methodology (3.1–3.9 + Prototype Scope Box) | 1525 | ≈12 | Algorithm 1 (S-003) | 3.40 + 0.45 = **3.85** | 2.00–3.00 | **+0.85** ⚠ |
| 4 | Experiments (4.1–4.6) | 1165 | 0 | Fig 1 + Fig 2 + Table | 2.00 + 0.85 = **2.85** | 2.50–3.50 | within band |
| 5 | **Limitations** (NOT counted) | 342 | 0 | none | 0.60 | 0.50–1.00 | within band |
| 6 | Conclusion | 168 | 0 | none | 0.30 | 0.50 | **−0.20** (room) |

**Main body subtotal (excludes Limitations + References)**:
* Current pages (no figures yet): 4512 words → ≈ **8.35 pages** (already 0.35 over the 8-page strict limit)
* After S-003 Algorithm 1 + S-006 Figs 1/2 + main results Table (planned additions ≈ 1.30 pages):
  → projected **≈ 9.65 pages** — **+1.65 pages over the 8-page hard limit** ⚠

---

## 3. Diagnosis

The biggest single-source overrun is **§3 Methodology (+0.85 page over upper-band target)**. Three contributing factors:

1. **§3.1–§3.6 (theoretical EDO body)** is fully written for the long-paper framing, with 12 equations including persona update, three-utility action selector, recursive audit signal, and Stage-2 belief update. This is necessary content; cutting equations reduces method clarity.
2. **§3.7 (TCPB prototype) + §3.8 (separation rationale) + Prototype Scope Box** together restate the same five substitutions (i)–(v) twice — once narratively in §3.7 and again as the canonical box. The single-source-of-truth refactor (S-004) reduced this to one canonical list, but §3.7 still re-introduces TCPB conceptually before deferring to the box.
3. **§3.9 Stage-2 Roadmap (R1/R2/R3)** is recently added (S-007) and contributes ~280 words by itself with one displayed equation. This block is fully content-bearing (it answers Session-6 reviewer feedback) but has clear compression headroom by inlining the (R1)/(R2)/(R3) sub-bullets.

**Other adjustments / reserves**:
* §1 Introduction sits at the top of its 1.0–1.5 page band; trimming 100–150 words is realistic without losing the contribution statement.
* §2 Related Work and §6 Conclusion are *both* under the lower band — but ARR reviewers do not penalize a tight Related Work, and conclusions deliberately stay short, so we should NOT use these as "compression slack" to grow §3 further.
* Math-heavy density factor (~450 wpp for §3) means each 100 words removed gives back ~0.22 page. To recover 1.65 pages, we must remove ~750 words OR equivalently ~6 equations OR a combination.

---

## 4. Concrete compression plan (no decisions required)

| Action | Source | Words removed | Pages recovered |
|---|---|---:|---:|
| C-1: Inline §3.9 (R1/R2/R3) sub-headers; collapse the three bold paragraphs into a single "Stage-2 substitutions remaining" paragraph + 1 inline equation (drop 2 equations) | §3.9 | 180 | 0.40 |
| C-2: Drop §3.7 narrative restatement of TCPB substitutions; replace with a 1-sentence pointer to the Prototype Scope Box | §3.7 | 90 | 0.20 |
| C-3: Trim §3.6 persona update derivation: keep equation + 1 explanatory sentence; remove the meta-paragraph "These produce persona tags that are neither pure self-estimates nor pure global scores…" | §3.6 | 70 | 0.16 |
| C-4: Trim §3.5 recursive audit prose: collapse the worked example "If $a → b → c$…" into a parenthetical | §3.5 | 50 | 0.11 |
| C-5: Trim §1 Introduction: collapse paragraphs 4 + 5 (the EDO motivation and contribution lead-in) into one tighter paragraph | §1 | 130 | 0.22 |
| C-6: Move the Prototype Scope Box content into a properly typeset `\fbox{...}` of ≤8 lines (currently 9 lines + lead-in paragraph) | §3 box | 70 | 0.16 |
| **TOTAL projected savings** | | **~590** | **~1.25 pages** |

After applying C-1..C-6:
* Estimated main body: 9.65 − 1.25 = **~8.40 pages** (still ~0.40 page over). Remaining options:
  * (a) Use **vertical tightening** in §3 equations (`\vspace{-2pt}` between displayed equations is compliant, used widely)
  * (b) Use the camera-ready +1 extra page (paper still has to fit 8 at submission → option (a) preferred for submission, defer (b) to camera-ready)
  * (c) Move R1/R2/R3 of §3.9 to **Appendix**, leaving a 1-paragraph forward reference in §3 — saves additional ~0.40 page

**Minimum compliant plan**: C-1 + C-2 + C-3 + C-5 + C-6 + (option-c moving §3.9 R1/R2/R3 to appendix) → recovers ~1.65 pages → projected exactly 8.0 pages. Algorithm 1 + Fig 1 + Fig 2 + Table all retained in main body.

---

## 5. Concrete dependencies before any cut is applied

| Cut | Depends on | Status |
|---|---|---|
| C-1 (inline §3.9) | None — can be done now | ✅ unblocked |
| C-2 (drop §3.7 narrative) | Verify Prototype Scope Box is the canonical reference (S-004 ✅) | ✅ unblocked |
| C-3 (trim §3.6) | None | ✅ unblocked |
| C-4 (trim §3.5) | None | ✅ unblocked |
| C-5 (trim §1) | Verify contribution statement remains explicit (`bold` per `demand.md §5`) | ✅ unblocked |
| C-6 (typeset Box) | Requires LaTeX migration first (S-013) | ⏳ blocked by U-009 / S-013 |
| Option-c (move §3.9 to Appendix) | Should be confirmed as post-merge cleanup | ⏳ blocked by U-003 (single-draft merge) |

---

## 6. Recommended next-action order (not yet executed; this is the audit deliverable)

1. **Wait for U-003 + U-009 + U-010 decisions** before any irreversible cut, because the merge will reshuffle line numbers and the LaTeX migration will change typesetting density (current Markdown estimates have ±0.3 page error bar).
2. After U-003 merge: re-run this audit on the merged single-source draft (re-run the Python word counter at bottom of this file).
3. After LaTeX migration (S-013): use `texcount` + `pdfinfo` to replace word-based estimates with **actual PDF page count**, which is the only number that matters for desk-reject.
4. Apply C-1 → C-5 → C-3 → C-4 → C-2 in that order (minimum-disruption priority).
5. If still over 8.0 pages after C-1..C-5 + figures: apply option-c (§3.9 → Appendix).

---

## 7. Reproducibility — the exact word counter used

```python
import re
with open(r'd:\Codes\idea04\docs\paper\EMNLP_paper_draft.md', 'r', encoding='utf-8') as f:
    lines = f.read().split('\n')

def count_range(start, end, label):
    words = 0
    for i in range(start, min(end+1, len(lines))):
        t = lines[i].strip()
        if t and not re.match(r'^#+\s', t) and not re.match(r'^---', t):
            words += len(re.split(r'\s+', t))
    print(f'{end-start+1:>5} lines  {words:>6} words  {label}')
    return words

# EDO portion only (L1-257); ignore short-paper duplicate (L258-365)
total = 0
total += count_range(0, 0, 'Title')
total += count_range(1, 4, '## Abstract')
total += count_range(5, 24, '## 1. Introduction')
total += count_range(25, 35, '## 2. Related Work')
total += count_range(36, 146, '## 3. Methodology (3.1-3.9 + Prototype Scope Box)')
total += count_range(148, 243, '## 4. Experiments (4.1-4.6)')
total += count_range(244, 252, '## 5. Limitations')
total += count_range(253, 256, '## 6. Conclusion')
print(f'EDO total: {total} words')
```

Result snapshot (2026-04-19):
```
    1 lines       0 words  Title
    4 lines     230 words  ## Abstract
   20 lines     779 words  ## 1. Introduction
   11 lines     303 words  ## 2. Related Work
  111 lines    1525 words  ## 3. Methodology (3.1-3.9 + Prototype Scope Box)
   96 lines    1165 words  ## 4. Experiments (4.1-4.6)
    9 lines     342 words  ## 5. Limitations
    4 lines     168 words  ## 6. Conclusion
EDO total: 4512 words
```

---

## 8. Headline finding (for SCIENTIST_TODO § C and reviewer-readiness review)

* **Current state**: ~8.35 main-body pages with no figures / Algorithm yet — already over the strict 8-page limit by ~0.35 page.
* **After planned figures + Algorithm**: ~9.65 pages — **+1.65 over the desk-reject limit**.
* **Compression plan**: ~1.25–1.65 pages recoverable through 5–6 surgical cuts, all of which are post-U-003-merge work.
* **Hard constraint**: any LaTeX-rendered estimate is ±0.3 pages; the audit MUST be re-run with `texcount` + actual PDF compilation after S-013.

This audit is referenced from `docs/coordination/SCIENTIST_TODO.md § B.1 → S-011`.
