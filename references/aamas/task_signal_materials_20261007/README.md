# Native task signal materials — 2026-10-07

Unmodified excerpts at file granularity from the local clean TeamBench checkout,
commit `d185aef1916fd86a9ba554d581fd256319a973af`. [Manifest](manifest.json)
records original paths, copy paths and SHA-256 hashes; [MIT license](upstream/LICENSE)
is retained. These are research inputs, **not activated benchmarks or experiment results**.

| Material | Reusable part | Decisive unresolved issue |
|---|---|---|
| [PIPE1 generator](upstream/generators/gen_pipe1_etl_fix.py:561) and [grader](upstream/tasks/PIPE1_etl_fix/grade.sh:29) | Field/type/default mapping; Planner/Executor information split (generator:738); actual ETL output record comparison | Producer data is largely preconstructed; peer-produced delivery quality, recipient judgment, ownership and future assignment have not been qualified |
| [Message queue generator](upstream/generators/gen_pipe3_msg_queue.py:871) and [grader](upstream/tasks/PIPE3_msg_queue/grade.sh:90) | Envelope, ack/dedup/DLQ state semantics; executable produce→consume test | Generator emits queue.py while tests/main import queue_impl; stdlib queue naming risk; producer check includes string matching. Static finding, not executed failure |
| [Stream-processing generator](upstream/generators/gen_pipe3_stream_processing.py:4) | Existing comparison scaffold and fixed serialization obligations | Renamed seeds are not independent roots; five historical producer trials do not supply natural category diversity |

No generator, grader, LLM, or GPU was executed in this inspection. Do not leak
grader/expected material into actor prompts. Before activation, independently
qualify task validity, provenance/authority, visibility, scorer coverage and root
split. Existing PIPE2 CSV failures must **not** be attributed to PIPE1 without evidence.

The useful next step for PIPE1 is to check whether a recipient truly needs a
peer-produced mapping/delivery, under a public contract that can be scored
without confusing recipient implementation work with producer quality. No such
adaptation has been implemented or accepted here.
