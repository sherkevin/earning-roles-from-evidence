# Evidence-Derived Organization (EDO): AAMAS revision

Current target (2026-09-16): **AAMAS 2027 Main Track** following the EMNLP/ARR rejection. Read these two documents in order: [paper requirements](docs/paper/aamas2027/REQUIREMENTS.md), then [current gaps and executable tasks](docs/coordination/AAMAS_TASKS.md). They are the sole active AAMAS specification and task ledger. The [AAMAS manuscript](article/aamas2027/README.md) remains an internal design/reanalysis with outstanding empirical gates.

Current empirical work: the [real-API acquisition probe](docs/scientist/analysis/AAMAS_ACQUISITION_PROBE_20260922.md) completed with a failed promotion gate ([results](artifacts/experiments/aamas2027/dev_20260922/report.md)); the planned full-dev census [stopped incomplete after transport failures](artifacts/experiments/aamas2027/headroom_20260922/report.md) at38/57 attempted tasks. That earlier iteration used921 benchmark/induction requests plus3 separate health requests. [Decisions 0005](docs/user/decisions/0005-retain-peer-judged-role-learning.md) and [0006](docs/user/decisions/0006-study-peer-judged-role-formation.md) select learning roles from actual collaborators' judgments during agent–workflow co-evolution; package replacement/conditional adoption is retired as the main question. One [real linked producer→recipient case](artifacts/experiments/aamas2027/peer_judgment_resume_v5_20260923/report.md) recorded acceptance and matching action, but no causal handoff value or later role update. The [A0 v3](artifacts/experiments/aamas2027/peer_judgment_a0_v3_20260923/report.md) and [A0 v4](artifacts/experiments/aamas2027/peer_judgment_a0_v4_20260923/report.md) prospective development diagnostics produced no further complete chains because of capped observations and transport UNKNOWNs; their attempts and stops remain separate. The [paired real-API delivery-visibility diagnostic](artifacts/experiments/aamas2027/peer_delivery_visibility_dev_v1_20260923/report.md) made 16 returned task calls across two fresh recipients, but both exhausted review before planning; handoff value remains indeterminate. An [independent audit](docs/scientist/analysis/AAMAS_ORIGINAL_Q1_NEXT_EXPERIMENT_AUDIT_20260923.md) retired the first 288-call four-role sketch because its preset seats and same-judge later selection could not identify a transferable role. The [RAPS novelty boundary](references/aamas/raps_20260923/README.md) and [CooperBench Click feasibility check](docs/scientist/analysis/AAMAS_ORIGINAL_Q1_BENCHMARK_NEXT_20260923.md) guide the next design. R0–R3 did not test the selected loop; the method is not locked.

The [AAMAS review rules for this story](docs/paper/aamas2027/AAMAS_REVIEW_RULES_PEER_JUDGED_ROLE_FORMATION.md) define the six P0 evidence gates and current reviewer verdict; they are a quality standard, not a method or result.

The [reuse-first assembly plan](docs/paper/aamas2027/PEER_ROLE_IMPLEMENTATION_ASSEMBLY_PLAN_20260924.md) maps the story to benchmark/runtime functions, conditional CooperBench/OpenHands choices, and matched baselines. The associated [ADR 0007](docs/user/decisions/0007-reuse-open-source-benchmark-runtime-first.md) records the reuse and licensing boundary.

Build: `python scripts/build_aamas2027.py`. Read-only evidence reanalysis: `python scripts/aamas_audit_evidence.py`.

The original ACL sources and historical coordination records below are preserved for provenance.

Research collaboration repository for EDO, originally submitted to EMNLP. Four roles (user, scientist, engineer, reviewer) share the active AAMAS task ledger; older role TODO entries remain historical evidence.

---

## 1-minute Entry

| Need | Read |
|---|---|
| Project map and storage rules | [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) |
| Role startup prompts | [`prompts/ROLE_PROMPTS.md`](./prompts/ROLE_PROMPTS.md) |
| Collaboration hard rules | [`.cursor/rules/collaboration-workflow.mdc`](./.cursor/rules/collaboration-workflow.mdc) |
| Active AAMAS scientific and venue requirements | [`REQUIREMENTS.md`](docs/paper/aamas2027/REQUIREMENTS.md) |
| Active gap audit, tasks, dependencies and execution evidence | [`AAMAS_TASKS.md`](docs/coordination/AAMAS_TASKS.md) |
| Historical method / experiment / EMNLP specification | [`idea.md`](idea.md), [`experiment.md`](experiment.md), [`docs/demand.md`](docs/demand.md) |
| User decisions | [`docs/coordination/USER_TODO.md`](./docs/coordination/USER_TODO.md) |
| Scientist tasks | [`docs/coordination/SCIENTIST_TODO.md`](./docs/coordination/SCIENTIST_TODO.md) |
| Engineer tasks | [`docs/coordination/ENGINEER_TODO.md`](./docs/coordination/ENGINEER_TODO.md) |
| Legacy engineering log | [`docs/coordination/implementation_log.md`](./docs/coordination/implementation_log.md) |
| Reviewer tasks | [`docs/coordination/REVIEWER_TODO.md`](./docs/coordination/REVIEWER_TODO.md) |
| Reviewer schema/template | [`prompts/reviewer_template.md`](./prompts/reviewer_template.md) |
| Current internal paper source | [`article/aamas2027/main.tex`](article/aamas2027/main.tex) |
| Build the internal paper PDF | [Build instructions](article/aamas2027/README.md) (generated PDFs are absent from this checkout) |

---

## Storage Rule

- `docs/coordination/` stores task state only.
- `docs/<role>/` stores durable role-authored handoffs, logs, results, runbooks, and decision briefs.
- `docs/chats/<role>/` stores lightweight cross-role memos.
- `artifacts/` stores experiment, figure, statistics, forensic, and reviewer evidence.
- `article/` stores only buildable paper sources and build outputs.

See [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) for the full convention.

---

## Role Loop

For the AAMAS revision, start with REQUIREMENTS.md and AAMAS_TASKS.md. Role TODO files point to that shared queue; update execution status there once, under the assigned owner. The following older role loop remains useful for historical/non-AAMAS work:

1. Read the project structure and own TODO/log.
2. Run pending -> done sweep.
3. Execute the highest-priority unblocked task (`P0 > P1 > P2 > P3`).
4. Write substantial cross-role context to `docs/<author-role>/...`, not into chat memory.
5. Stop only when the current highest-priority chain is complete and the remaining frontier is blocked.
