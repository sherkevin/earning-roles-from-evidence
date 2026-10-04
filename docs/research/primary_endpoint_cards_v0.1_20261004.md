# Primary endpoint cards v0.1

- **Status**: `DESIGN_ONLY / NOT_FROZEN`
- **Purpose**: give the paper's H1--H4 endpoint names a stable, auditable home without claiming preregistration before the values are agreed and frozen.
- **Scope**: paper writing and experiment specification only; this file authorizes no run and contains no result.
- **Source**: `article/aamas2027/main.tex`, `docs/research/versions/evaluation/storyline/storyline_v1.3_20260928_eval.md`

## Shared contract

Each card must be frozen before confirmation data are observed. The freeze must record the exact task/root split, policy arms, model/API route, candidate menu, cost budget, seed/stream rule, scorer version, primary endpoint, direction, minimum practically important difference or precision target, stream-level 95% interval, multiplicity rule, and stopping rule. The frozen file will be hashed and its path added to the paper manifest. Until then, the values below are design commitments, not preregistered thresholds.

## H1-information

| Field | Design value |
|---|---|
| Primary endpoint | Independent-target Brier score for situated-judgment prediction |
| Direction | Lower is better; compare incremental value against raw acceptance and terminal-only controls |
| Unit | Independently reset stream / held-out target event |
| Control | Same-information raw-acceptance and terminal-only arms |
| MCID or precision target | `NOT_FROZEN` |
| Interval / multiplicity | Stream-level 95% interval; exact correction `NOT_FROZEN` |
| Stopping rule | `NOT_FROZEN` |

## H2-utility

| Field | Design value |
|---|---|
| Primary endpoint | Future assignment quality--complete-cost utility on an unseen target root |
| Direction | Higher is better at matched information and total cost |
| Unit | Independently reset target stream |
| Control | Same-information contextual trust/bandit and no-evidence arms |
| MCID or precision target | `NOT_FROZEN` |
| Interval / multiplicity | Stream-level 95% interval; exact correction `NOT_FROZEN` |
| Stopping rule | `NOT_FROZEN` |

## H3-service

| Field | Design value |
|---|---|
| Primary endpoint | Selected-feedback update p95 latency and backlog under fixed arrival/concurrency budget |
| Direction | Lower is better and must remain within the service threshold |
| Unit | Feedback event within a predeclared stream window |
| Control | Same scorer and update workload with no-update or periodic-refit service arm |
| MCID or precision target | `NOT_FROZEN` |
| Interval / multiplicity | Stream-level 95% interval or predeclared service bound; exact form `NOT_FROZEN` |
| Stopping rule | `NOT_FROZEN` |

## H4-safety

| Field | Design value |
|---|---|
| Primary endpoint | False producer-attribution rate under recipient-only and mixed-ownership mutations |
| Direction | Lower is better; `UNKNOWN` must not be silently recoded as a negative label |
| Unit | Ownership-mutation event |
| Control | Ungated raw-label and responsibility-gate arms under the same visible event |
| MCID or precision target | `NOT_FROZEN` |
| Interval / multiplicity | Stream-level 95% interval; exact correction `NOT_FROZEN` |
| Stopping rule | `NOT_FROZEN` |

## Current interpretation

This manifest closes the traceability problem for the endpoint names, but it does **not** close the preregistration gate. The paper must continue to describe H1--H4 as design endpoints until MCID/precision, stopping, exact controls, and the confirmation split are frozen and hashed. No result, benchmark qualification, or submission-readiness claim may be inferred from this file.
