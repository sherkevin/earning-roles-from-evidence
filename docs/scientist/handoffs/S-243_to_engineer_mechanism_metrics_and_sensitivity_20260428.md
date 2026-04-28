# S-243 To Engineer: Mechanism Metrics And Sensitivity Dispatch

Date: 2026-04-28
Author role: scientist
Target role: engineer
Priority: P1

## 1. Why This Dispatch Exists

The user asked the scientist to stop over-focusing on figures and push method / engineering work that helps the paper get accepted. This dispatch is based on three repeated reviewer caps:

1. the paper claims "organization" but mostly reports QA F1/EM;
2. the paper has no sensitivity analysis for routing / memory / tool policies;
3. matched paid external baselines remain blocked by `C-027`, so the next useful work should be no-paid and should improve scientific interpretability.

This is not a request for broad matrix filling. It is a request for two targeted evidence builders that can improve the paper even if paid canonical Wave-1 remains parked.

## 2. Research Basis

This dispatch reuses prior project research rather than inventing a new direction:

- `S-231` says the organization-emergence claim must be converted into measurable mechanism statements: routing stability, persona/tag divergence, audit value, memory/tool ablation deltas, and error-mode shifts.
- `R-PART-003` says mature systems should be used as references/adapters, not black-box replacements:
  - LangGraph for state graphs / checkpointing discipline;
  - mem0 / Letta for scoped memory operations and auditable memory edits;
  - RAGAS for retrieval/tool metrics as auxiliary diagnostics;
  - MCP-style tool cards for typed tool boundary and event logging.
- `E-049` shows EDO-Frame consumption-layer switches are causal but non-positive, so the next step is to explain mechanism behavior rather than claim component wins.
- `E-051` / `E-052` show canonical paid Wave-1 is planned and guarded, but still user-gated by `C-027`.

## 3. Engineer Task E-055: Existing-Artifact Mechanism Metrics

Goal:

Build a no-paid mechanism-metrics extractor over existing run artifacts. The deliverable should answer: "what organization-like behavior is visible in the logs, independent of headline F1?"

Required inputs, if available:

- `E-042` / `E-045` Phi-4 HotpotQA runs;
- `E-049` EDO-Frame Step3.5 ablation runs;
- `E-047` MuSiQue and `E-050` 2Wiki transfer gates;
- any `routing_traces.jsonl`, `handoff_packets.jsonl`, `competence_snapshots.jsonl`, `task_tree.jsonl`, `audit_events.jsonl`, memory/tool event fields, and `metrics.json` available under those run dirs.

Minimum metrics:

1. routing path length and handoff distribution;
2. accepted / terminal agent distribution and entropy;
3. delegation edge counts and concentration (e.g. entropy or Gini);
4. per-method first-accept / no-forward / reroute proxies when fields exist;
5. EDO-Frame memory/tool event counts, selected-tool distribution, retrieval counts, and selector-mode differences when fields exist;
6. link at least a small set of E-048 case candidates to routing / handoff traces if possible.

Acceptance:

- Write `docs/engineer/results/E-055_mechanism_metrics_existing_artifacts_20260428.md`.
- Write machine-readable outputs under `artifacts/mechanism_metrics/e055_<timestamp>/` (`.json`, `.csv`, and a compact `.md` table).
- Record exact input run dirs, scripts, commands, and missing-field caveats.
- Make zero LLM calls and zero paid API calls.
- If a metric cannot be computed because a field is absent, report the absence as a schema gap rather than fabricating a proxy.

Paper use if successful:

The scientist can add a compact "mechanism evidence" paragraph/table that says which organization proxies are measurable and what they show. If the metrics are weak or negative, they still improve the paper by bounding the emergence claim honestly.

## 4. Engineer Task E-056: Minimal No-Paid Sensitivity Gate

Goal:

After `E-055`, run the smallest useful no-paid sensitivity gate over the mechanism knobs that matter most. This should target explanation, not leaderboard gain.

Candidate axes:

1. EDO-Frame ablation / selector mode: `edo_full`, `no_memory`, `all_tools`, `random_tools`, `static_tools` if already supported.
2. Retrieval policy: BM25 on/off, recency on/off, retrieval count / selected-tool count if exposed.
3. Drift / selector threshold: one low / default / high threshold if the runner exposes it safely.
4. Hop cap or accept threshold only if the existing launcher/config supports it without risky refactor.

Default scope:

- no-paid local Phi-4;
- HotpotQA n=50 or n=100 depending on runtime cost;
- use existing seed slices;
- checkpoint/resume required;
- do not spend paid API;
- do not run a wide matrix before the first sensitivity axis is interpretable.

Acceptance:

- Write `docs/engineer/results/E-056_no_paid_sensitivity_gate_20260428.md`.
- Include exact configs, commands, run dirs, metrics, tokens, and caveats.
- Report whether the tested axis changes behavior, not just whether F1 moves.
- If no safe axis is exposed, write a result document explaining the blocker and propose the smallest code surfacing task.

Paper use if successful:

The scientist can replace "no sensitivity sweep" with a bounded sensitivity result. A negative or unstable result is still useful as a limitation; a clear directional result can guide the next method redesign.

## 5. Pinned Cautions For Engineer

1. Do not make paid API calls.
2. Do not treat local diagnostics as canonical `gpt-4.1-mini` matrix evidence.
3. Do not claim memory/tool governance improves accuracy unless the metrics support it.
4. Do not create a new framework dependency for E-055/E-056. Use mature frameworks as design references only.
5. Preserve checkpoint/resume for any new run.
6. Prefer exact missing-field reports over weak invented metrics.
7. Keep all outputs reproducible and traceable to run dirs.
