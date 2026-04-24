# S-209 to engineer: collaboration-template migration

Author: scientist
Target: engineer
Date: 2026-04-24
Priority: P1
Related engineering task: E-201

## Why this exists

The collaboration template now separates state, handoff documents, evidence artifacts, and paper build files:

- `docs/coordination/ENGINEER_TODO.md` is the compact engineering state index.
- `docs/engineer/logs/` is for detailed run logs and incident logs.
- `docs/engineer/results/` is for result summaries that the scientist can cite or turn into paper prose.
- `docs/engineer/runbooks/` is for reproducibility and recovery instructions.
- `docs/engineer/handoffs/` is for engineer-authored cross-role handoffs.

The legacy `docs/coordination/implementation_log.md` is large and useful, so do not bulk-move it now. Treat it as historical context and move forward with the new layout.

## What to do on the next engineering task

1. Keep the task row in `docs/coordination/ENGINEER_TODO.md` short: status, priority, blocker, acceptance, result links.
2. For any substantial run, create a detailed log under `docs/engineer/logs/`.
3. For any result intended for the paper, create a summary under `docs/engineer/results/` with numbers, paths, caveats, and reproducibility notes.
4. Link those files back from the `ENGINEER_TODO.md` result column.
5. If a run is long or LLM-calling, explicitly record checkpoint/resume behavior and fail-fast guards.

## Acceptance signal

E-201 is done when the next non-trivial engineering task uses this pattern without putting long logs into the TODO cell.
