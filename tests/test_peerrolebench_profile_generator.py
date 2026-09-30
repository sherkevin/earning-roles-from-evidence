from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_metateam_profile_qualification import digest, profile  # noqa: E402
from peerrolebench_profile_generator import (  # noqa: E402
    DeterministicPublicProfileGenerator,
    PublicProfileGenerationRequest,
)


def _request(public_projection=None):
    selection = SimpleNamespace(
        candidates=(SimpleNamespace(key="agent-a@v1"), SimpleNamespace(key="agent-b@v1")),
        chosen_index=0, protocol_event_id="selection-0", event_id="decision-0", task_index=0,
    )
    feedback = SimpleNamespace(
        selection_event_id="selection-0", source_event_id="judgment-0",
        delivery_id="delivery-0", producer_id="agent-a", producer_version="v1",
        recipient_id="agent-r", protocol_event_id="judgment-0", sidecar_digest="a" * 64,
    )
    projection = public_projection or SimpleNamespace(
        source="recipient_judgment", candidate_key="agent-a@v1", source_event_id="judgment-0",
        disposition="eligible", provenance="public", arrival_index=2,
        public_payload=lambda: {
            "feedback_id": "feedback-0", "source_event_id": "judgment-0",
            "source": "recipient_judgment", "candidate_key": "agent-a@v1",
            "evidence_version": "evidence-v1", "source_index": 2, "arrival_index": 2,
            "arrived_at": 2.0, "delay": 0.0, "action": "use", "disposition": "eligible",
            "provenance": "public", "label": 1.0,
        },
    )
    return PublicProfileGenerationRequest(
        selection=selection, feedback_sidecar=feedback, public_projection=projection,
        attribution_gate=SimpleNamespace(eligible=True, gate_digest="b" * 64,
                                         sidecar_digest="a" * 64, protocol_event_id="judgment-0"),
        profile_id="profile-a-r1", profile_revision=1, profile=profile().profile,
        parser_version="fixture-parser-v1", model_config_digest=digest("model"),
    )


def test_deterministic_generator_returns_non_scientific_receipt():
    generated = DeterministicPublicProfileGenerator().generate(_request())
    assert generated.profile.selected_candidate_key == "agent-a@v1"
    assert generated.receipt.source_input_digest == generated.profile.source_input_digest
    assert generated.receipt.profile_digest == generated.profile.profile_digest
    assert generated.receipt.real_api_calls == 0
    assert generated.receipt.gpu_jobs == 0
    assert generated.receipt.scientific_claim_allowed is False


def test_unknown_projection_cannot_create_profile():
    unknown = SimpleNamespace(
        source="recipient_judgment", candidate_key="agent-a@v1", source_event_id="judgment-0",
        disposition="unknown", provenance="unknown", arrival_index=2,
        public_payload=lambda: {"feedback_id": "f", "source": "recipient_judgment"},
    )
    try:
        DeterministicPublicProfileGenerator().generate(_request(unknown))
    except ValueError as exc:
        assert "eligible public" in str(exc)
    else:
        raise AssertionError("UNKNOWN projection unexpectedly produced a profile")


def test_private_public_payload_is_rejected_before_generation():
    private = SimpleNamespace(
        source="recipient_judgment", candidate_key="agent-a@v1", source_event_id="judgment-0",
        disposition="eligible", provenance="public", arrival_index=2,
        public_payload=lambda: {"feedback_id": "f", "terminal_score": 1.0},
    )
    try:
        DeterministicPublicProfileGenerator().generate(_request(private))
    except ValueError as exc:
        assert "forbidden" in str(exc)
    else:
        raise AssertionError("private payload unexpectedly entered the generator")
