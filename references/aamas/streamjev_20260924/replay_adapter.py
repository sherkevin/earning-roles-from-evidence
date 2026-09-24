"""Pure adapter from selected-only replay observations to Stream-JEV events.

The adapter accepts already-serialized public observations.  It deliberately
does not import a benchmark cache, truth store, or judge.  A benchmark runner
must call ``make_feedback_event`` only after its terminal scorer has produced a
lawful correctness signal.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence, Tuple

from protocol import Candidate, DecisionEvent, FeedbackEvent, candidate_tuple


def make_decision_event(
    *,
    event_id: str,
    episode_id: str,
    decision_type: str,
    selector_input: Mapping[str, Any],
    chosen_id: str,
    propensity: float,
    state_version: str,
    observed_at: float,
    encoder_version: str = "unknown",
    feature_schema: str = "default",
    captured_features: Mapping[str, Sequence[float]] | None = None,
) -> DecisionEvent:
    """Convert a public selector input without reading hidden truth.

    Prior selected outputs in ``history`` remain visible, including a field
    named ``label``.  The adapter copies only the public observation fields and
    leaves hidden correctness data to the terminal judge.
    """
    raw_candidates = selector_input.get("candidates")
    if not isinstance(raw_candidates, Sequence) or isinstance(raw_candidates, (str, bytes)):
        raise ValueError("selector_input.candidates must be a sequence")
    candidates = candidate_tuple(
        Candidate(
            candidate_id=str(row["provider_id"] if "provider_id" in row else row["candidate_id"]),
            kind=str(row.get("kind", row.get("family", "candidate"))),
            version=str(row.get("version", row.get("snapshot_round", "unknown"))),
            description=str(row.get("name", row.get("description", ""))),
            metadata={k: row[k] for k in ("function", "family") if k in row},
        )
        for row in raw_candidates
    )
    context = {
        k: selector_input[k]
        for k in ("entity_id", "canonical_smiles", "available_functions", "remaining_calls", "history")
        if k in selector_input
    }
    return DecisionEvent(
        event_id=event_id,
        episode_id=episode_id,
        decision_type=decision_type,
        context=context,
        candidates=candidates,
        chosen_id=chosen_id,
        propensity=propensity,
        state_version=state_version,
        observed_at=observed_at,
        encoder_version=encoder_version,
        feature_schema=feature_schema,
        captured_features={k: tuple(float(x) for x in v)
                           for k, v in (captured_features or {}).items()},
    )


def make_feedback_event(
    *,
    feedback_id: str,
    source_event_id: str,
    correct: int | float,
    arrived_at: float,
    selected_at: float,
    metadata: Mapping[str, Any] | None = None,
) -> FeedbackEvent:
    """Create a delayed correctness event after terminal grading."""
    if correct not in (0, 1) and not (isinstance(correct, float) and 0.0 <= correct <= 1.0):
        raise ValueError("correct must be binary or a soft value in [0,1]")
    if arrived_at < selected_at:
        raise ValueError("feedback cannot arrive before the selected action")
    return FeedbackEvent(
        feedback_id=feedback_id,
        source_event_id=source_event_id,
        label=float(correct),
        arrived_at=arrived_at,
        delay=arrived_at - selected_at,
        metadata=dict(metadata or {}),
    )
