# REUSE-1 CooperBench scorer and task-root audit

**Status:** native host audit complete; official Docker scorer gate remains open  
**Model/API calls:** 0  
**Pinned benchmark:** CooperBench `63b9d44d9f39a02fccf5bf0052db48a917a011fd`  
**Sample:** `pallets_click_task/task2800`, feature 1 + feature 7

## What passed

- All 11 pinned task files matched the expected SHA-256 values.
- Feature, test and combined patches all passed `git apply --check`.
- Feature 1 gold patch plus tests: **68 passed**.
- Feature 7 gold patch plus tests: **72 passed**.
- Combined gold patch plus feature 1 tests: **68 passed**.
- Combined gold patch plus feature 7 tests: **72 passed**.
- Applying feature 1 and feature 7 independently to the base repository reproduced
  the expected content conflict in `src/click/shell_completion.py`.
- CooperBench runner/evaluator source files passed `py_compile`.

The base-with-hidden-tests failures are expected and retained: feature 1 had
1 failing test and feature 7 had 5 failing tests before its feature patch. They
show that the test patches are not vacuous.

## What is still open

The official image preflight did not reach Docker. Two anonymous registry token
requests stopped on TLS hostname mismatch for `auth.docker.io`; no image manifest,
architecture, size, pull or `test_merged` run was attempted. The earlier raw
preflight is preserved under
`artifacts/analysis/aamas2027/cooperbench_task2800_20260923/official_logs/`.

Static source inspection also confirms three scientific limits:

1. `runner_coop` preassigns agents to features.
2. The runner records conversations and patches, but no structured recipient
   acceptance, use, repair or role-update event.
3. The evaluator can report a lead/solo fallback after a merge problem, so
   `both_passed` cannot be treated as proof that a recipient used the producer's
   patch.

The complete structured trace is in `results.json` and `raw_events.jsonl`.

## Decision

CooperBench remains the primary **candidate** and a useful objective code
integration substrate. It is not yet the scientific benchmark lock. REUSE-1 is
complete only after either the official scorer becomes runnable or an independently
audited native-test scorer is specified with the same apply/merge/test/fallback
semantics, and after the thin recipient/handoff adapter passes its own vertical
slice.
