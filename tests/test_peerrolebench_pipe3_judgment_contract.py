from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from peerrolebench_pipe3_judgment_contract import validate_structured_judgment


DIGEST = "a" * 64
PATHS = ["producer.py", "processor.py", "models.py", "sink.py"]


def valid():
    return {
        "decision": "accept_with_rework", "confidence": 0.9,
        "rationale": "r", "repair_plan": "p", "observed_artifact_sha256": DIGEST,
        "target_role": "recipient", "target_paths": ["processor.py"],
        "defect_type": "recipient_integration", "evidence_refs": ["artifact_digest"],
    }


def test_structured_judgment_is_normalized():
    result = validate_structured_judgment(valid(), DIGEST, PATHS)
    assert result["target_role"] == "recipient"
    assert result["confidence"] == 0.9


@pytest.mark.parametrize("field,value", [
    ("target_role", "agent-x"),
    ("defect_type", "guess"),
    ("target_paths", ["hidden_test.py"]),
    ("evidence_refs", []),
])
def test_invalid_attribution_fields_are_rejected(field, value):
    payload = valid()
    payload[field] = value
    with pytest.raises(ValueError):
        validate_structured_judgment(payload, DIGEST, PATHS)


def test_digest_binding_is_required():
    payload = valid()
    payload["observed_artifact_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="digest"):
        validate_structured_judgment(payload, DIGEST, PATHS)
