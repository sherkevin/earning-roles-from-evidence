"""Zero-API symbolic audit of the current strict source gate and J overlay.

These are enumerated predicate inputs, not measured task outcomes or simulated
LLM responses. Upstream ledger/scorer validation is assumed, not established.
The audit does not change a gate, a label mapping, or historical evidence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

from peerrolebench_role_evidence_offer import PublicRoleEvidence, make_role_evidence_offer
from peerrolebench_role_evidence_scorer import JUDGMENT_LABELS, score_role_evidence
from peerrolebench_two_stage_gate import VERSION as GATE_VERSION, evaluate_source_gate

VERSION = "strict-source-judgment-support-audit-v1"
ROOT = Path(__file__).resolve().parents[1]


def _save(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _event(handle, kind: str, payload) -> None:
    handle.write(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(),
                             "event": kind, "payload": payload}, ensure_ascii=False) + "\n")
    handle.flush()


def _overlay(decisions_by_peer):
    evidence = []
    for peer, decisions in sorted(decisions_by_peer.items()):
        for index, decision in enumerate(decisions):
            identity = f"{peer}-{index}"
            evidence.append(PublicRoleEvidence(
                evidence_id=identity, candidate_key=peer, role="producer",
                source_task_index=index, delivery_id=f"delivery-{identity}",
                judgment_id=f"judgment-{identity}", action_id=f"action-{identity}",
                outcome_id=f"outcome-{identity}", artifact_sha256="a" * 64,
                judgment=decision, action={"accept": "use", "accept_with_rework": "repair",
                                           "reject_redo": "redo"}[decision],
                outcome_status="PASS", quality_score=None, available_index=index + 1,
            ))
    offer = make_role_evidence_offer(
        offer_id="symbolic-support-audit", task_id="SYMBOLIC_NOT_A_TASK_RUN", task_index=10,
        role="producer", context_key="symbolic", candidate_keys=tuple(sorted(decisions_by_peer)),
        evidence=evidence, evidence_version=VERSION, available_index=9,
    )
    return score_role_evidence(offer, base_scores=(0.0, 0.0), read_cut=9).payload()


def run(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    paths = [Path(__file__), ROOT / "scripts/peerrolebench_two_stage_gate.py",
             ROOT / "scripts/peerrolebench_pipe3_responsibility_label.py",
             ROOT / "scripts/peerrolebench_role_evidence_scorer.py",
             ROOT / "scripts/peerrolebench_role_evidence_offer.py"]
    axes = {"qp": ["PASS", "FAIL", "UNKNOWN"], "judgment": list(JUDGMENT_LABELS),
            "action": ["use", "repair", "redo"],
            "changed": [[], ["producer.py"], ["processor.py"], ["producer.py", "processor.py"]],
            "registered": [False, True], "y": ["PASS", "FAIL", "UNKNOWN"],
            "bound": [False, True], "used_artifact": [False, True]}
    config = {
        "version": VERSION, "kind": "symbolic_contract_audit", "api_calls": 0, "gpu_jobs": 0,
        "started_at": datetime.now(timezone.utc).isoformat(), "python": sys.version,
        "platform": platform.platform(), "command": sys.argv,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "gate_version": GATE_VERSION, "axes": axes, "expected_rows": 2592,
        "scope": "Explicit registration field; upstream validation assumed; no legacy branch, no live inference.",
        "hypotheses": ["Every publishable strict source row has J=1 and Qp=FAIL.",
                       "All-accept overlay equals its count-only formula.",
                       "Ungated category changes can change the existing overlay."],
        "delayed_target_scope": "Not audited: target feedback can vary independently of source eligibility.",
    }
    _save(output / "config.json", config)
    materials = {"agent_payloads": {"producer": {"writable_paths": ["producer.py"]},
                                    "recipient": {"writable_paths": ["processor.py"]}}}
    rows = 0
    eligible = []
    with (output / "raw.jsonl").open("x") as raw:
        try:
            for values in itertools.product(*axes.values()):
                case = dict(zip(axes, values))
                q_complete = case["qp"] != "UNKNOWN"
                y_complete = case["y"] != "UNKNOWN"
                gate = evaluate_source_gate(
                    materials,
                    {"status": case["qp"], "label": {"PASS": 1, "FAIL": 0, "UNKNOWN": None}[case["qp"]],
                     "coverage_complete": q_complete, "decision_complete": q_complete},
                    {"decision": case["judgment"], "target_role": "producer",
                     "observed_artifact_sha256": "a" * 64 if case["bound"] else "",
                     "producer_defect_registered": case["registered"]},
                    {"consumer_action": case["action"], "changed_paths": case["changed"],
                     "used_artifact": case["used_artifact"]},
                    {"status": case["y"], "coverage_complete": y_complete, "decision_complete": y_complete},
                )
                row = {"case_id": rows, "input": case, "gate": gate.payload(),
                       "judgment_scalar": JUDGMENT_LABELS[case["judgment"]]}
                _event(raw, "symbolic_case", row)
                rows += 1
                if gate.evidence_publish_allowed:
                    eligible.append(row)
            counts = []
            for n_b, n_c in itertools.product(range(3), repeat=2):
                score = _overlay({"peer-b@v1": ["accept"] * n_b, "peer-c@v1": ["accept"] * n_c})
                expected_means = [(1 + n) / (2 + n) for n in (n_b, n_c)]
                expected_scores = [2 * (m - .5) for m in expected_means]
                row = {"counts": [n_b, n_c], "actual": score,
                       "count_only_means": expected_means, "count_only_scores": expected_scores,
                       "exact_match": score["posterior_means"] == expected_means and score["scores"] == expected_scores}
                counts.append(row)
                _event(raw, "count_only_comparison", row)
            sensitivity = {j: _overlay({"peer-b@v1": [j], "peer-c@v1": []}) for j in JUDGMENT_LABELS}
            _event(raw, "ungated_symbolic_category_sensitivity", sensitivity)
            result = {
                "version": VERSION, "kind": "symbolic_contract_audit", "api_calls": 0, "gpu_jobs": 0,
                "rows": rows, "eligible_rows": len(eligible),
                "eligible_judgment_support": sorted({r["judgment_scalar"] for r in eligible}),
                "eligible_qp_support": sorted({r["input"]["qp"] for r in eligible}),
                "eligible_y_support": sorted({r["input"]["y"] for r in eligible}),
                "count_only_comparisons": len(counts), "count_only_exact": all(r["exact_match"] for r in counts),
                "ungated_judgment_scores_peer_b": {j: s["scores"][0] for j, s in sensitivity.items()},
                "eligible_case_ids": [r["case_id"] for r in eligible],
                "claim_scope": "Current strict source-publication scalar and stateless J overlay only.",
                "not_established": ["No claim about textual judgment information or target delayed-label support.",
                                    "No causal effect, empirical accuracy, sample-size estimate, or method innovation."],
                "ended_at": datetime.now(timezone.utc).isoformat(),
            }
            assert rows == config["expected_rows"]
            assert result["eligible_rows"] == 2
            assert result["eligible_judgment_support"] == [1.0]
            assert result["eligible_qp_support"] == ["FAIL"]
            assert result["count_only_exact"]
            assert len(set(result["ungated_judgment_scores_peer_b"].values())) == 3
            result["audit_status"] = "HYPOTHESES_VERIFIED_FOR_DECLARED_SCOPE"
            _save(output / "summary.json", result)
            _event(raw, "audit_completed", result)
            return result
        except Exception:
            error = {"audit_status": "ERROR", "rows_completed": rows, "traceback": traceback.format_exc()}
            _save(output / "failure.json", error)
            _event(raw, "audit_failed", error)
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output), ensure_ascii=False, indent=2))
