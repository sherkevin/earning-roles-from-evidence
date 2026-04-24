# idea04 - Emergent Delegation Organization (EDO)

EMNLP long paper collaboration repository for EDO. The repo is organized to let four roles (user, scientist, engineer, reviewer) keep moving with minimal user intervention.

---

## 1-minute Entry

| Need | Read |
|---|---|
| Project map and storage rules | [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) |
| Role startup prompts | [`prompts/ROLE_PROMPTS.md`](./prompts/ROLE_PROMPTS.md) |
| Collaboration hard rules | [`.cursor/rules/collaboration-workflow.mdc`](./.cursor/rules/collaboration-workflow.mdc) |
| Method idea and claims | [`idea.md`](./idea.md) |
| Experiment rules | [`experiment.md`](./experiment.md) |
| EMNLP/ARR requirement spec | [`docs/demand.md`](./docs/demand.md) |
| User decisions | [`docs/coordination/USER_TODO.md`](./docs/coordination/USER_TODO.md) |
| Scientist tasks | [`docs/coordination/SCIENTIST_TODO.md`](./docs/coordination/SCIENTIST_TODO.md) |
| Engineer tasks | [`docs/coordination/ENGINEER_TODO.md`](./docs/coordination/ENGINEER_TODO.md) |
| Legacy engineering log | [`docs/coordination/implementation_log.md`](./docs/coordination/implementation_log.md) |
| Reviewer tasks | [`docs/coordination/REVIEWER_TODO.md`](./docs/coordination/REVIEWER_TODO.md) |
| Reviewer schema/template | [`prompts/reviewer_template.md`](./prompts/reviewer_template.md) |
| Current paper source | [`article/latex/edo_paper.tex`](./article/latex/edo_paper.tex) |
| Current paper PDF | [`article/build/edo_paper.pdf`](./article/build/edo_paper.pdf) |

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

Every role should start by reading its prompt in [`prompts/ROLE_PROMPTS.md`](./prompts/ROLE_PROMPTS.md), then:

1. Read the project structure and own TODO/log.
2. Run pending -> done sweep.
3. Execute the highest-priority unblocked task (`P0 > P1 > P2 > P3`).
4. Write substantial cross-role context to `docs/<author-role>/...`, not into chat memory.
5. Stop only when the current highest-priority chain is complete and the remaining frontier is blocked.
