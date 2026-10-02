from pathlib import Path
import hashlib
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "references/aamas"))

from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction, Delivery, LaterAssignment, PeerRoleLedger, PeerSelection,
    ProducerScore, RecipientJudgment, RoleEvidenceUpdate, TerminalOutcome,
)
from peerrolebench_baseline_policies import TerminalOnlyPolicy  # noqa: E402
from peerrolebench_candidate_registry import CandidateRegistryEntry  # noqa: E402
from peerrolebench_pipe3_live_contract import (  # noqa: E402
    classify_ownership, unknown_no_update, validate_ledger_key_binding,
    validate_selection_receipt, validate_source_target_schedule,
)
from peerrolebench_pipe3_runner_v1 import Pipe3SelectionBoundary, make_offer  # noqa: E402
from peerrolebench_selection_preview import FixedChoiceRNG, preview_selection  # noqa: E402


def _registry():
    return [CandidateRegistryEntry("peer-b", "v1", "b" * 64, "fixture", "c" * 64),
            CandidateRegistryEntry("peer-c", "v1", "c" * 64, "fixture", "c" * 64)]


def _ledger():
    ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
    source = PeerSelection("s0", "PIPE3_stream_processing", 0, "selector", "producer", ("peer-b", "peer-c"), "peer-b", .5)
    ledger.record_selection(source); ledger.record_task_start("PIPE3_stream_processing", 0)
    artifact = "a" * 64
    ledger.record_delivery(Delivery("d0", "PIPE3_stream_processing", "peer-b", "recipient", artifact, "src", 0, "s0"))
    ledger.record_producer_score(ProducerScore("q0", "d0", artifact, "qp", "PASS", 1, 1.0, "d" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j0", "d0", "recipient", "accept", artifact))
    ledger.record_action(ConsumerAction("a0", "d0", "recipient", True, artifact, "e" * 64, 0.0, "use"))
    ledger.record_outcome(TerminalOutcome("y0", "d0", True, "qr", 1.0, "f" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e0", "j0", "a0", "y0", "v1", 1.0))
    ledger.record_assignment(LaterAssignment("as1", "PIPE3_stream_processing", 1, "peer-b", "producer", ("e0",), .5))
    target = PeerSelection("s1", "PIPE3_stream_processing", 1, "selector", "producer", ("peer-b", "peer-c"), "peer-b", .5)
    ledger.record_selection(target); ledger.record_task_start("PIPE3_stream_processing", 1)
    ledger.record_delivery(Delivery("d1", "PIPE3_stream_processing", "peer-b", "recipient", "b" * 64, "src1", 1, "s1"))
    ledger.record_producer_score(ProducerScore("q1", "d1", "b" * 64, "qp", "PASS", 1, 1.0, "d" * 64, True, True))
    ledger.record_judgment(RecipientJudgment("j1", "d1", "recipient", "accept", "b" * 64))
    ledger.record_action(ConsumerAction("a1", "d1", "recipient", True, "b" * 64, "e" * 64, 0.0, "use"))
    ledger.record_outcome(TerminalOutcome("y1", "d1", True, "qr", 1.0, "f" * 64))
    ledger.record_evidence_update(RoleEvidenceUpdate("e1", "j1", "a1", "y1", "v1", 2.0))
    return ledger


def test_source_target_and_ledger_binding_are_sealed():
    ledger = _ledger()
    result = validate_ledger_key_binding(ledger.events)
    assert result["valid"] is True
    schedule = validate_source_target_schedule(events=ledger.events, source_task_index=0,
        target_task_index=1, evidence_id="e0", assignment_id="as1", target_selection_id="s1")
    assert schedule["valid"] is True


def test_selection_receipt_binds_menu_registry_and_propensity():
    result = validate_selection_receipt(registry=_registry(), menu_keys=("peer-b@v1", "peer-c@v1"),
        chosen_key="peer-b@v1", probabilities=(.5, .5), chosen_index=0, propensity=.5)
    assert result["valid"] is True
    bad = validate_selection_receipt(registry=_registry(), menu_keys=("peer-b@v1", "peer-c@v1"),
        chosen_key="peer-b@v1", probabilities=(.5, .5), chosen_index=0, propensity=.4)
    assert bad["valid"] is False
    malformed = validate_selection_receipt(registry=_registry(), menu_keys=("peer-z@v9",),
        chosen_key="peer-z@v9", probabilities=(1.0,), chosen_index=3, propensity=1.0)
    assert malformed["valid"] is False


def test_ownership_table_is_conservative():
    common = dict(producer_paths=("producer.py",), recipient_paths=("processor.py",),
                  producer_score_status="FAIL", producer_label=0, producer_defect_registered=True)
    assert classify_ownership(changed_paths=("producer.py",), **common)["status"] == "ELIGIBLE"
    assert classify_ownership(changed_paths=("processor.py",), **common)["status"] == "PENDING_ATTRIBUTION"
    assert classify_ownership(changed_paths=("producer.py", "processor.py"), **common)["status"] == "UNKNOWN"
    assert classify_ownership(changed_paths=("sink.py",), **common)["status"] == "UNKNOWN"


def test_unknown_stops_without_state_or_update():
    result = unknown_no_update(state_before="s0", state_after="s0", reason="scorer timeout")
    assert result["valid"] is True
    assert result["label"] is None and result["policy_update_allowed"] is False
    assert result["assignment_created"] is False and result["target_selection_created"] is False


def test_preview_fixed_choice_preserves_propensity_before_assignment():
    boundary = Pipe3SelectionBoundary(TerminalOnlyPolicy(), _registry())
    offer = make_offer(offer_id="o", task_id="PIPE3_stream_processing", task_index=0,
        role="producer", context_key="ctx", candidate_keys=("peer-b@v1", "peer-c@v1"),
        public_rows=(), evidence_version="v1", available_index=0)
    preview = preview_selection(boundary, offer=offer, native_selection_id="s", selector_id="selector",
        role="producer", base_scores=(0.0, 0.0), rng=np.random.default_rng(0), state_version="s0",
        encoder_version="e0", feature_schema="f0", policy_version="p0", base_score_version="b0",
        rng_algorithm="numpy-pcg64", rng_draw=0, selected_at=0.0, read_cut=0, decision_index=0)
    assert preview.propensity == preview.probabilities[preview.chosen_index]
    assert FixedChoiceRNG(preview).choice(2, p=preview.probabilities) == preview.chosen_index
