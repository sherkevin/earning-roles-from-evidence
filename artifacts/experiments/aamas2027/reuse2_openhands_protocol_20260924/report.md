# REUSE-2 OpenHands protocol fixture

This is a zero-LLM integration fixture, not a scientific result. It uses the
pinned OpenHands SDK environment (`openhands-sdk==1.49.5`, commit
`e21d77673b738f056676044600c4ad81c5a575c8`) with `TestLLM` and three custom
tools. No network completion or paid API call was made.

The successful trace records four hash-chained project events:

1. `producer_delivery` creates an immutable artifact envelope and SHA-256.
2. `delivery_visible` exposes only the bounded delivery context.
3. `recipient_judgment` seals `accept` before any consumer action and records
   `terminal_outcome_available=false`.
4. `consumer_action` integrates the exact artifact and writes the output hash.

The OpenHands callback captured 9 events and the conversation reached
`FINISHED`. The successful result is in `result.json`; the append-only ledger is
`ledger.jsonl`; persisted SDK events are under `persistence/`.

The first run failed with a real `FileNotFoundError` because the adapter did not
create its project-owned consumer work directory. The failure is preserved under
`../reuse2_openhands_protocol_20260924_failed_attempt/` with structured cause
and impact. The fix creates the directory during `ConsumerGate` initialization.

CPU-only negative checks also pass: applying before a judgment raises an
`AssertionError`, and recording a second judgment is rejected. These checks
protect the ordering and immutability invariants independently of the scripted
agent run.

This fixture proves only that the evidence boundary can be implemented on top of
the runtime. It does not prove recipient judgment quality, causal producer value,
role transfer, or a benchmark result.
