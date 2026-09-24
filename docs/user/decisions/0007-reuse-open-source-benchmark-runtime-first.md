# ADR 0007 — Reuse pinned benchmark and runtime components before writing new infrastructure

**Status:** Accepted for the next implementation phase  
**Date:** 2026-09-24  
**Scope:** AAMAS peer-judged role-formation study

## Context

The active scientific question is whether an agent's role can be learned from
how an actual collaborator judges and uses that agent's delivered work, and
whether the resulting evidence changes later responsibility during agent–workflow
co-evolution. The current repository has diagnostic runners and one linked
producer→recipient witness, but no complete executable judgment → role evidence →
future assignment loop. Rebuilding a benchmark, agent runtime, sandbox, scorer,
and event logger from scratch would consume the budget while adding avoidable
implementation risk.

The user therefore directed a reuse-first implementation: identify each required
function, locate a maintained open-source project that already provides it, pin a
version, and write only the thin glue that is specific to peer-judged role
formation. Reuse is useful only when the component's interface, license, and
observability are inspectable. A project that merely calls itself multi-agent is
not evidence for the paper's producer–consumer claim.

## Decision

1. **Reuse before reimplementation.** The implementation will assemble existing
   benchmark, agent-runtime, workspace, tool, scorer, and logging components. New
   code is limited to the peer-judgment protocol, provenance/receipt schema,
   source-aware role update, future-assignment policy, adapters, controls, and
   analysis/replay tooling.
2. **Primary benchmark candidate.** Use CooperBench as the first benchmark
   adapter because its tasks contain real repository changes, separate feature
   patches, merge conflicts, and native tests. Pin the audited repository/task
   commits recorded in
   `references/aamas/cooperbench_20260923/` and the reuse audit. Do not copy its
   source or claim official scorer validity until the top-level license and the
   official Docker scorer are resolved. Until then, use the task data/specification
   and an independently implemented adapter, with the native tests as the
   externally observable outcome.
3. **Primary runtime candidate.** Use OpenHands Software Agent SDK, pinned to the
   audited MIT commit recorded under
   `references/aamas/reuse_design_20260924/runtime/`. Its agent, tool,
   conversation, workspace, event, and callback interfaces are reused. A
   zero-LLM smoke test must remain passing before any paid/API experiment.
4. **No unlicensed copying.** Meta-Team, CooperBench's top-level repository, and
   any other source without a clear redistributable license may inform a baseline
   or be reimplemented from its published description, but their code is not
   copied into the project. Every reused file or package must carry a source URL,
   commit/tag, license, checksum, and a short deviation note.
5. **Benchmark lock is conditional.** CooperBench becomes the primary scientific
   benchmark only after (a) an independent adapter can execute a complete
   producer→consumer→repair/use trace, (b) an official or independently audited
   scorer is available, (c) held-out task roots and task-level independence are
   specified, and (d) the same-information controls can run. If any gate fails,
   keep CooperBench as an engineering diagnostic and promote a legally reusable
   fallback only after the same protocol audit.
6. **Baselines are part of the method, not optional add-ons.** The first matrix
   will include fixed/no-role, pooled single-agent, raw acceptance, local
   contextual trust/bandit, terminal-only feedback, and a closest peer-feedback
   control when an implementation can be reproduced from a licensed source or
   paper. All arms receive the same task opportunities, models/tools, legal
   observations, storage and total API budget.

## Consequences

This decision sharply reduces engineering scope and makes the paper's novelty
auditable: the contribution is the judgment-to-role protocol and its causal
evaluation, not a new agent shell or game engine. It also introduces integration
and licensing risks. A benchmark can be structurally suitable yet fail to expose
recipient use or later responsibility; a runtime can import successfully yet
need adapters for durable provenance and cloned-state interventions. Those risks
are explicit gates in the assembly plan and cannot be papered over by reporting
task success alone.

## Evidence and supersession rule

The exact source audits, pinned commits, smoke logs, and license observations are
kept in `references/aamas/reuse_design_20260924/` and the earlier CooperBench and
Meta-Team audits. This ADR is superseded only by a later numbered ADR that names
the replacement benchmark/runtime and records why the gates failed or passed.
