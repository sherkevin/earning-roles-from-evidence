# Native replay infrastructure fixture

This post-hoc fixture re-executed saved public code from training task `692c77d_1`.
It made **zero LLM calls**, loaded no ground-truth solution and invoked no official
evaluator. The configuration was frozen before the native world executions.

The task was the first family in the previous acquisition contract. The valid
declared replacement supplied its saved trace. The cut was fixed at the midpoint
of its 15 public steps; no successful cut or task was searched for.

Two fresh worlds executed all saved code. Their public observations, midpoint
database changes and final database changes matched each other; observations
also matched the original source trajectory. Each used 45 native environment API
calls. This checks a single code replay, not fresh LLM generation or universal
deterministic replay. Supervisor completion is not an independently rescored win.

A third fresh world received only the saved midpoint database checkpoint.
Its first continuation failed because the REPL variable `playlists` was absent.
The logged native API-call count for that world is zero. Subsequently, the native
`load_state` / teardown lifecycle raised a freezegun `AttributeError`, followed
by `IndexError` during cleanup. The process exited with code 1. Complete stderr,
the observed NameError and both successful replay records remain preserved.

The result is **a partial infrastructure fixture with a retained failure**.
There was no repair, additional world, new model response or promoted candidate.
The summary was reconstructed offline from the existing files after the crash.

Useful reuse: future training-only continuation tests must reconstruct all
relevant state, including REPL locals and policy messages, and charge preparation
and environment calls. Full code-prefix replay is a candidate reconstruction
technique for this case. The database-only interface is insufficient. A verified
isolated-process continuation runner and broader fixtures are still required;
this record does not grant test-world resets or a free validation oracle.

See [configuration](config.json), [summary](summary.json), and
[retained native failure](controller.log). Raw task traces stay local.
