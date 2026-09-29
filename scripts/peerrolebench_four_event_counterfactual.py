"""Zero-call four-event identification probe for the candidate role updater.

This is deliberately a small, deterministic counterfactual.  It does not
simulate an LLM or claim benchmark efficacy.  It asks a narrower question:
can the current responsibility-aware candidate produce a different, justified
pre-execution assignment from an *exact same-updater* policy with the
responsibility gate removed on the minimum event stream proposed by the debate?
The control shares features, update rule, correction semantics, and capacity;
only the eligibility decision differs.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from peerrolebench_raresafe_candidate import RareAnchorState, RoleFeedback


@dataclass(frozen=True)
class Event:
    key: str
    source_index: int
    producer: str
    owner: str
    context: str
    feature: tuple[float, float]
    raw_label: float
    rare_status: str
    rare_label: float | None
    supersedes: str | None = None


class UngatedSameInfo:
    """Exact same-information control with the responsibility gate removed."""

    def __init__(self) -> None:
        self.state = RareAnchorState(dimension=2, window_size=8, reservoir_size=4, pending_size=4)

    def ingest(self, event: Event) -> str:
        return self.state.ingest(RoleFeedback(
            key=event.key,
            source_index=event.source_index,
            features=event.feature,
            label=event.raw_label,
            weight=1.0,
            status="eligible",
            supersedes=event.supersedes,
        ))

    def probabilities(self, context: str) -> tuple[float, float]:
        del context
        return self.state.probabilities(((1.0, 0.0), (0.0, 1.0)))

    def digest(self) -> str:
        return self.state.semantic_digest()


def _events() -> tuple[Event, ...]:
    return (
        # Recipient-owned integration error: public rejection exists, but the
        # producer contract is correct. RARE must no-op; the naive control uses
        # the same visible raw label.
        Event("e1", 1, "A", "R1", "c1", (1.0, 0.0), 0.0, "unknown", None),
        # Producer-owned defect: both methods receive the selected judgment.
        Event("e2", 2, "B", "R1", "c1", (0.0, 1.0), 0.0, "eligible", 0.0),
        # A late contradictory outcome corrects e2.
        Event("e2-correction", 3, "B", "R1", "c1", (0.0, 1.0), 1.0, "eligible", 1.0, "e2"),
    )


def _rare_probs(state: RareAnchorState, context: str) -> tuple[float, float]:
    del context  # The tiny probe encodes context in the event feature only.
    return state.probabilities(((1.0, 0.0), (0.0, 1.0)))


def _run(schedule: str) -> dict[str, Any]:
    events = _events()
    rare = RareAnchorState(dimension=2, window_size=8, reservoir_size=4, pending_size=4)
    trust = UngatedSameInfo()
    trace: list[dict[str, Any]] = []
    assignment: dict[str, Any] | None = None

    for event in events:
        if schedule == "after_assignment" and event.key == "e2-correction":
            continue
        rare_status = rare.ingest(RoleFeedback(
            key=event.key,
            source_index=event.source_index,
            features=event.feature,
            label=event.rare_label,
            weight=1.0,
            status=event.rare_status,
            supersedes=event.supersedes,
        ))
        trust_status = trust.ingest(event)
        trace.append({
            "event": event.key,
            "rare_status": rare_status,
            "trust_status": trust_status,
            "rare_digest": rare.semantic_digest(),
            "trust_digest": trust.digest(),
        })
        if schedule == "after_assignment" and event.key == "e2":
            assignment = _assignment(rare, trust, "c2")

    if assignment is None:
        assignment = _assignment(rare, trust, "c2")
    if schedule == "after_assignment":
        # The correction arrives after the decision and must not rewrite it.
        correction = next(event for event in events if event.key == "e2-correction")
        rare_status = rare.ingest(RoleFeedback(
            key=correction.key,
            source_index=correction.source_index,
            features=correction.feature,
            label=correction.rare_label,
            weight=1.0,
            status=correction.rare_status,
            supersedes=correction.supersedes,
        ))
        trust_status = trust.ingest(correction)
        trace.append({
            "event": correction.key,
            "rare_status": rare_status,
            "trust_status": trust_status,
            "after_assignment": True,
            "rare_digest": rare.semantic_digest(),
            "trust_digest": trust.digest(),
        })
    return {"schedule": schedule, "trace": trace, "assignment": assignment}


def _assignment(rare: RareAnchorState, trust: DelayedContextualTrust, context: str) -> dict[str, Any]:
    rare_p = _rare_probs(rare, context)
    trust_p = trust.probabilities(context)
    rare_choice = "A" if rare_p[0] >= rare_p[1] else "B"
    trust_choice = "A" if trust_p[0] >= trust_p[1] else "B"
    return {
        "owner": "R2",
        "context": context,
        "rare": {"chosen": rare_choice, "probabilities": rare_p, "state_digest": rare.semantic_digest()},
        "same_info_ungated": {"chosen": trust_choice, "probabilities": trust_p, "state_digest": trust.digest()},
        "same_choice": rare_choice == trust_choice,
        "same_probability": all(abs(a - b) < 1e-12 for a, b in zip(rare_p, trust_p)),
    }


def run_probe() -> dict[str, Any]:
    runs = [_run("before_assignment"), _run("after_assignment")]
    return {
        "probe": "four_event_same_information_counterfactual_v1",
        "events": [event.__dict__ for event in _events()],
        "runs": runs,
        "identification": {
            "same_choice_before_assignment": runs[0]["assignment"]["same_choice"],
            "same_choice_after_assignment": runs[1]["assignment"]["same_choice"],
            "candidate_separates_on_minimal_stream": not all(run["assignment"]["same_choice"] for run in runs),
            "interpretation": "The exact same-updater control produces the same probabilities and choices on this three-event stream; the stream therefore does not identify a responsibility-gate advantage. The late correction still cannot rewrite the sealed assignment. This is a candidate-level negative qualification, not an impossibility result.",
        },
        "api_calls": 0,
        "gpu": 0,
        "scientific_claim_allowed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_probe(), ensure_ascii=False, sort_keys=True, indent=2))
