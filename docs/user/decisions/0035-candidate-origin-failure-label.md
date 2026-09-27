# ADR 0035 — Candidate-origin failure labels are separate from scorer uncertainty

日期：2026-09-27
状态：Accepted
范围：producer quality objective scorer；不回写历史运行

## Context

The producer contract includes a public module that must import before any queue or
priority behavior can be used. The previous scorer treated every uncaught `TypeError`
and every incomplete check as `UNKNOWN`. That conflates a deterministic defect in the
sealed candidate delivery with a failure of the measurement apparatus. The distinction
matters because only the former is evidence about producer quality.

The real neutral-v2 episode exposed both cases: a dataclass field-order `TypeError`
originated in the delivered `mqueue/priority.py`, while a later `_seq` constructor
failure came from the scorer guessing an undocumented constructor signature. The first
is candidate evidence; the second is a scorer-contract defect. Historical v1/v2 logs
were not collected under this rule and remain unchanged.

## Decision

The next producer scorer uses a new versioned response schema with two independent
completeness fields:

- `decision_complete=true` means the hard import/delivery decision is complete;
- `coverage_complete=true` means every behavioral check ran to a determinate PASS/FAIL.

An import or delivery failure is eligible for `FAIL`, `label=0`, only when all of the
following are true: the runtime/scorer control passed with the same frozen fingerprint;
the required files decode and their digest matches; the worker started and returned a
structured response; the traceback or parser result identifies a producer-owned path;
the failure is in a pre-registered candidate-failure codebook; and the fixed fresh-worker
repeat count agrees. The response records `failure_origin`, `failure_stage`,
`failure_code`, `exception_class`, `source_path`, `decision_complete`, and
`coverage_complete`.

Worker startup/exit, timeout, permission/resource failure, runtime drift, response or
digest mismatch, hidden-driver misuse of an undocumented interface, and any unclassified
exception remain `UNKNOWN`, with no label, evidence, or controller update. A trusted-driver
TypeError is an explicit negative control and must also be `UNKNOWN`.

The runner gate is updated only for the new schema: a candidate-origin hard decision may
be recorded as a producer score despite incomplete downstream behavior coverage; an
`UNKNOWN` response or an incomplete decision still closes the episode before role
evidence. No historical response is reclassified.

## Consequences

This creates a cleaner objective signal for deterministic candidate defects while making
the scorer's own uncertainty visible. Qualification now requires a correct control,
candidate import/syntax failures, trusted-driver and infrastructure negative controls,
digest/schema mutations, and targeted near-misses before another real API episode.
The signal still measures producer contract quality, not the value of situated judgment;
it cannot by itself establish role learning or justify an A800 run.
