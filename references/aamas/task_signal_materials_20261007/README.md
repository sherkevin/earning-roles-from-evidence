# Native task signal materials — 2026-10-07

Unmodified excerpts at file granularity from the local clean TeamBench checkout,
commit `d185aef1916fd86a9ba554d581fd256319a973af`. [Manifest](manifest.json)
records original paths, copy paths and SHA-256 hashes; [MIT license](upstream/LICENSE)
is retained. These are research inputs, **not activated benchmarks or experiment results**.

| Material | Reusable part | Decisive unresolved issue |
|---|---|---|
| [PIPE1 generator](upstream/generators/gen_pipe1_etl_fix.py:561) and [grader](upstream/tasks/PIPE1_etl_fix/grade.sh:29) | Field/type/default mapping; native Planner rules → message → Executor implementation; partial output value/type checks | Peer delivery is a rule message, not the generated input data. Direct spec relay, full Verifier path, timezone, scorer coverage and persistent peer suitability remain unqualified |
| [Message queue generator](upstream/generators/gen_pipe3_msg_queue.py:871) and [grader](upstream/tasks/PIPE3_msg_queue/grade.sh:90) | Envelope, ack/dedup/DLQ state semantics; executable produce→consume test | Generator emits queue.py while tests/main import queue_impl; stdlib queue naming risk; producer check includes string matching. Static finding, not executed failure |
| [Stream-processing generator](upstream/generators/gen_pipe3_stream_processing.py:4) | Existing comparison scaffold and fixed serialization obligations | Renamed seeds are not independent roots; five historical producer trials do not supply natural category diversity |

No generator, grader, LLM, or GPU was executed in the initial source inspection.
The subsequent capture below executed four native generator calls. Do not leak
grader/expected material into actor prompts. Before activation, independently
qualify task validity, provenance/authority, visibility, scorer coverage and root
split. Existing PIPE2 CSV failures must **not** be attributed to PIPE1 without evidence.

The useful next step for PIPE1 is to check whether a recipient truly needs a
peer-produced mapping/delivery, under a public contract that can be scored
without confusing recipient implementation work with producer quality. No such
adaptation has been implemented or accepted here.

## Subsequent bounded offline inspection

- [Native role-view capture](../../../experiments/logs/n03_pipe1_native_material_audit_20261007_v1/summary.json):
  seeds 0–3, four business domains, one structural root; original Planner spec,
  Executor brief/workspace and parent-only expected records saved separately.
  Four generator calls; no candidate, grader, LLM or GPU execution. Two-role
  static projection, not a full native run.
- [Unmodified native harness](native_harness/manifest.json): initial Planner
  spec can be relayed through `send_message`; Executor reads full messages.
  Verifier also sees the full spec and can request up to two remediation rounds.
  Verbatim relay is a necessary diagnostic comparator, still NOT_RUN.
- [Timezone audit](../../../experiments/logs/n03_pipe1_timezone_audit_20261007_v1/summary.json):
  the 20 healthcare/financial records have different UTC vs Asia/Shanghai dates;
  saved expected dates all match the latter. Native `fromtimestamp` omits tz.
  The original capture's exact timezone is not established; future generation,
  actor execution and grading need a recorded shared convention.
- [Selection-value conditions and next decisions](../../../docs/research/candidates/benchmark_selection_value_20261007.md).

These additions qualify research questions, not the benchmark or the method.
