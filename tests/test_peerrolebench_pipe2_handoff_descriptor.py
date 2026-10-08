from __future__ import annotations

from dataclasses import replace
import csv
import io
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe2_handoff_descriptor import (  # noqa: E402
    DELIVERY_PATH, DELIVERY_SCHEMA, Pipe2HandoffDescriptor, canonical_digest,
    digest_changed_paths, make_descriptor,
)
from peerrolebench_pipe2_derived_material_adapter import build_derived_materials  # noqa: E402
from peerrolebench_pipe2_material_adapter_v2 import validate_extracted_rows  # noqa: E402


def fields():
    return dict(
        task_id="PIPE2_data_pipeline", source_task_index=0, candidate_key="producer-a@v1",
        candidate_source_digest="a" * 64, delivery_path=DELIVERY_PATH,
        delivery_schema=DELIVERY_SCHEMA, delivery_artifact_sha256="b" * 64,
        producer_contract_digest="c" * 64, recipient_before_manifest_digest="d" * 64,
        recipient_after_manifest_digest="e" * 64,
        recipient_changed_paths_digest=digest_changed_paths(("pipeline/transform.py",)),
        judgment_id="j0", action_id="a0", outcome_id="y0", target_task_index=1,
        source_read_cut=7, observation_available_index=7,
    )


def test_descriptor_separates_source_and_opaque_delivery_and_exposes_safe_projection():
    descriptor = make_descriptor(**fields())
    assert isinstance(descriptor, Pipe2HandoffDescriptor)
    assert descriptor.candidate_source_digest != descriptor.delivery_artifact_sha256
    public = descriptor.public_delivery_payload()
    assert "recipient_before_manifest_digest" not in public
    assert "recipient_changed_paths_digest" not in public
    assert public["delivery_path"] == DELIVERY_PATH
    assert public["producer_credit_allowed"] is False


@pytest.mark.parametrize("field,value", [
    ("delivery_path", "pipeline/extract.py"),
    ("delivery_schema", "source-code-v1"),
    ("delivery_artifact_sha256", "f" * 64),
    ("source_read_cut", 8),
    ("target_task_index", 0),
])
def test_descriptor_rejects_handoff_or_temporal_mutations(field, value):
    descriptor = make_descriptor(**fields())
    payload = descriptor.payload(include_digest=False)
    payload[field] = value
    # A new artifact digest is a valid *different* delivery identity; the
    # descriptor can only reject this mutation when the sealed receipt digest
    # is kept unchanged.  The runner must pin the expected artifact digest.
    descriptor_digest = (descriptor.descriptor_digest if field == "delivery_artifact_sha256"
                         else canonical_digest(payload))
    with pytest.raises(ValueError):
        Pipe2HandoffDescriptor(**payload, descriptor_digest=descriptor_digest)


def test_changed_path_digest_is_canonical_and_traversal_safe():
    assert digest_changed_paths(("pipeline/load.py", "pipeline/transform.py")) == digest_changed_paths(
        ("pipeline/transform.py", "pipeline/load.py", "pipeline/load.py"))
    with pytest.raises(ValueError):
        digest_changed_paths(("../hidden",))


def test_descriptor_cannot_authorize_policy_or_credit():
    descriptor = make_descriptor(**fields())
    payload = descriptor.payload(include_digest=False)
    payload["policy_update_allowed"] = True
    with pytest.raises(ValueError):
        Pipe2HandoffDescriptor(**payload, descriptor_digest=canonical_digest(payload))


def test_descriptor_boundary_matches_actual_pipe2_material_visibility():
    materials = build_derived_materials(0)
    producer = materials["agent_payloads"]["producer"]
    recipient = materials["agent_payloads"]["recipient"]
    assert "pipeline/extract.py" in producer["source_files"]
    assert "pipeline/extract.py" not in recipient["source_files"]
    assert tuple(recipient["required_delivery_paths"]) == ("artifact/extracted_rows.json",)
    source = producer["source_files"]["data/source.csv"]
    reader = csv.DictReader(io.StringIO(source, newline=""))
    rows = list(reader)
    artifact = validate_extracted_rows(rows, columns=tuple(reader.fieldnames or ()))
    assert artifact["schema"] == "pipe2-extracted-rows-v1"
    assert artifact["artifact_sha256"]
    assert artifact["artifact_sha256"] != materials["manifest"]["payload_sha256"]
