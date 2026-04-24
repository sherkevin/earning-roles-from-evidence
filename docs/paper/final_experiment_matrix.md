# Final Experiment Matrix — Baseline × Datasize

> **Created**: 2026-04-23 (scientist S-205) per user instruction "梳理实验，列一份 baseline * datasize matrix".
> **Owner**: scientist (matrix spec + paper sync) + engineer (cell execution).
> **Companion docs**: [`benchmark_inventory.md`](benchmark_inventory.md) for the authoritative roster / benchmark definitions, [`sota_baseline_survey_2026.md`](sota_baseline_survey_2026.md) for Axis A candidate rationale, [`external_baseline_plan.md`](external_baseline_plan.md) for Axis B module-swap rationale, [`benchmark_expansion_addendum_20260423.md`](benchmark_expansion_addendum_20260423.md) for claim-scope + next-benchmark expansion logic, and [`docs/coordination/ENGINEER_TODO.md`](../coordination/ENGINEER_TODO.md) for engineer execution.

This file is **not** a second benchmark-inventory source. It is the **execution-target matrix**: which rows and columns still need to be filled before we can honestly claim that our method was tested against recent external systems at broadly recognised data scales.

---

## 0. Headline

The long-term experimental target is:

> **Fill a benchmarked matrix of recent baselines × recognised datasizes, then check whether our flagship row is actually SOTA under the same task / backbone / scorer / context policy.**

This matrix exists to prevent the project from stopping at isolated smoke numbers (`n=5`, `n=50`) or a single lucky slice (`n=200`) and calling that "external comparison".

---

## 1. Hard rules for this matrix

1. **External systems must solve the same task family**.
   Recent multi-agent multi-hop QA systems take priority over generic agent frameworks.
2. **Datasize must be broadly recognisable**.
   The matrix uses only `n=200`, `n=500`, and benchmark `fullval`.
3. **Smoke is not completion**.
   `n=5` or `n=50` only proves the adapter runs; it does **not** close a matrix cell.
4. **The comparison backbone stays fixed**.
   Unless explicitly marked otherwise, this matrix uses the canonical API backbone `gpt-4.1-mini`. Local-model emergence experiments are tracked separately and must not be mixed into these rows.
5. **A paper-grade cell needs the same scorer + same context policy**.
   For retrieval-style baselines, use the same HotpotQA / MuSiQue provided context policy rather than an easier external corpus, unless the paper explicitly frames that as a different setting.
6. **Only completed artifacts count**.
   A cell is only fillable if it has a run directory, `metrics.json`, and a log / note that can be cited later.

---

## 2. Baseline roster

### 2.1 P0 rows — must be filled

| Row | Why it must be in the final matrix |
|---|---|
| **`single_agent`** | Canonical null baseline. Without it, we cannot tell whether organisation beats a monolithic call. |
| **`fixed_self_claim`** | Strongest existing author-internal simplicity anchor on HotpotQA-200. Our method should not avoid its own strongest internal comparator. |
| **`fixed_peer_calibrated`** | The delivered TCPB Stage-1 anchor already used in the paper. |
| **`edo_stage2_chain`** | Our current flagship "organisation" row; this is the row that must eventually compete for SOTA. |
| **MA-RAG** | Recent multi-hop QA SOTA-style full system; direct Axis A head-to-head. |
| **ReAgent** | Recent EMNLP 2025 full system; direct Axis A head-to-head. |
| **MAD** | Strong recent external debate baseline; also closes the reviewer overlap-risk concern. |

### 2.2 P1 rows — should be filled if bandwidth allows

| Row | Why it is still valuable |
|---|---|
| **AutoGen** | Well-known external agent framework; useful as a recognisable older external reference and Axis B host. |
| **ChatEval** | Useful older external peer-critique host; strengthens the "not only one host" story. |

### 2.3 P2 rows — opportunistic only

| Row | Status |
|---|---|
| **BELLE** | Add only if code is located and runnable. |
| **MAR** | Add only if code is located and runnable. |

---

## 3. Datasize ladder

| Datasize | Meaning | Why it is in the matrix |
|---|---|---|
| **`n=200`** | Canonical paper slice | Already used by the paper and cheap enough for broad baseline coverage. |
| **`n=500`** | Mid-scale stability slice | Big enough to reduce "lucky 200-sample" arguments, still affordable across many rows. |
| **`fullval`** | Full validation split (`HotpotQA=7405`, `MuSiQue=2417`) | The only scale that can support a serious "SOTA" sentence without sounding thin. |

**Explicit non-goal**: `n=5` / `n=50` are bring-up sizes only. They remain useful for engineering, but they do not close any matrix cell in this file.

---

## 4. Current-state snapshot

Legend:
- `✅` = already paper-grade enough for this matrix cell
- `🟡` = partial / provisional / smoke-only / single-seed-only
- `❌` = missing
- `◻` = optional row not yet prioritised

| Baseline / system | HotpotQA-200 | HotpotQA-500 | HotpotQA-7405 | MuSiQue-200 | MuSiQue-500 | MuSiQue-2417 | Priority | Current note |
|---|---|---|---|---|---|---|---|---|
| **`single_agent`** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | P0 | Critical null baseline; currently absent from the paper-facing matrix. |
| **`fixed_self_claim`** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | P0 | HotpotQA-200 exists in Table 1; larger scales still missing. |
| **`fixed_peer_calibrated`** | ✅ | ❌ | 🟡 | ❌ | ❌ | ❌ | P0 | `n=200` exists; fullval has seed42-only landing (`F1=0.6823`) but not full matrix-grade closure. |
| **`edo_stage2_chain`** | 🟡 | ❌ | 🟡 | ❌ | ❌ | ❌ | P0 | `n=200` / 3-shard preliminary exists; fullval has seed42-only landing (`F1=0.6884`) but not final closure. |
| **MA-RAG** | 🟡 | ❌ | ❌ | ❌ | ❌ | ❌ | P0 | Only `n=50` smoke exists today; still not a final matrix row. |
| **ReAgent** | 🟡 | ❌ | ❌ | ❌ | ❌ | ❌ | P0 | Only `n=50` diagnostic smoke exists today; adapter still format-sensitive. |
| **MAD** | 🟡 | ❌ | ❌ | ❌ | ❌ | ❌ | P0 | Only `n=50` smoke exists today; still missing proper `n=200+` matrix rows. |
| **AutoGen** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | P1 | Clone / install progress exists, but no matrix row yet. |
| **ChatEval** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | P1 | Clone / install progress exists, but no matrix row yet. |

---

## 5. What "matrix complete" means

### 5.1 P0 completion

The matrix is **P0-complete** only when:

1. The seven P0 rows above are filled on **HotpotQA** at `n=200`, `n=500`, and `fullval`.
2. The same seven P0 rows are filled on **MuSiQue** at `n=200`, `n=500`, and `fullval`.
3. Every filled cell has a traceable artifact path (`metrics.json` + log / note).

### 5.2 Paper-grade completion

A cell is **paper-grade** when it has:

1. the same scorer used by our main paper tables,
2. the same backbone family (`gpt-4.1-mini`, unless the table explicitly says otherwise),
3. the same context policy / fairness setup,
4. at least one reproducible artifact directory,
5. and, for any row that will support a headline sentence, enough variance evidence that we are not relying on a one-off lucky slice.

### 5.3 SOTA claim gate

We may only write a serious "SOTA" sentence if:

1. the **P0 matrix is materially complete** on the benchmark where the claim is made,
2. our flagship row (`edo_stage2_chain`, or a later replacement) is at the top of the relevant fullval comparison under the same setting,
3. and no stronger recent external row is simply missing from that same benchmark block.

If those conditions fail, the honest claim is **competitive / partially superior / cost-superior**, not "SOTA".

### 5.4 Scope of the SOTA claim

Even if this matrix is completed and won, the default claim scope is still:

> **recent open-code multi-agent multi-hop QA SOTA under a controlled evaluation setup**

It does **not automatically** justify a broader "multi-agent collaboration SOTA" sentence. For that broader claim, see [`benchmark_expansion_addendum_20260423.md`](benchmark_expansion_addendum_20260423.md): we would still want at least one modern collaboration-native benchmark (preferably **MultiAgentBench**) and one stronger decentralized family baseline (preferably **AgentNet**).

---

## 6. Engineer execution order

The intended long-term order is **claim-first, not symmetry-first**.

When time / budget forces a choice, engineer should fill the cell that most strengthens the paper's headline claim, not the cell that merely makes the matrix look visually more complete.

The intended long-term priority is:

1. **Finish HotpotQA `n=200` claim-critical P0 rows first**:
   prioritize the modern external rows (`MA-RAG`, `ReAgent`, `MAD`) plus the corresponding our-row anchor on the same slice; keep `single_agent` in the first wave as the null floor.
2. **Create deterministic `n=500` slices** for HotpotQA and MuSiQue:
   these do not exist yet and should be added as new seed files.
3. **Scale the same HotpotQA claim-critical rows to `n=500`**.
4. **Scale the same HotpotQA claim-critical rows to `fullval`**.
5. **Then close the remaining HotpotQA P0 completeness gaps**:
   backfill any internal anchors that are still missing after the decisive head-to-head rows are landed.
6. **Repeat the same P0 ladder on MuSiQue**.
7. **Then fill P1 rows** (AutoGen, ChatEval) if budget / time still allows.

In short: **direct recent-baseline head-to-head on the primary benchmark beats matrix symmetry; symmetry comes after claim survival is secured**.

This turns all existing tickets into one unified objective:

> **Every future reproduce / rerun / scaling batch should be understood as filling one missing cell in this matrix.**

**Important scope guard**:
- `E-030` = finish the QA-first core matrix.
- `E-031` = AgentNet probe (best next baseline-family expansion).
- `E-032` = MultiAgentBench probe (best next benchmark expansion).

The latter two are deliberate expansions, not excuses to leave the core matrix unfinished.

---

## 7. Artifact contract per filled cell

For each newly filled cell, engineer should land:

1. a run directory under `artifacts/`,
2. a `metrics.json`,
3. a short note or log with the exact benchmark slice / backbone / context policy,
4. and an `ENGINEER_TODO.md` sub-entry that names the filled cell explicitly.

Scientist then updates this matrix doc and the benchmark inventory.

---

## 8. Cross-references

- **Benchmark roster / definitions**: [`benchmark_inventory.md`](benchmark_inventory.md)
- **Claim scope + expansion guidance**: [`benchmark_expansion_addendum_20260423.md`](benchmark_expansion_addendum_20260423.md)
- **Axis A candidate survey**: [`sota_baseline_survey_2026.md`](sota_baseline_survey_2026.md)
- **Axis B module-swap plan**: [`external_baseline_plan.md`](external_baseline_plan.md)
- **Engineer ticket dispatch / execution log**: [`docs/coordination/ENGINEER_TODO.md`](../coordination/ENGINEER_TODO.md)
- **Scientist coordination state**: [`docs/coordination/SCIENTIST_TODO.md`](../coordination/SCIENTIST_TODO.md)

---

## 9. Maintenance

This file is updated when:

1. a new matrix cell is filled,
2. a baseline row is upgraded from smoke-only to paper-grade,
3. a datasize column is created (for example, the new deterministic `n=500` slices),
4. or a row is dropped / replaced by explicit user decision.

**Owner split**:
- engineer fills cells and records artifacts in `ENGINEER_TODO.md`;
- scientist synchronises this matrix and the paper-facing docs.
