# 0009 — Adopt AnyJev as the shared dynamic-selector stack

Status: Accepted for the shared implementation path. Date: 2026-09-24.

## Context

The peer-selection project and the companion tool-selection project need to
use the same decision framework and base model. Our earlier single-project
audit favored Kev for its training and serving ergonomics. The companion
project then audited `nokia-applied-research/AnyJev` at commit
`a59a69eaa91e62dc9b42924f8491f76d1b1972ea` and verified the actual
freeze–observe–fit–export lifecycle with a fake-backend smoke test.

AnyJev exposes a frozen-model hidden-state head, typed `Question.noul`,
`observe(question, state, label)`, closed-form `fit_head`, and artifact
persistence. Its built-in update still refits all accumulated observations at
30, 60, 120, ... labels; it is a useful baseline and scaffold, not our
event-level learning contribution.

## Decision

1. **Shared framework:** use AnyJev pinned to commit
   `a59a69eaa91e62dc9b42924f8491f76d1b1972ea` under Apache-2.0.
2. **Shared base model:** use `Qwen/Qwen3-4B` through AnyJev's local HF or
   vLLM backend for the first cross-project implementation. The model,
   tokenizer, question text, and readout settings are part of the experiment
   manifest and must be identical across projects. The `内部` idealab
   messages API does not expose hidden states/logits, so it cannot be called
   the AnyJev L2 backend; it may generate task content or serve as an external
   judge instead.
3. **Shared decision primitive:** score each candidate with a fixed binary
   question (`Question.noul`) rather than making the whole candidate menu one
   `choice` question. This supports selected-only labels, local menu sizes
   beyond the current letter-readout limit, and stable candidate IDs.
4. **Shared wrapper contract:** both projects implement
   `score(context, candidates)`, `choose(context, candidates)`,
   `observe(event_id, candidate_id, label, observed_at)`,
   `snapshot()`, and `restore(snapshot)`. The wrapper returns probability,
   uncertainty, propensity, and state version for every choice.
5. **Shared update semantics:** AnyJev `observe`/periodic `fit_head` is the
   no-online-update and scheduled-refit baseline. The proposed method adds a
   per-agent/private residual adapter with delayed selected-only feedback,
   bounded replay and forgetting; full head refits remain asynchronous and
   version-gated.
6. **State/feedback boundary:** pre-action scoring state must not contain the
   selected tool's output or the recipient's post-execution artifact outcome.
   Those fields belong only to the delayed feedback event. If a benchmark
   scores already-produced outputs, it must be named reranking rather than
   pre-execution tool selection.
7. **Label policy:** binary labels are primary so tool correctness and peer
   delivery acceptance have an unambiguous first experiment. Three-level
   labels (for example correct / usable-after-repair / failed) are a later
   ablation only after each project freezes its rubric. Tool and peer labels
   are not pooled into one head unless their semantics and calibration are
   demonstrated to match.

## Rationale

The two projects have the same statistical problem: score a small set of
candidate actions, execute one action, receive a delayed selected-action
outcome, and update a frozen decision representation. AnyJev already covers
the expensive representation and persisted head path, which lets the two
projects share code and makes differences in labels, candidate identity and
feedback timing explicit. The wrapper is where our contribution lives, so it
can be evaluated identically on tools and peers.

Encoding each candidate as a separate `noul` state avoids AnyJev's current
letter-readout limit for large `choice` menus and keeps the selected-only
feedback mapping exact (`Yes` index 0, `No` index 1). It also lets the peer
project retain local graph neighborhoods while the tool project changes its
available tool set.

## Consequences and gates

- Kev is retained as an external strong baseline in the audit, but is removed
  from the shared mainline until a later ablation.
- We must run a real Qwen3-4B inference smoke in this repository before
  claiming model compatibility; the copied fake-backend result is only a
  lifecycle test.
- Candidate IDs must include provider/tool-or-agent/version/configuration;
  changing a version creates a cold-start candidate and cannot silently reuse
  stale labels.
- AnyJev's artifact loader does not by itself pin every tokenizer/weight
  detail. The wrapper must record and validate model revision, tokenizer
  digest, hidden size/layer count, selected feature layer, question/schema
  versions and head hash before loading a snapshot.
- Every event records the candidate menu hash, chosen candidate, propensity,
  feedback delay, update version, and checkpoint hash. Unselected candidates
  receive no fabricated label.
- The first implementation gate is a vertical slice for both projects with
  the same wrapper and logs, followed by DecisionBench/CooperBench evaluation
  for peers and the tool benchmark for tools.
