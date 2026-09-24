# Q1: Earning roles through reusable evidence of collaboration

Historical discussion v6.1, 2026-09-22. **Retired as the main-paper problem by [decision 0006](../../user/decisions/0006-study-peer-judged-role-formation.md).** The former final-lock review kept this conditional-adoption candidate stable while withholding a method lock; the text below preserves that assessment rather than endorsing it today. The [requirements](../../paper/aamas2027/REQUIREMENTS.md) and [task ledger](../../coordination/AAMAS_TASKS.md) remain authoritative. The previous exact-state retention design is preserved in the [v5 snapshot](../../../artifacts/analysis/aamas2027/problem_entry_20260922/q1_v5_assessed_snapshot.txt); [contract.json](../../../configs/aamas2027/contract.json) marks that specification as reference-only. Its parameter blocks are not a runnable specification of the proposal below.

**Status update, 2026-09-23:** [decisions 0005](../../user/decisions/0005-retain-peer-judged-role-learning.md) and [0006](../../user/decisions/0006-study-peer-judged-role-formation.md) select role formation from actual collaborators' judgments while agents and workflows co-evolve. This assessed conditional-adoption candidate does not implement that loop and is retired as the main Q1. Its analysis and evidence limits remain available for comparison; G0 in the active ledger governs the next formulation.

## 1. Historical v6.1 problem entry (retired as main Q1)

**Execution status:** resumed by explicit user instruction on 2026-09-22. The first real acquisition probe is complete: both arms scored6/6, the fixed promotion gate failed, and the package is not promoted. The independent planned full-dev census stopped at38/57 under its disclosed infrastructure recovery rule (33 protocol-valid successes,2 protocol-valid failures,3 UNKNOWNs,19 unstarted). No full-population headroom verdict or active inference remains. This document remains the assessed candidate, not a locked method; the [active task ledger](../../coordination/AAMAS_TASKS.md) links immutable protocols and actual results.

**How can a team admit newly acquired capabilities into reusable workflows without exhaustively retesting every executor combination or accepting harmful collaboration regressions?**

Task experience can improve an agent's local behavior while changing the assumptions on which collaborators rely. Local capability estimates alone may not tell us whether the new behavior is useful in a particular workflow. The proposed decision is conditional adoption: use a new package where collaboration is supported, retain a previous package elsewhere, or qualify a changed handoff before adopting it.

The important distinction is between knowing that an executor can perform a subtask and knowing that its contribution can be used successfully by the rest of this workflow. This is an interaction problem, not a claim that more agents are inherently better.

| Preserved commitment | Function in the narrower story |
|---|---|
| Experience-induced private skills/memory | Real learned changes generate the candidate capabilities to adopt |
| Earning roles from evidence | Evidence qualifies a contribution in its collaboration context; a global reputation score is insufficient |
| First-class composable workflows | A workflow retains executable obligations at its handoffs, so organizational knowledge can survive changed executors and enter new compositions |

Working narrative: experience changes local procedures; changed procedures may alter compatibility; contribution evidence identifies the coordination conditions under which they remain useful; the workflow retains those conditions; new executors earn responsibilities by satisfying them. This is a candidate causal chain, not a demonstrated effect or three independent priority claims.

## 2. AAMAS fit and competing entries

The [official AAMAS 2027 call](https://warwick.ac.uk/fac/sci/dcs/aamas2027/calls/call-for-main-track/) explicitly includes interaction protocols, coordination, self-improving agents and failure recovery in GAAI. COINE covers teamwork and organizations, but generative-agent architectures primarily belong in GAAI. Official evaluation concerns originality, significance, soundness, reproducibility, clarity and engagement with prior work. There is no verified acceptance-probability advantage from selecting a fashionable label.

Our inference about fit: a bounded coordination decision, a recognizable failure of a competent alternative, and a mechanism that explains the resulting behavior provide a stronger paper identity than broad claims of coevolution or emergence. This is editorial judgment, not a venue rule. Centralized coordination and a contribution using standard components can still fit; scientific value must come from a substantive problem, mechanism or finding.

| Entry considered | Assessment |
|---|---|
| **A. Conditional adoption under collaboration incompatibility** | Formerly recommended in v6.1; retired as main Q1 by decision 0006. A concrete team decision with an interpretable failure witness, but its replacement premise does not capture the selected co-evolution problem. Novelty would still need to exceed synergy matching and integration testing |
| B. Counterfactual failure attribution and local repair | Useful diagnostic instrument for A. Replay/repair already have close precedents; replay is costly and there need not be a uniquely blameworthy agent |
| C. Assign experience to develop complementary capabilities | Legitimate longer-horizon learning problem, but changes the project into curriculum/resource allocation. Training allocation to learning teams is already studied; free artifact migration also weakens an identity-based story |

No active curriculum, new backbone training, unrestricted topology search, security-governance system or general debugging framework is added to the main proposal.

## 3. Minimal mathematical model

Let \(d_u,d_v\) denote complete effective execution packages for adjacent producer and consumer roles: model/settings, role instructions, tools and actually loaded artifacts. Let \(h\) be the handoff protocol, \(x\) the task and observable state. The producer emits \(z\); the consumer uses it in a continuation:

\[
z\sim P_{d_u}(\cdot\mid x),\qquad
S_x(d_u,d_v,h)=\Pr(Y=1\mid x,d_u,d_v,h).
\tag{1}
\]

\(Y\) is the independently scored continuation or task outcome under a fixed remainder policy and budget. If only a local proxy is available, label it separately; it is not automatically task success. Local contribution quality \(Q_x(d_u)\) is measured with an adequate role-specific assessment, independently of the adoption mechanism.

A diagnostic interaction is

\[
Q(d_u^{new})\ge Q(d_u^{old}),\quad
\Delta_{v_1}>0,\quad\Delta_{v_2}<0,\qquad
\Delta_v=\mathbb E_X[S_X(d_u^{new},d_v,h)-S_X(d_u^{old},d_v,h)].
\tag{2}
\]

Use the same task distribution in the two partner comparisons. Otherwise task mix alone can produce the apparent reversal. A negative team change with improved local quality is sufficient to motivate investigation; the crossing is a stronger witness that a universal package ranking is inadequate. Neither is a new theorem.

Illustrative invented probabilities, **not results**:

| Producer package | Local quality | Team success with consumer A | Team success with consumer B |
|---|---:|---:|---:|
| Old | 0.80 | 0.80 | 0.80 |
| Newly learned | 0.90 | 0.92 | 0.64 |

A marginal-quality selector prefers the new package everywhere. Conditional selection keeps it with A and the old one with B. A competent pairwise compatibility matcher can already express this solution; beating marginal selection alone establishes little novelty.

For a workflow \(w=(G,\{K_e\}_{e\in E})\), bindings \(\beta\) select role packages. A coordination record

\[
K_e=(\sigma_e,\Gamma_e,h_e,\mathcal T_e,\mathcal E_e)
\tag{3}
\]

contains the role interface, guarded semantic obligations, an executable handoff procedure, qualification cases and provenance/coverage evidence. These are empirical requirements, not universal correctness certificates. Obligations concern facts a consumer needs (such as source-linked identity, temporal scope or unresolved ambiguity), not merely a JSON schema.

The scientific target is useful adoption at a bounded total qualification and execution cost:

\[
\max_\pi\;\mathbb E[Y_\pi]\quad
\text{subject to }C_{acquisition}+C_{qualification}+C_{coordination}+C_{execution}\le B.
\tag{4}
\]

The old/new package, binding and handoff are decisions; the graph can initially remain fixed. Composition becomes a transfer test for learned coordination obligations, rather than a second unrestricted search problem.

## 4. Candidate mechanism and why it could work

The candidate is **qualification using learned workflow handoff requirements**. It is not frozen pseudocode yet.

1. **Retain useful versions and actual handoff evidence.** A successful local skill proposal becomes an available candidate, not a global replacement. Log what its consumers received and which observable obligations they needed. Retention/storage costs apply equally to baselines.
2. **Learn bounded, executable coordination requirements from training experience.** Propose a small predicate/handoff change from a real success or failure. Ground it in available observations; do not invent missing evidence. Compare the original and changed handoff with the same prefix, consumer and resources in an isolated training environment. Use a separate allowed validation instance for admission. An LLM critique alone neither verifies the obligation nor establishes causal blame.
3. **Qualify changed packages against reusable requirements.** Reuse parameterized qualification cases attached to the workflow boundary. A new package receives its own measured evidence; no old success counts are copied into its new state. A passing test is empirical support only for the covered conditions. Unseen conditions remain unqualified.
4. **Adopt conditionally.** Choose among retaining the old package, adopting the new package, or adopting with a validated handoff change. Preserve working combinations where there is insufficient evidence. New tasks remain solvable through the common fresh-planning fallback; the proposed policy may not exclude difficult cases from evaluation.

Initially allow only a small predefined grammar of source-grounded handoff operations and predicates; separate proposal, validation and evaluation data. Repeatedly tuning against the same qualification cases will overfit. Arbitrary natural-language rules or an unconstrained LLM judge do not solve this issue.

The intuitive benefit comes from preventing detectable downstream regressions while retaining improvements where they actually help. In a simplified comparison, let \(p\) be harmful-update frequency, \(d\) detection probability, \(L\) avoided loss, \(f\) false-rejection rate, \(O\) forgone improvement and \(c\) qualification cost, all utilities/costs expressed on a common scale. Net benefit is positive only if

\[
pdL>(1-p)fO+c.
\tag{5}
\]

This is bookkeeping intuition under the stated partition of cases, not a new optimality result. It explains why the method may work when updates create repeated, locally diagnosable compatibility problems and tests are cheap; it also explains why it loses when compatibility is already standardized, regressions are rare, checks are noisy or tests cost almost a full task.

The **harder and potentially more valuable hypothesis** is that learned obligations transfer to combinations not exhaustively tested. One possible explanatory model is

\[
S_x(d_u,d_v,h)=\mathbb E_{z\sim P_{d_u}(\cdot\mid x)}
[g_{d_v}(\psi_h(z,x),x)].
\tag{6}
\]

A small learned boundary representation \(\psi_h\) would capture what the consumer needs; then useful qualification may be shared across packages/compositions. This factorization requires sufficient represented information and a fixed relevant continuation; it is not assumed true merely because a message is well typed. Its predictive transfer and total-cost benefit must be tested against empirical pairwise matching. No linear sample-complexity or semantic-certification claim follows without further assumptions and proof.

## 5. Closest work and defensible novelty boundary

The [new primary-source cache](../../../references/aamas/problem_entry_20260922/sources.json) supplements the [earlier audit](../../../references/aamas/design_lock_20260922/evidence.json). The search is targeted, not an exhaustive priority proof.

| Work / inspection boundary | What it already covers and implication |
|---|---|
| [Modeling and Learning Synergy, AAMAS 2012](https://www.ifaamas.org/Proceedings/aamas2012/papers/5B_4.pdf), model/learning/team-formation sections | Learns individual capability and pairwise synergy from group outcomes. Nonadditivity, compatibility graphs and partner-sensitive selection are established |
| [Updates in Human-AI Teams, AAAI 2019](https://ojs.aaai.org/index.php/AAAI/article/view/4087), official abstract/record | Better individual models can disrupt teamwork; performance/compatibility tradeoff is established. Do not claim this phenomenon first |
| [AgentNet, NeurIPS 2025](https://papers.nips.cc/paper_files/paper/2025/hash/9a379c1b05793d1c42dc832269834515-Abstract-Conference.html); FlowEvo/PSN in the earlier audit | Experience specialization, organization, skill/workflow coevolution and typed/local repair are already close |
| [SkillMAS](https://arxiv.org/html/2605.09341v1), §§2.2–2.4; preprint v1, formal venue unverified | Shared retained evidence guides skill evolution and organization edits, with executor utility and bounded restructuring. Coupling skill learning with earned responsibilities is insufficient novelty |
| [Meta-Team](https://arxiv.org/html/2605.29790v1), §§3.1–3.2; preprint v1, formal venue unverified | Cross-agent evidence, downstream feedback, teammate profiles and three levels of evolution. Generic collaborative reflection and learned handoffs are insufficient novelty |
| [Pact](https://docs.pact.io/), official documentation | Consumer-driven executable integration contracts are established engineering. Automatically storing/checking a handoff contract is not itself new |
| [Learning Assumptions for Compositional Verification, TACAS 2003](https://link.springer.com/chapter/10.1007/3-540-36577-X_24), official record; related [2002 NASA report](https://ntrs.nasa.gov/citations/20030017771), method inspected | Automatically learning environmental assumptions and discharging them against other components predates this proposal. The report is not mislabeled as proceedings text |
| [Learning-based Assume-Guarantee Regression Verification, CAV 2016](https://homepage.iis.sinica.edu.tw/~bywang/papers/cav16.pdf), pp. 1–5, model/queries and reuse mechanism | Learns and reuses contextual assumptions to reduce repeated verification of evolving systems. Uses finite symbolic transition models and a mechanical teacher answering membership/equivalence queries. Our broad learning/reuse/cost slogan overlaps; stochastic black-box agents lack that teacher |
| [Weighted Automata in Compositional Reasoning about Concurrent Probabilistic Systems, POPL 2015](https://feihe.github.io/materials/popl15.pdf), pp. 503–504, abstract/introduction | Learns weighted assumptions for MDP components through a mechanical teacher. Stochasticity alone is also established; this limited inspection does not establish absence of finite-feedback alternatives |
| [Assumption Generation for Verification of Learning-Enabled Autonomous Systems](https://arxiv.org/html/2305.18372v1), abstract/model; 2023 preprint, venue unverified | Generates assumptions around opaque learned perception components using known finite controller/plant models and a safety property. Merely involving learned components is not sufficient distinction |
| [Trace-Based Assurance](https://arxiv.org/html/2603.18096v1), §§IV–V; preprint | Trace contracts, budgeted counterexample tests, boundary fault injection and regression coverage. No novelty claim for instrumentation/testing alone |
| [AgenTracer](https://arxiv.org/html/2509.03312v1), attribution/replay method; [Causal Agent Replay](https://arxiv.org/html/2606.08275v1), attribution formulation | Replay-based intervention/attribution are prior art; inspected versions do not establish this project's access or replay validity |
| [Allocating Training Instances to Learning Agents](https://www.cs.cmu.edu/~mmv/papers/14arms-LiemhetcharatVeloso.pdf), abstract/model; 2014 author paper, precise proceedings status not audited | Allocation of finite training opportunities to improve team coordination is established; entry C cannot claim this general idea |

The candidate contribution would be an effective way to **learn and reuse task-conditioned coordination requirements to qualify genuinely changed capabilities with less testing than pairwise/full-workflow re-evaluation**, accompanied by a controlled account of when it succeeds or fails. Learning/reusing assumptions, including probabilistic ones, is established; a possible remaining distinction is a useful finite-feedback procedure for stochastic black-box agents without exact component models or an equivalence oracle. That procedure is still missing, and this targeted search does not establish priority for it. A package-version table plus familiar tests, or substituting agents into a traditional verification story, is not enough. If the mechanism does not transfer obligations or materially improve adoption cost/quality, narrow the paper to a substantively demonstrated empirical finding or reject this entry.

## 6. Decisive evidence before another method lock

### 6.1 First establish that the problem exists in this setting

Use genuine training-derived old/new packages and independently adequate local assessments. Hold tasks, world states, downstream packages, budget and ordinary semantic interfaces fixed. Repeatedly estimate the package-by-partner comparison in Equation (2), including the unchanged-state control. Show uncertainty and all predeclared update cases, including improvements without regressions. Do not synthesize the main effect by deleting required fields, confusing units, degrading prompts or selecting a favorable weak model.

A competent universal semantic interface/canonicalizer is essential. If it cheaply removes the mismatch, the proposed problem reduces to ordinary integration hygiene. Irreducibly wrong local outputs are ordinary skill errors, not proof of collaboration incompatibility.

### 6.2 Then test the proposed distinction

| Control | What a gain would have to establish |
|---|---|
| Local-quality admission + competent common interface | Downstream compatibility matters beyond measured local competence |
| Contextual pairwise compatibility matching | Reusable obligations add something beyond observing successful pairs |
| Equal-budget integration/regression testing, random or coverage-based test selection | Gain is not just extra tests or a standard test-selection policy |
| Full-workflow validation within the same total budget | Local qualification saves useful cost without concealing missed interactions |
| Retain-old / pin-all-versions | Gain includes useful adoption, not simply refusing all change |
| Pooled same-learner with the same version/test library and context management | Value survives a capable centralized implementation |
| Meta-Team/SkillMAS or faithful closest feasible adaptation | Contribution survives current collaborative-evolution alternatives; formal baseline replacement requires a later frozen contract |

First study a fixed small workflow. Hold out entire package/consumer combinations and later entire workflow compositions; keep discovery/qualification cases separate from confirmation cases. A method that only memorizes observed pairs does not demonstrate transfer. Training replay needs verifiable snapshots and identical charged access for all methods. No live test-world rewind, hidden answer injection or free counterfactual simulator is added by this proposal.

Core measurements: local quality; team regression/improvement after updates; supported adoption coverage; false admission/rejection; success on untested combinations; qualification calls/tokens plus full total cost. A few vivid traces are explanatory, not the primary evidence.

AppWorld remains the first feasibility environment because the runtime is already audited and tasks have real state/dependencies. ScienceWorld remains a secondary candidate. Neither is inherently a multiagent compatibility benchmark. Their prior source pins and test boundaries remain protected; their final role and the six-arm matrix are reopened where this new question requires different evidence. No third dataset is selected here.

## 7. What is preserved and what is reopened

Preserved: acquired artifacts rather than invented personas; task-grounded evidence; reusable/composable workflows; equal model/tool opportunity; full cost; no gold in policy; official test integrity; historical negative evidence; strong pooled controls.

Reopened: the primary scientific question; exact-state reuse as the headline mechanism; unconditional two-PASS qualification; whether a role score can omit partner/input-distribution information; admission/qualification procedure; main comparison/estimand and final baseline matrix. Primitive state hashes remain necessary provenance, but do not replace behavioral evidence about changed collaborations.

Do not treat this discussion as a frozen new controller. The bounded predicate/procedure language, qualification-case selection, independent feedback access, admission rule and transfer split need an executable specification after the first development witness. The old 7,941-episode matrix is not authorized confirmation for this candidate. A-T04 is reopened; method-specific A-T05 work is no longer READY. Independent infrastructure/headroom work remains valid.

## 8. Final-lock decision

**Do not irreversibly lock v6 as a method. Retain its research question for one bounded specification/feasibility closure, without another narrative pivot.** This is the scientist's assessment with one independent skeptical review, not an official AAMAS review or acceptance prediction. Positive outcomes are not a prerequisite for preregistration; an executable, distinguishable intervention and a feasible observation protocol are. Freezing a hypothesis must not freeze its truth.

The v5 critique remains in the archival snapshot: weak residual distinction from competent matching, thin exact-state evidence coverage and an endpoint that did not establish evolution. V6 improves the decision problem but has not supplied the missing algorithm.

| Paper dimension | Current judgment | What prevents final lock |
|---|---|---|
| Importance and venue fit | Plausible coordination question; GAAI fit is credible | Natural frequency/severity after competent interfaces is unmeasured |
| Story coherence | Skills, earned responsibility and workflows form a coherent candidate chain | Acquired specialization/composition could become incidental to generic update testing |
| Originality | Broad assumption learning/reuse and compatibility management are established | No specified finite-feedback mechanism distinguishes the proposal from strong simple alternatives |
| Method completeness | An objective and record schema exist | No reproducible learner, test policy or adoption decision rule |
| Soundness | Useful uncertainty/feedback boundaries are acknowledged | Transfer relies on an unestablished sufficient boundary representation |
| Experimental feasibility | AppWorld infrastructure exists | Lawful semantic feedback, faithful replay and cost-saving qualification remain unverified |
| Evidence | Historical environment/headroom results only | No acquired-update interaction or transferable-qualification result |

### 8.1 Why the present intuition does not yet establish a method

Equations (1)–(2) define outcomes and a diagnostic interaction; (3) defines a record; (4) gives an objective; (5) states when checking could pay; (6) hypothesizes a useful representation. None specifies how to learn a requirement, select the next paid test, or decide adoption from the available history. The decisive work remains inside the verbs **learn, qualify and transfer**.

For Equation (6) to explain transfer, the representation must retain downstream-relevant information across the supported producer changes, with consumer and relevant continuation fixed. Agreement on observed cases does not establish this invariance. A constructed counterexample fixes a task and uses messages \(z=(a,b)\), abstraction \(\psi(z)=a\), local score \(Q(z)=a\), and downstream success \(Y=b\). Observed packages emit \((1,1)\); a new package emits \((1,0)\). Local quality and abstract observations agree perfectly, while downstream success reverses. Any predictor restricted to that shared abstraction has worst-case probability error at least 0.5 across these two cases. This is an identifiability counterexample, not evidence that AppWorld naturally exhibits the phenomenon. Its [arithmetic record](../../../artifacts/analysis/aamas2027/problem_entry_20260922/final_lock_reasoning.json) is explicitly synthetic.

Keeping the entire message/history could avoid this particular information loss, but would not explain compact transferable requirements or cheaper qualification. A new consumer, a changed task distribution and a changed continuation each introduce separate transfer assumptions; they cannot all be justified by one unseen-pair experiment.

The feedback issue is equally concrete. Public checks may not label semantic usefulness; a full continuation can supply a lawful training outcome but may cost nearly as much as full-workflow testing. Reusing the same qualification cases across adaptively proposed versions can overfit. Discovery, fresh validation, replay, retained state and rejected candidates all consume budget. Local audit acceptance is not independent task truth.

### 8.2 Conditions under which the idea is worth testing

There is a credible conditional intuition: repeated tasks may share a small number of stable consumer requirements; learned updates may sometimes violate these requirements; checking them may be cheaper than rerunning every complete combination. If all three conditions hold, retaining and selectively reusing qualification evidence can improve adoption at a fixed budget. If failures are idiosyncratic, a common interface removes them, or useful checks require full continuations, this advantage can disappear.

The retained innovations must have causal roles. Acquired artifacts must generate genuine behavior changes. Earned responsibility must change an adoption/binding decision using relevant evidence. Workflow memory must transfer useful requirements beyond storing observed pair outcomes. If every new pair requires an independent full test and a bespoke patch, the demonstrated result is update testing, not reusable organizational learning. A strong centralized implementation remains an essential comparator, not an automatic disqualifier for AAMAS.

### 8.3 Finite closure before a new method freeze

Complete the following outputs within the existing A-T03/A-T04 work; do not add another parallel plan. The next diagnostic contract must declare its native population, maximum candidate revisions, run/test budget and decision point **before any new model execution**. Numerical feasibility choices are still pending; this review does not silently authorize a pilot.

1. **Executable minimal policy.** Specify one finite predicate/handoff language, learner, candidate/test-selection rule, uncertainty treatment, accept/reject/UNKNOWN transitions, version retention and fallback. Acceptance: another researcher can determine the next action from the same history, budget and random seed. Include one worked trace and one abstention case; avoid an unspecified LLM judgment as the whole mechanism.
2. **Observation and intervention contract.** Enumerate what each component can see, which independent training outcomes are available, how snapshots/continuations work and what every query costs. Acceptance: small isolation/replay fixtures execute without evaluator leakage or a free oracle. Experimental measurement access must not silently become policy access.
3. **One exact transfer claim.** Define the held-out unit, fixed consumer/continuation, supported package changes and intended task distribution. State whether sufficiency is an assumption, an empirical hypothesis or a proved property. Acceptance: a concrete success/failure test beyond memorized pair identities; no simultaneous claim of arbitrary partner, distribution and composition transfer.
4. **Bounded development assessment.** Assess natural incompatibility, feedback reliability and actual qualification cost on the declared development population, retaining all candidates and outcomes. Acceptance: an auditable feasibility/stop decision and cost estimate. A favorable effect is not required to complete the task; do not keep changing tasks/backbones until the desired witness appears.
5. **A decisive confirmation contract.** Resolve the comparison capabilities in Section 6 into feasible nonredundant arms, including common interfaces, contextual matching and equal-budget regression-test selection. Freeze primary quality/cost criteria, useful-effect thresholds, uncertainty, independent splits and failure handling. Acceptance: a specified result could refute the contribution even if selected examples look good.

At that declared decision point, proceed only with an executable procedure whose remaining empirical uncertainty is honestly testable at feasible cost. Otherwise close this candidate as unsupported for the intended mechanism paper; do not rename it or add modules to bypass the failure. Development selection must be disclosed and confirmation remain independent. A scientifically substantial negative finding may support a separately stated paper, but is not an automatic fallback claim.

After a justified freeze, hold the hypothesis, algorithm and confirmatory protocol fixed and report the result. Integrity defects or newly invalid assumptions require a documented amendment or stopping decision; an instruction never to change the plan cannot make a false assumption true. AppWorld/ScienceWorld source pins remain preserved, while final benchmark roles and baseline implementations depend on closing the specification above. No confirmation runs are launched by this review.

## 9. First real empirical iteration

The [complete acquisition result](../../../artifacts/experiments/aamas2027/dev_20260922/report.md)
tests only the earliest link: whether a fixed package of procedures induced from
six actual training trajectories improves independent native task execution.
It uses the named idealab provider, qwen3.8-max, the original native prompt,
fresh AppWorld states and the unchanged official scorer. There were 329 real
benchmark/induction attempts, including unsuccessful requests and the declared
same-task acquisition replacement. No confirmation task was used.

Both treatment and control scored 6/6. There were no success wins or losses,
and no success flip in the two unchanged-agent repeats. The gate independently
fails for insufficient wins and one unwaived empty-text API response. Treatment
used 99 versus 96 attempted calls and 19.9% more known context tokens; induction
and acquisition add 102 calls. A decrease in output tokens does not establish a
uniform resource improvement. This does not support the useful-capability claim.

The [independent trajectory audit](../../../artifacts/experiments/aamas2027/dev_20260922/behavior_audit/review.md)
covered every pair with arm names masked before the key was revealed. Both arms
already perform most pagination, joins, deduplication and collect-before-update
procedures. Some checking and scheduling differ; the clearest case adds separate
archive-existence checks and manual deletion, increasing calls from 15 to 26.
No failure prevented by those extra checks was observed. This is exploratory
behavioral evidence, not a consumer interaction or a new mechanism result.

The story therefore remains conditional: first establish useful acquired
changes, then investigate whether downstream requirements can qualify them more
cheaply than competent alternatives. Source-linked summaries are an acquisition
baseline, not the innovation. Reusable finite-feedback qualification remains the
candidate distinction and still needs an executable learner and a real witness.
The empirical result does not justify adding a consumer module to manufacture
an interaction, claiming equivalence from six pairs, or declaring all AppWorld
tasks saturated.

The next independent diagnostic was the [planned complete dev census](../../../configs/aamas2027/headroom_census_v1.json),
already required by B5.2. It preserved all57 native IDs and competent settings,
but [stopped incomplete](../../../artifacts/experiments/aamas2027/headroom_20260922/report.md)
after the original outage and one documented infrastructure recovery.38 tasks
were attempted:33 protocol-valid successes,2 protocol-valid failures,3 UNKNOWNs;19 are unstarted.
The592 real requests include159 during recovery. Conservative success bounds
are33–55/57, so no full-population headroom/floor/ceiling verdict is available.
Both observed protocol-valid failures were audited; neither establishes a consumer
interaction. Acquisition v1 remains unpromoted and no new treatment follows.

The [concrete independent method review](AAMAS_Q1_FEASIBILITY_REVIEW_20260922.md)
distinguishes implementable conditional-memory regression screening from the
unestablished reusable qualification mechanism. The [zero-LLM replay fixture](../../../artifacts/experiments/aamas2027/replay_fixture_20260922/report.md)
also shows that database-only restoration does not restore REPL state; its native
teardown failure is retained. No method freeze or completed faithful-replay claim
is made. This bounded empirical cycle provides real evidence and reusable code,
not a resolved scientific contribution.
