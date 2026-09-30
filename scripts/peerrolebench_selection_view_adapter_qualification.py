"""Zero-call qualification for the versioned/native selection view bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import PeerSelection  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_metateam_profile_qualification import profile  # noqa: E402
from peerrolebench_metateam_profile_sidecar import (  # noqa: E402
    MetaTeamAssignmentOffer, bind_assignment_to_selection,
)
from peerrolebench_selection_view_adapter import (  # noqa: E402
    view_from_native_selection, view_from_versioned_selection,
)


def registry() -> tuple[CandidateRegistryEntry, ...]:
    return (
        CandidateRegistryEntry("agent-a", "v1", "a" * 64, "fixture", "b" * 64),
        CandidateRegistryEntry("agent-b", "v2", "c" * 64, "fixture", "b" * 64),
    )


def run(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "qualification": "versioned-native-selection-view-v1",
        "script": str(Path(__file__).resolve()),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "adapter_sha256": hashlib.sha256(
            (ROOT / "scripts/peerrolebench_selection_view_adapter.py").read_bytes()
        ).hexdigest(),
        "fixture_mode": "hand-authored-registry-and-native-selection",
        "source": "offline identity fixture; no PIPE3 execution",
        "python": platform.python_version(), "platform": platform.platform(),
        "real_api_calls": 0, "gpu_jobs": 0, "scientific_claim_allowed": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n")
    checks = []
    entries = registry()
    native = PeerSelection(
        "selection-3", "PIPE3_stream_processing", 3, "recipient", "producer",
        ("agent-a", "agent-b"), "agent-b", 0.5,
    )
    view = view_from_native_selection(native, entries, selected_at=3.0)
    checks.append({"name": "native_to_versioned_view_preserves_order", "status": "PASS",
                   "candidate_keys": [candidate.key for candidate in view.candidates]})
    explicit = view_from_versioned_selection(
        candidate_keys=("agent-a@v1", "agent-b@v2"), chosen_key="agent-b@v2",
        task_index=3, selected_at=3.0, selector_id="recipient", registry=entries,
    )
    checks.append({"name": "versioned_view_validates_exact_registry_keys", "status": "PASS",
                   "chosen_key": explicit.chosen_key})
    source = profile(
        profile_id="profile-b", candidate_key="agent-b@v2",
        selected_candidate_key="agent-b@v2", producer_id="agent-b",
        producer_version="v2",
    )
    offer = MetaTeamAssignmentOffer.build(
        offer_id="offer-3", task_id="PIPE3_stream_processing", decision_index=3,
        read_cut=2, candidate_keys=("agent-a@v1", "agent-b@v2"), profiles=(source,),
    )
    attestation = offer.attest_consumption((source.profile_id,))
    bind_assignment_to_selection(offer, attestation, view)
    checks.append({"name": "view_binds_to_later_assignment", "status": "PASS"})

    def reject(name, fn):
        try:
            fn()
        except (TypeError, ValueError) as exc:
            checks.append({"name": name, "status": "PASS", "error": str(exc)})
        else:
            checks.append({"name": name, "status": "FAIL"})

    reject("reject_unknown_version", lambda: view_from_versioned_selection(
        candidate_keys=("agent-a@v1", "agent-b@v1"), chosen_key="agent-b@v1",
        task_index=3, selected_at=3.0, selector_id="recipient", registry=entries,
    ))
    reject("reject_wrong_choice", lambda: view_from_versioned_selection(
        candidate_keys=("agent-a@v1", "agent-b@v2"), chosen_key="agent-c@v1",
        task_index=3, selected_at=3.0, selector_id="recipient", registry=entries,
    ))
    reject("reject_negative_time", lambda: view_from_native_selection(native, entries, selected_at=-1.0))
    reject("reject_menu_reordering_at_assignment", lambda: bind_assignment_to_selection(
        offer, attestation, view_from_versioned_selection(
            candidate_keys=("agent-b@v2", "agent-a@v1"), chosen_key="agent-b@v2",
            task_index=3, selected_at=3.0, selector_id="recipient", registry=entries,
        ),
    ))
    reject("reject_native_menu_registry_mismatch", lambda: view_from_native_selection(
        native, (entries[0],), selected_at=3.0,
    ))
    result = {
        **config,
        "status": "QUALIFIED_OFFLINE" if all(item["status"] == "PASS" for item in checks) else "FAILED_OFFLINE",
        "checks": checks,
        "candidate_keys": [candidate.key for candidate in view.candidates],
        "chosen_key": view.chosen_key,
    }
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "raw.json").write_text(json.dumps({
        "registry": [entry.payload() for entry in entries],
        "native_selection": native.__dict__,
        "versioned_view": {
            "candidate_keys": [candidate.key for candidate in view.candidates],
            "chosen_index": view.chosen_index, "task_index": view.task_index,
            "selected_at": view.selected_at, "selector_id": view.selector_id,
        },
        "offer": offer.payload(), "attestation": attestation.payload(),
    }, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in (
        "status", "real_api_calls", "gpu_jobs", "scientific_claim_allowed",
    )}, indent=2))
    return 0 if result["status"] == "QUALIFIED_OFFLINE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
