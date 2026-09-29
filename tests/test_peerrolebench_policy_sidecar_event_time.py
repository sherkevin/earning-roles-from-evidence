from dataclasses import replace
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_policy_sidecar import EVENT_TIME_SIDECAR_VERSION  # noqa: E402
from peerrolebench_policy_sidecar_replay import replay_policy_sidecars, SidecarRow  # noqa: E402
from peerrolebench_policy_sidecar_stream_qualification import canonical_ledger, sidecars, manifest_for  # noqa: E402
from peerrolebench_baseline_policies import TerminalOnlyPolicy  # noqa: E402


def _v4_rows():
    rows = sidecars(canonical_ledger())
    updated = {}
    for name, row in rows.items():
        if name == "selection":
            updated[name] = row
            continue
        event = replace(
            row.sidecar,
            sidecar_version=EVENT_TIME_SIDECAR_VERSION,
            arrival_index=1 if name == "judgment" else 2,
            artifact_sha256="b" * 64,
            delivery_record_hash="c" * 64,
            action_id="action-0",
            action_record_hash="d" * 64,
        )
        updated[name] = SidecarRow(event, row.ledger_record, event.sidecar_digest)
    return canonical_ledger(), updated


def test_event_time_replay_requires_frozen_schedule_and_accepts_matching_schedule():
    ledger, rows = _v4_rows()
    ordered = [rows["selection"], rows["outcome"], rows["judgment"]]
    result = replay_policy_sidecars(
        ledger, ordered, TerminalOnlyPolicy, manifest_for(ordered),
    )
    assert result["status"] == "INVALID"
    assert "frozen expected arrival schedule" in result["error"]

    result = replay_policy_sidecars(
        ledger, ordered, TerminalOnlyPolicy, manifest_for(ordered),
        expected_arrival_indices={
            rows["judgment"].sidecar.feedback_id: 1,
            rows["outcome"].sidecar.feedback_id: 2,
        },
    )
    assert result["status"] == "PASS"
    assert result["update_count"] == 1
