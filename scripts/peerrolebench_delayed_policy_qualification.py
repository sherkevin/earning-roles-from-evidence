"""Zero-call qualification for the delayed policy adapter candidate.

The qualification exercises the adapter's temporal and lineage boundaries
with a real ``FeatureContextualTrustPolicy``.  It deliberately makes no LLM,
API, or GPU calls and therefore cannot support an efficacy claim.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_baseline_policies import CandidateRef, FeatureContextualTrustPolicy, Feedback  # noqa: E402
from peerrolebench_delayed_policy_adapter import (  # noqa: E402
    DelayedPolicyAdapter, LaterChannelPayload, VERSION,
)
from peerrolebench_role_evidence_offer import PublicRoleEvidence, make_role_evidence_offer  # noqa: E402
from peerrolebench_two_stage_gate import LaterCredit, SourceGate  # noqa: E402


CONFIG_VERSION = "delayed-policy-adapter-qualification-v1"


def gate(allowed: bool = True) -> SourceGate:
    return SourceGate(
        gate_version="two-stage-role-evidence-v2", producer_paths_changed=("producer.py",),
        recipient_paths_changed=(), q_complete=True, y_complete=True, target_role="producer",
        artifact_binding_present=True, later_use_valid=False, attribution_eligible=allowed,
        evidence_publish_allowed=allowed, policy_update_allowed=False,
        status="ELIGIBLE" if allowed else "PENDING_ATTRIBUTION",
        reason="qualification fixture",
    )


def build_offer():
    evidence = PublicRoleEvidence(
        evidence_id="e-source", candidate_key="peer-b@v1", role="producer", source_task_index=0,
        delivery_id="d0", judgment_id="j0", action_id="a0", outcome_id="o0",
        artifact_sha256="a" * 64, judgment="accept", action="use", outcome_status="PASS",
        quality_score=1.0, available_index=2,
    )
    return make_role_evidence_offer(
        offer_id="offer-1", task_id="task", task_index=1, role="producer", context_key="ctx",
        candidate_keys=("peer-b@v1", "peer-c@v1"), evidence=(evidence,),
        evidence_version="role-evidence-v1", available_index=2,
    )


def build_adapter() -> DelayedPolicyAdapter:
    policy = FeatureContextualTrustPolicy(
        dimension=2, ridge=1.0, trust_scale=1.0,
        encoder_version="hash64-v1", feature_schema="matrix-features-v1",
    )
    return DelayedPolicyAdapter(policy, namespace="qualification-ns", state_cap_bytes=1 << 20)


def choose(adapter: DelayedPolicyAdapter):
    return adapter.policy.choose(
        event_id="target-selection", context_key="ctx", selector_id="selector",
        candidates=(CandidateRef("peer-b", "v1"), CandidateRef("peer-c", "v1")),
        base_scores=(100.0, 0.0), rng=np.random.default_rng(0), state_version="initial",
        encoder_version="hash64-v1", feature_schema="matrix-features-v1",
        captured_features={"peer-b@v1": (1.0, 0.0), "peer-c@v1": (0.0, 1.0)},
    )


def credit(outcome_id: str = "o-later") -> LaterCredit:
    return LaterCredit.build(
        assignment_id="assignment-1", source_evidence_id="e-source",
        later_outcome_id=outcome_id, later_quality=1.0 if outcome_id == "o-later" else 0.0,
    )


def channel(selection, *, source: str = "recipient_judgment", outcome_id: str = "o-later",
            assignment_candidate_key: str = "peer-b@v1", feedback_id: str = "feedback-1"):
    return LaterChannelPayload(
        credit=credit(outcome_id),
        feedback=Feedback(
            feedback_id=feedback_id, source_event_id=selection.event_id, source=source,
            label=1.0, arrived_at=3.0, delay=1.0, action="accept",
            disposition="eligible", provenance="public", arrival_index=3,
        ),
        target_outcome_id=outcome_id, assignment_candidate_key=assignment_candidate_key,
        namespace="qualification-ns",
    )


def run(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "config_version": CONFIG_VERSION, "adapter_version": VERSION,
        "policy": "contextual_trust_linear", "namespace": "qualification-ns",
        "state_cap_bytes": 1 << 20, "real_api_calls": 0, "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "cases": ["valid_publish_then_delayed_update", "duplicate_assignment_noop",
                   "alternate_outcome_rejected", "wrong_candidate_rejected",
                   "wrong_channel_rejected", "closed_source_gate_rejected",
                   "snapshot_restore_idempotency"],
    }
    (output_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    raw = output_dir / "raw.jsonl"
    rows = []

    def event(case: str, status: str, **payload):
        row = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "case": case,
               "status": status, "payload": payload}
        with raw.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False, default=str) + "\n")
        rows.append(row)

    def execute(case: str, fn):
        try:
            payload = fn()
            event(case, "PASS", **(payload or {}))
        except Exception as exc:
            event(case, "FAIL", error_type=type(exc).__name__, error=str(exc))

    def valid():
        adapter = build_adapter(); before = adapter._state_digest()
        receipt = adapter.publish(build_offer(), source_gate=gate()); selection = choose(adapter)
        result = adapter.apply_later_credit(channel(selection))
        assert receipt.state_digest_before == before == receipt.state_digest_after
        assert receipt.policy_updates_before == receipt.policy_updates_after == 0
        assert result == "UPDATED_ONCE" and adapter.policy.updates == 1
        return {"publish_unchanged": True, "update_result": result, "updates": adapter.policy.updates}

    def duplicate():
        adapter = build_adapter(); adapter.publish(build_offer(), source_gate=gate()); selection = choose(adapter)
        adapter.apply_later_credit(channel(selection)); result = adapter.apply_later_credit(channel(selection))
        assert result == "NOOP_DUPLICATE" and adapter.policy.updates == 1
        return {"result": result, "updates": adapter.policy.updates}

    def alternate():
        adapter = build_adapter(); adapter.publish(build_offer(), source_gate=gate()); selection = choose(adapter)
        adapter.apply_later_credit(channel(selection))
        try:
            adapter.apply_later_credit(channel(selection, outcome_id="o-other", feedback_id="feedback-2"))
        except ValueError:
            return {"alternate_rejected": True, "updates": adapter.policy.updates}
        raise AssertionError("alternate outcome was accepted")

    def wrong_candidate():
        adapter = build_adapter(); adapter.publish(build_offer(), source_gate=gate()); selection = choose(adapter)
        try:
            adapter.apply_later_credit(channel(selection, assignment_candidate_key="peer-c@v1"))
        except ValueError:
            return {"wrong_candidate_rejected": True, "updates": adapter.policy.updates}
        raise AssertionError("wrong candidate was accepted")

    def wrong_channel():
        adapter = build_adapter(); adapter.publish(build_offer(), source_gate=gate()); selection = choose(adapter)
        try:
            adapter.apply_later_credit(channel(selection, source="terminal_outcome"))
        except ValueError:
            return {"wrong_channel_rejected": True, "updates": adapter.policy.updates}
        raise AssertionError("wrong channel was accepted")

    def closed_gate():
        adapter = build_adapter()
        try:
            adapter.publish(build_offer(), source_gate=gate(False))
        except ValueError:
            return {"closed_gate_rejected": True, "updates": adapter.policy.updates}
        raise AssertionError("closed source gate was accepted")

    def restore():
        adapter = build_adapter(); adapter.publish(build_offer(), source_gate=gate()); selection = choose(adapter)
        adapter.apply_later_credit(channel(selection)); restored = DelayedPolicyAdapter.restore(adapter.snapshot())
        result = restored.apply_later_credit(channel(selection))
        assert result == "NOOP_DUPLICATE" and restored._state_digest() == adapter._state_digest()
        return {"result": result, "state_restored": True}

    for case, fn in (("valid_publish_then_delayed_update", valid), ("duplicate_assignment_noop", duplicate),
                      ("alternate_outcome_rejected", alternate), ("wrong_candidate_rejected", wrong_candidate),
                      ("wrong_channel_rejected", wrong_channel), ("closed_source_gate_rejected", closed_gate),
                      ("snapshot_restore_idempotency", restore)):
        execute(case, fn)
    passed = sum(row["status"] == "PASS" for row in rows)
    summary = {**config, "status": "QUALIFIED_OFFLINE" if passed == len(rows) else "FAILED_OFFLINE",
               "passed": passed, "total": len(rows), "raw_event_count": len(rows),
               "policy_updates_observed_in_valid_case": 1 if passed == len(rows) else None,
               "runner_started": False, "unknown_denominator": 0}
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), ensure_ascii=False, sort_keys=True))
