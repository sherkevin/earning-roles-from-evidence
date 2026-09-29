"""Zero-call qualification for the MetaTeam-L2-public profile boundary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import hashlib
import platform
import sys
from types import SimpleNamespace

from peerrolebench_metateam_profile_sidecar import (
    MetaTeamProfile,
    MetaTeamAssignmentOffer,
    PROFILE_SCHEMA,
    _digest,
    build_public_profile_fixture,
    replay_public_profile_fixture,
    reject_private_public_input,
)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def profile(**overrides):
    base = dict(
        profile_id="profile-a-r1",
        profile_revision=1,
        adapter_variant="public",
        candidate_key="agent-a@v1",
        producer_id="agent-a",
        producer_version="v1",
        recipient_id="agent-r",
        selected_candidate_key="agent-a@v1",
        selection_event_id="sel-0",
        source_event_id="judgment-0",
        delivery_id="delivery-0",
        source_decision_index=0,
        source_arrival_index=2,
        available_index=2,
        source_disposition="eligible",
        source_provenance="public",
        source_input_digest=digest("public-event-bundle-0"),
        profile_schema=PROFILE_SCHEMA,
        parser_version="fixture-parser-v1",
        model_config_digest=digest("profile-model-config-v1"),
        profile={
            "reliability": "medium",
            "strengths": ["queue integration"],
            "weaknesses": ["priority ordering"],
            "communication_style": "concise status updates",
            "notes": ["derived from selected public interaction"],
        },
    )
    base.update(overrides)
    return MetaTeamProfile(**base)


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "qualification": "metateam-l2-public-profile-boundary-v1",
        "script": str(Path(__file__).resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "schema_script_sha256": hashlib.sha256(
            Path(__file__).with_name("peerrolebench_metateam_profile_sidecar.py").read_bytes()
        ).hexdigest(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "argv": list(sys.argv),
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "profile_schema": PROFILE_SCHEMA,
        "adapter_status": "NOT_IMPLEMENTED / QUALIFICATION_REQUIRED",
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    checks = []

    valid = profile()
    valid.consume_before(decision_index=2, read_cut=2)
    checks.append({"name": "valid_public_profile_and_later_consumption", "status": "PASS"})

    try:
        profile(source_arrival_index=4, available_index=3)
    except ValueError as exc:
        checks.append({"name": "reject_profile_before_arrival", "status": "PASS", "error": str(exc)})
    else:
        checks.append({"name": "reject_profile_before_arrival", "status": "FAIL"})

    try:
        profile(source_disposition="unknown")
    except ValueError as exc:
        checks.append({"name": "unknown_does_not_create_profile", "status": "PASS", "error": str(exc)})
    else:
        checks.append({"name": "unknown_does_not_create_profile", "status": "FAIL"})

    try:
        profile().consume_before(decision_index=0, read_cut=2)
    except ValueError as exc:
        checks.append({"name": "reject_same_decision_assignment", "status": "PASS", "error": str(exc)})
    else:
        checks.append({"name": "reject_same_decision_assignment", "status": "FAIL"})

    try:
        profile().consume_before(decision_index=1, read_cut=1)
    except ValueError as exc:
        checks.append({"name": "reject_pre_watermark_consumption", "status": "PASS", "error": str(exc)})
    else:
        checks.append({"name": "reject_pre_watermark_consumption", "status": "FAIL"})

    corrected = profile(
        profile_id="profile-a-r2", profile_revision=2, available_index=4,
        source_arrival_index=4, supersedes_profile_id=valid.profile_id,
    )
    corrected.consume_before(decision_index=4, read_cut=4)
    checks.append({"name": "late_correction_preserves_lineage", "status": "PASS"})

    try:
        reject_private_public_input({"source_event_id": "j0", "trajectory": "hidden trace"})
    except ValueError as exc:
        checks.append({"name": "reject_hidden_trajectory_input", "status": "PASS", "error": str(exc)})
    else:
        checks.append({"name": "reject_hidden_trajectory_input", "status": "FAIL"})

    try:
        mutated = valid.payload()
        mutated["profile"]["notes"].append("post-hoc mutation")
        # A payload mutation must change the canonical digest; it must not be
        # mistaken for a valid profile record.
        if valid.profile_digest == _digest(mutated):
            raise AssertionError("digest unexpectedly accepted mutated payload")
        checks.append({"name": "profile_digest_detects_posthoc_mutation", "status": "PASS"})
    except Exception as exc:
        checks.append({"name": "profile_digest_detects_posthoc_mutation", "status": "FAIL", "error": str(exc)})

    selection = SimpleNamespace(
        candidates=(SimpleNamespace(key="agent-a@v1"), SimpleNamespace(key="agent-b@v1")),
        chosen_index=0, protocol_event_id="selection-0", event_id="decision-0", task_index=0,
    )
    feedback_sidecar = SimpleNamespace(
        selection_event_id="selection-0", source_event_id="judgment-0",
        delivery_id="delivery-0", producer_id="agent-a", producer_version="v1",
        recipient_id="agent-r",
    )
    public_projection = SimpleNamespace(
        source="recipient_judgment", candidate_key="agent-a@v1",
        source_event_id="judgment-0", disposition="eligible", provenance="public",
        arrival_index=2,
        public_payload=lambda: {
            "feedback_id": "feedback-0", "source_event_id": "judgment-0",
            "source": "recipient_judgment", "candidate_key": "agent-a@v1",
            "evidence_version": "evidence-v1", "source_index": 2,
            "arrival_index": 2, "arrived_at": 2.0, "delay": 0.0,
            "action": "use", "disposition": "eligible", "provenance": "public",
            "label": 1.0,
        },
    )
    built = build_public_profile_fixture(
        selection=selection, feedback_sidecar=feedback_sidecar,
        public_projection=public_projection, profile_id="builder-profile-0",
        profile_revision=1, profile=valid.profile, parser_version="fixture-parser-v1",
        model_config_digest=digest("profile-model-config-v1"),
    )
    if built.source_input_digest != digest("public-event-bundle-0"):
        # The builder intentionally hashes its complete public source bundle;
        # it must not reuse an arbitrary caller-provided digest.
        checks.append({"name": "builder_binds_complete_public_source_digest", "status": "PASS"})
    else:
        checks.append({"name": "builder_binds_complete_public_source_digest", "status": "FAIL"})
    replayed = replay_public_profile_fixture(
        built, selection=selection, feedback_sidecar=feedback_sidecar,
        public_projection=public_projection,
    )
    if replayed.profile_digest == built.profile_digest:
        checks.append({"name": "builder_replay_preserves_profile_digest", "status": "PASS"})
    else:
        checks.append({"name": "builder_replay_preserves_profile_digest", "status": "FAIL"})
    offer = MetaTeamAssignmentOffer.build(
        offer_id="offer-0", task_id="PIPE3_stream_processing", decision_index=3,
        read_cut=2, candidate_keys=("agent-a@v1", "agent-b@v1"), profiles=(built,),
    )
    attestation = offer.attest_consumption((built.profile_id,))
    if attestation.policy_input_digest == attestation.expected_input_digest(
        offer.offer_digest, (built.profile_id,), 2
    ):
        checks.append({"name": "assignment_offer_consumption_digest", "status": "PASS"})
    else:
        checks.append({"name": "assignment_offer_consumption_digest", "status": "FAIL"})
    try:
        MetaTeamAssignmentOffer.build(
            offer_id="offer-too-early", task_id="PIPE3_stream_processing", decision_index=3,
            read_cut=1, candidate_keys=("agent-a@v1", "agent-b@v1"), profiles=(built,),
        )
    except ValueError as exc:
        checks.append({"name": "assignment_offer_rejects_pre_watermark_profile", "status": "PASS", "error": str(exc)})
    else:
        checks.append({"name": "assignment_offer_rejects_pre_watermark_profile", "status": "FAIL"})
    try:
        build_public_profile_fixture(
            selection=selection, feedback_sidecar=feedback_sidecar,
            public_projection=SimpleNamespace(**{**public_projection.__dict__, "source": "terminal_outcome"}),
            profile_id="builder-profile-terminal", profile_revision=1, profile=valid.profile,
            parser_version="fixture-parser-v1", model_config_digest=digest("profile-model-config-v1"),
        )
    except ValueError as exc:
        checks.append({"name": "builder_rejects_terminal_projection", "status": "PASS", "error": str(exc)})
    else:
        checks.append({"name": "builder_rejects_terminal_projection", "status": "FAIL"})

    result = {
        "qualification": config["qualification"],
        "status": "QUALIFIED_OFFLINE" if all(c["status"] == "PASS" for c in checks) else "FAILED_OFFLINE",
        "checks": checks,
        **config,
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.out_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    sys.exit(main())
