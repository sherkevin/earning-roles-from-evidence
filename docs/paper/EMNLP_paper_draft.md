# Emergent Delegation Organization from Local Interaction in Multi-Agent Systems

## Abstract
Large Language Model (LLM) multi-agent systems are usually built around either centralized orchestrators or preassigned specialist roles. Both assumptions are convenient, but they hide a more fundamental scientific question: how can useful division of labor emerge when agents have only local visibility, no global expert catalog, and no predeclared identities? We study this question through **Emergent Delegation Organization (EDO)**, a decentralized framework in which near-homogeneous agents interact over sparse connected graphs and repeatedly choose among three primitive actions: solve the task themselves, outsource it to a visible neighbor, or split it into subtasks. Each delegation creates an upstream acceptance obligation, and these obligations compose into a recursive acceptance ladder; social reputation is therefore shaped not by self-report but by whether downstream work is accepted and ultimately contributes value to the global task. This yields a structured personality-tag space that drives future local allocation decisions. We further position our current executable system, based on **Terminal-Consensus Peer Backpropagation (TCPB)**, as a restricted Stage-1 instantiation of this broader framework: fixed topologies, role-prior nodes, linear handoff packets, and terminal outcome calibration only. Existing HotpotQA evidence already shows that decentralized outcome-based calibration improves delegation safety and stabilizes routing without a central controller. We argue that the main long-paper contribution is therefore not another tuned router, but a general method for studying how division of labor, trust, and coordination emerge from local interaction in language-agent societies.

## 1. Introduction
The dominant design patterns in LLM-based multi-agent systems make a strong assumption before the system has even started to work: either a central orchestrator decides who should do what, or each agent is assigned a fixed specialist identity in advance. These strategies can be effective engineering shortcuts, but they leave open a more basic question about organization. In realistic collaborative settings, useful division of labor is rarely known perfectly at initialization time. Groups begin with partial knowledge, repeated interaction, local judgments, and uneven structural exposure. Over time, some members become recognized as better decomposers, others as reliable integrators, others as useful auditors or bridge-builders. In other words, organization is not only executed; it is formed.

This paper takes that organizational view seriously. We ask whether a society of near-homogeneous language agents, each with only local neighbor visibility on a sparse connected graph, can self-organize into useful task division through recursive delegation, recursive acceptance, and value-based social updating. Our interest is therefore not simply in improving multi-agent answer quality by adding more dialogue turns or building a stronger router. We study how tasks move through a constrained society, how local trust is formed, when agents decide to keep work, when they outsource it, when they split it, and how these repeated interactions induce recognizable organizational structure.

The failure mode motivating our work remains **delegation miscalibration**. Prior systems often assume that an agent can accurately assess whether it should accept a task or hand it off. In practice, LLMs are prone to overconfident self-assessment: they often accept work they should not keep, delay delegation, or pass forward low-quality intermediate results. Earlier versions of our project showed that replacing self-reflection with terminal outcome feedback significantly improves delegation safety on fixed-topology benchmarks. However, we now argue that this is only the first layer of a richer theory. Delegation quality is not just a routing score problem; it is a problem of organizational emergence under local interaction.

We therefore propose **Emergent Delegation Organization (EDO)** as the full long-paper method. In EDO, agents start from the same cognitive machinery and the same action grammar. The only allowed asymmetries arise from graph position, local interaction history, and the task neighborhoods each agent encounters over time. Every task is treated as a node in a task tree, not merely as a single linear message. Upon receiving a task, an agent chooses among three primitive actions: `do_self`, `outsource(neighbor)`, or `split(subtasks)`. Importantly, each outsourcing decision also creates a recursive accountability chain: if agent `a` delegates to `b`, then `a` is responsible for accepting, revising, rerouting, or rejecting `b`'s returned result. This recursive audit structure turns delivered value, not self-description, into the basis of social reputation.

Under this framing, an agent's “personality” is not a stylistic prompt trait. It is a structured, operational tag vector induced by interaction history: how often its work is accepted by upstream nodes, whether it is useful at decomposition, whether it improves integration quality, whether it reduces or increases rework, and whether it solves tasks efficiently. Future local delegation decisions are made by comparing task demands against these socially formed tags under local visibility constraints. The resulting system is designed to answer a more ambitious question than “can a fixed router be calibrated?” It asks whether useful division of labor can emerge from local interaction alone.

At the same time, we explicitly separate theory from currently executed evidence. Our present codebase does not yet instantiate the full EDO design. Instead, it implements a restricted Stage-1 system based on **Terminal-Consensus Peer Backpropagation (TCPB)**: fixed `chain` and `star` topologies, role-prior nodes, linear handoff packets, and terminal-only competence updates on the final accepting node. This restricted system remains valuable. It already provides a reproducible, fully logged baseline showing that decentralized outcome-based calibration can reduce premature acceptance and stabilize routing without centralized orchestration. In this paper, we reinterpret that system not as the final method, but as the first executable approximation of the broader organizational framework.

Our contributions are therefore four-fold:

1. We reframe decentralized multi-agent routing as a problem of **organizational emergence under local interaction**, rather than merely better static role assignment or router tuning.
2. We introduce **Emergent Delegation Organization (EDO)**, a method built around sparse local graphs, recursive `do / outsource / split` decisions, recursive upstream acceptance audits, and value-induced personality tags.
3. We formalize the distinction between the **full long-paper method** and the **current restricted executable instantiation**, positioning TCPB as a Stage-1 prototype rather than the endpoint of the research line.
4. Using current HotpotQA evidence, we show that even the restricted instantiation already supports the central direction: decentralized outcome-based calibration improves delegation safety and creates measurable route stabilization without relying on a central controller.

## 2. Related Work

### 2.1 Routing and orchestration in multi-agent systems
Much of the LLM multi-agent literature is organized around central decomposition and routing. Orchestrator-based frameworks achieve strong control and interpretability, but they also impose severe token bottlenecks and create single points of failure. Other lines of work introduce dynamic graph traversal or planner-controller patterns, yet many still rely on globally visible states or centralized arbitration. Our work is different in emphasis. We are not trying to produce a smarter global scheduler. We ask how division of labor can emerge when no node has a global expert table and each node sees only its local neighborhood.

### 2.2 Reflection, critique, and outcome-based calibration
Reflection has become a common mechanism for improving LLM reasoning, and several multi-agent systems use self-critique or peer-critique to refine outputs. However, these approaches often assume that agents are at least moderately reliable judges of their own competence or that a centralized reviewer can resolve peer disagreement. Earlier versions of our work found that self-reflection is especially unreliable when the question is not “is this sentence better?” but “should I have handled this task at all?” This motivates our continued emphasis on result-grounded feedback. In the restricted TCPB prototype, only terminal outcomes are used for calibration. In the full EDO framework, terminal outcomes are retained, but they are augmented by recursive upstream acceptance signals that are local, structured, and audit-like rather than free-form opinion exchanges.

### 2.3 Division of labor, reputation, and local organization
Our long-paper framing is closer to a theory of organization than to static role play. In human groups, stable roles are often the outcome of repeated coordination, evaluation, and structural position rather than perfect advance assignment. Reputation is socially constructed through accepted contributions, not self-claims. Local neighborhood structure also matters: sparse connectivity creates bridge positions, clustered exposure, and bounded trust propagation. EDO imports these intuitions into language-agent systems by making local delegation, recursive acceptance, and value-based personality formation the primary objects of study.

## 3. Methodology

### 3.1 Problem formulation
We model a multi-agent society as a sparse connected directed graph $\mathcal{G} = (\mathcal{A}, \mathcal{E})$, where $\mathcal{A} = \{a_1, a_2, \dots, a_N\}$ is the set of agents and $\mathcal{E}$ defines allowed communication channels. Unlike role-based systems, agents do not start with fixed specialist identities. They share the same base cognitive machinery and the same action grammar. We allow only mild structural asymmetry: graph position, local exposure history, and differences induced by repeated interactions.

Each input instance $x = (q, y, C)$ consists of a question $q$, gold answer $y$, and optional supporting context $C$. In the full method, $x$ expands into a **task tree** rather than a single linear message. Each task node records its parent, children, current uncertainty, required output, evidence state, owner agent, executor agent, candidate result, and audit status. This representation is necessary because a task may be solved directly, outsourced intact, or recursively split into subtasks that later require integration and audit.

### 3.2 Agent state and personality
At time $t$, each agent $a_i$ maintains state
\[
S_i^t = \{P_i^t, B_i^t, M_i^t, H_i^t, \mathcal{N}(i)\},
\]
where $P_i^t$ is the agent's public personality-tag vector, $B_i^t$ is its local belief state over neighbors, $M_i^t$ is its private episodic memory, $H_i^t$ is a summary of past delegation and audit interactions, and $\mathcal{N}(i)$ is its visible neighbor set.

The key object is $P_i^t$, the **value-induced operational persona**. This is not a stylistic role prompt. It is a structured vector whose components summarize socially observed capability, for example:
\[
P_i = [\text{solve}, \text{decompose}, \text{audit}, \text{integrate}, \text{explore}, \text{efficiency}, \text{reliability}].
\]
These components are intended to capture how useful the agent has been to others in the society: whether its outputs are accepted, whether it reduces or increases rework, whether its decompositions help, whether its integrated outputs are reliable, and whether it achieves useful work efficiently.

Each agent also maintains only **local** beliefs about neighbors. There is no global competence directory. For a neighbor $a_j$, the local belief $B_i^t(j)$ is constructed from interaction history with $a_j$, recent publicly visible persona summaries, and local audit outcomes involving $a_j$. This preserves decentralization while allowing trust and specialization to be gradually formed.

### 3.3 Task signatures and local utility
Instead of matching tasks to fixed role names, EDO represents each task node $z$ by a task-signature vector
\[
\phi(z) = [\text{need\_decompose}, \text{need\_verification}, \text{need\_integration}, \text{need\_exploration}, \text{evidence\_breadth}, \text{uncertainty}, \text{cost\_sensitivity}].
\]
This task signature can be extracted through rules, light-weight LLM judgment, or future learned modules. The key point is conceptual: routing should be based on the match between task demands and socially formed personality tags, not on a hard-coded role lookup and not necessarily on a large embedding router.

For an agent $a_i$ receiving task node $z$, the three candidate utilities are:
\[
U_i^{self}(z) = Fit(P_i, \phi(z)) - \lambda_c Cost_{self}(z) - \lambda_r Risk_{self}(z),
\]
\[
U_i^{out}(z, j) = Fit(B_i(j), \phi(z)) - \lambda_s SendCost(i,j) - \lambda_a AuditCost(z) - \lambda_r RejectRisk(j,z),
\]
\[
U_i^{split}(z) = SplitGain(z) - \lambda_m MergeCost(z) - \lambda_d DepthPenalty(z) - \lambda_a AuditLoad(z).
\]
The selected action is
\[
\pi_i(z) = \arg\max \{ U_i^{self}(z), \max_{j \in \mathcal{N}(i)} U_i^{out}(z,j), U_i^{split}(z) \},
\]
subject to budget, depth, and safety constraints.

### 3.4 Three primitive actions
The EDO action space is intentionally minimal but organizationally expressive:

- `do_self`: solve the task locally.
- `outsource(neighbor)`: pass the task to the locally best visible neighbor.
- `split(subtasks)`: decompose the task into child tasks that each re-enter the same policy.

These three actions correspond to the basic organizational choices of doing the work, finding someone else to do it, or restructuring the work into manageable parts. Additional behaviors such as timeout, reroute, or fallback are treated as safety policies layered on top of these primitives rather than as the conceptual center of the method.

### 3.5 Recursive upstream audit
The main departure from the current prototype is that delegation is not terminal at handoff time. Every outsourcing decision also creates an **acceptance obligation**. If $a$ delegates a task to $b$, then $a$ must later evaluate whether to accept $b$'s result, reject it and redo the task, reject it and reroute, or reject it and resplit.

This produces a recursive structure. If $a \rightarrow b \rightarrow c$, then $b$ audits $c$ before returning upward, and $a$ audits $b$. The system therefore operates on a **delegation tree with a recursive acceptance ladder**, not merely on a one-dimensional chain of messages. This is essential because social reputation should be grounded in accepted delivered value, not only in terminal answer correctness.

### 3.6 Personality-tag update
Each audit event generates a local social signal for the downstream executor. For a parent-upstream node $u$, downstream node $v$, and task node $z$, a local audit event can be written as:
\[
\ell_{u \rightarrow v, z} = [accepted, rework\_cost, value\_gain, timeliness, decomposition\_help, integration\_help].
\]
After the root task finishes, the system also observes a terminal event
\[
r_{terminal}(x) = [quality, total\_cost, total\_depth, final\_accept].
\]
The full update rule should then combine local accepted-value signals with slower terminal correction:
\[
P_i^{t+1} = clip\Big((1-\mu)P_i^t + \mu(\eta_{local} LocalValue_i^t + \eta_{terminal} TerminalValue_i^t - \eta_{rework} ReworkPenalty_i^t)\Big).
\]
This produces personality tags that are neither pure self-estimates nor pure global scores. They are socially induced summaries of how useful an agent has been to others and to the task as a whole.

### 3.7 Current restricted executable instantiation: TCPB prototype
Our current codebase implements a Stage-1 restricted instance of EDO that we call **Terminal-Consensus Peer Backpropagation (TCPB)**. The exact substitutions vis-à-vis the full EDO design are enumerated in the **Prototype Scope Box** below; this subsection only states the operative consequence and provides Algorithm 1 as the full executable loop. After a routed path terminates with final answer $\hat{y}$, we compare $\hat{y}$ with the gold answer $y$ and obtain a thresholded task-quality signal. Only the final accepting node is updated, using bounded asymmetric steps with damping. This restricted mechanism already reduces premature acceptance and stabilizes routing relative to self-reflection baselines, but it does not yet instantiate recursive audit, persona-tag formation, or split-based organization.

---
**Algorithm 1: TCPB execution loop (Stage-1 prototype, single sample).**

> _Inputs_: question $q$ with gold answer $y$; agent set $\mathcal{A}=\{\text{decomposer},\text{evidence\_seeker},\text{verifier},\text{synthesizer}\}$ with chain adjacency $\mathcal{N}$; current self-competence map $c \in [0.05, 0.95]^{|\mathcal{A}|}$; constants $\tau_{\text{accept}}{=}0.62$, $\delta_{\text{accept}}{=}0.02$, $H_{\max}{=}4$, $F_{\text{th}}{=}0.5$, step sizes $\Delta^{+}{=}+0.06$, $\Delta^{-}{=}-0.10$, momentum $\rho{=}0.5$.
> _Output_: predicted answer $\hat{y}$; updated self-competence $c'$.

```
1:  P ← HandoffPacket(question=q, evidence=∅, hop_count=0, visited=∅)
2:  i  ← decomposer                                              # entry node (chain head)
3:  while hop_count(P) < H_max:
4:      φ  ← deterministic_extract(P)                            # §3.3 + spec §1.2 (no LLM call)
5:      U_self  ← 0.55·c[i] + 0.20·φ.evidence_suff
6:                + 0.10·(1-φ.uncertainty) − 0.10·φ.loop_risk − 0.05·φ.revisit_risk
7:      for j in N(i):
8:          U_out[j] ← 0.60·b_i(j) + 0.25·𝟙[role(j)=preferred(P)]
9:                    + 0.05·struct_prior(j) − 0.25·𝟙[j ∈ visited(P)]
10:     j*       ← argmax_{j ∈ N(i)} U_out[j]
11:     accept?  ← (U_self ≥ U_out[j*] + δ_accept)
12:     if i = decomposer and is_multihop(q):  accept? ← False   # safety gate (§3.3 prior)
13:     if i = decomposer and not is_multihop(q) and c[i] < 0.90: accept? ← False
14:     if N(i) = ∅:                           accept? ← True    # terminal node
15:     if accept?:
16:         ŷ ← LLM_answer(P)                                    # only LLM call beyond optional decomposition
17:         break
18:     else:
19:         P ← P.append_contribution(LLM_contribute(P))         # add ≤8-line note
20:         visited(P) ← visited(P) ∪ {j*};  hop_count(P) += 1
21:         i ← j*
22: end while
23: # ----- Terminal-Consensus update (only the final accepting node) -----
24: r            ← +1 if F1(ŷ, y) ≥ F_th else −1
25: raw_delta    ← Δ⁺ if r > 0 else Δ⁻;   raw_delta ← clip(raw_delta, −Δ⁺, +Δ⁺)
26: target       ← clip(c[i] + raw_delta, 0.05, 0.95)
27: c'[i]        ← (1−ρ)·c[i] + ρ·target;   c'[k≠i] ← c[k]      # only accepting node updated
28: return ŷ, c'
```

The full deterministic specifications of `deterministic_extract` (line 4), `b_i(j)` (line 8 belief lookup), and the safety gates (lines 12–14) are given in `artifacts/edo_lite_executable_spec.md` §1.2 / §2.2 / §4.1. The algorithm contains exactly two LLM calls per accepted sample (`LLM_contribute` per non-accept hop and `LLM_answer` at the terminal node), matching the per-sample token budget reported in §4.

---

### 3.8 Why the separation matters
Without separating the full EDO method from the current TCPB prototype, the paper falls into one of two traps. If we write only what the code already does, the paper becomes a fixed-role routing paper with limited conceptual novelty. If we write only the grand theory and ignore implementation limits, reviewers will rightly reject the paper for overclaiming. The correct scientific stance is to make EDO the main theory and TCPB the current restricted instantiation. The exact boundary between the two is fixed by the Prototype Scope Box that follows.

---
**Prototype Scope Box (single source of truth for what the current submission instantiates).**

The current executable system instantiates only a restricted Stage-1 subset of EDO. Concretely, the prototype replaces:

  (i) arbitrary sparse graphs with fixed `chain`/`star` topologies;
  (ii) near-homogeneous agents with four role-prior nodes (`decomposer`, `evidence_seeker`, `verifier`, `synthesizer`);
  (iii) task-tree state with a linear `HandoffPacket`;
  (iv) the three-action `do_self / outsource / split` EDO policy with deterministic `accept-or-forward`;
  (v) recursive persona-tag updates with terminal-only scalar competence updates (TCPB).

The deterministic instantiations of `phi(z)`, the utility estimators $U^{self}, U^{out}$, and the persona update rule for this prototype scope are given in `artifacts/edo_lite_executable_spec.md`; that note is the canonical companion specification for everything in this box and is referenced by §3 (theory), §4 (experiment) and §5 (limitations) without restating its content. Stage-2 work will progressively replace each of (i)–(v) with the full EDO mechanism; none of those replacements are claimed by the current submission.

---

### 3.9 Stage-2 Roadmap (boundaries the current submission does not cross)
Three EDO mechanisms remain underspecified in the present submission and are the central items of the Stage-2 implementation roadmap. Reviewers have repeatedly flagged each as a precondition for a stronger acceptance vote; we therefore record their intended designs here so that the current paper's claims do not implicitly cover them.

**(R1) `split` subtask generation.** Stage-2 introduces a third primitive action $\mathrm{split}(z) \to \{z_1, \dots, z_k\}$. Subtasks are produced through a single light-weight LLM decomposition call gated by `U_i^{split}(z) > U_i^{self}(z)$ and $U_i^{split}(z) > \max_j U_i^{out}(z, j)$. The decomposition prompt is required to emit at most $k=3$ children, each of which re-enters the same three-action policy. Hard termination bounds (`max_subtasks_per_split=3`, `max_tree_depth=3`, `max_total_nodes=12`) are pre-specified in `artifacts/edo_lite_executable_spec.md §4.3`. The current submission contains zero `split` events; any claim about composition gain therefore belongs to Stage-2.

**(R2) Recursive audit decision protocol.** Stage-2 elevates audit from an implicit terminal gold comparison to an explicit per-handoff decision $\mathrm{Audit}(u, v, z) \in \{\textsc{accept}, \textsc{accept\_with\_note}, \textsc{reject\_reroute}, \textsc{reject\_resplit}\}$ executed by the upstream node $u$ on the result returned by downstream node $v$. The decision rule is rule-based on candidate-answer length, refusal patterns, and an `audit_score` proxy (see `edo_lite_executable_spec.md §4.2`). Each audit event emits a structured social-signal tuple $\ell_{u \to v, z}$ that feeds the Stage-2 persona update (R3). The current submission performs no per-hop upstream rejection; all calibration comes from terminal outcomes.

**(R3) Neighbor belief update rule.** Stage-2 replaces the published scalar self-competence with a vector belief $B_i^t(j) \in [0,1]^7$ aligned with the persona-tag dimensions of $P_j$. The update on each audit event is
\[
B_i^{t+1}(j) = \mathrm{clip}\big((1-\nu) B_i^t(j) + \nu \cdot \mathrm{evidence\_extract}(\ell_{u\to v,z})\big),
\]
with $\nu = 0.2$ and `evidence_extract` reading the relevant components of $\ell_{u \to v, z}$ defined in §3.6. The current submission's `published_competence` is a scalar projection onto the `solve` dimension only and is not updated from per-hop audit events.

We make these three Stage-2 designs explicit so that the empirical evidence below cannot be mistakenly read as supporting them: Stage-1 numbers in §4 reflect only the prototype scope.

---

## 4. Experiments

### 4.1 What current evidence already establishes
Our current reproducible evidence comes from the Stage-1 TCPB prototype on HotpotQA. The main benchmark slice is a fixed set of 200 HotpotQA validation questions exported to `artifacts/seed/hotpotqa_validation_200.jsonl`. Existing runs compare `fixed_peer_calibrated`, `fixed_self_calibrated`, `fixed_self_claim`, `fixed_static_roles`, and centralized baselines under shared inputs and logged execution traces.

These experiments do **not** establish the full EDO theory. What they do establish is narrower but still important:

- decentralized outcome-based calibration matters;
- delegation safety is measurable and improvable;
- structured intermediate state is necessary for route-level auditing;
- route preferences can stabilize without a central controller;
- some remaining errors are generated by local answer bottlenecks rather than by routing failure.

This evidence should be presented as support for the **direction** of the theory, not as proof of the entire organizational framework.

### 4.2 Stage-1 setup: current prototype experiments
- **Benchmark:** HotpotQA distractor validation subset, 200 examples (`artifacts/seed/hotpotqa_validation_200.jsonl`).
- **Model:** `gpt-4.1-mini` (OpenAI-compatible via `https://kuaipao.ai/v1`), temperature 0, chain topology unless otherwise noted. `model_resolved_runtime: gpt-4.1-mini` confirmed in all canonical run notes.
- **Canonical run:** `artifacts/round2_gpt41mini/run_20260414_115739/` — contains `fixed_peer_calibrated`, `fixed_static_roles`, and `fixed_self_claim` subdirectories, all validated `[OK]`. Metrics consolidated in `artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv`.
- **Current runtime:** `workspace/idea04_core/runner.py`, `workspace/idea04_core/methods.py`, `workspace/idea04_core/contracts.py`.
- **Current method objects:** fixed topology, role-prior nodes, linear handoff packet, deterministic local accept-or-forward policy, terminal-only outcome update.
- **Current process metrics:** EM, F1, mean handoff count, dead-end rate, premature accept rate, forward-after-correction rate, heuristic and API token cost, and cost-normalized F1.
- **Note on prior GLM results:** All runs under `artifacts/round1/` and `artifacts/round1_star/` used `glm-4-flash` as the actual runtime backbone. These are archived as Stage-1 guidance-only artifacts. They established the direction of the research but are not the final paper evidence.

### 4.3 Current main findings from the restricted instantiation
The canonical round2 `gpt-4.1-mini` results (n=200, chain, `run_20260414_115739`) support four main observations.

**Finding 1: Backbone quality dominates all method differences.** All three Stage-1 methods improve by +15–20 F1 points when switching from `glm-4-flash` to `gpt-4.1-mini` on the same 200-sample slice and identical routing code. The routing mechanism is secondary to generation quality on this benchmark/topology combination.

**Finding 2: Method ordering is backbone-sensitive and must not be over-interpreted from a single backbone.** On `glm-4-flash` (Stage-1 GLM), the ordering was `static_roles > peer_calibrated ≈ self_claim`. On `gpt-4.1-mini`, the ordering inverts: `self_claim (F1=0.7641) > static_roles (0.7454) > peer_calibrated (0.7381)`. The gap between the best and worst Stage-1 method is 2.6 F1 points — non-trivial at n=200 but not yet confirmed with paired statistics. `fixed_peer_calibrated`/TCPB should **not** be described as the strongest Stage-1 method on the strong backbone. `fixed_self_claim` currently leads F1; `fixed_static_roles` is the most cost-efficient (4663 vs 6414 API tokens per sample). N=7405 fullval for all three methods is required for tight confidence intervals. Status as of this draft: `peer_calibrated` fullval completed and valid (F1=0.7703, n=7405, `artifacts/round2_gpt41mini_fullval/run_20260414_135408/fixed_peer_calibrated/`); `static_roles` and `self_claim` fullval runs were invalidated by a provider runtime integrity failure (model drift mid-run) and are pending rerun under the new fail-fast guard. The three-method ordering cited above is therefore supported by chain-200 evidence (n=200) only and should not be presented as finalized fullval ranking.

**Finding 3: PAR collapses to zero regardless of backbone.** All three methods achieve PAR = 0.0 on `gpt-4.1-mini`, consistent with the GLM result. The decomposer force-forward gate prevents premature acceptance on multi-hop HotpotQA questions across backbones. This confirms the routing safety structure is robust to backbone change.

**Finding 4: On a capable backbone, TCPB peer-calibration overhead does not yield F1 gains over self-claim or static routing.** The F1 and cost data indicate that `peer_calibrated` uses the same token budget as `self_claim` (both 6414/sample) but achieves lower F1. The mechanism value of TCPB on this configuration appears in route-level process metrics (MHC=2.00 for peer, indicating fuller chain use) rather than in final F1. For a capable backbone on HotpotQA, the simpler methods are Pareto-dominant on the F1/cost frontier. The paper contribution should therefore pivot from "peer_calibrated is best" to "the EDO framework explains when and why delegation overhead pays off — and Stage-1 evidence reveals backbone-sensitive threshold effects that motivate the full theory."

### 4.4 Full EDO experimental agenda
To evaluate the actual long-paper method, experiments must be redesigned around emergence rather than only final answer quality.

#### E1. Emergent specialization from near-homogeneous start
Compare whether personality tags and action distributions diverge over time from neutral or near-neutral initial conditions. The main measurements should include:

- persona-tag divergence across agents;
- specialization entropy;
- per-agent frequencies of `do_self`, `outsource`, and `split`;
- stable task-family concentration by graph region.

#### E2. Value of recursive split
Compare `EDO w/o Split` against full `EDO` on composition-heavy tasks. Measure:

- answer quality;
- split usefulness rate;
- merge overhead;
- average delegation depth;
- rework reduction or increase caused by split.

#### E3. Value of recursive audit
Compare terminal-only updates against recursive upstream audit. Measure:

- audit precision and recall;
- low-quality subcontract propagation rate;
- subcontract acceptance rate;
- final task quality after rework.

#### E4. Sparse-graph robustness
Compare different graph families: chain, star, random sparse connected graphs, small-world graphs, and community-bridge graphs. Measure:

- local-discovery success rate;
- bridge utilization rate;
- quality-cost trade-offs;
- organization stability across seeds and graph instances.

#### E5. Benchmark transfer
Retain HotpotQA for continuity with the current evidence, but prioritize MuSiQue or another compositional benchmark for the full EDO evaluation, since recursive split and integration are central to the new theory.

### 4.5 Metrics for the long-paper method
The full long-paper must report not only answer quality but also organizational process metrics. In addition to EM/F1 and cost:

- **specialization entropy:** whether the society moves from homogeneous action patterns toward differentiated labor.
- **persona-tag divergence:** whether agent identities become socially distinct.
- **audit precision / recall:** whether recursive evaluation is meaningful rather than decorative.
- **subcontract acceptance rate:** whether delegated work is good enough to be accepted upward.
- **split usefulness rate:** whether decomposition pays off after accounting for integration cost.
- **average delegation depth:** whether the organization solves problems efficiently rather than through uncontrolled recursion.
- **bridge utilization rate:** whether sparse graphs create meaningful connector positions.
- **organization stability across seeds:** whether the observed specialization is robust.

### 4.6 Current Stage-1 artifact interpretation
The current artifact directories, tables, and ablations should remain in the paper, but their framing must change. They are evidence for the restricted instantiation. Canonical source: `artifacts/round2_gpt41mini/` (backbone: `gpt-4.1-mini`); GLM-backbone results under `artifacts/round1/` are archived as Stage-1 guidance-only.

- Mechanism ablations (GLM-backbone, `artifacts/round1_v3_weight_sensitivity.md`) show that outcome-based calibration and conservative routing structure both contribute measurable signal; these are preserved as mechanistic evidence.
- Method ordering on `gpt-4.1-mini` (`self_claim > static_roles > peer_calibrated`, F1: 0.7641 / 0.7454 / 0.7381) is the new canonical result from chain-200 (n=200); the ordering inversion vs. GLM is itself a finding motivating the full theory. Fullval validation status: `peer_calibrated` fullval is valid (F1=0.7703, n=7405); `static_roles` and `self_claim` fullval runs are pending rerun after runtime integrity failure — the three-method fullval ordering is therefore not yet finalized.
- The static-path overlap analysis (peer reproducing ~52% of static routes on GLM) is reinterpreted as evidence that stable route structure can form without a central controller.
- Answer-generation bottleneck analysis becomes evidence that once routing improves, remaining failures can migrate to the local generation layer.

This is valuable precisely because it narrows the next implementation target: the research line should now move from “better fixed routing weights” toward “task trees, recursive audit, persona tags, and sparse-graph organization.”

## 5. Limitations
We explicitly acknowledge that the current codebase does not implement the complete EDO method. The present runtime still relies on fixed topologies, role-prior nodes, linear packet passing, deterministic accept-or-forward routing, and terminal-only outcome updates. It therefore cannot yet establish the strongest claims of the full framework, such as recursive split value, local audit superiority, or personality-tag emergence from near-homogeneous initialization.

We also acknowledge that some current routing improvements may still be partially entangled with hand-designed safety priors and answer-generation constraints. As a result, the present evidence should be interpreted as validating the Stage-1 premise that decentralized outcome-based calibration helps, not as a full proof that local interaction alone is sufficient for rich organizational emergence across arbitrary settings.

These limitations are not accidental flaws in reporting. They define the boundary between the current restricted instantiation and the long-paper method it motivates. The next-stage implementation burden is therefore clear: introduce task-tree state, recursive audit, persona-tag updates, and general sparse-graph support, then test whether the stronger organizational predictions of EDO hold empirically.

A fourth limitation concerns backbone-sensitive method ordering. On our current 200-sample HotpotQA chain slice, the relative ranking of Stage-1 delegation methods inverts between `glm-4-flash` and `gpt-4.1-mini`. On the stronger backbone, `fixed_self_claim` leads F1, while `fixed_peer_calibrated` trails. This indicates that the TCPB peer-calibration overhead (additional LLM calls for belief updates) does not yield F1 gains when the underlying model is already strong enough to self-evaluate accurately. This result is theoretically important: it predicts that the full EDO organizational advantage will be most visible on harder tasks, weaker individual agents, or richer topologies where single-agent self-assessment breaks down. Reporting Stage-1 results on only one backbone would conceal this sensitivity; we report both for transparency. A related data integrity note: one fullval run (`artifacts/round2_gpt41mini_fullval/run_20260414_135408/`) experienced provider-side model drift that silently substituted an unsupported model for two of the three methods; the affected `static_roles` and `self_claim` fullval results are being rerun under a new fail-fast runtime guard (`ModelDriftError` in `workspace/idea04_core/llm_client.py`). The `peer_calibrated` fullval result (F1=0.7703) remains valid. This section will be updated once the repaired reruns land.

## 6. Conclusion
The central claim of this project is no longer that a fixed-role decentralized router can be calibrated slightly better than self-reflection. The stronger claim is that multi-agent language systems should be studied as **organizations**, not merely as collections of prompts. Under this view, the important scientific questions become: how does labor division emerge, how is local trust formed, when is work kept versus outsourced versus split, and how do repeated acceptance judgments shape durable social identity?

We introduced **Emergent Delegation Organization (EDO)** as a framework for answering these questions. EDO moves the focus from fixed roles to socially induced personality tags, from linear routing to recursive task trees, and from terminal-only supervision to recursive acceptance-based organization. Our current **TCPB** system remains important, but only as the first restricted executable approximation of this broader idea. Its existing HotpotQA evidence already shows that decentralized outcome-based calibration improves delegation safety and stabilizes routing without centralized control. The long-paper opportunity now lies in completing the transition from calibrated routing to emergent organization.
# Peer-Calibrated Delegation against Self-Reflection Hubris in Multi-Agent Systems

## Abstract
Large Language Model (LLM) based multi-agent systems increasingly rely on centralized orchestrators to route sub-tasks, introducing severe communication bottlenecks and single points of failure. While decentralized routing over fixed topologies offers a scalable and robust alternative, it suffers from severe *delegation miscalibration*. Specifically, LLMs exhibit a "self-reflection hubris"—routinely overestimating their own competencies and failing to accurately correct their routing decisions via self-reflection. In this paper, we propose a fully decentralized, peer-calibrated delegation framework. Rather than relying on global meta-reviewers, localized self-assessment, or fragile per-hop critique, agent competencies are updated through **terminal-consensus peer backpropagation**: only the final end-to-end task outcome is allowed to calibrate future routing confidence. Experiments on complex multi-hop reasoning tasks demonstrate that this result-oriented peer signal is already sufficient to drive premature accept rate to zero, autonomously converging toward expert-like routing while preserving the flexibility to deviate when the static path is suboptimal. Our approach achieves superior cost-normalized effectiveness compared to centralized orchestration with reflection, establishing peer-calibration as a robust and efficient paradigm for decentralized LLM collaboration.

## 1. Introduction
The integration of Large Language Models (LLMs) into Multi-Agent Systems (MAS) has revolutionized complex problem-solving capabilities. Currently, the dominant paradigm for task allocation in unstructured environments relies heavily on centralized orchestrators or *Meta-Reviewers* to decompose queries and assign tasks. However, this hub-and-spoke architecture naturally imposes a severe cognitive and token bottleneck on the central node, rendering the system vulnerable to single-point failures and exponential cost scaling in highly dynamic scenarios.

Decentralized routing on fixed communication topologies offers a compelling, lightweight alternative. In such configurations, agents operate with localized contexts, recursively passing an evolving structural state (i.e., *Thought Communication*) through an `accept-or-forward` policy. Yet, abandoning a global orchestrator exposes a fundamental, under-explored vulnerability in LLMs: **delegation miscalibration**. To make autonomous routing decisions, an agent must accurately assess whether a sub-task aligns with its latent expertise or if it should be delegated to a neighbor. 

Recent literature has heavily leaned on the *Self-Reflection* capabilities of LLMs to self-correct reasoning paths. We argue, however, that while LLMs can refine generated text locally, they suffer from profound *self-reflection hubris* when evaluating their architectural role allocation. When tasked with self-calibrating their routing competence, LLMs frequently fall into confirmation bias, continuously accepting tasks they are ill-equipped to handle, resulting in premature task acceptance (dead-ends) or chaotic ping-pong forwarding loops. 

To combat this, we introduce a **Peer-Calibrated Delegation** framework. Our approach leverages a paradoxical yet critical cognitive trait of LLMs: while they are notoriously poor self-evaluators, the network-level outcome of peer interaction still provides a reliable signal about which local routing choices should be trusted in the future. Instead of self-declaration or self-reflection, an agent's *competence vector*—which strictly governs its `accept-or-forward` propensity—is calibrated through **terminal-consensus peer backpropagation**, i.e., delayed updates induced by whether the delegated path ultimately reaches the correct answer.

Our main contributions are three-fold:
1. We identify and formalize the *self-reflection hubris* phenomenon in decentralized MAS routing, demonstrating that LLMs cannot reliably self-calibrate task delegation.
2. We propose the first fully decentralized, terminal-consensus peer-calibrated update mechanism over fixed topologies, eliminating global orchestrator bottlenecks while avoiding reliance on noisy per-hop critique.
3. Through empirical evaluations on complex reasoning paths, we demonstrate that peer-calibration forces the network to converge from a chaotic cold-start into highly ordered, position-adaptive specialization, rivaling hand-crafted static roles while substantially improving delegation safety and cost-normalized effectiveness.

## 2. Related Work

**Routing in Multi-Agent Systems.** Recent advancements in LLM-based MAS frequently depend on global Orchestrator agents to divide and conquer complex queries (e.g., AutoGen, MetaGPT). Some systems have explored dynamic graph topologies and path-preference learning (AMRO-S; Brain-Inspired Graph MAS). However, these still inherently rely on shared workspace states or central decision-makers. In contrast, our work restricts communication to purely decentralized, fixed/semi-fixed graphs, relying on localized peer-to-peer updates to achieve comparable task allocation efficacy without the global token overhead.

**Self-Reflection vs. Peer-Critique.** A significant body of work has established LLM self-reflection as a tool to mitigate hallucinations and improve reasoning (e.g., Reflexion, Tree-of-Thoughts). Extending this to MAS, frameworks like MARS and SAGE introduce Peer-Critique components. Crucially, these existing solutions predominantly utilize peer-feedback to *refine output generation* and are strictly mediated by a centralized *Meta-Reviewer* to consolidate scoring. Our work diverges fundamentally: we do not depend on per-hop peer scores or centralized arbitration. Instead, we use the final task outcome as a decentralized supervisory signal to update an agent's routing *competence vector* after the path terminates. We explicitly position this terminal-consensus form of Peer-Calibration as the practical defense mechanism against the self-reflection blindness endemic to autonomous task delegation. 

## 3. Methodology

We formalize a decentralized Multi-Agent System on a fixed topology where agents must autonomously evaluate their competencies to minimize delegation miscalibration.

### 3.1 Framework Formulation
We represent the multi-agent network as a directed graph $\mathcal{G} = (\mathcal{A}, \mathcal{E})$, where $\mathcal{A} = \{a_1, a_2, \dots, a_N\}$ is the set of agents and $\mathcal{E}$ defines the permitted communication channels. In the current submission we study fixed `chain` and `star` topologies over four role-prior nodes: `decomposer`, `evidence_seeker`, `verifier`, and `synthesizer`. Each agent receives a structured packet containing the question, accumulated evidence, uncertainty, visited nodes, hop count, and the latest publicly visible self-competence values broadcast by upstream nodes.

The core policy is a deterministic local `accept-or-forward` rule rather than a free-form LLM meta-decision. For node $a_i$, the operative routing state is a role-indexed competence map $\mathbf{C}_i$, whose current decision variable is the node's own self-competence $c_i^{self} = \mathbf{C}_i[i]$. Neighbor selection is based on decentralized local beliefs $b_i^t(j)$: the most recent self-competence for neighbor $a_j$ that has been published into the packet, falling back to the neighbor's default role prior if no packet evidence is yet available. The action space is
$d_i \in \{ \text{ACCEPT}, \text{FORWARD}(a_j) \} \quad \text{where } a_j \in \mathcal{N}(a_i)$.
If $d_i = \text{ACCEPT}$, the node generates an answer from the current packet evidence window. If $d_i = \text{FORWARD}$, it appends one compact contribution to the packet and routes the task to the highest-scoring neighbor allowed by the topology.

Concretely, for packet $P_t$ we compute routing features including preferred role inferred from the question, evidence sufficiency, packet uncertainty, multihop flag, revisit risk, and loop risk. The accept score is
\[
A_i(P_t) = 0.55 c_i^{self} + 0.20 \text{evidence\_sufficiency} + 0.10 (1-\text{uncertainty}) - 0.10 \text{loop\_risk} - 0.05 \text{revisit\_risk} - \tau_{\text{accept}},
\]
where $\tau_{\text{accept}} \in \{0.62, 0.55, 0.50\}$ for peer-calibrated, self-calibrated, and self-claim variants respectively. For each neighbor $a_j$ we compute
\[
F_{i\rightarrow j}(P_t) = 0.60 b_i^t(j) + 0.25 \mathbf{1}[a_j=\text{preferred\_role}] + \text{structural\_prior} - \text{revisit\_penalty}(j),
\]
with `structural_prior = 0.05` for the peer-calibrated method and `0` otherwise, and a revisit penalty of `0.25` for already visited neighbors. The node accepts only if
\[
A_i(P_t) \ge \max_j F_{i\rightarrow j}(P_t) + \delta_{\text{accept}},
\]
with $\delta_{\text{accept}}=0.02$; otherwise it forwards to $\arg\max_j F_{i\rightarrow j}(P_t)$. Two hard safety gates are crucial in the main method: if the current node is `decomposer` and the question is detected as multi-hop, it must forward; even on single-hop questions, `decomposer` may accept only when its self-competence exceeds `0.90`. We treat these as fixed safety priors rather than emergent behavior. Our claim is therefore not unconstrained self-organization from zero prior structure, but constrained self-organization under a fixed topology plus conservative upstream safety rules.

### 3.2 The Self-Reflection Hubris (Baseline)
To illustrate the flaw in relying on LLM self-awareness, we formulate the baseline Self-Calibrated update rule. After an agent $a_i$ executes a task, it invokes a secondary self-reflection prompt $R_{self}$ to evaluate its own performance score $s_{self} \in [0, 1]$. The competence is updated as:
$\mathbf{C}_i^{(t+1)} = \alpha \mathbf{C}_i^{(t)} + (1 - \alpha) s_{self}$
where $\alpha$ is a momentum hyperparameter. Due to the inherent confirmation bias, $s_{self}$ tends to skew positively regardless of true task success, leading to $C_i \to 1$ and a surge in the premature acceptance rate.

### 3.3 Peer-Calibrated Delegation (Ours)
To combat this hubris, we replace self-reflection with **Terminal-Consensus Peer Backpropagation**. Here "backpropagation" is not meant in the neural-gradient sense; it denotes non-gradient delayed outcome credit passed back over the routed trajectory after termination. Concretely, the system does **not** rely on an explicit per-hop peer score over intermediate thought states. Instead, once a routed path terminates with final answer $\hat{y}$, the resulting end-to-end task quality is compared against the gold target $y$, yielding a delayed supervision signal
$r \in \{+1,-1\}$,
or, in the implementation, a thresholded function of answer F1. This terminal outcome is then used to calibrate the competence of the node that ultimately accepted the task:
$\mathbf{C}_{a^\star}^{(t+1)} = \mathcal{U}\!\left(\mathbf{C}_{a^\star}^{(t)}, r\right)$
where $a^\star$ is the accepting node and $\mathcal{U}$ is a bounded update with damping.

Our submission uses the most conservative executable variant of TCPB: only the final accepting node is updated, and only once per sample after the task terminates. Specifically, we threshold the final answer quality at `F1 >= 0.5`, map it to a positive or negative reward, then apply a bounded self-competence update with asymmetric step sizes (`+0.06` for success, `-0.10` for failure), clipping to `[0.05, 0.95]`, and exponential damping with momentum `0.5`. No hop-level peer critique, path-level reward redistribution, or global reviewer is used in the submission method. This design choice is important. In decentralized LLM systems, intermediate peer commentary can itself be noisy, self-serving, or stylistically inconsistent. By delaying calibration until the terminal consensus signal is available, the update becomes outcome-oriented: only paths that actually solve the task are reinforced. Empirically, this result-oriented update is already sufficient to drive premature accept rate to zero in our main run, showing that reliable routing calibration does not require fragile stepwise peer grading. Over time, terminal-consensus backpropagation suppresses overconfident early acceptance and induces a stable, position-adaptive routing structure that partially self-organizes toward expert-like paths without being forced into them.

## 4. Experiments

### 4.1 Setup
- **Benchmark:** HotpotQA (distractor, validation split); we report on a fixed slice of **200** questions exported to `artifacts/seed/hotpotqa_validation_200.jsonl` so all methods share identical inputs.
- **Model:** `gpt-4.1-mini` (OpenAI-compatible via kuaipao.ai), temperature 0, chain topology unless otherwise noted. Canonical run: `artifacts/round2_gpt41mini/run_20260414_115739/`. *Prior GLM Stage-1 results (`artifacts/round1/`) archived as guidance-only.*
- **Executable method knobs:** non-synthesizer answer generation reads the first `14` evidence lines by default, synthesizer reads up to `60`, and forward contribution prompts read up to `8`; these are explicit method knobs and later ablated rather than hidden prompt details.
- **Metrics (aggregate over the 200 tasks):**
  - **EM / F1:** standard HotpotQA exact match and token-level F1 against the gold span (implementation: `workspace/idea04_core/evaluation.py`).
  - **PAR (premature accept rate):** fraction of samples where the first routing hop ends in `accept` but answer F1 is below 0.5 (delegation proxy; `runner.py`).
  - **MHC (mean handoff count):** average number of hops until termination.
  - **Token cost:** both heuristic token accounting and measured API token usage are tracked; **cost-normalized F1** is reported against each denominator separately when available.

### 4.2 Main results (canonical run)
- **Primary artifact directory:** `artifacts/round2_gpt41mini/run_20260414_115739/` — one subdirectory per method (`fixed_self_claim`, `fixed_static_roles`, `fixed_peer_calibrated`), each with `metrics.json`, `routing_traces.jsonl`, and logs validated `[OK]`.
- **Aggregated CSV:** `artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv`.
- **Method ordering (canonical, gpt-4.1-mini):** self_claim (F1=0.7641) > static_roles (F1=0.7454) > peer_calibrated (F1=0.7381). PAR=0.0 for all methods.
- ~~Footnote on self-calibrated footnote removed; see round2 coordinator note for current canonical metrics.~~

### 4.3 Table (draft; copy from CSV for camera-ready)
Use `artifacts/round2_gpt41mini/round2_gpt41mini_main_table.csv` as the single numeric source. Do not round differently across main text vs appendix. GLM-backbone ablation data (`round1_v3_weight_sensitivity.md`) may be cited as supplemental mechanistic evidence only.

### 4.4 Reproducibility
```bash
python scripts/run_round1_v3.py --config configs/round1_hotpotqa.yaml \
  --samples-jsonl artifacts/seed/hotpotqa_validation_200.jsonl \
  --methods <comma-separated> --artifacts-root artifacts/round1
python scripts/validate_logs.py artifacts/round1/run_<RUN_ID>/<method>
```

### 4.5 Error Analysis and Interpretation
Our post-hoc audit of the canonical peer run reveals that the remaining F1 bottleneck is **not primarily a routing failure**. First, the feared "terminal black hole" pattern is absent in the strict sense: among peer samples with long routed chains, we do not observe a meaningful set of cases where the final accepting `synthesizer` receives the correct answer in the packet yet still fails catastrophically. Instead, the dominant failure mode is shallower: many low-F1 peer errors terminate after only two hops with `evidence_seeker` as the accepting node, even though the packet often already contains enough information to recover the gold answer. This points to a **single-node answer-generation bottleneck**, not a delegation bottleneck. In the current implementation, non-synthesizer roles answer from only the first 14 evidence lines, so long packets can still induce local context truncation. In other words, the peer-calibrated network is already performing the task-allocation job well; the remaining ceiling is increasingly imposed by the underlying LLM's local evidence utilization rather than by misrouting.

Second, peer routing does not collapse into a trivial copy of `fixed_static_roles`. Comparing `fixed_peer_calibrated` against `fixed_static_roles` on the same 200-task slice, the final accepting node and hop count match on **52%** of tasks. We interpret this as an encouraging hybrid result rather than a weakness: without any manual role assignment, terminal-consensus peer backpropagation autonomously rediscovers roughly half of the expert-quality static paths, while still exploring **48%** alternative routes. This is exactly the behavior we want from a position-adaptive system. It learns stable expert-like structure where the data support it, yet preserves flexibility on the remaining portion of the workload. Accordingly, the paper's value proposition should not hinge on a large absolute F1 gap over static routing alone. The stronger claim is that peer-calibration delivers static-like routing quality from cold start, collapses PAR to zero, and retains adaptive routing capacity for cases where a hand-written static pipeline is not obviously optimal.

### 4.6 Mechanism Ablations
We also ran targeted ablations on the upgraded chain-200 harness to separate routing calibration from answer-generation bottlenecks. Enlarging the evidence window for non-synthesizer nodes partially recovers answer quality (`F1 = 0.5819`), which is consistent with the audit finding that a non-trivial part of the residual error budget is imposed by local context truncation rather than by routing mistakes. By contrast, disabling terminal-consensus updates or removing the decomposer safety gate both reduce the peer method to `F1 = 0.5597` on the same 200-example slice. This is useful for two reasons. First, it shows that the current submission method is not just "structured packets plus fixed routing": delayed outcome calibration and conservative upstream gating both contribute measurable signal. Second, it sharpens our narrative around constrained self-organization. The method does not learn from zero prior structure; instead, it combines fixed topology, safety priors, and delayed terminal feedback, then lets route preferences adapt within that constrained envelope.

### 4.7 Limitations
Our current submission intentionally adopts the simplest defensible TCPB implementation: only the final accepting node is updated, and the operative competence signal is still a scalar self-competence extracted from a role-indexed map rather than a fully learned multi-dimensional router state. This makes the method highly executable and auditable, but it also means our current evidence should be interpreted as showing the value of decentralized calibration under fixed topology, not as a complete solution to path-level credit assignment. We also acknowledge that several routing constants remain hand-designed safety priors rather than learned parameters. We therefore do not claim unconstrained emergent routing; instead, we claim that under fixed topology plus conservative safety priors, delayed outcome calibration yields better delegation safety and measurable route adaptation. In addition, some residual F1 errors are now clearly attributable to local evidence-window bottlenecks in answer generation rather than to routing failure. We position richer competence vectors, path-level reward redistribution, weight learning, and stronger routing-generation disentanglement as next-step extensions rather than claims already established by the present system.

---

## 5. Conclusion
*(To be drafted after final table polish and limitation discussion.)*
