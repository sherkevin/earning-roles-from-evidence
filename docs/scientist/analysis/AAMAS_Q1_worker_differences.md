# Q1: How can task experience create capabilities and reusable workflows?

Discussion draft v4, 2026-09-16; published-work novelty audit and EDO-C fusion added. **The user selected C: acquired specialization, with workflows as first-class, persistent and composable objects.** The broad ingredients have published precedents; the narrower candidate contribution is evidence-conditioned workflow transfer across changing acquired capabilities. This is a research recommendation, not established novelty or a frozen method. The [requirements](../../paper/aamas2027/REQUIREMENTS.md) and [task ledger](../../coordination/AAMAS_TASKS.md) remain authoritative; this note is not another plan.

## 1. Central question

**Can initially comparable agents acquire complementary capabilities from different task histories, and can their team turn coordination experience into reusable workflows that improve performance on new task compositions under a fixed resource budget?**

An agent learns how to perform a contribution; a team learns how to organize contributions. Assignment connects them: it uses current capability and determines opportunities to acquire future capability. A workflow preserves organizational knowledge beyond a conversation or set of agent IDs.

| User intuition | Operational interpretation | Evidence still needed |
|---|---|---|
| Skills, workflows, tools and memory create capability differences | Explicit resources in execution state, with a shared frozen model initially | Different artifacts must produce different held-out response profiles |
| Early tasks shape an agent | Task exposure changes artifacts; allocation changes later exposure | Persistence, order effects and harmful lock-in are hypotheses |
| Failure produces memory; success produces skill | Both produce evidence and candidate lessons/procedures | Success does not validate every component; failure does not invalidate all components |
| Communication forms composable workflows | Traces can yield parameterized execution templates | Stored conversations need abstraction, contracts and validation |
| Differentiated agents and workflows produce emergence | Measure acquired complementarity, reusable organization and compositional transfer | Artifact count and routing concentration alone establish none of these |

The organizing insight is that **allocation changes both the current execution graph and the future capability distribution**. This broad loop is already described by AgentNet; it is motivation, not our novelty claim. The fusion proposed here gives the loop one organizational object: a workflow preserves responsibility structure, while local accepted evidence earns a scoped binding of an agent to each responsibility. Section 9 narrows the candidate to preserving useful workflow structure while acquired executors change, using those evidence-conditioned bindings and selective rebinding/reconstruction. Capability-based routing itself also has precedents. The proposed distinction needs a specific mechanism and causal transfer evidence.

## 2. State, feedback and objective

### 2.1 Agent state and capability

For n agents and tasks X_1,...,X_T, let X_t contain only permitted inputs and metadata. Initially agents share model parameters φ, instructions P, tools and update rules. Define

$$
L_{j,t}=(\mathcal S_{j,t},\mathcal M_{j,t},\mathcal T_{j,t},\mathcal W_{j,t}),
\qquad \Xi_t=(L_{1,t},\ldots,L_{n,t},\mathcal L_t,R_t).
\tag{1}
$$

- **Skills S:** versioned single-agent procedures with applicability conditions, input/output schemas and supporting evidence. They may call tools. Under this ontology, procedures delegating to several agents are workflows.
- **Memory M:** provenance-linked episodes, observations, warnings and unresolved hypotheses. Both successful and failed episodes can be memories; storage does not imply validated procedural knowledge.
- **Tools T:** executable interfaces and access rights. Availability differs from learned competence using a tool. Initially T_j,t=T_0 for everyone; learned tool-use procedures belong to S. Tool acquisition is deferred.
- **Workflow access W:** references an agent may invoke. The team library L stores definitions once. Initially catalog access is equal; access to a workflow does not imply competence in every role.
- **Allocation records R:** estimates of suitability for capability slots, conditioned on task and artifact versions; not true competence.

Working context resets per task; skills, selected memories, workflows and allocation records persist. Skills/memories start empty or from the same disclosed seed; workflow grammar and any seed templates are shared across methods. Do not inject different role personalities to manufacture the specialization we intend to explain.

At a cloned, frozen checkpoint, define individual capability using an independently scored contribution Z under a common probe protocol and budget b:

$$
\mu_{j,t}(x;b)=\mathbb E[Z(j,x;L_{j,t},b)].
\tag{2}
$$

Probes cannot update live learning state. Individual probes prohibit delegation and use the same compatible contribution interface; permitted single-agent skills/tools remain available. Workflow-mediated whole-task ability is assessed separately: an agent invoking an excellent team is not thereby an excellent individual executor. For a common probe distribution D and the same feasible workers, contextual complementarity is

$$
G_t=\mathbb E_{X\sim D}\max_j\mu_{j,t}(X;b)
-\max_j\mathbb E_{X\sim D}\mu_{j,t}(X;b)\ge0.
\tag{3}
$$

One uniformly superior agent can produce variance while G_t=0. These maxima are theoretical diagnostics, not deployable test-label oracles. Estimation needs uncertainty and protection against maximizing noisy sample means. G_t>0 does not show that our router can exploit it.

### 2.2 Coupled decisions

Let H_t be the relevant decision maker's authorized view of history, not omniscient access to private artifacts. A policy chooses workflow construction/retrieval, executor bindings and bounded execution decisions. Here a_t denotes a contingent episode controller whose step-level decisions can respond to legitimate new messages, rather than one immutable pre-episode action. Write

$$
a_t\sim\pi(\cdot\mid X_t,H_t),\quad
(\tau_t,F_t)\sim K(\cdot\mid X_t,\Xi_t,a_t),\quad
\Xi_{t+1}=U(\Xi_t,\tau_t,F_t).
\tag{4}
$$

Here τ_t records contributions, dependencies, versions, attempts and costs; F_t is permitted environment/audit feedback. Artifact proposal, validation and promotion are charged parts of U. Participating agents update only from authorized observations. Nonparticipants do not silently receive private traces. Initial coordination may be centralized; this definition does not establish decentralization.

| Outcome | Meaning | Policy access |
|---|---|---|
| F_t, including audit acceptance A_t | Actually observable feedback | As declared by the contract |
| Z_t | Independent correctness of a specified contribution | Evaluator-only unless a particular check is a declared public service |
| Y_t | Independent final utility, e.g. hidden-test success | Evaluator-only for final assessment |

Public tests, simulator rewards or disclosed verifiers can supply feedback if all methods receive the same access and cost. Hidden evaluation answers/tests cannot affect updates, retries, stopping or selection. If acceptance is all we observe, call it acceptance rather than correctness.

Compare complete policies from matched initial states:

$$
V_T(\pi;B)=\frac1T\mathbb E_\pi\sum_{t=1}^T Y_t,
\quad C_t^{calls}\le B_c,\quad C_t^{tokens}\le B_k,
\quad \operatorname{bytes}(\mathcal P_t)\le B_s.
\tag{5}
$$

Here P_t is all policy-readable persistent state: memories, skills, workflow definitions, allocation records, indexes, retained traces and validation evidence, including any history later supplied through H_t. Truly evaluator-only logs may be excluded only if inaccessible to policies. Persistent capacity is total across the system; declare additional per-agent and per-call retrieval/context limits. Charge routing, tools, failures, abstraction, validation and workflow search. Report latency/concurrency and offline development costs separately. Preparation phases need equal disclosed preparation budgets. They must not hide online learning cost.

Assigning work can build future capability, so immediate-reward routing need not optimize the horizon. Another policy would create different artifacts; a contextual oracle on our realized checkpoints is therefore not a full-horizon regret comparator. Compare full streams for total effects and cloned checkpoints for mechanism explanations.

## 3. Workflow as a first-class object

### 3.1 Trace, template, instance

A **trace** records one execution. A **template** defines a reusable family of executions. An **instance** binds a template to input data, exact versions and actual agents. Temporal message order alone does not identify necessary causal dependencies.

Define

$$
w=(\mathrm{id},v,\Sigma_{in},\Sigma_{out},P_w,Q_w,G_w,\rho_w,\Gamma_w,\ell_w,\mathcal E_w).
\tag{6}
$$

| Field | Meaning |
|---|---|
| id, v | Stable identifier and immutable version |
| Σ_in, Σ_out | Typed input/output schemas, including units and provenance |
| P_w, Q_w | Preconditions/postconditions; label verified predicates versus empirical expectations |
| G_w | Skill/tool/subworkflow nodes with data and control edges |
| ρ_w | Capability requirements for executor slots, independent of agent IDs |
| Γ_w | Guards, acceptance checks, failure propagation and allowed state/side effects |
| ℓ_w | Budget, depth, retry and termination limits |
| E_w | Origin traces, validation, scope, failures, dependencies and retirement status |

Initially use finite DAGs after bounded retry expansion, with no cyclic subworkflow references. An instance I_t=(w^v,X_t,β_t,ν_t) binds slots through β_t and pins dependency versions through ν_t. Future bindings can change after failures only under declared, logged rules. Reconstruction recovers an execution specification, not identical stochastic outputs.

First-class means addressable, retrievable, executable, inspectable, composable, decomposable, versioned and retireable. A prose plan inside a prompt alone is insufficient for this operational claim.

### 3.2 Evidence-earned role bindings

The original EDO principle is retained as a **binding rule**, not as a global reputation score. A workflow slot is an abstract responsibility, such as "extract source-linked records" or "check unit consistency". For slot $r\in R(w)$, context $\kappa$ includes the task family, interface contract, workflow version and dependency versions. Let $e_{j,r,\kappa,t}$ be the evidence ledger for assigning agent $j$ to that slot and context:

$$
e_{j,r,\kappa,t}=\bigl(n^+_{j,r,\kappa,t},n^-_{j,r,\kappa,t},\bar v_{j,r,\kappa,t},\bar c_{j,r,\kappa,t},\nu_{j,t},t_{\mathrm{last}}\bigr).
\tag{18}
$$

Each update is produced by the upstream owner of the slot after inspecting the returned artifact and its provenance. It records accepted value, repair/rework, interface validity and cost, together with the exact capability and workflow versions used. The ledger is scoped to $(r,\kappa)$: evidence that an agent extracted text well does not automatically authorize it to integrate a result, and evidence under an obsolete artifact version is stale. The update may be an EMA or a calibrated posterior chosen in A-T04; the scientific object is the scope and provenance of the evidence, not a particular estimator.

Let $\operatorname{LCB}(e_{j,r,\kappa,t})$ denote a prespecified lower confidence bound for the declared contribution utility, and let $\theta_r$ be a development-fixed useful threshold. The eligible binding set is

$$
\mathcal B_t(r,\kappa)=\left\{j:
\operatorname{fresh}(e_{j,r,\kappa,t},\nu_{j,t},v_w)\land
\operatorname{LCB}(e_{j,r,\kappa,t})\ge\theta_r\right\}.
\tag{19}
$$

An execution instance uses a binding $\beta_t$ with $\beta_t(r)\in\mathcal B_t(r,\kappa)$ when exploitation is selected; a declared exploration rule may also sample an unproven agent at bounded cost. An audit rejection does not directly label the whole workflow or every participant. It updates the implicated slot, invalidates dependent bindings when the relevant contract/version changed, and selects among unchanged reuse, rebind, local repair or fresh construction. Thus the original acceptance ladder becomes a scoped, revocable responsibility assignment inside a reusable workflow.

This separation prevents three circular claims. A role ledger is not correctness: acceptance may be noisy and must be evaluated against independent contribution checks. A workflow is not a list of trusted names: $\beta_t$ is late-bound and version-aware. A successful final answer is not credit for every edge: promotion requires slot-level provenance and, where needed, independent composition validation. The empirical question is whether these scoped bindings preserve utility and reduce invalid compositions after executor changes beyond ordinary capability matching with the same evidence.

### 3.3 Composition and decomposition

Sequential composition w_2∘w_1 needs compatible schemas and semantic assumptions:

$$
\Sigma_{out}(w_1)\preceq\Sigma_{in}(w_2),\qquad
Q_{w_1}(z)\Rightarrow P_{w_2}(z)
\tag{7}
$$

on the relevant execution domain. The schema relation permits an explicit validated adapter. Also check permissions, side effects, provenance, freshness and resources. With sound contracts and represented state effects, the standard rule is

$$
\{P_1\}w_1\{Q_1\},\quad Q_1\Rightarrow P_2,\quad
\{P_2\}w_2\{Q_2\}
\Longrightarrow\{P_1\}w_2\circ w_1\{Q_2\}.
\tag{8}
$$

This is a conditional composition rule, not a new theorem or proof of LLM correctness. Natural-language declarations do not establish its premises. Components validated separately can fail together under a changed intermediate-output distribution. Validate the actual composition; do not multiply component success rates without justified assumptions.

Parallel composition needs an explicit join and checks for conflicting writes, shared resources and incompatible assumptions. Decomposition must expose every dependency crossing a cut, including state and provenance. A convenient conversation boundary is not necessarily a valid interface.

**Example:** extraction produces source-linked table records; normalization produces records in declared units; aggregation computes a statistic. JSON schema compatibility alone cannot prevent feeding values in thousands of dollars into a component expecting dollars. The reusable knowledge includes the unit contract and check. A new comparison task could combine these workflows with a join/comparison node and newly bind the roles. This is an illustrative construction, not a selected benchmark or result.

### 3.4 Workflow pool

The task-to-workflow relation is many-to-many. Let

$$
\mathcal C_t(x)=\{w:\operatorname{applicable}(w,x),\ w\text{ retrieved, constructed, or composed from }\mathcal L_t\},
\quad (w_t,\beta_t)\in\operatorname{Select}_{\pi}(x,\mathcal C_t(x),R_t,B).
\tag{9}
$$

Retrieval proposes candidates; contract checks remove infeasible ones; feedback measures actual usefulness. Bound search depth, candidate count and validation cost. Include fresh-construction/direct fallback. Similar task wording is not an applicability proof, and reuse must not hide uncharged combinatorial search.

## 4. From experience to reusable capability

### 4.1 Evidence and promotion

Use the lifecycle `evidence → candidate abstraction → permitted validation → promotion/versioning → monitored reuse → revise or retire` for both skills and workflows. For an artifact q,

$$
q\sim\operatorname{Propose}(\operatorname{View}_{r}(\tau_{\le t},F_{\le t})),\qquad
\operatorname{promote}(q)=\mathbf1\{\operatorname{valid}(q)\land
\operatorname{beneficial}(q;D_{val})\land\operatorname{withinBudget}(q)\}.
\tag{10}
$$

View_r is the proposing actor r's authorized observation projection; workflow induction receives only explicitly shareable summaries and dependencies. It cannot bypass private-state access. D_val is a separate permitted validation source, never hidden confirmatory evaluation. The contract must specify its sampling, observable checks, candidate count and reuse. Adaptive screening needs fresh validation batches or an appropriate prespecified correction/monitoring rule; repeatedly optimizing the same small set overfits it.

For a frozen candidate on a declared reference distribution, a paired utility comparison can support promotion when a prespecified lower confidence bound exceeds a useful threshold and protected regression strata stay within tolerances. This depends on the sampling/uncertainty model. With proxy feedback, it concerns the proxy, not hidden correctness. Cheap duplicate, provenance and interface checks precede expensive validation. The exact rule remains an A-T04 design choice, not an implemented guarantee.

Rollback restores an earlier version for future use; it cannot undo previous environmental effects. Retiring a component must invalidate or revalidate dependent workflows. Bounded storage requires consolidation and eviction rules as well as insertion.

### 4.2 Outcomes do not automatically assign component credit

A failed task may contain a correct extractor and faulty integration. A successful task may contain wasted calls, an error corrected downstream or a lucky guess. Thus "failure → memory, success → skill" is a **candidate-generation heuristic**, not the acceptance rule. Capture both outcomes: failure can yield a useful diagnostic skill; success can remain merely an episode when transfer is unproven. Warnings need applicability conditions and supporting traces.

Observable team reward is legitimate feedback, but does not identify marginal contributions. Contribution checks, provenance and controlled development ablations can support attribution; otherwise mark it unresolved. Giving every node terminal reward and treating the resulting score as competence confuses participation with causal usefulness.

### 4.3 Improvement is a distributional target

The intended improvement is

$$
\Delta_{j,t}(D;b)=\mathbb E_{X\sim D}
[\mu_{j,t+1}(X;b)-\mu_{j,t}(X;b)].
\tag{11}
$$

Promotion aims for useful positive Δ, not universal pointwise monotonicity. Finite feedback cannot guarantee improvement on every future task or distribution. Artifacts can introduce stale advice, retrieval distraction, interference and extra cost. Regression probes and retirement are therefore part of learning itself.

## 5. Early experience and specialization

The proposed feedback loop is

$$
\text{task exposure}\rightarrow\text{private artifacts}\rightarrow
\text{capability profiles}\rightarrow\text{binding/execution}\rightarrow
\text{workflow evidence}\rightarrow\text{future exposure}.
\tag{12}
$$

Separate two hypotheses:

1. **Experience-content dependence:** randomized prefixes containing different tasks, followed by a common suffix, produce different capability profiles.
2. **Order dependence:** different permutations of the same prefix multiset, followed by a common suffix, produce differences beyond total exposure.

Probe cloned checkpoints on the same unseen tasks without updating live state. Align worker labels when comparing profile sets; renamed identical capabilities are not divergence. Record difficulty, primitive-demand coverage and assignment counts. Balanced corrective exposure tests whether the differences persist, adapt or disappear.

Persistent assignments with equal capability indicate authority lock-in, not specialization. Persistent differences lowering team utility may be harmful lock-in. Useful specialization can also remain adaptable. Declare prefix length and recovery horizon from development, rather than selecting a dramatic trajectory afterward.

Initially symmetric agents can become asymmetric through different sampled experience. Greedy allocation can instead concentrate experience in one worker. Exploration is a plausible response, but diversity is not automatically optimal and "the first few tasks determine destiny" is too strong.

## 6. Three implementations within selected C

These choices refine C; they do not reopen A/B.

| Design | Learned objects | Strength | Limitation |
|---|---|---|---|
| C1: whole-template reuse | Private skills/memories; validated complete workflows; runtime binding | Smallest complete learning/reuse loop; useful comparator | Cannot substantiate compositional transfer; may reduce to case retrieval |
| **C2: typed subworkflow reuse and composition** | C1 plus interface-preserving decomposition and bounded composition | Directly tests the user's workflow proposal | Requires valid boundaries and meaningful unseen task combinations |
| C3: joint curriculum and structure learning | C2 plus active learning-opportunity allocation and broad workflow rewriting | Addresses the horizon value of cultivating specialists | Much harder credit, comparison and nonstationarity problem |

**Recommend narrow C2, with C1 as a comparator and C3 deferred.** C2 is an implementation scope, not by itself a novel algorithm: AWM already builds more complex workflows from earlier ones, and GPTSwarm recursively composes graphs. The candidate distinction and additional portability controls are in section 9. Use a shared frozen model, fixed common tools, bounded private memories/skills, one versioned DAG pool and runtime binding. Begin with sequential/fork-join operators and bounded retries/depth; choose numerical limits on development data. A simple router can support a useful finding, but cannot establish novel routing.

The minimal complete loop is:

1. Retrieve applicable workflows or decompose the task into typed subrequests with a charged planner.
2. Compose a bounded candidate; check dependencies, access, interfaces and budget; fall back if infeasible.
3. Bind slots using permitted capability evidence and declared exploration.
4. Execute with typed outputs, local checks, provenance and complete accounting.
5. Propose lessons, skills and workflow templates from authorized feedback; validate before promotion.
6. Reuse versions on new tasks, monitor regressions and propagate retirement to dependents.

A supplied task grammar can make interfaces tractable, but must be disclosed and given to comparators. Human-authored decomposition for every test task cannot support autonomous workflow-discovery claims. The benchmark needs repeated useful substructures and independent outcomes; a workflow pool attached to arbitrary single-step QA would poorly test this proposal.

## 7. Required evidence and failure conditions

### 7.1 Four questions

| Question | Necessary evidence | Narrowing/falsifying outcome |
|---|---|---|
| H1: acquired useful differences? | Matched held-out contribution profiles change; complementarity and artifact interventions explain utility | Different memories but no useful differences, or one generalist explains the gain |
| H2: retained organization helps? | Workflow reuse improves utility/cost over charged fresh construction with comparable artifact access | Matching compute, validation and context removes the gain |
| H3: composition transfers? | Unseen combinations of familiar demands benefit over whole-template reuse and fresh planning | Near-duplicate traces, answers or templates explain improvement |
| H4: complete system helps? | Stream utility/cost beats close methods and pooled-artifact alternatives | A simpler pooled agent or controller matches the effect |

For clean compositional transfer, freeze a checkpoint after permitted acquisition and test unseen composition families without committing evaluation feedback or new artifacts. Preserve familiar primitive coverage where intended but hold out composition graphs/task families, not only wording. Audit near-duplicate traces and answer-bearing artifacts. Separately evaluate ongoing co-development in online streams; later repetitions of a composition are no longer evidence of first-use transfer.

### 7.2 Focused controls

Use a small primary set and separate checkpoint interventions:

- Full C2 versus private artifact learning with fresh workflow construction and no retention.
- C2 versus C1: composition versus complete-template reuse, with comparable induction, feedback and budget rules.
- Learned versus fixed/uniform binding with the same workflow machinery.
- Mutable versus frozen acquired artifacts from a common declared checkpoint; specify exactly which artifact families are frozen.
- A pooled-memory/skill single agent or central controller with equal total storage, tool access, preparation budget and per-call context limits, plus a faithful close external method.

Full policies create different histories; match initial conditions/rules, not realized memories copied from the full method. Cloned checkpoints separately permit swapping private artifacts while records remain fixed, swapping records while artifacts remain fixed, and consistently renaming everything as a symmetry check. Pin catalog access and workflow versions. A consistent renaming should preserve behavior under coupled randomness.

A stronger claim that differentiation and composition reinforce one another needs a defined 2×2 intervention:

$$
I=[V_{11}-V_{10}]-[V_{01}-V_{00}].
\tag{13}
$$

One possible first factor is private versus pooled acquisition at equal total capacity; the second is composition enabled/disabled. Positive I supports an access/acquisition-regime interaction with composition. It does not isolate acquired differentiation as the cause, because pooling also changes access and learning dynamics. A differentiation-specific reinforcement claim requires a more direct matched intervention or additional identifying evidence. Do not add an interaction claim if evidence supports only reusable organization.

### 7.3 Statistics and cost

Use independently reset streams as units for online inference, with paired task orders across methods. Include failure and exhaustion in denominators. Transfer-probe analysis must respect shared checkpoints and task-family dependence. Use development variability and minimum useful effects to choose sample size; thousands of dependent steps are not thousands of independent learning systems.

Report quality-cost curves, acquisition overhead, first-use/reuse performance, regressions and capacity. Short horizons may not amortize induction cost; that is a meaningful boundary. Avoid the full Cartesian product of controls, models, budgets and topologies.

## 8. Mathematical guardrails retained from Q1 v1

### 8.1 Conditional equality and history

At a fixed context I, fixed state and common downstream protocol/budget, let routing randomization not anticipate potential outcomes. Then

$$
\mathbb E[Y(j)\mid I]=m(I)\ \forall j
\Longrightarrow \mathbb E[Y(J)\mid I]=\sum_j\pi(j\mid I)m(I)=m(I).
\tag{14}
$$

This immediate null is not a horizon-level result: C changes later states. It does not rule out complementary error correlations when choosing teams rather than individuals.

Prior exchangeability is weaker than conditional equality. In the earlier illustrative model, latent accuracies .9 and .1 are randomly assigned to worker IDs. Both initially have mean .5; one perfectly observed success by worker 1 yields next-task means .82 and .18. Initial symmetry therefore does not prohibit learning.

With frozen response states, a common reference history distribution and the same feasible set,

$$
G_H=\mathbb E_{X,H}\max_j\mathbb E[Y(j)\mid X,H]
-\mathbb E_X\max_j\mathbb E[Y(j)\mid X]\ge0.
\tag{15}
$$

Conditional Jensen gives this information-value statement. It omits history-acquisition costs and does not compare two coevolving full policies. Consistent renaming of workers and histories preserves information; it is not a history-destruction intervention.

### 8.2 Audit acceptance and correctness

For binary contribution truth Z and acceptance A, at matched frozen states let p_j=P(Z=1|j), with false acceptance α_j and false rejection β_j. Then

$$
q_j=P(A=1\mid j)=\alpha_j+(1-\alpha_j-\beta_j)p_j.
\tag{16}
$$

Common worker-independent α,β with α+β<1 preserve quality order. Worker-specific audits may reverse it: truth (.7,.6) with perfect audits and truth (.4,.8) with error pairs (.5,0), (0,.25) both yield acceptance (.7,.6). If other observations are uninformative, acceptance cannot distinguish those worlds. More samples of that channel do not repair identification.

Even common informative noise does not preserve an uncalibrated cost trade-off. For κ=1−α−β>0,

$$
q_j-\lambda c_j=\alpha+\kappa\bigl(p_j-(\lambda/\kappa)c_j\bigr).
\tag{17}
$$

This matters for promotion and binding alike. Independent checks, justified noise assumptions and matched opportunities remain necessary. These elementary statements are explanatory, not sufficient theoretical novelty. A fixed-step EMA has residual variance; it is not a convergence result for evolving capabilities.

## 9. Published-work comparison and the remaining candidate contribution

### 9.1 Verdict and source boundaries

**Q1 does not yet establish a novel method. Its broad ingredients and much of the proposed coevolution story already appear in published work.** In particular, combining private experience, evolving specialization and changing coordination is not new relative to AgentNet; treating agent graphs as recursively composable objects is not new relative to GPTSwarm; inducing and extending workflows from experience is not new relative to AWM.

The following comparison was checked on 2026-09-16. It uses formal proceedings or venue OpenReview records, not a preprint date as proof of acceptance. The [source manifest](../../../references/aamas/q1_novelty/sources.json) preserves downloads, hashes and failed accesses; the [evidence index](../../../references/aamas/q1_novelty/evidence.json) records paper versions and claim locations. Where venue PDFs returned HTTP 403, the accepted publication record and the inspected author arXiv version are explicitly separate. Absence statements below are confined to inspected methods, not assertions that nobody has addressed the problem.

### 9.2 What published papers already cover

| Published work | Mechanism in the inspected paper | Consequence for Q1 |
|---|---|---|
| [Reflexion, NeurIPS 2023](https://openreview.net/forum?id=vAElhFcKW6) | Task feedback produces verbal reflection retained in episodic memory; later attempts use it (§3/Algorithm 1, author text pp.3–4) | Failure-to-memory and improvement without weight updates are established ingredients |
| [Voyager, TMLR 2024](https://openreview.net/forum?id=ehfRiF0R3a) | Automatic curriculum, reusable executable skill library, self-verification and composition of simpler skills (§2.2–2.3, author text pp.4–5) | Success-to-skill, lifelong accumulation and compositional procedural reuse are not new |
| [GPTSwarm, ICML 2024](https://proceedings.mlr.press/v235/zhuge24a.html) | Agent computational graphs recursively combine into larger graphs; node prompts and inter-agent edges optimize from feedback (§2.1–2.5, final pp.2–4) | First-class graphs, recursive composition and simultaneous component/coordination improvement are prior art |
| [AWM, ICML 2025](https://proceedings.mlr.press/v267/wang25bx.html) | Abstracts parameterized subroutines from trajectories; supports offline/online memory; builds more complex workflows using earlier workflows (§2.3, §3.1/Fig.5, Appendix E, final pp.3–5 and 14) | Workflow induction, a persistent pool, reuse, progressive composition and even order sensitivity are already explored; do not reduce AWM to whole-trajectory replay |
| [AFlow, ICLR 2025](https://openreview.net/forum?id=z5uVAKwmjf) | Searches code-represented workflows with reusable operators, MCTS and execution feedback (§3–4, inspected ICLR-marked author version) | Automatic workflow construction/optimization and operator composition are not new |
| [AgentSquare, ICLR 2025](https://openreview.net/forum?id=mPdmDYIQ7f) | Planning/reasoning/tool/memory modules with uniform interfaces; a module pool supports recombination and evolution (§2–3, author version) | A modular resource ontology and software-like component reuse are not sufficient novelty |
| [ADAS, ICLR 2025](https://openreview.net/forum?id=t9U3LW7JVX) | Meta-agent searches code-defined agents, retaining an archive of discoveries; evaluates transfer across domains/models (§2–4, ICLR-marked author version) | Archiving useful agent designs and showing generic transfer do not establish the proposed distinction |
| [EvoMAC, ICLR 2025](https://openreview.net/forum?id=4R71pdPBZp) | Textual feedback updates agents and their collaboration connections during test-time refinement for each task (§3.1–3.2, author version) | Joint evolution of agents and workflow connections is not unique; distinguish per-task refinement from persistent cross-task acquisition |
| [G-Memory, NeurIPS 2025](https://openreview.net/forum?id=mmIAp3cVS0) | Insight/query/interaction graphs, extraction of core collaboration subgraphs, role-conditioned retrieval and cross-task updates (§4.1–4.3, author v2 pp.5–6) | Organizational memory, inter-agent trajectory reuse and agent-specific memory support already exist; a memory graph is not our contribution |
| [AgentNet, NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/hash/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html) | Private router/executor memories, task-experience specialization, capability matching, split/forward/execute decisions and evolving weighted connectivity (§3.1–3.4, final pp.4–7; §4.4 pp.9–10) | The closest overlap with C's acquired-specialization loop; neither coevolution nor capability-based selection can be claimed first |
| [RepuNet, AAMAS 2026](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UEHN4980.pdf) | Direct and indirect peer/self reputation is stored per target and used to update network ties and partner selection (§3, proceedings) | Evidence-conditioned partner choice and topology change are prior art; our candidate must be slot-, workflow-, interface- and version-scoped, with executor transfer and invalidation rather than a general reputation value |
| [ReAcTree, AAMAS 2026](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UCGT7089.pdf) | Dynamic subgoal agents, sequence/fallback/parallel controls, subgoal episodic retrieval and shared working memory (§4–5, proceedings pp.321–323) | Dynamic decomposition plus memory is established. It also retains varied local termination states from successful overall episodes, so prior work does not uniformly equate global success with local success |
| [LEGOMem, AAMAS 2026 extended abstract](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/VLUA1303.pdf) | Distills full-task and subtask procedural memories, assigns them to orchestrator/task agents, compares dynamic/query-rewrite retrieval (§1–2, proceedings pp.3116–3117) | Splitting experience into reusable modules and allocating memory across a MAS is already directly relevant AAMAS work. The formal publication is three pages; its ten-page author preprint is not a full AAMAS paper |

The four-resource description remains useful for specification, but is an ontology. Version IDs, schemas, rollback and storage limits are valuable implementation disciplines. They become a research contribution only if a specific new mechanism or controlled finding depends on them and survives comparison with existing modular planning, service composition and memory methods.

### 9.3 The three closest comparisons

**Against AgentNet:** the published method already says agents naturally specialize through task experience without explicit role assignment. It stores participating trajectory fragments and uses capability vectors to route future tasks. The narrower proposed difference is an independently retained, executable **workflow template with abstract role slots**, which can be reconstructed with a different distribution of acquired worker capabilities. AgentNet's inspected organizational state is primarily agent connectivity, capability vectors and routing experience. This does not make an added template store automatically novel; its portability must produce a measurable capability that the faithful comparator or a simple extension lacks.

**Against AWM/GPTSwarm:** both defeat a broad claim about composable workflows. AWM explicitly extends earlier subroutines; GPTSwarm recursively combines computational graphs. Q1 must test more than composition: whether execution knowledge learned with one team remains valid when executors change, which interface assumptions matter, and when reuse is cheaper than reconstruction. AWM also has cross-template generalization and an order analysis; merely adding either experiment is not new.

**Against G-Memory/LEGOMem:** these already preserve organizational experience and deliver appropriate fragments to agents. The distinction to pursue is between retrieving examples that guide another planning episode and inducing a parameterized execution structure whose binding and validity can be tested independently of the original agents. A strong baseline must receive the same retained evidence and capability observations. Do not artificially deny retrieval methods the information our method uses.

**Against RepuNet:** context-dependent peer/self reputation and topology rewiring already establish that interaction evidence can change partner choice. The proposed distinction is narrower: evidence is attached to an abstract slot inside a versioned workflow, carries interface and dependency provenance, expires when those conditions change, and directly controls reuse versus revalidation/rebinding/repair. This is a candidate execution mechanism, not a claim that evidence-based partner selection is new.

### 9.4 Recommended candidate: evidence-conditioned workflow transfer

The more specific research question is:

> **When agent capabilities change through experience, which parts of a learned collaborative procedure remain reusable, and can scoped evidence earned at local responsibility boundaries preserve useful structure by rebinding executors and selectively repairing incompatible subworkflows?**

Write a retained template as $w=(G,C)$, with execution graph $G$ and interface/role contracts $C$. Let $\beta$ bind abstract slots to concrete agents, $L$ denote their acquired states, and $\mathcal R_t$ be the evidence ledger of scoped role bindings $(w,r,\kappa,j,e)$. The useful object is the conditional execution value $V(w,\beta;x,L,\mathcal R_t)$, not a task-to-fixed-team lookup. Changes in task $x$, executor state $L$, role evidence $\mathcal R_t$ and workflow structure $G$ are different interventions. The difficulty is deciding whether a failure reflects an unsuitable binding, a broken interface assumption or an obsolete decomposition.

An illustrative sequence clarifies the intended increment. A team learns `extract evidence → normalize units → calculate → check`. Later, a different agent has acquired the best extraction skill, while the old calculator's output format changes. A remembered list of names is stale; a prose precedent may require planning everything again. The proposed mechanism would retain the supported dependency structure, bind extraction to the currently suitable agent using evidence scoped to that slot and interface, and revalidate or repair the affected calculation interface. Whether this actually helps, and whether ordinary capability matching already suffices, are experimental questions.

The resulting causal line is:

$$
\text{task exposure}\rightarrow\text{skill/memory candidates}\rightarrow
\text{audited contribution}\rightarrow\text{scoped earned role}\rightarrow
\text{promoted workflow template}\rightarrow
\text{late binding/rebinding}\rightarrow\text{new audited evidence}.
\tag{20}
$$

This gives each layer one job. Skills and memories change what an agent can do; a role binding records what responsibility that agent has earned under a particular workflow and interface; a workflow stores how responsibilities depend on one another. The role is therefore neither a prompt persona nor a permanent reputation. It can be explored, revoked, made stale by a version change, or transferred to another executor when the evidence and contract permit it.

The candidate contribution is correspondingly narrow: **evidence-conditioned workflow rebinding**. The method would retain an independently validated organizational structure while making executor assignment a scoped, auditable and revisable decision. This is a mechanism hypothesis, not a priority claim. It differs from AgentNet's inspected agent-level capability/connectivity adaptation and from AWM's inspected workflow induction by making role evidence a first-class, versioned condition for reusing a workflow after the acquired executor population changes. A faithful method may already implement an equivalent rule; the same-information baseline below is designed to discover that case.

To become more than architecture, the mechanism must specify:

1. **Induction:** extract a minimal candidate subgraph with typed inputs/outputs, semantic preconditions, evidence provenance and role requirements. Message order alone is not enough; development deletion/replay probes can assess which dependencies matter.
2. **Evidence-conditioned reuse:** record the task/interface/capability conditions under which a component was validated. On new tasks or changed artifact versions, estimate applicability from allowed observations and obtain charged validation where needed. A declared contract is not a certified guarantee.
3. **Selective adaptation:** choose among unchanged reuse, rebinding, local recomposition and fresh planning under one budget. Rebinding preserves the graph; recomposition changes it. The algorithm must explain this choice, its costs and fallback rather than simply asking an unrestricted LLM to solve it.

This is a candidate contribution within C2, not a claim that late binding, contracts or repair were invented here. A targeted follow-up on adaptive service composition and hierarchical plan repair remains necessary before asserting algorithmic priority. No named system or implementation has been frozen by this audit.

### 9.5 Evidence that could make the contribution defensible

Use two independently controlled transfer axes after acquisition: **new task compositions** and **changed executor capability assignments**. Keep template structure fixed in the executor-only test; keep executor states fixed in the task-only test; then test both together. New wording alone is not a new composition. Artifact swaps must respect declared access and cannot be disguised as natural learning; natural continued-learning streams are a separate ecological test.

The decisive comparisons are retained full templates, fresh planning, identity-bound replay, retrieved procedural examples, and **the same template library plus ordinary capability matching without the proposed validity/repair mechanism**. The last is essential: beating a stale ID lookup alone would be an easy, uninformative result. Include faithful AgentNet and a task-compatible AWM/LEGOMem-style memory method, with shared feedback and total acquisition/inference/storage budgets.

Measure held-out utility/cost, transfer loss after the change, recovery cost, valid interface rate, how much structure is retained, and unnecessary reconstruction. These diagnostics complement the individual frozen probes from section 7. Contracts must reduce concrete composition failures beyond schema checks; they need not improve every scenario. If matching alone recovers the benefit, withdraw the contract/repair novelty. If pooled memory or fresh planning wins, report the boundary rather than excluding it.

A second possible paper is a causal finding about **useful specialization versus self-reinforcing assignment lock-in**, and whether workflow reuse amplifies or mitigates it. AgentNet already motivates specialization, and AWM already discusses order, so novelty would require an identified mechanism, intervention and consequential boundary, not the existence of those phenomena alone.

### 9.6 Recent alerts and confidence limits

- [EvoSkillBank](https://openreview.net/forum?id=I9siUH3wEc) has a current COLM 2026 venue record. Its inspected abstract explicitly covers trace-to-skill candidates and adding, merging, deprecating or rejecting skills. Treat it as current accepted-work competition, separate from older completed proceedings. This audit inspected its record/abstract only; it cannot support detailed claims about what its method lacks. Skill governance is not a safe fallback novelty claim.
- [EvoFlow](https://arxiv.org/abs/2502.07373) describes workflow-population retrieval, crossover, mutation and diversity. Only a preprint/CoRR record was verified here; do not label it a confirmed conference paper. It still matters for novelty. The search also surfaced recent workflow-subgraph and typed-composition preprints; this is not an exhaustive priority search through all of 2026.
- Sources retrieved through OpenReview include discussion records, but this comparison relies on publication metadata and paper content, not reviewer opinions. Conference status and the inspected full-text version are separately recorded. No empirical scores from different papers are compared as if their datasets/budgets matched.

**Current judgment:** the broad Q1 story is substantially anticipated; the proposed portability/repair mechanism and causal evidence are the strongest candidates to develop, but no completed innovation is established yet. A-T03 selects tasks/feedback/resources; A-T04 must close the exact mechanism and prior-work gap. The [historical audit](../../../artifacts/analysis/aamas2027/t02_20260916/report.json) and current [memory](../../../codes/edo_frame/edo_frame/note_board_memory.py), [tools](../../../codes/edo_frame/edo_frame/tool_registry.py) and [events](../../../codes/edo_frame/edo_frame/events.py) provide starting components, not evidence for these claims. Earlier A/B designs remain controls, not primary recommendations.

## 10. Evidence boundary

This revision incorporates an independent bounded design review covering conditional symmetry, exposure/order, allowed feedback, attribution, semantic composition, full-policy versus checkpoint comparisons and focused controls. No runtime or model experiment validates this design yet.

The previous [illustrative arithmetic](../../../artifacts/analysis/aamas2027/q1_math_checks.json) checks earlier toy calculations and audit-bound algebra only, not the new workflow design or promotion rule. The composition rule is standard and conditional on sound premises. General background: [Bandit Algorithms](https://tor-lattimore.com/downloads/book/book.pdf); no regret guarantee is imported for this system.

No new benchmark result, superiority, guaranteed improvement, established early lock-in or first-in-literature claim is asserted.
