from __future__ import annotations

import csv
import io
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_handoff_descriptor_v2 import (  # noqa: E402
    DELIVERY_PATH, DELIVERY_SCHEMA, Pipe2HandoffDescriptor, canonical_digest,
    digest_changed_paths, make_descriptor, make_descriptor_from_snapshots,
)
from peerrolebench_pipe2_derived_material_adapter import build_derived_materials  # noqa: E402
from peerrolebench_pipe2_material_adapter_v2 import validate_extracted_rows  # noqa: E402


def fields():
    return dict(
        schema="pipe2-typed-handoff-v2",
        task_id="PIPE2_data_pipeline", source_task_index=0, candidate_key="producer-a@v1",
        candidate_source_digest="a" * 64, delivery_id="d0", delivery_path=DELIVERY_PATH,
        delivery_schema=DELIVERY_SCHEMA, delivery_artifact_sha256="b" * 64,
        producer_contract_digest="c" * 64,
        judgment="accept_with_rework", action="repair", used_artifact=True,
        outcome_status="PASS", delivery_event_index=2, judgment_event_index=3,
        action_event_index=4, outcome_event_index=5,
        judgment_id="j0", action_id="a0", outcome_id="y0",
        judgment_record_hash="f" * 64, action_record_hash="e" * 64,
        outcome_record_hash="d" * 64, target_task_index=1,
        source_read_cut=6, observation_available_index=6,
        recipient_before_manifest_digest="1" * 64,
        recipient_after_manifest_digest="2" * 64,
        recipient_changed_paths_digest=digest_changed_paths(("pipeline/transform.py",)),
    )


def records(**overrides):
    values = fields()
    values.update(overrides)
    return {
        "delivery": {"event_type": "producer_delivery", "event_index": values["delivery_event_index"],
                     "record_hash": "a" * 64,
                     "payload": {"delivery_id": values["delivery_id"]}},
        "judgment": {"event_type": "recipient_judgment", "event_index": values["judgment_event_index"],
                      "record_hash": values["judgment_record_hash"],
                      "payload": {"judgment_id": values["judgment_id"], "delivery_id": values["delivery_id"],
                                  "decision": values["judgment"]}},
        "action": {"event_type": "consumer_action", "event_index": values["action_event_index"],
                    "record_hash": values["action_record_hash"],
                    "payload": {"action_id": values["action_id"], "delivery_id": values["delivery_id"],
                                "action": values["action"]}},
        "outcome": {"event_type": "terminal_outcome", "event_index": values["outcome_event_index"],
                     "record_hash": values["outcome_record_hash"],
                     "payload": {"outcome_id": values["outcome_id"], "delivery_id": values["delivery_id"],
                                 "success": values["outcome_status"] == "PASS"}},
    }


def test_v2_separates_source_and_opaque_delivery_and_hides_internal_fields():
    descriptor = make_descriptor(**fields())
    assert isinstance(descriptor, Pipe2HandoffDescriptor)
    public = descriptor.public_delivery_payload()
    assert "recipient_before_manifest_digest" not in public
    assert "judgment" not in public
    assert public["delivery_id"] == "d0"
    assert public["producer_credit_allowed"] is False


@pytest.mark.parametrize("field,value", [
    ("delivery_path", "pipeline/extract.py"),
    ("delivery_schema", "source-code-v1"),
    ("source_read_cut", 1),
    ("target_task_index", 0),
    ("action_event_index", 2),
])
def test_v2_rejects_handoff_or_temporal_mutations(field, value):
    payload = fields()
    payload[field] = value
    payload["descriptor_digest"] = canonical_digest(payload)
    with pytest.raises(ValueError):
        Pipe2HandoffDescriptor(**payload)


def test_v2_keeps_a_noisy_judgment_action_mismatch_as_observation_data():
    payload = fields()
    payload.update(judgment="accept", action="repair")
    descriptor = make_descriptor_from_snapshots(
        recipient_before={"pipeline/transform.py": "before\n"},
        recipient_after={"pipeline/transform.py": "after\n"},
        recipient_allowed_paths=("pipeline/transform.py",),
        event_records=records(judgment="accept", action="repair"),
        **{key: value for key, value in payload.items()
           if key not in {"recipient_before_manifest_digest", "recipient_after_manifest_digest",
                          "recipient_changed_paths_digest"}},
    )
    assert descriptor.judgment == "accept"
    assert descriptor.action == "repair"


def test_v2_rejects_unbound_or_arbitrary_event_ids():
    payload = fields()
    bad = records()
    bad["action"]["payload"]["delivery_id"] = "other-delivery"
    with pytest.raises(ValueError, match="bound to delivery"):
        make_descriptor_from_snapshots(
            recipient_before={"pipeline/transform.py": "before\n"},
            recipient_after={"pipeline/transform.py": "after\n"},
            recipient_allowed_paths=("pipeline/transform.py",), event_records=bad,
            **{key: value for key, value in payload.items()
               if key not in {"recipient_before_manifest_digest", "recipient_after_manifest_digest",
                              "recipient_changed_paths_digest"}},
        )


def test_v2_rejects_delivery_artifact_in_source_manifest():
    with pytest.raises(ValueError, match="opaque delivery"):
        make_descriptor_from_snapshots(
            recipient_before={DELIVERY_PATH: "opaque"}, recipient_after={DELIVERY_PATH: "opaque"},
            recipient_allowed_paths=(DELIVERY_PATH,), event_records=records(),
            **{key: value for key, value in fields().items()
               if key not in {"recipient_before_manifest_digest", "recipient_after_manifest_digest",
                              "recipient_changed_paths_digest"}},
        )


def test_v2_boundary_matches_actual_pipe2_material_visibility_and_artifact():
    materials = build_derived_materials(0)
    producer = materials["agent_payloads"]["producer"]
    recipient = materials["agent_payloads"]["recipient"]
    assert "pipeline/extract.py" in producer["source_files"]
    assert "pipeline/extract.py" not in recipient["source_files"]
    assert tuple(recipient["required_delivery_paths"]) == (DELIVERY_PATH,)
    source = producer["source_files"]["data/source.csv"]
    reader = csv.DictReader(io.StringIO(source, newline=""))
    artifact = validate_extracted_rows(list(reader), columns=tuple(reader.fieldnames or ()))
    assert artifact["schema"] == DELIVERY_SCHEMA
    assert artifact["artifact_sha256"]
    assert artifact["artifact_sha256"] != materials["manifest"]["payload_sha256"]
