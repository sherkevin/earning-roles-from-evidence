import json
import subprocess
import sys

from scripts.peerrolebench_shared_source_v2 import (
    canonical_source_digest, project_source_to_arms, validate_arm_projections,
)
from scripts.peerrolebench_shared_source_v2_qualification import SEALED_DIGESTS, _source


def test_external_seal_and_projection_digest_are_verified():
    source = _source()
    rows = project_source_to_arms(source, SEALED_DIGESTS["ELIGIBLE"])
    assert source["source_receipt_digest"] == canonical_source_digest(source)
    assert validate_arm_projections(rows, SEALED_DIGESTS["ELIGIBLE"])["valid"] is True
    for row in rows:
        row["action"]["changed_paths"] = ["processor.py"]
    try:
        validate_arm_projections(rows, SEALED_DIGESTS["ELIGIBLE"])
    except ValueError as exc:
        assert any(token in str(exc) for token in ("mutation", "seal"))
    else:
        raise AssertionError("shared nested mutation was accepted")


def test_pending_and_unknown_have_distinct_typed_denominators():
    pending = project_source_to_arms(_source("PENDING_ATTRIBUTION"), SEALED_DIGESTS["PENDING_ATTRIBUTION"])
    unknown = project_source_to_arms(_source("UNKNOWN"), SEALED_DIGESTS["UNKNOWN"])
    assert validate_arm_projections(pending, SEALED_DIGESTS["PENDING_ATTRIBUTION"])["episode_status"] == "STOPPED_PRE_TARGET"
    assert validate_arm_projections(unknown, SEALED_DIGESTS["UNKNOWN"])["episode_status"] == "SOURCE_INCOMPLETE"


def test_qualification_is_zero_call_and_passes(tmp_path):
    out = tmp_path / "qualification"
    proc = subprocess.run(
        [sys.executable, "scripts/peerrolebench_shared_source_v2_qualification.py", "--output", str(out)],
        check=True, capture_output=True, text=True,
    )
    assert json.loads(proc.stdout)["passed"] is True
    summary = json.loads((out / "summary.json").read_text())
    assert summary["case_count"] == 10
    assert summary["llm_calls"] == 0
    assert summary["scientific_claim_allowed"] is False
