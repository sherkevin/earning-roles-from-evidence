# AAMAS 2027 paper requirements

Version 1.3, 2026-09-16. Owner: scientist. This is the single active scientific and venue requirements document for the AAMAS revision. [AAMAS_TASKS.md](../../coordination/AAMAS_TASKS.md) is the single active gap/status/execution ledger. Historical EMNLP specifications and S-518 proposals are evidence, not competing instructions. Revision rationale: v1.1 selected C with reusable/composable workflows; v1.2 incorporated the requested published-work audit; v1.3 fuses the original EDO local-audit principle with C as a candidate scoped role-binding mechanism. Broad capability/workflow coevolution and evidence/reputation routing are prior art. Evidence-conditioned workflow transfer across changing acquired executors is a narrower candidate, still requiring a locked mechanism and evidence. Official requirements and historical results are unchanged.

## 1. Target and authority

Target: a completed, credible AAMAS 2027 Main Track submission, provisionally in **Generative and Agentic AI (GAAI)**. These requirements aim to remove identifiable rejection risks; satisfying them does not guarantee acceptance. They are not a formula inferred from successful papers.

Three sources of requirements must remain distinct:

- **Official:** mandatory venue rules and published assessment criteria, linked below.
- **Scientific:** project-specific standards needed to support this paper's claims, including actual EMNLP reviews and the current code/evidence audit.
- **Editorial:** our recommended presentation and experimental priorities. These are adjustable when the contribution changes; they are not AAMAS rules.

The [official call](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/) values original, significant, sound, reproducible and clearly presented agent research with appropriate prior-work engagement. GAAI requires an identifiable agent or multiagent contribution. Generic prompting, tool use or language-model improvements do not suffice. COINE is an alternative only if organization/reputation itself becomes the central general contribution. Area selection is about fit, not presumed acceptance odds.

The current six-page manuscript is an **internal design and historical reanalysis**, not a completed empirical contribution. Its allocation-only protocol predates selected C and must be rewritten after the benchmark and mechanism contracts are locked. Neither an EMA update, a sparse graph nor a workflow library is independently sufficient novelty.

## 2. Conference style and the intended scientific contribution

The useful AAMAS orientation is: specify the agents, their information and decisions, explain the interaction mechanism, and demonstrate a consequence for coordination. A QA score alone does not establish organizational learning. Organization must be observable in allocation and useful under a fair execution contract.

The selected question is: **Can task experience create complementary agent capabilities, and can reusable, composable workflows turn those capabilities into better performance on new task combinations at a controlled cost?** The fused organizing mechanism is an evidence-conditioned role binding: local, provenance-linked audits determine which agent may temporarily own an abstract workflow slot under a specific interface and version. The chain `task exposure -> artifacts -> audited contribution -> scoped role binding -> reusable organization -> utility` motivates the design but is not itself novel. The [Q1 discussion and published-work audit](../../scientist/analysis/AAMAS_Q1_worker_differences.md) recommend focusing C2 on when this scoped evidence preserves workflow structure across changed executor capabilities and when rebinding or local repair is needed. This remains a candidate, not a frozen claim. Early lock-in, improvement and synergy remain hypotheses.

Recent examples support this orientation, not a universal aesthetic preference:

| Primary source | Relevant lesson for this project |
|---|---|
| [Roles in Asset Markets, AAMAS 2024](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p40.pdf) | Define roles through measured interaction structure and interventions. |
| [Hierarchical Language Agent, AAMAS 2024](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p1219.pdf) | Evaluate the coordination constraint, including responsiveness. |
| [Soft Condorcet Optimization, AAMAS 2025](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1253.pdf) | Give a precise decision problem and connect the analysis to it. |
| [Partner Selection, AAMAS 2025](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p1282.pdf) | Explain how history changes partner choice and the resulting behavior. |
| [SCMRAG, AAMAS 2025](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p50.pdf) | QA can fit AAMAS; the agent mechanism still needs a distinct contribution. |
| [Reputation, AAMAS 2026](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UEHN4980.pdf) and [ReAcTree, AAMAS 2026](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UCGT7089.pdf) | Reputation, dynamic relationships, trees and memory already have close precedents. |
| [Human-LLM Team Guidelines, AAMAS 2026](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/JOWO4591.pdf) | The venue accepts different contribution types; rigor must match the claim. |

This is a purposive sample from the 2024--2026 proceedings, not an analysis of acceptance predictors. The [source archive](../../../references/aamas/README.md) preserves downloads and hashes. Do not equate an award nomination with a win.

## 3. Requirements and acceptance evidence

`P0` blocks the core scientific or submission contract. `P1` is necessary for the intended breadth/strength but can be revised only with an explicit narrower claim and reviewer check. A task can be completed with a negative result; the corresponding positive claim cannot.

### A-R01 — A consequential agent problem (Scientific, P0)

Define initial agent equality, private capability artifacts, permitted observations, workflow structure/binding, task outcomes and full-horizon resource objective. Explain how assignment both uses and changes capability, and why reusable organization matters relative to a pooled-artifact agent/controller. **Acceptance:** one problem definition connecting acquired specialization and reusable workflows, with falsifiable transfer/utility questions. A diagram, artifact count or higher QA score alone does not pass; workflow persistence alone is not emergence.

### A-R02 — A defensible contribution relative to close work (Scientific, P0)

Use the Q1 source-linked matrix: AgentNet already couples experience-induced specialization and evolving coordination; GPTSwarm recursively composes graphs; [AWM](https://proceedings.mlr.press/v267/wang25bx.html) induces and extends workflows; [LEGOMem](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/VLUA1303.pdf) allocates full/subtask procedural memory (AAMAS 2026 extended abstract); G-Memory preserves organizational experience. Compare AFlow, AgentSquare, ADAS, EvoMAC, Voyager and Reflexion for the relevant components, and check context/role-dependent reputation such as RepuNet where applicable. The candidate mechanism is a versioned, scoped evidence ledger that binds agents to abstract workflow slots and triggers reuse, revalidation, rebinding or local repair after capability/interface changes. **Acceptance:** an executable mechanism or controlled finding beyond these overlaps, supported by a faithful close baseline and a strong simple alternative receiving the same evidence. If pursuing portability, compare the same template library plus ordinary capability matching without scoped validity/repair evidence. Schemas, versioning, a four-resource ontology, a workflow pool or evidence/reputation routing alone do not pass. Distinguish proceedings, extended abstracts, current accepted records and preprints; scope absence claims to inspected versions. Q1's fusion narrows the candidate but does not close A-R02.

### A-R03 — Identifiable acquired capabilities (Scientific, P0)

Start agents from common model/prompts, artifact seeds and tool access; let declared task experience create private differences. Distinguish tool availability from learned tool-use skill and workflow access from ability to execute its roles. Prior exchangeability does not imply conditional equality after experience. **Acceptance:** matched held-out checkpoint probes establish useful acquired response differences, with a conditional-null control, consistent identity renaming and artifact/record interventions. Complementarity must exceed simply finding one superior generalist. Separate early-prefix content from order, and capability persistence from assignment lock-in. Selection of a lucky identity or storing different memories is insufficient. Full-policy comparisons match initial conditions and opportunity rules; resulting exposure histories may differ.

### A-R04 — An executable, label-isolated protocol (Scientific, P0)

Specify persistent skills/memory/workflows/records, temporary context, access boundaries, typed workflow nodes/edges, runtime binding, scoped evidence-earned role certificates, invalidation/expiry, attribution and termination. Separate execution trace, template and bound instance. Define candidate extraction, allowed validation, promotion, dependency versioning, eviction/retirement and fallback; both outcomes can generate candidates. Composition/decomposition must preserve semantic assumptions and state dependencies, not just schemas. **Acceptance:** executable transitions and bounded acyclic composition, label isolation, private access enforcement, deterministic resume equivalence, and a logged choice among reuse, revalidation, rebinding, repair and fresh construction when evidence or versions change. Hidden answers/tests cannot affect policy updates, retries or stopping. Public environment feedback is allowed only when explicitly contracted and equally available to comparators. Primary streams run serially; parallelism is across independently reset streams. Old gold-fed calibration is ineligible.

### A-R05 — Traceable and correctly scored evidence (Scientific, P0)

Every table row must identify runtime/config hashes, checkpoint, dataset version/split/native IDs, prompt/tool interface, scorer and selection history. **Acceptance:** paired outputs align one-to-one with matching labels; official scoring is pinned or differences are explicitly labeled; missing outputs remain missing. The .7641 GPT-4.1-mini/200 and .4324 Qwen/7,405 results must never appear as a single-population contrast. Current source inspection does not prove historical runtime identity. Previously inspected validation data are historical/development evidence, not a fresh confirmatory test.

### A-R06 — Comparable and complete resource accounting (Scientific, P0)

Report quality at shared attempted-call/token caps, actual usage, failures, retries, tool time and wall-clock/concurrency. Charge decomposition, artifact induction/validation, workflow search/composition, retrieval, verification and integration. Bound all policy-readable persistent storage, including records, indexes and retained traces/validation history, plus per-call context/retrieval and preparation budgets; pooled comparators get equal total capacity. **Acceptance:** atomic pre-dispatch reservations survive errors/resume; tokenizer/completion bounds are pinned; unknown usage is conservative, not zero. Show quality-cost and acquisition-amortization behavior. Equal backbone or a nominal 72-versus-4 cap contrast is not fairness. Report development/search costs separately.

### A-R07 — Strong, faithful comparators (Scientific, P0)

Include budget-matched direct reasoning, a pooled-memory/skill agent or central controller, private learning without workflow retention, whole-template reuse without composition, fixed/uniform binding and the nearest feasible skill/workflow-learning method. A simple bandit is an allocator control, not by itself the closest full-system baseline. Deduplicate equivalent arms. Match observations, tools, models, initial opportunities and budgets; charge selection and acquisition. **Acceptance:** pinned faithful adapters, disclosed deviations, development-selected settings and all prespecified comparisons retained. A per-item oracle is only an upper bound; framework count cannot replace conceptual closeness.

### A-R08 — Evidence that isolates capability and workflow learning (Scientific, P0)

Specify focused contrasts for mutable versus frozen artifacts, workflow retention versus fresh construction, composition versus whole-template reuse, and learned versus fixed binding. Define which state each intervention freezes/swaps and when. **Acceptance:** full-policy streams share initial conditions/rules/budgets, while cloned-checkpoint probes isolate artifact, workflow and record effects. Do not copy the full policy's realized memories into live controls. Consistent renaming is a symmetry check; association-breaking swaps are different interventions. Define a 2x2 interaction only if claiming reinforcement between differentiation and composition. Routing entropy, extra context/calls or benchmark-name routing cannot establish the mechanism.

### A-R09 — Frozen design and appropriate uncertainty (Scientific, P0)

Lock acquisition/development/confirmation splits, task composition families, feedback, method, baselines, budgets, contrasts, failure handling and minimum useful effect. Separate online co-development from frozen-checkpoint first-use transfer; hold out compositions beyond surface wording and prevent answer/trace leakage. **Acceptance:** independent reset streams and paired stream-level inference; transfer analysis respects checkpoint/family dependence. Start planning with five streams and justify the final count from development precision; this is not a conference rule or power guarantee. Handle repeated candidate validation and secondary multiplicity explicitly. Include failures; no post-result replacement of splits, seeds or endpoints.

### A-R10 — Correct analysis of feedback, promotion and composition (Scientific, P0)

Connect the analysis to observation quality, artifact promotion/regression or composition failure. Common informative audit errors can preserve correctness rank; worker-specific errors need not, and fixed-step EMA retains variance. Terminal reward does not identify component credit. **Acceptance:** measure independent contribution truth against permitted feedback, state validation-selection assumptions and distinguish empirical contracts from sound semantic premises. No universal improvement or compositional-correctness theorem follows from finite success rates or schema matching. Elementary identities remain explanatory, not sufficient novelty; real and synthetic audit checks are labeled separately.

### A-R11 — Breadth and boundary matched to the claim (Scientific, P1)

For the intended general claim, retain a small-model continuity setting and add one materially stronger feasible open-weight model and one public executable non-QA task. Prioritize unseen compositions, artifact swaps, negative transfer, early-exposure content/order and recovery from stale workflows. Check a focused neighborhood of exploration, promotion and composition limits; graph scaling is required only if claimed. **Acceptance:** frozen resources/splits/scorers, same mechanism for transfer, visible neutral/harmful outcomes and historical Qwen/Phi-4 boundaries. If breadth is infeasible, narrow and re-review scope; BBH is not interactive coordination and repaired MBPP is not fresh confirmation.

### A-R12 — A readable completed scientific paper (Editorial + Scientific, P0)

One research question, a small defined vocabulary, one protocol and a main result answering it. Include a real trajectory from task/trace through artifact validation, workflow version and later reuse/composition, with a failure example. **Acceptance:** distinguish the contribution from close work; main text includes decisive cost/transfer controls; show effects and uncertainty without calling every numerical maximum a winner. Historical Hotpot/2Wiki boundaries remain when those results are used. Reconcile every empirical sentence with exact raw evidence. The old allocation-only scaffold and a list of proposed tests are not the final C paper.

### A-R13 — Reproducible, inspectable artifacts (Scientific, P0)

Provide a minimal runner, exact environment/configs, dataset/scorer pins, artifact/workflow schema and genealogy, dependency hashes, access rules, resume and small-replication commands. **Acceptance:** a fresh environment reproduces a fixture and declared small real run; every used skill/workflow version traces to allowed evidence and validation; missing evidence stays explicit. Do not package the dirty workspace or invent nested Git provenance for flattened `codes/` directories.

### A-R14 — Correct submission format (Official, P0)

Use the [official submission instructions and template](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/instructions/): English anonymous LaTeX/PDF, at most eight content pages plus reference-only pages, unchanged layout/style, and a single anonymous supplement ZIP no larger than 25 MB. Essential evidence belongs in the main paper; supplement reading is optional. **Acceptance:** build, page, citation, font, anonymity and ZIP checks pass on the frozen release. Count limitations as content; no ACL-style exemption. Preserve official class files and replace the internal submission ID only with the real ID.

### A-R15 — Author obligations and research disclosure (Official, P0)

Meet account, abstract and paper deadlines; supply an eligible reciprocal reviewer or valid exemption; confirm author order, overlapping submissions and AI-methodology assistance details. Follow the [reciprocal reviewer policy](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/reciprocal-reviewer-policy/) and [Findings policy](https://warwick.ac.uk/fac/sci/dcs/aamas2027/guidelines-and-policies/findings/). **Release acceptance:** author-confirmed prerequisites, abstract receipt/real ID, and tool/version/relevant methodology prompts disclosed rather than a grammar-only declaration. Full-paper receipt and future rebuttal are subsequent A-T12 obligations, not prerequisites for creating the release. Scientific responsibility remains with the authors. This internal audit is author-side assistance, not an official conference peer review.

Findings is automatic unless authors opt out, uses the same format, and is not a separate submission track. Negative, replication or exploratory work can also qualify for the main proceedings when the contribution is strong. No result type automatically ensures acceptance.

## 4. Actual rejection feedback -> requirements

Source: [author-provided OpenReview compilation](../../../EMNLP2026-OpenReview-审稿意见汇总.md), submission 11746. AC `jU7U`; reviewers `F61c`, `vJUA`, `2sxq`, `Dz77`. The source's overall ratings are 2 for the AC and 3/2.5/1/1.5 respectively. Internal simulated reviews are not treated as external feedback.

| Feedback ID | Actual concern / attribution | Requirements that resolve it |
|---|---|---|
| V01 | Dense prose and late notation/acronyms; AC, 2sxq, Dz77. Terminology/evidence-level distinctions; vJUA | A-R01, A-R12 |
| V02 | Missing complete execution example; F61c | A-R04, A-R12, A-R13 |
| V03 | Unexplained .76 versus .43 Hotpot result; AC, Dz77 | A-R05, A-R12 |
| V04 | 72 versus 4 calls; real calls/wall time and equal-cost baselines absent; AC, F61c, vJUA | A-R06, A-R07 |
| V05 | Small Hotpot effect and gains concentrated on 2Wiki; AC, F61c, Dz77 | A-R05, A-R08, A-R09, A-R12 |
| V06 | Small headline backbone; AC, Dz77 | A-R11 |
| V07 | QA-only evidence does not support general-framework claims; AC, Dz77 | A-R01, A-R11 |
| V08 | Missing closest adaptive role/resource-allocation work; AC, vJUA | A-R02, A-R07 |
| V09 | Arbitrary constants and unclear hyperparameter choice; AC, Dz77 | A-R04, A-R09, A-R11 |
| V10 | Neutral controls and negative effects require honest interpretation, including Phi-4; vJUA | A-R08, A-R10, A-R11 |
| V11 | Component/variant identity table and condensed main-text framework matrix requested; vJUA. The underlying matrix has eight framework families across three benchmarks (24 cells), not 24 distinct families | A-R07, A-R12 |
| V12 | Software/reproducibility clarity and ratings; F61c, vJUA, 2sxq, Dz77. Low dataset ratings do not require inventing a new dataset | A-R05, A-R13 |
| V13 | No author response during discussion; AC | A-R15; maintain evidence index for rebuttal |

The author-side audit adds A-R03, complete label isolation and stream/resume semantics in A-R04, scorer/provenance checks in A-R05, valid online controls in A-R08, corrected mathematical boundaries in A-R10, and the insufficient synthetic-transfer diagnosis in A-R11. Fixing prose alone does not close an empirical concern.

## 5. Paper shape and stop rules

Suggested eight-page content budget, to adjust after results: introduction/problem 1.0; closest work 0.6; model/protocol 1.7; analysis 0.5; experiments/results 3.2; discussion/limitations/conclusion 1.0. References are additional. This is a project layout suggestion, not a required venue structure. Lead with the supported contribution, not the repair history.

Expected central evidence: (1) quality versus full cost with close/pooled comparators, (2) acquired capability profiles and state interventions, (3) held-out composition transfer and a feedback/regression boundary, and (4) a real trace-to-workflow-to-reuse example. These can share figures/tables. Do not demand a fixed dataset/baseline count, universal SOTA, positive ablations, strategic-agent theory or a new convergence theorem merely to resemble a 'best paper'.

Before freezing the abstract, choose the supported route:

- **Mechanism contribution:** useful acquired capabilities and reusable/composable organization survive matched-budget state, transfer and simple-baseline controls, with a distinction from close prior work. Stronger interaction/emergence wording needs its own defined evidence.
- **Analysis/negative contribution:** a reproducible, nontrivial failure phenomenon with explanatory interventions and scientific significance; rewrite the paper around that finding.
- **Insufficient contribution:** only old router gains, trivial identities, or an underpowered null remain. Continue research or move the cycle; formatting and Findings do not repair missing soundness or significance.

No silent waiver of a failed requirement. Record evidence, revised scope and independent review in the task ledger before changing the claim or release gate.

## 6. Calendar and document contract

Verified against the official pages on 2026-09-16. AoE is UTC-12; Beijing is 20 hours ahead.

| Event | Official date (AoE) | Beijing time |
|---|---|---|
| All authors have OpenReview accounts | 2026-09-17 | Sep 18, 19:59:59 |
| Mandatory abstract (approximately 100--300 words) | 2026-10-01 | Oct 2, 19:59:59 |
| Full paper | 2026-10-08 | Oct 9, 19:59:59 |
| Rebuttal | 2026-11-20--24 | Ends Nov 25, 19:59:59 |
| Notification / camera-ready | Dec 21 / Jan 25, 2027 | Published date / Jan 26, 19:59:59 |

Conference: May 3--7, 2027, Hanoi. Recheck live rules before submission. This document does not authorize external submission or reviewer commitments.

Requirements live here; gaps, task status, execution evidence and scoped decisions live only in [AAMAS_TASKS.md](../../coordination/AAMAS_TASKS.md). Role TODO files point there. `submission_gate.json` is a conservative machine gate mapped to these requirements, not a third research plan. Source PDFs, raw reviews, audit JSON and the S-518 execution record remain supporting evidence. A requirement changes only with a dated rationale and corresponding task updates.
