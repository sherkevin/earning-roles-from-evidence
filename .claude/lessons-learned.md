# Engineering lessons

### 0001-idealab-single-authentication-header | 2026-09-22 | earning-roles

- **Symptom:** the first real inference health request returned HTTP 401.
- **Cause:** it sent both `x-api-key` and `Authorization`; idealab explicitly
  rejects simultaneous authentication headers on its code endpoint.
- **Prevention:** map cc-switch `ANTHROPIC_AUTH_TOKEN` to the Bearer header only,
  validate with a real small call, and archive failed attempts before retrying.
- **Evidence:** `artifacts/experiments/aamas2027/dev_20260922/preflight_raw.jsonl`.
- **Outcome:** the next request returned HTTP 200 with model `qwen3.8-max` and
  real usage. Endpoint/catalog availability alone was not called inference health.

### 0002-httpx-ipv6-cidr-import | 2026-09-22 | earning-roles

- **Symptom:** importing the official ReAct parser failed in litellm/httpx before any task model call.
- **Cause:** NO_PROXY contained `::1/128`; httpx turned it into an invalid URL host. Early bracket/removal attempts targeted `::1` and missed the CIDR.
- **Prevention:** inspect parser source and the relevant sanitized environment value before patching. Normalize only `::1/128` to equivalent `::1` inside the experiment subprocess; do not modify global proxy settings.
- **Evidence:** all fixture failures and the eventual check are in `artifacts/experiments/aamas2027/dev_20260922/runtime_fixture_raw.jsonl`.

### 0003-semantic-arm-label-in-storage-path | 2026-09-22 | earning-roles

- **Symptom:** memory-arm solving completed, but official evaluation had zero assertions and a storage exception.
- **Cause:** pinned AppWorld tests whether the substring `memory` occurs anywhere in a DB changes path, so a normal arm label was mistaken for SQLite in-memory storage.
- **Prevention:** keep scientific labels in metadata, use neutral hashes for native storage paths, and test both treatment and control scorer paths before broad execution.
- **Repair:** preserve original errors; copy already saved state files byte-for-byte to neutral paths and call the unchanged official scorer. Do not rerun a model or treat an unavailable scorer as a task-quality failure.
- **Evidence:** `scorer_storage_repair.json` and per-episode `rescoring_raw.jsonl` under the current experiment directory.

### 0004-requested-output-is-not-total-generation-cap | 2026-09-22 | earning-roles

- **Symptom:** all six induction responses reported output usage above the requested text limit.
- **Cause:** the provider's reported total includes reasoning generation; the nominal parameter is not an independently enforced aggregate spend limit.
- **Prevention:** distinguish requested settings from actual reported usage, include cached input and reasoning output, retain unknown failed-request usage, and use attempted-call ceilings explicitly. Do not publish an exact dollar bill without prices.
- **Evidence:** the first round's six induction raw responses and `analysis.json`.

### 0005-resume-must-respect-persisted-outage-stop | 2026-09-22 | earning-roles

- **Symptom:** pre-inference independent review found that a controller could skip completed tasks after restart and thereby bypass a prior two-task outage stop.
- **Cause:** the circuit breaker was checked only after newly completed work.
- **Prevention:** before any paid subprocess, check durable stop events and the ordered completed prefix, including a crash between result persistence and stop-event persistence.
- **Outcome:** fixed before the full-dev census's first request; the reviewed code and contract were then hashed and frozen.

### 0006-cost-categories-must-partition-the-full-ledger | 2026-09-22 | earning-roles

- **Symptom:** total 329 raw requests reconciled, but acquisition subtotal 86 omitted the 16-call explicitly tagged repair; a residual 48 was incorrectly described as null cost.
- **Cause:** an exact-stage filter did not include the repair stage; the independent reviewer checked arithmetic without reclassifying every episode.
- **Prevention:** include every stage and assert acquisition 102 + validation 195 + unchanged controls 32 = raw 329. Category-level checks are necessary even when the grand total passes.
- **Repair:** preserved the pre-fix report/analyzer/review and added a correction record; official scores and gate decision are unchanged.

### 0007-database-checkpoint-is-not-complete-agent-state | 2026-09-22 | earning-roles

- **Symptom:** a native checkpoint copied into a fresh world lost `playlists` at the first continuation; native teardown also raised freezegun errors.
- **Cause:** AppWorld `save_state` stores database changes, not the REPL namespace or model messages. Its `load_state` closes process-global runtime state, interacting with context-manager cleanup.
- **Prevention:** reconstruct and validate the complete continuation state in isolated processes; charge prefix execution and environment calls. Do not infer faithful replay from matching DB files.
- **Evidence:** `artifacts/experiments/aamas2027/replay_fixture_20260922/` preserves the config, two identical complete code replays, failed database-only continuation and unmodified stderr. Zero new LLM calls; the overall fixture is explicitly partial.

### 0008-single-trajectory-difference-is-not-causal-proof | 2026-09-23 | earning-roles

- **Symptom:** a report described a treatment-versus-control trace difference as experience changing behavior.
- **Cause:** each arm was run once and repeated untreated execution also changed request count and actions; the analysis skipped this variance check when moving from observation to causal wording.
- **Prevention:** state the observed contrast first, inspect unchanged-agent repeat variation, and reserve attribution to acquired content for a prospectively controlled comparison that separates content, generic reminders and prompt length.
- **Evidence:** [reassessment](../docs/scientist/analysis/AAMAS_Q1_FEASIBILITY_REVIEW_20260922.md#报告判断的再次复核) and [task record](../docs/coordination/AAMAS_TASKS.md); frozen raw runs remain unchanged.
