# 0004 — Continue only unstarted census tasks after a verified outage recovery

Status: Infrastructure execution amendment, 2026-09-22.
Authority: the user's resumed empirical work, decisions 0001 and 0003.
This records an implementation decision; it is not a new user preference.

## Context

The original 57-task census stopped after two consecutive transport failures,
as required by its frozen circuit breaker. Its ordered prefix contains 27
attempted tasks: 23 clean successes, two clean failures and two infrastructure
UNKNOWNs. The prefix used 433 real request attempts. Thirty original task IDs
have never started. The observed scientific outcomes preceded this amendment.

DNS resolution subsequently recovered. One separate real, nonbenchmark health
request to the same named provider and model succeeded. That request and its
usage are logged separately from the census, including the earlier failures.

## Decision

Keep the original controller's stop permanent. Use a separate, frozen recovery
controller to continue only the original 30 unstarted IDs in the original order.
Do not rerun or replace either interrupted task; both stay UNKNOWN in the
scientific analysis. Preserve every original result and raw trace by hash.

Keep the model, native prompt, runtime, scorer, per-task budget and all scientific
decision thresholds unchanged. Any transport-stopped task during this recovery
ends it permanently. A process failure or partial episode also prevents replay.
Persist these stops across controller restarts and take an exclusive local lock.

## Rationale

Continuing untouched tasks after verified connectivity can complete the declared
population without selecting cases by their outcomes or manufacturing failures.
It cannot be described as an unchanged original preregistration: the amendment
was made after partial results, and that timing must remain visible.

## Consequences

- At most 30 new episodes and 900 new request attempts; combined ceiling 1,333.
- Original interrupted outcomes contribute uncertainty, not valid task failures.
- No second automatic recovery, task replacement or treatment is authorized.
- The failed acquisition package remains closed under decision 0002.
- A complete census can still be scientifically inconclusive because of UNKNOWNs.
- The recovery code, configuration, health receipt, original-prefix hashes and
  prelaunch review correction are retained alongside the original frozen files.

Executable amendment: [recovery v1](../../../configs/aamas2027/headroom_recovery_v1.json).
Evidence: [recovery freeze](../../../artifacts/experiments/aamas2027/headroom_20260922/recovery_freeze.json).
