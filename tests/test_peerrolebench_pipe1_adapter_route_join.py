from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_pipe1_adapter_route_join import validate_adapter_route_join  # noqa: E402
from peerrolebench_pipe1_offline_adapter import validate_source_target_fixture  # noqa: E402
from peerrolebench_pipe1_route_receipt import canonical_digest  # noqa: E402
from peerrolebench_pipe3_live_contract_qualification import _registry  # noqa: E402
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from test_peerrolebench_pipe1_route_receipt import _receipt  # noqa: E402


def _events():
    task = "PIPE1_etl_fix"
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    ledger.record_selection(PeerSelection("s0", task, 0, "selector", "producer", ("peer-b", "peer-c"), "peer-b", .5))
    ledger.record_task_start(task, 0)
    ledger.record_delivery(Delivery("d0", task, "peer-b", "recipient", "a" * 64, "src", 0, "s0"))
    ledger.record_producer_score(ProducerScore("q0", "d0", "a" * 64, "qp", "PASS", 1, 1.0, "d" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "recipient", "accept", "a" * 64))
    ledger.record_action(ConsumerAction("a0", "d0", "recipient", True, "a" * 64, "e" * 64, 0.0, "use"))
    ledger.record_outcome(TerminalOutcome("y0", "d0", True, "qr", 1.0, "f" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "y0", "v1", 1.0))
    ledger.record_assignment(LaterAssignment("as1", task, 1, "peer-b", "producer", ("e0",), .5))
    ledger.record_selection(PeerSelection("s1", task, 1, "selector", "producer", ("peer-b", "peer-c"), "peer-b", .5))
    ledger.record_task_start(task, 1)
    ledger.record_delivery(Delivery("d1", task, "peer-b", "recipient", "b" * 64, "src1", 1, "s1"))
    ledger.record_producer_score(ProducerScore("q1", "d1", "b" * 64, "qp", "PASS", 1, 1.0, "d" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", "b" * 64))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, "b" * 64, "e" * 64, 0.0, "use"))
    ledger.record_outcome(TerminalOutcome("y1", "d1", True, "qr", 1.0, "f" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "y1", "v1", 2.0))
    return ledger.events


def _adapter():
    return validate_source_target_fixture(
        events=_events(), task_id="PIPE1_etl_fix", source_task_index=0,
        target_task_index=1, evidence_id="e0", assignment_id="as1",
        target_selection_id="s1", registry=_registry(),
        menu_keys=("peer-b@v1", "peer-c@v1"), chosen_key="peer-b@v1",
        probabilities=(.5, .5), chosen_index=0, propensity=.5,
    )


def _route():
    receipt = _receipt()
    candidates = [{"candidate_id": "peer-b", "version": "v1"}, {"candidate_id": "peer-c", "version": "v1"}]
    receipt["candidate_registry"]["candidates"] = candidates
    receipt["candidate_registry"]["registry_digest"] = canonical_digest({
        "registry_id": receipt["candidate_registry"]["registry_id"],
        "registry_version": receipt["candidate_registry"]["registry_version"],
        "candidates": candidates,
    })
    receipt["allocation"].update({
        "permutation": ["peer-b@v1", "peer-c@v1"],
        "probabilities": {"peer-b@v1": .5, "peer-c@v1": .5},
        "propensities": {"peer-b@v1": .5, "peer-c@v1": .5},
        "chosen": "peer-b@v1",
    })
    receipt["visibility"].update({
        "eligible_candidate_ids": ["peer-b@v1", "peer-c@v1"],
        "chosen_candidate_id": "peer-b@v1",
        "observed_candidate_ids": ["peer-b@v1"],
    })
    return receipt


def test_matching_adapter_and_route_are_ready_for_preflight_only():
    result = validate_adapter_route_join(adapter_result=_adapter(), route_receipt=_route())
    assert result["status"] == "READY_FOR_PREFLIGHT"
    assert result["valid"] is True
    assert result["policy_update_allowed"] is False


def test_route_chosen_peer_mismatch_fails_closed():
    route = _route()
    route["allocation"]["chosen"] = "peer-c@v1"
    result = validate_adapter_route_join(adapter_result=_adapter(), route_receipt=route)
    assert result["status"] == "UNKNOWN"
    assert result["update_boundary"]["assignment_created"] is False


def test_route_task_mismatch_fails_closed():
    route = _route()
    route["target"]["task_id"] = "other-task"
    result = validate_adapter_route_join(adapter_result=_adapter(), route_receipt=route)
    assert result["status"] == "UNKNOWN"


def test_invalid_route_does_not_get_promoted():
    route = _route()
    route["visibility"]["selected_only"] = False
    result = validate_adapter_route_join(adapter_result=_adapter(), route_receipt=route)
    assert result["status"] == "UNKNOWN"
    assert result["route_valid"] is False


def test_adapter_update_flag_cannot_be_enabled_by_join():
    adapter = _adapter()
    adapter["policy_update_allowed"] = True
    result = validate_adapter_route_join(adapter_result=adapter, route_receipt=_route())
    assert result["status"] == "UNKNOWN"
    assert result["policy_update_allowed"] is False
