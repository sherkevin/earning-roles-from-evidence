# 0008 — Freeze benchmark layers and baseline matrix

Status: Accepted for the next implementation phase; the scientific lock remains conditional on the scorer and vertical-slice gates below. Date: 2026-09-24.

## Context

The active question is whether a peer's situated judgment and actual use of a
delivered artifact can improve later responsibility assignment. The current
survey found no public benchmark that contains the whole chain. Existing work
separates into two useful layers: selector substrates, where an orchestrator
chooses among peers, and task environments, where a delivered artifact can be
used, repaired and checked by an independent evaluator.

DecisionBench provides the first layer with an 11-model peer pool, delegation
logs, cost metrics and profile interventions, but its public implementation
does not update peer profiles from recipient use or change future duties.
CooperBench provides real repositories, feature patches, conflicts and native
tests, but preassigns feature owners and has no peer-judgment or later-role
protocol. AgentWorld provides a larger stateful multi-agent stress environment,
but its skills and responsibilities are mostly specified by task files.

## Decision

### Benchmark layers

**Primary role-formation substrate:** CooperBench at the audited commit
`63b9d44d9f39a02fccf5bf0052db48a917a011fd`, used through an independent thin
adapter. It is eligible for scientific experiments only after: (a) a complete
producer → recipient judgment/use/repair → terminal scorer → later assignment
vertical slice, (b) a legal redistribution/scorer decision, (c) a held-out
task-root split, and (d) matched controls.

**Selector benchmark:** DecisionBench at the pinned paper/code/data revisions
recorded in `references/aamas/decisionbench_20260923/README.md`. It is used to
test peer-selection quality, adaptation, exploration, cost and calibration. It
does not by itself establish role formation.

**Secondary external-validity benchmark:** AgentWorld at the pinned source
manifest revision. It is considered only after the CooperBench vertical slice
passes. Its preset skills, resources and usernames must be randomized or made
exchangeable before interpreting a role-learning result.

**Controls and threat baselines:** MARBLE/MultiAgentBench, TeamBench and
AgentNet are not primary benchmarks. MARBLE and TeamBench provide fixed-role
and deterministic-grader controls. AgentNet is the closest threat baseline for
decentralized routing, dynamic graph structure and experience-based updates.

### Baseline matrix

The main CooperBench matrix is:

- B0: pooled single-agent or centralized selector;
- B1: fixed cooperation with no role update;
- B2: recipient redo/no handoff;
- B3: raw recipient acceptance;
- B4: same-information local contextual trust or bandit;
- B5: terminal-only feedback;
- B6: closest reproducible peer-feedback or dynamic-role control;
- P: proposed peer-judgment evidence and later-assignment policy.

DecisionBench additionally reports random-local, static profile, static trust,
same-information contextual bandit, global selector and no-online-update arms.
An AgentNet-style dynamic router is a required threat comparison whenever its
information and budget can be matched. TeamBench-style role-violation and
verifier–grader disagreement are diagnostic metrics, not replacements for the
main task scorer.

Every arm receives the same task roots, model/tool access, legal observations,
storage, opportunity stream and total API/test budget. Controls must not copy
the proposed arm's realized memory or future assignments.

### Scale defaults

The first selector smoke uses three persistent agents. The main sparse-graph
configuration uses five persistent agents in an undirected ring with degree two;
each selector sees only its local neighbors. Three versus five agents is the
primary scale/heterogeneity ablation. Ten or more agents are reserved for
external stress tests and are not part of the initial claim.

The main run uses the same underlying model for all agents and gives each agent
private selector state. Different models, skills or prompts are a later
heterogeneity ablation. This isolates online peer selection from static model
ability differences.

## Rationale

This split prevents three different claims from being conflated. DecisionBench
can tell us whether an adaptive selector is useful. CooperBench can tell us
whether selected deliveries are actually adopted and whether evidence changes
future responsibility. AgentWorld can test transfer to stateful multi-agent
work. The baseline matrix distinguishes peer judgment from ordinary trust,
terminal reward, centralized routing and generic dynamic graphs.

The scale defaults follow the observed literature pattern: two agents are the
natural handoff unit in CooperBench; three agents are common in MARBLE, TeamBench
and AgentNet; AgentNet's own results make five agents the first useful
heterogeneity/scalability comparison. These are implementation defaults, not a
claim that one team size is universally optimal.

## Consequences

The next implementation work is benchmark adapters, scorer/label audits,
matched baseline runners and a replayable vertical slice. The JEV architecture,
online update rule, graph exploration policy and label weighting remain open
until these benchmark interfaces are executable. A positive selector score on
DecisionBench cannot be promoted to a role-formation result without the
CooperBench artifact-use and later-assignment chain.

If CooperBench fails the scorer or attribution gates, it remains an engineering
diagnostic; no benchmark is promoted merely for convenience. If B4 matches P,
the claim is narrowed to ordinary contextual selection. If P changes role
labels without changing later assignments, task utility or total cost, the
paper will not call it role learning.
