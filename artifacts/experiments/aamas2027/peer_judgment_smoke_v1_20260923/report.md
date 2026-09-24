# Peer-judgment observation smoke v1 — development result

2026-09-23. This is a real idealab API / native AppWorld **development** attempt, not a role-learning or paper-method experiment. The [prospective contract](../../../../configs/aamas2027/peer_judgment_smoke_v1.json) fixed two train IDs, order, isolation, feedback and per-agent call caps before execution. [Raw per-call/event logs](episodes/), [per-task results](processed_results.json) and the [exact runner bytes](runner_at_execution.py) are retained. Both episode logs record runner SHA256 `2eaaab855ed207515f7833cc4bac89b475f5235af95cd09f667d442f7fe63780` and source-config SHA256 `722178646940ac20473cca9bb6d4dc24d28a8df516b11a2c184afe437d2676de`.

| Native task, fixed order | Real inference and environment trace | Result |
|---|---|---|
| `22cc237_1` | One producer API attempt; no model response, no environment step; read timeout after 120 s, usage unknown | Transport UNKNOWN; no proposal or consumer judgment |
| `3c13f5a_1` | One successful `qwen3.8-max` response (3,664 input and 2,824 reported output tokens); zero public read steps | Model directly emitted a proposal citing `source_steps=[1]` that never occurred; schema/provenance check rejected it. No consumer was called or task scored |

Total: 2 attempted real LLM calls, 1 successful response, 1 unknown-usage attempt, 0 grounded proposals, 0 sealed consumer judgments, 0 official task outcomes. The second task ran after the first timeout as fixed by the contract. We cannot infer whether consumer judgments help role learning; the initial observation protocol failed before that stage.

One implementation refinement was briefly written to the working runner while the first child process was active, before either task's outcome was inspected. It was **reverted to the exact first-episode SHA before the second child started**, and both episode headers verify identical script hashes. The refinement was not used by either episode; the archived runner contains the executed bytes. The name `proposal_actually_used` in that version would at most show a matching successful HTTP request wrapper, not prove cognitive reliance or successful payment creation; no consumer action occurred in v1. Any later development version must record attempted use and confirmed API success separately.

The observed failure suggests a limited, explicit revision: require at least one real public read before accepting a source-linked proposal, and allow a charged validation-feedback repair within a prospective cap. A provider timeout may receive one charged retry only if declared before the next run. New sibling IDs and a new contract are needed; v1 IDs are not rerun or treated as confirmation.
