# 0001 — Resume bounded empirical iteration

Status: Accepted by explicit user instruction, 2026-09-22.

## Context

The previous checkpoint paused research and experiments. It preserved a candidate
question about adopting learned capabilities into workflows, but no executable
qualification method or new capability-transfer evidence. Earlier API screens
tested only a few AppWorld development families.

## Decision

The user has resumed work and authorized the following cycle: refine the story,
identify the contribution, specify a coherent method, run small experiments on
real data with real LLM APIs, and retain or revise the proposal from the results.
The cc-switch provider named `内部` (idealab) is an authorized API source.

This instruction supersedes the operational pause, not the preserved evidence.
The current session owns both implementation and scientific integration; one
independent read-only reviewer checks experimental identification. No second
execution owner or concurrent duplicate benchmark run is introduced.

## Rationale

Further prose-only revisions cannot establish whether the central phenomenon
exists. A bounded development experiment can falsify prerequisites cheaply and
produce concrete traces for method design.

## Consequences

- Pull and inspect the current repository before changing the design.
- Freeze the diagnostic population, interventions, costs and stopping rules
  before outcome-dependent model calls.
- Use native training/development tasks; leave confirmation tasks untouched.
- Log every real request, response, error, configuration and raw task outcome.
- Keep credentials in cc-switch; never copy them to files or tool output.
- Treat development results as diagnostics, not confirmation or acceptance odds.
- Preserve unsuccessful attempts and distinguish API/runtime failures from
  scientific failures.
- Continue independent work when clarification is optional; ask the user when
  a missing resource or scope decision is genuinely required.

## Record ownership

This checkout is the active local working copy. The session's evidence is saved
under `artifacts/experiments/aamas2027/` and linked from the sole AAMAS task ledger.
Historical Shervin/Mac records retain their original provenance. New files are
not claimed synchronized to another device until an actual transfer is verified.
