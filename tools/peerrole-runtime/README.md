# Bounded consumer execution runtime

This task adapter reuses `@anthropic-ai/sandbox-runtime` 0.0.77 (Apache-2.0).
Install its exact dependency closure with `npm ci --ignore-scripts`; the
checked-in lockfile records registry URLs and integrity hashes. The source
inspection archive is under `references/aamas/sandbox_runtime_20260926/`.
The npm artifact is pinned separately; a matching version is not a claim that
the registry package was byte-for-byte rebuilt from the archived Git commit.

Python parent dependency: `python3 -m pip install -r requirements.txt`.
The reviewed worker interpreter is the existing uv CPython 3.12 installation
at `~/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`.
The adapter currently supports macOS only, not Nebula/Linux deployment.

The parent sends bounded JSON operations to a public worker holding only an
immutable source copy. Expectations and assertions stay in the parent.
The sandbox denies reads by default, permits the Python/system runtime and
public copy, writes only to scratch, and permits no network. Candidate forks
are disabled by a per-process limit. CPU, file size and descriptor limits are
hard limits; a parent process-tree RSS watchdog is **not** a hard memory cap.
RPC/session deadlines and output caps prevent blocking on partial lines.

This is a non-adversarial development evaluator. Python event instrumentation
shares candidate memory and is not tamper-proof. Native TeamBench pytest is
not run by this adapter; its in-process assertions are not secretly protected
by the filesystem sandbox. Do not promote this to a complete benchmark or
production security boundary from the listed canaries alone.

Reproduction (writes a new log directory):

```sh
python3 scripts/peerrolebench_runtime_qualification.py --output experiments/logs/NEW_UNIQUE_ID
```

The first resource-limit and cleanup failures are retained. The v3 runtime
qualification passed the twelve listed checks and discriminated the five
reviewed fixtures. A subsequent targeted regression changed resource errors
returned by the worker from FAIL to UNKNOWN; that mapping has separate tests.
