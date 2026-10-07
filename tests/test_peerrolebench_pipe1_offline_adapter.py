from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peerrolebench_pipe1_offline_adapter import validate_source_target_fixture  # noqa: E402
from peerrolebench_pipe3_live_contract_qualification import _registry  # noqa: E402
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)


def _pipe1_events():
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


def _kwargs(events):
    return dict(
        events=events,
        task_id="PIPE1_etl_fix",
        source_task_index=0,
        target_task_index=1,
        evidence_id="e0",
        assignment_id="as1",
        target_selection_id="s1",
        registry=_registry(),
        menu_keys=("peer-b@v1", "peer-c@v1"),
        chosen_key="peer-b@v1",
        probabilities=(0.5, 0.5),
        chosen_index=0,
        propensity=0.5,
    )


def test_valid_fixture_is_ready_but_never_updates_policy():
    result = validate_source_target_fixture(**_kwargs(_pipe1_events()))
    assert result["status"] == "READY_FOR_ROUTE"
    assert result["route_ready"] is True
    assert result["ledger"]["valid"] is True
    assert result["schedule"]["valid"] is True
    assert result["selection"]["valid"] is True
    assert result["policy_update_allowed"] is False
    assert result["update_boundary"]["label"] is None


def test_wrong_task_id_fails_closed_without_assignment_or_update():
    events = _pipe1_events()
    events[0]["payload"]["task_id"] = "other-task"
    result = validate_source_target_fixture(**_kwargs(events))
    assert result["status"] == "UNKNOWN"
    assert result["route_ready"] is False
    assert result["update_boundary"]["assignment_created"] is False
    assert result["update_boundary"]["target_selection_created"] is False
    assert result["policy_update_allowed"] is False


def test_artifact_binding_mutation_fails_closed():
    events = _pipe1_events()
    judgment = next(row for row in events if row["event_type"] == "recipient_judgment")
    judgment["payload"]["observed_artifact_sha256"] = "f" * 64
    result = validate_source_target_fixture(**_kwargs(events))
    assert result["status"] == "UNKNOWN"
    assert result["route_ready"] is False
    assert result["ledger"]["valid"] is False
    assert result["update_boundary"]["label"] is None


def test_ownership_unknown_is_reported_without_role_credit():
    result = validate_source_target_fixture(
        **_kwargs(_pipe1_events()),
        ownership_cases=[dict(
            changed_paths=("producer.py", "processor.py"),
            producer_paths=("producer.py",),
            recipient_paths=("processor.py",),
            producer_defect_registered=True,
            producer_score_status="FAIL",
            producer_label=0,
        )],
    )
    assert result["status"] == "READY_FOR_ROUTE"
    assert result["ownership_status"] == "UNKNOWN"
    assert result["ownership"][0]["policy_update_allowed"] is False


def test_external_chosen_peer_mismatch_fails_closed():
    kwargs = _kwargs(_pipe1_events())
    kwargs.update(chosen_key="peer-c@v1", chosen_index=1)
    result = validate_source_target_fixture(**kwargs)
    assert result["status"] == "UNKNOWN"
    assert result["route_ready"] is False
    assert any("chosen peer" in error for error in result["selection_binding"]["errors"])
    assert result["update_boundary"]["policy_update_allowed"] is False


def test_external_menu_mismatch_fails_closed():
    kwargs = _kwargs(_pipe1_events())
    kwargs.update(menu_keys=("peer-c@v1", "peer-b@v1"), chosen_key="peer-c@v1", chosen_index=0)
    result = validate_source_target_fixture(**kwargs)
    assert result["status"] == "UNKNOWN"
    assert result["route_ready"] is False
    assert any("candidate menu" in error for error in result["selection_binding"]["errors"])


def test_wrong_evidence_or_source_index_fails_closed():
    kwargs = _kwargs(_pipe1_events())
    kwargs.update(evidence_id="e1")
    result = validate_source_target_fixture(**kwargs)
    assert result["status"] == "UNKNOWN"
    assert result["route_ready"] is False

    kwargs = _kwargs(_pipe1_events())
    kwargs.update(source_task_index=-1)
    result = validate_source_target_fixture(**kwargs)
    assert result["status"] == "UNKNOWN"
    assert result["route_ready"] is False


def test_malformed_row_fails_closed_without_exception():
    events = _pipe1_events() + [None]
    result = validate_source_target_fixture(**_kwargs(events))
    assert result["status"] == "UNKNOWN"
    assert result["route_ready"] is False
