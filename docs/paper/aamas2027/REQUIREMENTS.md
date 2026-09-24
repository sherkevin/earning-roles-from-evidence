# AAMAS 2027 paper requirements

Version 1.5.8, 2026-09-24. Owner: scientist. This is the single active scientific/venue specification; [AAMAS_TASKS.md](../../coordination/AAMAS_TASKS.md) is the sole active status/execution ledger. The author's [decisions 0005](../../user/decisions/0005-retain-peer-judged-role-learning.md) and [0006](../../user/decisions/0006-study-peer-judged-role-formation.md) select **peer-judged role formation during agent–workflow co-evolution** as the active research direction. The exact judgment-to-role algorithm, observation protocol and evaluation remain open. [Q1 v6.1](../../scientist/analysis/AAMAS_Q1_worker_differences.md) and the prior [contract.json](../../../configs/aamas2027/contract.json) are historical conditional-adoption/rebinding candidates, **retired as main-paper questions**; their original bytes and Q1 v5 are [preserved](../../../artifacts/analysis/aamas2027/problem_entry_20260922/snapshots.json). Official rules, benchmark pins, test integrity and historical evidence remain preserved.

## 1. Target and authority

**Execution checkpoint, 2026-09-22:** the user resumed real-data experiments with real idealab APIs after the preserved pause checkpoint. [Decision 0001](../../user/decisions/0001-resume-real-api-iteration.md) records authorization. The first acquisition probe completed329 real attempts; both arms scored6/6 and the promotion gate failed ([audited result](../../../artifacts/experiments/aamas2027/dev_20260922/report.md)). The independent planned57-task census [stopped incomplete](../../../artifacts/experiments/aamas2027/headroom_20260922/report.md) after its one disclosed infrastructure recovery:38 attempted,33 protocol-valid successes,2 protocol-valid failures,3 UNKNOWNs,19 unstarted;592 real requests. No full-population headroom verdict is available. Total benchmark/induction requests are921, plus3 separate health requests. This supplies executable diagnostic evidence, not a useful capability or coordination result. [Independent method review](../../scientist/analysis/AAMAS_Q1_FEASIBILITY_REVIEW_20260922.md) retains the no-lock judgment; scientific requirements remain open. The active task ledger records scope and execution. The preceding paused iteration performed only catalog/path checks.

Target: a completed, credible AAMAS 2027 Main Track submission, provisionally in **Generative and Agentic AI (GAAI)**. These requirements aim to remove identifiable rejection risks; satisfying them does not guarantee acceptance. They are not a formula inferred from successful papers.

Three sources of requirements must remain distinct:

- **Official:** mandatory venue rules and published assessment criteria, linked below.
- **Scientific:** project-specific standards needed to support this paper's claims, including actual EMNLP reviews and the current code/evidence audit.
- **Editorial:** our recommended presentation and experimental priorities. These are adjustable when the contribution changes; they are not AAMAS rules.

The [official call](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/) values original, significant, sound, reproducible and clearly presented agent research with appropriate prior-work engagement. GAAI requires an identifiable agent or multiagent contribution. Generic prompting, tool use or language-model improvements do not suffice. COINE is an alternative only if organization/reputation itself becomes the central general contribution. Area selection is about fit, not presumed acceptance odds.

The current six-page manuscript is an **internal design and historical reanalysis**, not a completed empirical contribution. Its allocation-only protocol predates selected C and must be rewritten around the eventual supported design once matching evidence exists. Neither an EMA update, a sparse graph nor a workflow library is independently sufficient novelty.

## 2. Scientific core and design status

The author-retained core is: **an agent's role should be learned from how other agents actually judge and use its delivered work, and that learned role must affect future responsibility.** “Others' judgment” here means a real upstream owner or downstream consumer assessing acceptance, repair and actual utility, with terminal outcomes correcting some local mistakes. It is not self-description or an arbitrary detached judge score. Agents and workflows develop together through collaboration; an agent is not assumed to be an independently updated plug-in for a fixed workflow. The [original research setting](../../../idea.md) further specifies no central dispatcher or preset expert identity, sparse local neighbors and recursively available do/outsource/split decisions. A one-hop development probe can test a necessary signal, but cannot establish the full decentralized/recursive claim. This is the selected research direction, not proof of an original algorithm. The exact Q1 wording, judgment-to-role update, observation rights and evaluation remain under G0/A-T04.

The previous v6.1 question—“How can a team admit newly acquired capabilities into reusable workflows without exhaustively retesting every executor combination or accepting harmful collaboration regressions?”—is **not the paper's main question** under decision 0006. Its assumption that replacement into an existing workflow is the central decision conflicts with this project's co-evolution framing. Compatibility failures may occur, but their diagnosis or cheaper qualification is not a gate for peer-judged role formation. Preserve v6.1 as historical analysis and a possible comparator boundary, not an active method plan.

The three retained commitments have distinct roles to operationalize: private experience can change what an agent can deliver; **other agents' situated evaluation of that delivery** must shape role evidence; workflows preserve and evolve the task dependencies and consumer contexts in which judgment occurs. For identification, hold initial conditions and all non-target update **rules** common across arms; do not permanently freeze the resulting agent skills or workflow states. The paper's candidate new operator must be the judgment-to-role update, with its effect on later responsibility measured in naturally evolving streams. Generic coevolution, pairwise synergy, reputation, executable contracts and local repair are prior art.

### 2.1 Selected problem and scientific obligations

GAAI remains the provisional area because the question concerns interaction and adaptation among generative agents; this is a fit judgment, not an acceptance predictor. A working Q1 for G0 to operationalize is: **as agents and their workflows develop together, when can the actual recipient's judgment of a delivered contribution become reliable evidence for the producer's future responsibilities?** The answer must be a measured mechanism, not the slogan that other agents judge one another.

| Dimension | Required evidence / decision |
|---|---|
| Phenomenon | Independent producer and consumer agents perform genuinely dependent work; the recipient can accept, use, repair or reject a specific deliverable |
| Observation | Log the judge, producer, task/dependency context, deliverable, use/rework, cost and lawful later outcome; distinguish the recipient's opinion from independent task quality |
| Mechanism | One executable, source-aware judgment-to-producer-role update; define judge error, task mix, selection bias, uncertainty and when later evidence corrects local judgment |
| Consequence | Role evidence changes later responsibilities, and that change improves a prespecified team quality–cost objective rather than just producing diverse role labels |
| Co-evolution | Use common initial conditions, task opportunities, access and update rules across arms while allowing realized agent capabilities and workflow structures to evolve; diagnose the role-evidence contribution separately |
| Distinction | Beat or honestly match strong same-information contextual trust, raw-acceptance, terminal-only and pooled-selection alternatives with complete judgment and coordination costs |

The scientific question remains open if real recipients cannot provide useful judgments or if a simple trust rule explains all later allocation gains. Neither result can be repaired by renaming a router or adding independent learning modules after seeing outcomes.

### 2.2 Minimal mechanism boundary before implementation

A candidate event is a producer's attributable deliverable, the real consumer's acceptance/use/rework decision and its consequence, with task context, judge identity, provenance and cost. Terminal feedback may correct local misjudgment where legally observable, but it does not by itself identify each contributor's value. The judged agent's role evidence/profile must be distinct from a particular delegator's private belief about that agent. The sharing scope and exact update rule remain to be specified under G0/A-T04; the old binary acceptance EMA is a baseline, not a selected method.

Private memories/skills and workflows may change naturally under a declared common update rule. The primary experiment must observe judgment→role→later responsibility in longitudinal streams. Matched snapshots, swaps or short replays can diagnose a single arrow, but cannot replace the full co-evolution result or supply a free deployment counterfactual. Freeze policy code, legal feedback, initial opportunities and budget before the development test; do not freeze all realized states or separately optimize skill learning, workflow search and role learning as one unidentified method.

### 2.3 Benchmark infrastructure retained; final experiment fit reopened

The reuse-first implementation map, benchmark/runtime gates and matched baseline
matrix are recorded in the [peer-role assembly plan](PEER_ROLE_IMPLEMENTATION_ASSEMBLY_PLAN_20260924.md).
That plan selects CooperBench as a conditional primary candidate and OpenHands
SDK as a runtime candidate; this requirements document remains the scientific
authority, so neither choice is a positive result or a completed benchmark lock.

| Environment | Retained facts | Current role |
|---|---|---|
| [AppWorld](https://github.com/StonyBrookNLP/appworld), source `42b5bcf3cd334fee33f0c37c02070a9f5807add5`, data 0.2.0 | 57 dev, 168 test-normal, 417 test-challenge; existing API/scorer feasibility evidence; native total 732 | Reusable stateful task and scoring infrastructure, **not** already an independent producer–consumer multi-agent evaluation |
| [ScienceWorld](https://github.com/allenai/ScienceWorld), source `e8216d6044e8e39be9fcb185e3b2dfb602584b52`, 1.3.0 | 30 task types; native variation splits; JAR/runtime still unverified | Secondary candidate only after a valid multi-agent observation boundary and method exist |

Preserve the four-route ceiling on `530b157`, all recorded R0–R3 outcomes and test integrity. No weak-model hunting, degraded prompts, arbitrary re-labeling of one agent's code segments as a team, or favorable subset selection creates a valid role-learning experiment. OfficeBench remains rejected for evaluator failures. Other environment decisions remain in the [design source index](../../../references/aamas/design_lock_20260922/evidence.json).

### 2.4 Comparisons and decision before a method lock

Compare with self-description/fixed roles, terminal-only learning, raw acceptance rates, task/context-specific trust or bandits, a same-information role selector and a capable pooled controller. Include faithful close MAS methods if the final claim overlaps them. All arms receive equal initial models/tools/opportunities and the same lawful information, comparable storage and total API/test budgets. Their histories may diverge because their policies differ; do not make a live control inherit the proposed arm's realized memories or workflow.

Use development data to estimate judging quality and determine a bounded experiment, then freeze an independent confirmation contract before seeing its outcomes. A local paired/swap diagnostic tests whether judgments contain information beyond task difficulty and judge leniency; longitudinal full-policy streams test whether the update changes assignments and team utility after charging all costs. No experiment reported so far supplies these results.

### 2.5 Literature and historical candidate boundary

[Task-specific trust](https://www.ifaamas.org/Proceedings/aamas2008/proceedings/mainTrackPapers.htm), [CADMAS-CTX](https://arxiv.org/html/2604.17950v1), [RepuNet](https://arxiv.org/html/2505.05029v3), [RAPS](https://arxiv.org/html/2602.08009), [AgentNet](https://papers.nips.cc/paper_files/paper/2025/hash/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html), [SkillMAS](https://arxiv.org/html/2605.09341v1), [Meta-Team](https://arxiv.org/html/2605.29790v1), [Sero](https://arxiv.org/html/2605.28433v1), [C3](https://arxiv.org/html/2603.06859v2) and [DecisionBench](https://arxiv.org/html/2605.19099v1) constrain claims about trust, reputation, credit, downstream feedback, decentralized witness propagation, evolving organization and old-trace capability cards for later delegation. Actual consumer use/rework and later correction are a hypothesis to test against these near neighbors, not established priority. The [peer-judgment source cache](../../../references/aamas/peer_judgement_20260923/README.md), [pinned RAPS manuscript](../../../references/aamas/raps_20260923/README.md) and [pinned DecisionBench code audit](../../../references/aamas/decisionbench_20260923/README.md) record inspected versions and access limits; the [dated novelty boundary](../../scientist/analysis/AAMAS_PEER_JUDGMENT_NOVELTY_BOUNDARY_20260923.md) is a targeted comparison, not proof of novelty.

[Marginal-Contribution Policy Gradients](https://arxiv.org/html/2604.22785v2) already combines learned contribution estimates with sparse costly counterfactual evaluations and probability-weighted correction; [DAC](https://arxiv.org/html/2606.10684v1) already uses an actual downstream generator's abstention as an upstream searcher training signal, though its roles are preset. Their [pinned primary-source cache](../../../references/aamas/causal_peer_role_20260923/README.md) limits any claim that sparse counterfactual calibration or downstream acceptance is itself new. The proposed recipient-use/repair signal and later earned responsibility remain a hypothesis, not an established distinction.

The former v5/v6.1 package-rebinding and conditional-adoption discussions remain in their [archived design](../../../artifacts/analysis/aamas2027/problem_entry_20260922/q1_v5_assessed_snapshot.txt) and [assessed Q1](../../scientist/analysis/AAMAS_Q1_worker_differences.md). They are no longer the main problem, mechanism, acceptance gate, experimental endpoint or required positive witness. Their compatibility and regression-testing precedents may inform controls or limitations only when relevant to the selected role-learning claim.

## 3. Requirements and acceptance evidence

`P0` blocks the core scientific or submission contract. `P1` is necessary for the intended breadth/strength but can be revised only with an explicit narrower claim and reviewer check. A task can be completed with a negative result; the corresponding positive claim cannot.

### A-R01 — A consequential agent problem (Scientific, P0)

Define initial agent equality, private capability artifacts, permitted observations, agent–workflow co-evolution, task outcomes and full-horizon resource objective. Explain how actual consumer judgments can alter a producer's later responsibility within that evolution, and why this matters relative to a pooled-artifact agent/controller. **Acceptance:** one problem definition connecting real dependent delivery, situated judgment, judged-agent role evidence and future responsibility, with falsifiable utility questions. The judgments must come from real collaborators and causally affect later assignment; a diagram, artifact count or higher QA score alone does not pass.

### A-R02 — A defensible contribution relative to close work (Scientific, P0)

Use the [peer-judgment source cache](../../../references/aamas/peer_judgement_20260923/README.md), [RAPS manuscript audit](../../../references/aamas/raps_20260923/README.md), [DecisionBench code audit](../../../references/aamas/decisionbench_20260923/README.md), historical Q1 primary-source audits and newly relevant close work. Compare task-specific trust, contextual peer calibration, RepuNet, RAPS, AgentNet, SkillMAS, Meta-Team, Sero, C3 and DecisionBench before claiming a new role-learning mechanism; other workflow/repair precedents remain relevant only to claims actually made. Meta-Team already uses agents' reports of how peers' outputs affected downstream execution to revise teammate profiles and team-level roles. RAPS already combines decentralized first-hand publication assessment, second-hand witness reports, witness credibility and reputation-aware brokerage, while reactive subscription specializes an initially generic pool. Sero already links contribution credit to role evolution. C3 explicitly studies sound upstream work followed by a downstream error and supplies fixed-history counterfactual decision credit. DecisionBench already uses old traces summarized by external judges as capability cards for later delegation, although its public implementation does not update the cards from actual recipients' structured use/rework. Thus peer feedback plus co-evolution, witness propagation, generic credit-guided roles, avoiding shared terminal blame, and old-trace profiling before delegation alone are not novelty claims. **Acceptance:** an executable judgment-to-role update or controlled finding beyond these overlaps, supported by a faithful close baseline and a strong simple alternative with the same information and testing opportunity. Mere binary acceptance averages, pairwise compatibility scores, versioned contracts or collaborative reflection do not pass. Distinguish proceedings, extended abstracts, accepted records, preprints and abstract-only inspection. Do not infer novelty from a design lock or limited search.

The close-work comparison must also include Marginal-Contribution Policy Gradients and DAC when claiming counterfactual calibration or downstream acceptance as a novel signal. A role-value estimand must name the feasible alternative worker or recipient-alone action, recipient and workflow context, official quality measure, complete cost, and lawful observation time; sparse replay is charged. A method that differs only by feeding peer reports into an existing audit-correction formula or same-information contextual bandit does not satisfy A-R02.

### A-R03 — Identifiable evolving capability context (Scientific, P0)

Start agents from common model/prompts, artifact seeds and tool access; let declared task experience and collaboration change private state under the same update rules. Distinguish tool availability from learned tool-use skill and workflow access from ability to execute its roles. Prior exchangeability does not imply conditional equality after experience. **Acceptance:** measure role-relevant response differences and their evolution on matched, unseen task opportunities, with an identity-renaming and conditional-null control. Show that later role assignments track useful differences rather than a lucky identity, task mix or one generally superior agent. A claim that private skill learning itself improves capability requires separate held-out checkpoint and artifact interventions; it is not a prerequisite positive result for the judgment-to-role question. Full-policy comparisons match initial conditions and opportunity rules while allowing exposure histories to diverge.

### A-R04 — An executable, label-isolated protocol (Scientific, P0)

Specify persistent skills/memory/workflows/role records, temporary context, access boundaries, workflow dependencies, attribution and termination. Separate execution trace, evolving workflow description and bound instance. Define the actual judging agent, judged deliverable, recorded use/rework, legal observation, judgment-to-role update and later responsibility decision. Separate a delegator's local belief from role evidence accumulated about the judged agent. Give all arms the same initial task opportunities and non-target skill/workflow update rules, while allowing realized states to co-evolve. **Acceptance:** executable transitions, label isolation, private access enforcement, deterministic resume equivalence and logged judgment/role/assignment decisions. Confirmatory evaluator answers/tests cannot affect policy updates, retries or stopping. The declared training-only binary terminal feedback service is permitted supervision and equally available; it intentionally supersedes v3 acquisition feedback, without changing old outcomes. Public environment feedback is allowed only when explicitly contracted and equally available to comparators. Primary streams run serially; parallelism is across independently reset streams. Old gold-fed calibration is ineligible.

### A-R05 — Traceable and correctly scored evidence (Scientific, P0)

Every table row must identify runtime/config hashes, checkpoint, dataset version/split/native IDs, prompt/tool interface, scorer and selection history. A claimed handoff fact must point to the actual lawful observation containing that fact; merely citing any successful public GET is insufficient. Record claim-level provenance validity separately from factual accuracy and recipient acceptance. **Acceptance:** paired outputs align one-to-one with matching labels; official scoring is pinned or differences are explicitly labeled; missing outputs remain missing. The .7641 GPT-4.1-mini/200 and .4324 Qwen/7,405 results must never appear as a single-population contrast. Current source inspection does not prove historical runtime identity. Previously inspected validation data are historical/development evidence, not a fresh confirmatory test.

### A-R06 — Comparable and complete resource accounting (Scientific, P0)

Report quality at shared attempted-call/token caps, actual usage, failures, retries, tool time and wall-clock/concurrency. Charge decomposition, artifact induction/validation, workflow search/composition, retrieval, verification and integration. Bound all policy-readable persistent storage, including records, indexes and retained traces/validation history, plus per-call context/retrieval and preparation budgets; pooled comparators get equal total capacity. **Acceptance:** atomic pre-dispatch reservations survive errors/resume; tokenizer/completion bounds are pinned; unknown usage is conservative, not zero. Show quality-cost and acquisition-amortization behavior. Equal backbone or a nominal 72-versus-4 cap contrast is not fairness. Report development/search costs separately.

### A-R07 — Strong, faithful comparators (Scientific, P0)

Include budget-matched direct reasoning, a capable pooled-memory/skill agent or controller, self-report/fixed roles, terminal-only feedback, raw acceptance rates, task/context-specific trust or bandit, a same-information role selector and the closest feasible peer-feedback or evolving-organization method. Assess a C3-style fixed-history replay baseline when state restoration and its full cost are feasible; document the restoration failure or cost if not. Add workflow-retention/composition arms only for workflow-specific claims; old/new-package regression-testing controls are no longer mandatory for the main question. Deduplicate equivalent arms. Match observations, tools, models, initial opportunities and budgets; charge judgment, selection and acquisition. **Acceptance:** pinned faithful adapters, disclosed deviations, development-selected settings and all prespecified comparisons retained. A per-item oracle is only an upper bound; framework count cannot replace conceptual closeness.

### A-R08 — Evidence that isolates peer judgment during co-evolution (Scientific, P0)

Hold initial execution opportunities, legal observations, shared update rules and budgets constant while disabling or shuffling the judgment-to-producer association; compare consumer-use/rework evidence with raw acceptance and terminal-only variants. Measure judge error and downstream use independently, including task difficulty and selection effects. Define what each short-run snapshot/swap holds fixed and distinguish it from the primary longitudinal comparison. **Acceptance:** full-policy streams share initial conditions/rules/budgets while their agent capabilities and workflows may diverge through experience; cloned-checkpoint probes isolate the role-record effect without pretending to be free live counterfactuals. Do not copy the proposed arm's realized memories into live controls. Consistent renaming is a symmetry check; association-breaking swaps are different interventions. Test workflow composition or capability-learning components separately only if claiming their independent effects. Routing entropy, extra context/calls or benchmark-name routing cannot establish the mechanism.

### A-R09 — Frozen design and appropriate uncertainty (Scientific, P0)

Lock acquisition/development/confirmation splits, task opportunities, feedback, method, baselines, budgets, contrasts, failure handling and minimum useful effect. Separate online agent–workflow co-development from frozen-checkpoint signal diagnostics; prevent answer/trace leakage and evaluate later allocation and team utility on unseen tasks or task families. A stronger workflow-composition claim needs a separate method-independent holdout definition. **Acceptance:** independent reset streams and paired stream-level inference; transfer analysis respects checkpoint/family dependence. Use development streams to estimate variability/cost and freeze the final independent confirmation count before test outputs. The former five/ten stream plan belonged to v5 and does not supply power for the reopened question. Keep snapshot-conditional and full-learning-population uncertainty distinct. Handle repeated candidate validation and secondary multiplicity explicitly. Include failures; no post-result replacement of splits, seeds or endpoints.

### A-R10 — Correct analysis of judgment and its claimed boundaries (Scientific, P0)

Connect the analysis to observation quality, peer-judge reliability and selection bias, artifact promotion/regression or composition failure as applicable. Common informative audit errors can preserve correctness rank; worker- or judge-specific errors need not, and fixed-step EMA retains variance. Terminal reward does not identify component credit; a consumer's acceptance can also be mistaken. If the recipient makes a separate completion error after using a valid contribution, a shared terminal failure cannot automatically become negative producer-role evidence. Conversely, acceptance or matching action alone does not establish that the producer caused the action. **Acceptance:** measure independent contribution truth against permitted feedback, separate producer-content, source-provenance and consumer-action failures, state validation-selection assumptions and distinguish empirical contracts from sound semantic premises. No universal improvement or compositional-correctness theorem follows from finite success rates or schema matching. Elementary identities remain explanatory, not sufficient novelty; real and synthetic audit checks are labeled separately.

### A-R11 — Breadth and boundary matched to the claim (Scientific, P1)

Under the user's API pivot, retain qwen3.8-max for initial diagnostics; MiniMax-M3 and ScienceWorld are provisional breadth choices to finalize after mechanism feasibility. These are router identifiers, not verified weight identities; record returned model/route metadata and disclose reproducibility limits. The failed 3B and unexecuted 14B paths remain historical, not mandatory new experiments. Prioritize role-learning transfer across task and recipient contexts, judgment mistakes, negative transfer and recovery; defer early-order/scaling claims. Test artifact promotion, workflow composition and graph scaling only if claimed. **Acceptance:** frozen resources/splits/scorers, same mechanism for transfer, visible neutral/harmful outcomes and historical Qwen/Phi-4 boundaries. If breadth is infeasible, narrow and re-review scope; BBH is not interactive coordination and repaired MBPP is not fresh confirmation.

### A-R12 — A readable completed scientific paper (Editorial + Scientific, P0)

One research question, a small defined vocabulary, one protocol and a main result answering it. Include a real trajectory from producer delivery through consumer judgment, role-evidence update, evolving workflow and later responsibility, with a failure or mistaken judgment example. **Acceptance:** distinguish the contribution from close work; main text includes decisive same-information/cost controls; show effects and uncertainty without calling every numerical maximum a winner. Historical Hotpot/2Wiki boundaries remain when those results are used. Reconcile every empirical sentence with exact raw evidence. The old allocation-only scaffold and a list of proposed tests are not the final paper.

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

Expected central evidence: (1) a real producer→consumer judgment→producer-role update→later-responsibility trajectory, (2) later team quality versus full cost against close same-information trust and pooled controls, (3) a judgment-source or correction intervention that explains the role mechanism and its failure boundary, and (4) longitudinal streams where agents and workflows can evolve under common rules. Separate skill or workflow-composition effects require separate interventions only if claimed. These can share figures/tables. Do not demand a fixed dataset/baseline count, universal SOTA, positive ablations, strategic-agent theory or a new convergence theorem merely to resemble a 'best paper'.

Before freezing the abstract, choose the supported route:

- **Mechanism contribution:** situated judgments from real collaborators form role evidence that changes later responsibilities and improves a declared team quality–cost outcome beyond same-information alternatives during agent–workflow co-evolution. Independent skill-learning, workflow-composition or emergence claims need their own evidence.
- **Analysis/negative contribution:** a reproducible, nontrivial failure phenomenon with explanatory interventions and scientific significance; rewrite the paper around that finding.
- **Insufficient contribution:** only old router gains, trivial identities, or an underpowered null remain. Continue research or move the cycle; formatting and Findings do not repair missing soundness or significance.

No silent waiver of a failed requirement. Record evidence, revised scope and independent review in the task ledger before changing the claim or release gate.

## 6. Calendar and document contract

Calendar verified against official pages on 2026-09-16; review criteria/area fit rechecked 2026-09-22. AoE is UTC-12; Beijing is 20 hours ahead.

| Event | Official date (AoE) | Beijing time |
|---|---|---|
| All authors have OpenReview accounts | 2026-09-17 | Sep 18, 19:59:59 |
| Mandatory abstract (approximately 100--300 words) | 2026-10-01 | Oct 2, 19:59:59 |
| Full paper | 2026-10-08 | Oct 9, 19:59:59 |
| Rebuttal | 2026-11-20--24 | Ends Nov 25, 19:59:59 |
| Notification / camera-ready | Dec 21 / Jan 25, 2027 | Published date / Jan 26, 19:59:59 |

Conference: May 3--7, 2027, Hanoi. Recheck live rules before submission. This document does not authorize external submission or reviewer commitments.

Requirements live here; gaps, task status, execution evidence and scoped decisions live only in [AAMAS_TASKS.md](../../coordination/AAMAS_TASKS.md). Role TODO files point there. `submission_gate.json` is a conservative machine gate mapped to these requirements, not a third research plan. Source PDFs, raw reviews, audit JSON and the S-518 execution record remain supporting evidence. A requirement changes only with a dated rationale and corresponding task updates.
