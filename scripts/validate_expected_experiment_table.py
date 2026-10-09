#!/usr/bin/env python3
"""Validate logical consistency of the numerical expected-result guide.

This checks arithmetic and the intended direction pattern only. It cannot
establish that any target is scientifically true; that requires the frozen
live experiment and independent scoring described in the activation manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path", type=Path)
    ap.add_argument("--source-pdf", type=Path)
    args = ap.parse_args()
    data = json.loads(args.json_path.read_text())
    version = data["version"]
    assert version.startswith("expected_v")
    assert data["status"] == "GUIDE_EXPECTATION_NOT_OBSERVED"
    assert data["watermark_required"] is True
    assert data["scientific_result"] is False
    assert data["new_api_calls"] == data["gpu_jobs"] == data["benchmark_runs"] == 0
    correspondence = data["correspondence"]
    legacy_correspondence = {
        "overview": {"data_rows": 4, "columns": 5},
        "table_2_artifactrole": {"data_rows": 7, "columns": 6},
        "table_3_service_safety": {"data_rows": 7, "columns": 8},
        "table_4_ablations": {"data_rows": 7, "columns": 6},
        "row_order": {
            "table_2_artifactrole": ["Uniform", "No update", "Raw acceptance", "Terminal only", "Contextual-trust-linear", "Pooled controller", "RARE"],
            "table_3_service_safety": ["No update", "History only", "Contextual-trust-linear", "RARE", "Recipient-only mutation", "Mixed ownership mutation", "Delayed / out-of-order feedback"],
            "table_4_ablations": ["No evidence / no update", "Public evidence only", "Delayed update only", "Evidence + delayed update (RARE)", "RARE without ownership gate", "RARE without selected-only rule", "RARE without correction/replay"],
        },
    }
    if version.startswith("expected_v3"):
        assert correspondence["overview"]["columns_exact"] == [
            "RQ", "Track / unit", "Policy contrast", "Primary result table", "Primary estimand"
        ]
        assert correspondence["table_2_artifactrole"]["columns_exact"] == [
            "Policy", "Brier ↓", "Calibration ↓", "Quality–cost utility ↑",
            "Assignment change ↑", "Complete cost ↓", "Streams"
        ]
        assert correspondence["table_3_service_safety"]["columns_exact"] == [
            "Policy / intervention", "Track", "Update p95 ↓", "Backlog p95 ↓",
            "State bytes ↓", "False attribution ↓", "unknown precision ↑",
            "Forgetting / recovery ↓"
        ]
        assert correspondence["table_4_ablations"]["columns_exact"] == [
            "Intervention", "Removed or changed component", "Future utility ↑",
            "Assignment change ↑", "False attribution ↓", "Complete cost ↓"
        ]
        assert correspondence["row_order"]["table_2_artifactrole"][-1] == "rare"
        assert correspondence["row_order"]["table_3_service_safety"][3] == "rare"
        assert correspondence["row_order"]["table_4_ablations"][3].endswith("(rare)")
    else:
        assert correspondence == legacy_correspondence

    assumptions = data["design_assumptions"]
    assert assumptions["structural_roots"] == 3
    assert assumptions["independent_streams_per_arm"] == 3
    assert assumptions["streams_per_arm"] == 9
    lam = float(assumptions["utility_lambda"])

    hero = data["table_2_artifactrole"]
    assert len(hero) == 7
    assert [row["method"] for row in hero] == correspondence["row_order"]["table_2_artifactrole"]
    assert all(row["streams"] == 9 for row in hero)
    for row in hero:
        expected_q = row["utility"] + lam * row["complete_cost"]
        assert close(row["implied_quality"], expected_q), (row["method"], expected_q, row["implied_quality"])
    by_name = {row["method"]: row for row in hero}
    candidate_name = "rare" if version.startswith("expected_v3") else "RARE"
    assert by_name[candidate_name]["brier"] < by_name["Contextual-trust-linear"]["brier"]
    assert by_name[candidate_name]["calibration"] < by_name["Contextual-trust-linear"]["calibration"]
    assert by_name[candidate_name]["utility"] > by_name["Contextual-trust-linear"]["utility"]
    assert by_name[candidate_name]["complete_cost"] > by_name["Contextual-trust-linear"]["complete_cost"]

    service = data["table_3_service_safety"]
    assert len(service) == 7
    assert [row["method"] for row in service] == correspondence["row_order"]["table_3_service_safety"]
    assert all(row["streams"] == 9 for row in service)
    svc = {row["method"]: row for row in service}
    assert svc[candidate_name]["update_p95_ms"] > svc["Contextual-trust-linear"]["update_p95_ms"]
    assert svc[candidate_name]["backlog_p95"] > svc["Contextual-trust-linear"]["backlog_p95"]
    assert svc[candidate_name]["state_kib"] > svc["Contextual-trust-linear"]["state_kib"]
    # PeerSelect has no owner-truth contract; H4a is deliberately N/A there.
    if version.startswith(("expected_v2", "expected_v3")):
        assert all(row["false_attribution"] is None for row in service[:4])
        assert all(row["owner_truth_recall"] is None for row in service[:4])
        assert all("unknown_abstention_rate" in row for row in service)
        for row in service:
            assert close(row["unknown_abstention_rate"], 1.0 - row["coverage"]), row["method"]
        if version.startswith("expected_v3"):
            assert all("unknown_precision" in row and "unknown_precision_sd" in row for row in service)
            assert all(0.0 <= row["unknown_precision"] <= 1.0 for row in service)
    else:
        assert svc[candidate_name]["false_attribution"] < svc["Contextual-trust-linear"]["false_attribution"]
    assert svc[candidate_name]["coverage"] < svc["Contextual-trust-linear"]["coverage"]
    assert svc[candidate_name]["recovery_steps"] < svc["Contextual-trust-linear"]["recovery_steps"]

    ablations = data["table_4_ablations"]
    assert len(ablations) == 7
    assert [row["intervention"] for row in ablations] == correspondence["row_order"]["table_4_ablations"]
    assert all(row["streams"] == 9 for row in ablations)
    for row in ablations:
        expected_q = row["utility"] + lam * row["complete_cost"]
        assert close(row["implied_quality"], expected_q), (row["intervention"], expected_q, row["implied_quality"])
    ab = {row["intervention"]: row for row in ablations}
    rare_key = "Evidence + delayed update (rare)" if version.startswith("expected_v3") else "Evidence + delayed update (RARE)"
    ownership_key = "rare without ownership gate" if version.startswith("expected_v3") else "RARE without ownership gate"
    selected_only_key = "rare without selected-only rule" if version.startswith("expected_v3") else "RARE without selected-only rule"
    rare = ab[rare_key]
    assert rare["utility"] > ab["No evidence / no update"]["utility"]
    assert rare["false_attribution"] < ab[ownership_key]["false_attribution"]
    assert rare["false_attribution"] < ab[selected_only_key]["false_attribution"]

    if args.source_pdf:
        digest = hashlib.sha256(args.source_pdf.read_bytes()).hexdigest()
        assert digest == data["source_matrix_sha256"], (digest, data["source_matrix_sha256"])
    print(json.dumps({"valid": True, "status": data["status"], "tables": {"hero": 7, "service": 7, "ablations": 7}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
