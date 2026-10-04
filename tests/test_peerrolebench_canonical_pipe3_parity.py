import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_canonical_pipe3_parity_qualification import run  # noqa: E402


def test_canonical_pipe3_parity_qualification_passes_without_calls(tmp_path):
    result = run(tmp_path / "parity")
    assert result["status"] == "QUALIFIED_OFFLINE_PUBLIC_INPUT_PARITY"
    assert result["passed"] is True
    assert result["real_api_calls"] == 0
    assert result["gpu_jobs"] == 0
    assert result["scientific_claim_allowed"] is False
    assert result["cells"]["valid"]["checks"]["independent_state_namespaces"] is True
    assert result["cells"]["late"]["false_accept"] is False
    assert result["cells"]["mutation"]["false_accept"] is False

    summary = json.loads((tmp_path / "parity" / "summary.json").read_text())
    assert summary["fixture"]["role_offer_bundle_digest"]
    assert summary["fixture"]["role_public_projection_digest"]
    assert summary["fixture"]["history_state_digest"]
    assert summary["fixture"]["phi_digest"]
