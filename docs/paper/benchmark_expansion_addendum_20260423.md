# Benchmark Expansion Addendum — Claim Scope, Community Benchmarks, and Baseline Coverage

> **Created**: 2026-04-23 (scientist S-206) from user-provided survey of 2024-2025 community benchmarks and baseline families.
> **Companion docs**: [`benchmark_inventory.md`](benchmark_inventory.md), [`final_experiment_matrix.md`](final_experiment_matrix.md), [`sota_baseline_survey_2026.md`](sota_baseline_survey_2026.md), [`external_baseline_plan.md`](external_baseline_plan.md), [`best_paper_agenda_3month.md`](best_paper_agenda_3month.md)

This addendum answers two questions that the current benchmark docs did not answer explicitly:

1. **How persuasive is the current baseline set?**
2. **If we beat those rows, can we honestly write "SOTA"?**

The short answer is:

> **Current rows are strong enough for a narrow "multi-agent multi-hop QA" SOTA claim, but not yet for a broad "multi-agent collaboration" SOTA claim.**

---

## 0. Executive verdict

### 0.1 What the current baseline set is already good for

If we complete the current HotpotQA + MuSiQue matrix against:

- `single_agent`
- `fixed_self_claim`
- `fixed_peer_calibrated`
- `edo_stage2_chain`
- **MA-RAG**
- **ReAgent**
- **MAD**
- and, ideally, representative older external hosts (**AutoGen**, **ChatEval**)

under the **same backbone / same scorer / same context policy / same datasize ladder**, then the resulting evidence is already strong enough to support:

> **"state-of-the-art among recent open-code multi-agent multi-hop QA baselines under a controlled evaluation setup"**

That is a serious and defensible claim.

### 0.2 What the current baseline set is *not* enough for

Even if we beat all of the above on HotpotQA + MuSiQue, that is **not yet** the same as proving:

- generic **multi-agent collaboration SOTA**
- generic **decentralized agent-society SOTA**
- or broad **language-agent benchmark SOTA**

Why not:

1. The task family is still concentrated around **multi-hop QA**.
2. We do not yet cover the newer 2025 **collaboration-native** benchmarks that the community will increasingly recognize.
3. We still lack a clean external baseline from the **decentralized dynamic-routing** family (the closest conceptual gap is currently **AgentNet**).

### 0.3 Practical implication

For the current paper, we should distinguish **three levels of claim strength**:

| Coverage reached | Honest wording |
|---|---|
| HotpotQA + MuSiQue + recent open-code multi-hop QA baselines | **SOTA on recent open-code multi-agent multi-hop QA baselines** |
| Above + one 2025 collaboration benchmark (MultiAgentBench or Collab-Overcooked) | **SOTA / strongest results across multi-hop QA and a contemporary collaboration benchmark** |
| Above + MultiAgentBench + Collab-Overcooked + GAIA-style agent task | **broad collaborative-agent SOTA** becomes much more defensible |

---

## 1. Baseline-family coverage: what we still need

The user survey is correct that "more baselines" does not simply mean "more rows". The persuasive target is:

> **one strong representative from each important baseline family**

rather than blindly running every framework in the ecosystem.

### 1.1 Family A — Single-agent null

Representative:

- `single_agent`

Why it matters:

- proves whether organization adds value at all
- prevents reviewers from saying the team-of-agents result is just an expensive rephrasing of a single strong call

Status:

- **must remain mandatory**

### 1.2 Family B — Centralized orchestration

Recommended representative:

- **AutoGen**

Optional alternates, but not all needed:

- MetaGPT
- CrewAI
- LangGraph supervisor-style pipelines
- AnyMAC

Why only one representative is enough:

- these systems mostly defend the same conceptual baseline class: **central coordinator / supervisor / SOP-driven role orchestration**
- running all of them is expensive but only marginally increases argumentative coverage

Recommendation:

- **keep AutoGen as the primary representative**
- treat MetaGPT / CrewAI / LangGraph as citation-level family members unless a reviewer explicitly asks for one of them

### 1.3 Family C — Debate / round-table

Representatives already in scope:

- **MAD**
- **ChatEval**

Why this family matters:

- it is the cleanest competing explanation for gains from multi-agent interaction
- if we beat this family, we can argue the win is not merely "more discussion"

Recommendation:

- current coverage is already good here; do **not** add many more debate variants unless a specific one is leaderboard-dominant

### 1.4 Family D — Decentralized dynamic routing

Highest-priority missing representative:

- **AgentNet**

Why this family is the biggest remaining conceptual hole:

- our paper's novelty rests heavily on **decentralized coordination + dynamic routing + peer-induced specialization**
- centralized baselines and debate baselines do not fully test whether that *decentralized* component matters
- the most direct community-facing counterargument is still: "you beat centralized or debate systems, but did you beat another decentralized dynamic coordinator?"

Recommendation:

- **AgentNet is the single best new baseline candidate to add**
- if code is runnable, it is higher-value than adding a second generic supervisor framework

### 1.5 Family E — Task-specific recent SOTA

Representatives already chosen:

- **MA-RAG**
- **ReAgent**

Why they matter:

- they are the strongest recent open-code systems directly tied to multi-hop QA
- they are what make a narrow "multi-hop QA SOTA" sentence plausible

Recommendation:

- these rows remain **non-negotiable**

---

## 2. Benchmark expansion: which datasets are actually worth adding

The user survey lists many reasonable tasks. The right way to absorb them is to tier them.

### 2.1 Tier A — add to the benchmark roadmap

These are the best next benchmarks if we want broader community credibility.

| Benchmark | Why it deserves to be added |
|---|---|
| **MultiAgentBench (ACL 2025)** | Probably the single strongest 2025 collaboration-native benchmark for our story. It explicitly measures coordination quality, supports multiple communication topologies, and is already framed in language-agent terms. |
| **Collab-Overcooked (EMNLP 2025)** | Strong fit for dynamic do/split/delegate decisions and natural-language coordination. Excellent for showing specialization and peer-evaluated task assignment. |
| **GAIA** | Broad, recognizable, and repeatedly used in agent papers. Good for showing the method is not trapped inside QA. |

### 2.2 Tier B — strong EMNLP-friendly extensions

| Benchmark | Why it is valuable |
|---|---|
| **2WikiMultiHopQA** | Natural extension of the current multi-hop QA story; already present in our docs as reserved Stage-2 space. |
| **ESConv** | Keeps us inside a very EMNLP-friendly NLP task family while still testing specialization and multi-stage collaboration. |

### 2.3 Tier C — optional / later

| Benchmark | Recommendation |
|---|---|
| **TruthfulQA / MMLU / BoolQ** | Good for debate-style sanity checks, but not first-line evidence for our decentralization story. |
| **SWE-bench / MBPP** | Useful if we pivot harder toward agentic coding, but currently off the main narrative. |
| **Generic web-agent suites** | Only worth it after one collaboration-native benchmark already lands. |

---

## 3. Recommended timeline fit

### 3.1 What fits the current near-term matrix

Near-term matrix completion should stay focused on:

- **HotpotQA**
- **MuSiQue**
- recent open-code external baselines
- same-backbone controlled comparisons

This is still the shortest route to a strong, honest paper.

### 3.2 What should be the *first* benchmark expansion beyond QA

If we add only **one** new benchmark family soon, the order should be:

1. **MultiAgentBench**
2. **Collab-Overcooked**
3. **GAIA**

Reason:

- MultiAgentBench is the most compact "reviewer-understandable" bridge from our current paper to modern collaboration benchmarking.
- Collab-Overcooked is a very good fit, but it adds environment complexity.
- GAIA is broader and more recognizable, but it can also introduce more confounds.

### 3.3 What should be the *first* new baseline beyond the current roster

If we add only **one** new baseline family representative, it should be:

> **AgentNet**

because it is the most direct "decentralized dynamic coordination" counterfactual.

---

## 4. Writing guidance for the paper

### 4.1 If we only finish the current QA matrix

Use wording like:

> "We evaluate against recent open-code multi-agent multi-hop QA systems and find that ..."

or

> "Under a controlled backbone and context policy, our method achieves the strongest results among recent reproducible multi-agent multi-hop QA baselines."

### 4.2 If we additionally land one 2025 collaboration benchmark

Use wording like:

> "Beyond multi-hop QA, the same coordination rule also improves performance on a contemporary collaboration benchmark ..."

This is much stronger than a pure QA claim.

### 4.3 Only use broad "multi-agent collaboration SOTA" wording when

all of the following are true:

1. the HotpotQA + MuSiQue core matrix is materially complete,
2. at least one strong 2025 collaboration benchmark is landed,
3. and the decentralized-baseline gap (preferably AgentNet) is no longer open.

---

## 5. Concrete recommendation

For this project, the best expansion path is:

1. **Finish the current QA matrix first** (`HotpotQA + MuSiQue`, same backbone, complete datasize ladder).
2. **Add AgentNet as the next new baseline candidate**.
3. **Add MultiAgentBench as the first benchmark expansion**.
4. **Add Collab-Overcooked second** if bandwidth remains.
5. **Use GAIA as the broader cross-task proof point**, not as the very first expansion.

This gives the best balance between:

- community recognizability,
- fit to our decentralization story,
- and execution realism.

### 5.1 Entry conditions for the two most important expansions

To keep scope disciplined, the two recommended expansions should enter under explicit gates:

#### AgentNet (`E-031`) — baseline-family expansion gate

Promote AgentNet from "probe" to "real matrix candidate" only if:

1. we can identify a runnable repo / branch,
2. the evaluation task is close enough to our current controlled setting to avoid meaningless apples-to-oranges comparison,
3. and the current QA-first matrix has at least its **HotpotQA P0 `n=200` block** materially underway.

Interpretation:

- AgentNet is the best **next** baseline, but it should not replace unfinished core rows like `single_agent`, MA-RAG, ReAgent, or MAD at the same datasize.

#### MultiAgentBench (`E-032`) — benchmark expansion gate

Promote MultiAgentBench from "probe" to "official benchmark addition" only if:

1. the current QA-first matrix is no longer blocked at the most basic level,
2. we can identify a **small pilot subset** whose success metric maps cleanly onto our framework,
3. and the engineering burden does not force us to abandon unfinished P0 QA rows.

Interpretation:

- MultiAgentBench is the strongest first non-QA benchmark, but it should enter as a **pilot slice first**, not as an open-ended commitment to the entire suite.

#### Scope discipline rule

If a proposed new benchmark or baseline would delay completion of the QA-first core matrix **without** giving a stronger conceptual counterfactual than AgentNet / MultiAgentBench, it should be deferred.

---

## 6. Cross-references

- **Current authoritative roster**: [`benchmark_inventory.md`](benchmark_inventory.md)
- **Current execution-target matrix**: [`final_experiment_matrix.md`](final_experiment_matrix.md)
- **Axis A survey**: [`sota_baseline_survey_2026.md`](sota_baseline_survey_2026.md)
- **Axis B host/swap plan**: [`external_baseline_plan.md`](external_baseline_plan.md)
- **Best-Paper 2-3 month path**: [`best_paper_agenda_3month.md`](best_paper_agenda_3month.md)
