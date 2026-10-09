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
    assert data["status"] == "GUIDE_EXPECTATION_NOT_OBSERVED"
    assert data["watermark_required"] is True
    assert data["scientific_result"] is False
    assert data["new_api_calls"] == data["gpu_jobs"] == data["benchmark_runs"] == 0
    correspondence = data["correspondence"]
    assert correspondence == {
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
    assert by_name["RARE"]["brier"] < by_name["Contextual-trust-linear"]["brier"]
    assert by_name["RARE"]["calibration"] < by_name["Contextual-trust-linear"]["calibration"]
    assert by_name["RARE"]["utility"] > by_name["Contextual-trust-linear"]["utility"]
    assert by_name["RARE"]["complete_cost"] > by_name["Contextual-trust-linear"]["complete_cost"]

    service = data["table_3_service_safety"]
    assert len(service) == 7
    assert [row["method"] for row in service] == correspondence["row_order"]["table_3_service_safety"]
    svc = {row["method"]: row for row in service}
    assert svc["RARE"]["update_p95_ms"] > svc["Contextual-trust-linear"]["update_p95_ms"]
    assert svc["RARE"]["backlog_p95"] > svc["Contextual-trust-linear"]["backlog_p95"]
    assert svc["RARE"]["state_kib"] > svc["Contextual-trust-linear"]["state_kib"]
    assert svc["RARE"]["false_attribution"] < svc["Contextual-trust-linear"]["false_attribution"]
    assert svc["RARE"]["coverage"] < svc["Contextual-trust-linear"]["coverage"]
    assert svc["RARE"]["recovery_steps"] < svc["Contextual-trust-linear"]["recovery_steps"]

    ablations = data["table_4_ablations"]
    assert len(ablations) == 7
    assert [row["intervention"] for row in ablations] == correspondence["row_order"]["table_4_ablations"]
    for row in ablations:
        expected_q = row["utility"] + lam * row["complete_cost"]
        assert close(row["implied_quality"], expected_q), (row["intervention"], expected_q, row["implied_quality"])
    ab = {row["intervention"]: row for row in ablations}
    rare = ab["Evidence + delayed update (RARE)"]
    assert rare["utility"] > ab["No evidence / no update"]["utility"]
    assert rare["false_attribution"] < ab["RARE without ownership gate"]["false_attribution"]
    assert rare["false_attribution"] < ab["RARE without selected-only rule"]["false_attribution"]

    if args.source_pdf:
        digest = hashlib.sha256(args.source_pdf.read_bytes()).hexdigest()
        assert digest == data["source_matrix_sha256"], (digest, data["source_matrix_sha256"])
    print(json.dumps({"valid": True, "status": data["status"], "tables": {"hero": 7, "service": 7, "ablations": 7}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
