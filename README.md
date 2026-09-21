# Evidence-Derived Organization (EDO): AAMAS revision

Current target (2026-09-16): **AAMAS 2027 Main Track** following the EMNLP/ARR rejection. Read these two documents in order: [paper requirements](docs/paper/aamas2027/REQUIREMENTS.md), then [current gaps and executable tasks](docs/coordination/AAMAS_TASKS.md). They are the sole active AAMAS specification and task ledger. The [AAMAS manuscript](article/aamas2027/README.md) remains an internal design/reanalysis with outstanding empirical gates.

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
| Current internal paper PDF | [`article/aamas2027/build/main.pdf`](article/aamas2027/build/main.pdf) |

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
