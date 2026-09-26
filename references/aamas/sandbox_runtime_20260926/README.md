# N01 macOS sandbox source evidence

- Source: https://github.com/anthropics/sandbox-runtime (redirected from `anthropic-experimental/sandbox-runtime`).
- Pin: `ddbeb74711c4097014ef3056791efa83f553116c`.
- License: Apache-2.0; package manifest at this pin reports `0.0.77`.
- This is a minimal evidence snapshot, not an installed runtime or complete buildable checkout. File hashes and source URLs are in `provenance.json`.

## Source-supported cause of the startup failure

`upstream/src/sandbox/macos-sandbox-utils.ts:813` explains that denying the root inode causes dyld to abort before execution. Its precise carve-out is:

```scheme
(allow file-read* (literal "/"))
```

This permits the root vnode, not reads of all descendants. The upstream regression explanation is at `upstream/test/sandbox/allow-read.test.ts:244`; executable test cases begin at line 286. Directory metadata needed for `realpath` is handled separately at `macos-sandbox-utils.ts:822`.

Root subsequently reported that this exact addition passed the existing local canary. The execution evidence is in `experiments/logs/n01_isolation_canary_20260926_uv312_rootvnode/`; the source-review subtask performed no canary, model, or GPU execution. Passing the enumerated canaries does not qualify a production sandbox or isolate test expectations already in candidate process memory.

## Reusable route and configuration limits

The maintained CLI is `srt --settings <config.json> <command>`; the documented library API is `SandboxManager.initialize` / `wrapWithSandbox` / `reset`. macOS uses Seatbelt; Linux uses bubblewrap. `srt` was not found on this host's PATH, and nothing was installed.

Read access is allowed by default: `allowRead` alone is not an allowlist. Restricted evaluation therefore needs an explicit `denyRead` region plus narrow read exceptions. Do not copy the upstream regression test's broad `/private` exception into our benchmark, whose private materials can also live there. The CLI also has default writable paths such as `/tmp/claude`; audit those when adopting the complete runtime. Leave `allowLocalBinding` false and `allowedDomains` empty for an offline consumer.

The installed `codex-cli 0.152.1` also exposes a direct `codex sandbox` command, including `--sandbox-state-json`, `--sandbox-state-readable-root`, `--sandbox-state-disable-network`, `--permission-profile`, and `--log-denials`. Only help/version were read; its state schema and runtime behavior were not qualified. Do not treat a generic read-only profile as private-material read isolation.
