# N03 live-runner scorer integration audit (2026-09-27)

## Scope

This is an engineering audit of `scripts/peerrolebench_real_closed_loop.py`
against the scorer IPC preflight. It does not claim a qualified benchmark,
real-agent efficacy, or a producer-quality label.

## What the runner does now

`evaluate()` seals the recipient source and then creates one `SandboxedWorker`
with the public worker `peerrolebench_consumer_worker.py`. The parent process
imports `peerrolebench_consumer_checks.run_checks` and drives the worker with
four assertions. The resulting `consumer_score.json` is used as the terminal
outcome after a strict ledger replay. Thus the current scorer is parent-side
and the worker is only a public operation bridge; it is not an independent
hidden scorer.

The IPC preflight (`n03_scorer_ipc_preflight_20260927_v2`) established only
that a private worker can return a fixture PASS/FAIL while a separately
sandboxed candidate probe cannot read the private worker path. The fixture
truth is a preserved delivery digest, so this preflight is a boundary test,
not task scoring.

## Smallest safe integration seam

1. Keep `SandboxedWorker` as the transport and source-isolation adapter.
   Launch a versioned scorer worker via its `worker_path` argument, with the
   same sealed source files and public interface names.
2. Pass only a bounded public request containing `op`, task id, seed, delivery
   artifact digest, and a public scorer version. Do not pass expected answers,
   private tests, parent ledger paths, or the operator's trusted directory.
3. Keep all assertions and expected values in the scorer worker's trusted copy.
   The worker must return a versioned object with `status` in `{PASS, FAIL}`,
   `coverage_complete: true`, the echoed artifact digest, per-check statuses,
   and a canonical response digest. It must not return hidden expected values.
4. The parent must validate the response shape, scorer version, echoed digest,
   coverage, and canonical response digest before constructing
   `TerminalOutcome`. A worker timeout, permission/runtime error, malformed
   JSON, missing coverage, digest mismatch, or unexpected status is `UNKNOWN`
   and disables both the role-evidence update and controller update.
5. Record scorer worker hash, request digest, response digest, exit/timeout
   metadata, and the sealed source digest in the raw ledger log. A score file
   hash alone is insufficient to bind the label to the delivered artifact.
6. Keep the producer objective scorer separate from the recipient integration
   scorer. For DIST1, a first independent scorer may evaluate only the
   contracted producer-owned `queue.py`/`priority.py` behaviour. It must not
   silently run native `grade.sh` over recipient-owned `consumer.py`, because
   that would reintroduce responsibility misattribution. Producer and
   recipient results need distinct scorer versions and ledger fields before
   either can be used for role learning.

## Required tests before a live LLM run

- Correct and wrong artifact digests produce independent worker PASS/FAIL;
- response digest tampering and artifact-digest mismatch are rejected;
- scorer timeout, exit-without-response, permission failure, malformed JSON,
  incomplete coverage, and unexpected status all become `UNKNOWN` with no
  update;
- a complete valid scorer response passes the existing strict replay gate;
- an incomplete or invalid ledger never reaches scorer acceptance or update;
- the candidate cannot read the private scorer worker or its expected data;
- the runner's control arm can still run the existing parent-side checks, but
  its result is labelled diagnostic and is not pooled with the independent
  scorer condition.

## Risks and non-goals

The existing macOS sandbox is a qualified development adapter, not hostile
Python containment: candidate and scorer instrumentation share the worker
address space, and its RSS watcher is not a hard memory cap. The hidden worker
boundary therefore supports an information-flow claim only under the
non-adversarial source contract. Native TeamBench grading remains unqualified
until its task data, runtime, and responsibility split are independently
validated.

No new LLM or GPU run should be started from this audit. The next experiment
is justified only after the versioned task-specific scorer and the above
failure semantics are integrated and replay-tested offline.
