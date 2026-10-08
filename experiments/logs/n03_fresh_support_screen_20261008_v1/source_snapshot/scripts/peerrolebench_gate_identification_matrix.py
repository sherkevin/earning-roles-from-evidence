"""Zero-call matrix for identifying the value of the responsibility gate.

The matrix keeps the candidate updater, feature vectors, correction semantics,
capacities and assignment operator fixed.  The diagnostic ungated arm differs
only by consuming a visible raw recipient signal even when attribution makes
that signal ineligible for producer evidence.  Missing raw signals are skipped
by both arms; they are never converted to label zero.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from typing import Any

from peerrolebench_raresafe_candidate import RareAnchorState, RoleFeedback


@dataclass(frozen=True)
class MatrixEvent:
    key: str
    source_index: int
    feature: tuple[float, float]
    raw_label: float | None
    producer_label: float | None
    producer_status: str
    supersedes: str | None = None


def _common_events(raw_label: float | None, feature: tuple[float, float]) -> tuple[MatrixEvent, ...]:
    return (
        # Recipient-owned integration: raw acceptance is observable, but it is
        # not a producer label. The gate arm must no-op this row.
        MatrixEvent("recipient", 1, feature, raw_label, None, "ineligible"),
        # Producer-owned evidence arrives with a later contradictory correction.
        MatrixEvent("producer", 2, (0.0, 1.0), 0.0, 0.0, "eligible"),
        MatrixEvent("producer-correction", 3, (0.0, 1.0), 1.0, 1.0, "eligible", "producer"),
    )


def _ingest(state: RareAnchorState, event: MatrixEvent, *, gated: bool) -> str:
    if gated:
        status = event.producer_status
        label = event.producer_label
    elif event.raw_label is None:
        status = "unknown"
        label = None
    else:
        status = "eligible"
        label = event.raw_label
    return state.ingest(RoleFeedback(
        key=event.key,
        source_index=event.source_index,
        features=event.feature,
        label=label,
        weight=1.0,
        status=status,
        supersedes=event.supersedes,
    ))


def _run(events: tuple[MatrixEvent, ...]) -> dict[str, Any]:
    gated = RareAnchorState(dimension=2, window_size=8, reservoir_size=4, pending_size=4)
    ungated = RareAnchorState(dimension=2, window_size=8, reservoir_size=4, pending_size=4)
    trace = []
    for event in events:
        gated_status = _ingest(gated, event, gated=True)
        ungated_status = _ingest(ungated, event, gated=False)
        trace.append({
            "event": event.key,
            "gated_status": gated_status,
            "ungated_status": ungated_status,
            "gated_digest": gated.semantic_digest(),
            "ungated_digest": ungated.semantic_digest(),
        })
    candidates = ((1.0, 0.0), (0.0, 1.0))
    gated_p = gated.probabilities(candidates)
    ungated_p = ungated.probabilities(candidates)
    gated_choice = "A" if gated_p[0] >= gated_p[1] else "B"
    ungated_choice = "A" if ungated_p[0] >= ungated_p[1] else "B"
    return {
        "events": [event.__dict__ for event in events],
        "trace": trace,
        "gated": {"theta": gated.theta, "probabilities": gated_p, "chosen": gated_choice, "digest": gated.semantic_digest()},
        "ungated_raw": {"theta": ungated.theta, "probabilities": ungated_p, "chosen": ungated_choice, "digest": ungated.semantic_digest()},
        "probability_separation": any(abs(a - b) > 1e-12 for a, b in zip(gated_p, ungated_p)),
        "choice_separation": gated_choice != ungated_choice,
    }


def run_matrix() -> dict[str, Any]:
    positive = _run(_common_events(1.0, (1.0, 0.0)))
    zero = _run(_common_events(0.0, (1.0, 0.0)))
    missing = _run(_common_events(None, (1.0, 0.0)))
    diagonal = _run(_common_events(1.0, (2 ** -0.5, 2 ** -0.5)))
    cases = {
        "raw_positive_orthogonal": positive,
        "raw_zero_orthogonal": zero,
        "raw_missing_orthogonal": missing,
        "raw_positive_nonorthogonal": diagonal,
    }
    return {
        "probe": "gate_identification_matrix_v1",
        "cases": cases,
        "interpretation": (
            "A visible positive raw acceptance signal creates a gate-vs-ungated separation, "
            "whereas raw zero or missing signals do not. This qualifies an identifiable "
            "gate-ablation condition only; it is not evidence of efficacy or novelty."
        ),
        "api_calls": 0,
        "gpu": 0,
        "scientific_claim_allowed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_matrix(), ensure_ascii=False, sort_keys=True, indent=2))
