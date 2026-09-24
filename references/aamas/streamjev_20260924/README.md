# Stream-JEV prototype (2026-09-24)

This directory contains the first executable vertical slice for the shared
peer/tool decision runtime. It is a method prototype, not a paper result.

- `protocol.py`: shared typed-decision, action and delayed-feedback contract.
- `fast_state.py`: deterministic dual fast state (decayed posterior + RLS
  residual) used to test update semantics before loading a neural encoder.
- `neural_fast_state.py`: cached-embedding candidate scorer and bounded gated
  fast-state core intended for short-unroll meta-training.
- `online_head.py`: selected-only `OnlineRLSHead`, the current stable
  parameter-learning mainline. It updates a low-dimensional utility head on
  every arrived feedback, records exact propensities, and deduplicates replay
  retries when a feedback id is supplied.
- `test_streamjev.py`, `test_neural_fast_state.py`: contract, permutation,
  selected-only and stability tests.
- `experiments/synthetic_meta_train.py`: historical hidden-regime smoke. Its
  result is invalidated for scientific claims because it used an oracle target;
  see `experiments/logs/synthetic_meta_train_20260924_invalidated.json`.
- `experiments/selected_only_rls.py`: corrected selected-only randomized smoke
  with paired seeds and label-shuffle/no-feedback controls.

The neural scorer and A800 runner will consume the same event contract. The
prototype intentionally has no LLM/API dependency and must not be interpreted
as evidence that the final method works. The synthetic smoke is only a
falsification probe; real replay and same-information baselines are still
required.
