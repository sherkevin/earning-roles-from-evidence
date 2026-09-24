# Stream-JEV prototype (2026-09-24)

This directory contains the first executable vertical slice for the shared
peer/tool decision runtime. It is a method prototype, not a paper result.

- `protocol.py`: shared typed-decision, action and delayed-feedback contract.
- `fast_state.py`: deterministic dual fast state (decayed posterior + RLS
  residual) used to test update semantics before loading a neural encoder.
- `neural_fast_state.py`: cached-embedding candidate scorer and bounded gated
  fast-state core intended for short-unroll meta-training.
- `test_streamjev.py`, `test_neural_fast_state.py`: contract, permutation,
  selected-only and stability tests.
- `experiments/synthetic_meta_train.py`: hidden-regime delayed-feedback smoke;
  its raw events and metrics are under `experiments/logs/`.

The neural scorer and A800 runner will consume the same event contract. The
prototype intentionally has no LLM/API dependency and must not be interpreted
as evidence that the final method works. The synthetic smoke is only a
falsification probe; real replay and same-information baselines are still
required.
