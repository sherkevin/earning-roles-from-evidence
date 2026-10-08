#!/usr/bin/env python3
"""Fail-closed validator for the v4 benchmark/baseline closure receipt.

This validates an evidence receipt; it does not run a benchmark, infer a result,
or grant scientific truth.  A valid CLOSED_FULL receipt still needs independent
scientific review.  No external packages are required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

VERSION = "v4_20261008"
SCOPE = "benchmark_baseline_acceptance"
GATES = {f"B{i}" for i in range(1, 8)}
GATE_STATUSES = {"PASS", "FAIL", "UNSTUDIED", "BLOCKED", "N_A_PREDECLARED"}
RECEIPT_STATUSES = {"OPEN", "CLOSED_FULL", "FAIL"}
OUTCOMES = {"positive", "neutral", "adverse", "insufficient"}
READINESS = {"exploratory", "findings_ready", "proceedings_ready"}
SENTINELS = {
    "judgment_permutation",
    "trace_only",
    "candidate_id_menu_order_permutation",
    "version_swap_stale_evidence",
    "recipient_only_mixed_unknown",
    "unselected_label_censoring",
    "replay_idempotence_correction_lineage",
    "gold_future_label_injection",
}
REQUIRED_ARMS = {
    "uniform",
    "no_update",
    "raw_acceptance",
    "terminal_only",
    "contextual_trust_linear",
    "pooled_controller",
    "RARE",
    "closest_published",
}
HEX64 = set("0123456789abcdef")


class ReceiptError(Exception):
    pass


def _err(errors: list[str], where: str, message: str) -> None:
    errors.append(f"{where}: {message}")


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _hash(value: Any, where: str, errors: list[str]) -> bool:
    ok = isinstance(value, str) and len(value) == 64 and set(value) <= HEX64
    if not ok:
        _err(errors, where, "expected 64 lowercase hexadecimal characters")
    return ok


def _bool(value: Any, where: str, errors: list[str]) -> bool:
    if not isinstance(value, bool):
        _err(errors, where, "expected boolean")
        return False
    return True


def _nonnegative_int(value: Any, where: str, errors: list[str]) -> bool:
    # bool is an int subclass, but is never a valid denominator.
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _err(errors, where, "expected non-negative integer")
        return False
    return True


def _artifact_ref(value: Any, where: str, root: Path, errors: list[str]) -> bool:
    """Require a path plus digest and verify the bytes, even for OPEN receipts."""
    if not isinstance(value, dict):
        _err(errors, where, "expected {path, sha256}")
        return False
    path = value.get("path")
    digest = value.get("sha256")
    good = _hash(digest, f"{where}.sha256", errors)
    if not _nonempty(path):
        _err(errors, f"{where}.path", "must be non-empty")
        return False
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    if not candidate.is_file():
        _err(errors, f"{where}.path", f"file does not exist: {path}")
        return False
    if good:
        actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual != digest:
            _err(errors, where, f"sha256 mismatch for {path}")
            return False
    return good


def _require_keys(obj: dict[str, Any], keys: set[str], where: str, errors: list[str]) -> None:
    for key in sorted(keys - obj.keys()):
        _err(errors, where, f"missing required field {key!r}")


def _validate_denominator(value: Any, where: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        _err(errors, where, "must be a non-empty object")
        return False
    keys = {"attempted", "started", "completed", "known", "unknown", "failed", "unstarted"}
    _require_keys(value, keys, where, errors)
    valid = True
    for key in keys:
        if key not in value or not _nonnegative_int(value[key], f"{where}.{key}", errors):
            valid = False
    if valid:
        if value["attempted"] != value["started"] + value["unstarted"]:
            _err(errors, where, "attempted != started + unstarted")
            valid = False
        if value["started"] != value["completed"] + value["failed"]:
            _err(errors, where, "started != completed + failed")
            valid = False
        if value["completed"] != value["known"] + value["unknown"]:
            _err(errors, where, "completed != known + unknown")
            valid = False
    return valid


def _validate_gate(gate: Any, index: int, root: Path, errors: list[str]) -> str | None:
    where = f"gates[{index}]"
    if not isinstance(gate, dict):
        _err(errors, where, "must be an object")
        return None
    required = {
        "gate_id", "claim_scope", "required_evidence", "pre_run_hash", "artifact_path",
        "replay_command", "denominator", "verifier", "status", "decision_reason",
    }
    _require_keys(gate, required, where, errors)
    gate_id = gate.get("gate_id")
    if gate_id not in GATES:
        _err(errors, f"{where}.gate_id", "must be one of B1..B7")
    for key in ("claim_scope", "required_evidence", "replay_command", "decision_reason"):
        if not _nonempty(gate.get(key)):
            _err(errors, f"{where}.{key}", "must be non-empty")
    _hash(gate.get("pre_run_hash"), f"{where}.pre_run_hash", errors)
    _artifact_ref(gate.get("artifact_path"), f"{where}.artifact_path", root, errors)
    _validate_denominator(gate.get("denominator"), f"{where}.denominator", errors)
    verifier = gate.get("verifier")
    if not isinstance(verifier, dict):
        _err(errors, f"{where}.verifier", "must identify an independent verifier")
    else:
        _require_keys(verifier, {"identity", "independent", "report"}, f"{where}.verifier", errors)
        if not _nonempty(verifier.get("identity")):
            _err(errors, f"{where}.verifier.identity", "must be non-empty")
        if verifier.get("independent") is not True:
            _err(errors, f"{where}.verifier.independent", "must be true")
        _artifact_ref(verifier.get("report"), f"{where}.verifier.report", root, errors)
    status = gate.get("status")
    if not isinstance(status, str) or status not in GATE_STATUSES:
        _err(errors, f"{where}.status", f"must be one of {sorted(GATE_STATUSES)}")
    if status == "N_A_PREDECLARED":
        if not _nonempty(gate.get("na_rationale")) or not _nonempty(gate.get("na_cell_scope")):
            _err(errors, where, "N_A_PREDECLARED requires na_rationale and na_cell_scope")
        if gate.get("na_pre_registered") is not True:
            _err(errors, where, "N_A_PREDECLARED requires na_pre_registered=true")
    return gate_id if isinstance(gate_id, str) else None


def _validate_roots(value: Any, readiness: str, root: Path, errors: list[str], precision_justification: Any) -> None:
    if not isinstance(value, list) or not value:
        _err(errors, "roots", "must be a non-empty list")
        return
    ids: set[str] = set()
    signatures: set[str] = set()
    for i, item in enumerate(value):
        where = f"roots[{i}]"
        if not isinstance(item, dict):
            _err(errors, where, "must be an object")
            continue
        _require_keys(item, {"root_id", "structural_signature", "split", "manifest"}, where, errors)
        rid, sig = item.get("root_id"), item.get("structural_signature")
        if not _nonempty(rid) or rid in ids:
            _err(errors, where, "root_id must be non-empty and unique")
        if not _nonempty(sig) or sig in signatures:
            _err(errors, where, "structural_signature must be non-empty and unique")
        if isinstance(rid, str):
            ids.add(rid)
        if isinstance(sig, str):
            signatures.add(sig)
        _artifact_ref(item.get("manifest"), f"{where}.manifest", root, errors)
    if len(ids) < 2:
        _err(errors, "roots", "at least two structurally distinct roots are required")
    if readiness == "proceedings_ready" and len(ids) < 3:
        justification = precision_justification
        if not isinstance(justification, dict) or justification.get("pre_registered") is not True:
            _err(errors, "roots", "proceedings_ready requires three roots or a pre-registered two-root precision justification")


def _validate_streams(value: Any, arms: set[str], roots: set[str], errors: list[str]) -> set[tuple[str, str, str]]:
    observed: set[tuple[str, str, str, str]] = set()
    if not isinstance(value, list) or not value:
        _err(errors, "streams", "must be a non-empty list")
        return observed
    seen: set[tuple[str, str, str]] = set()
    for i, item in enumerate(value):
        where = f"streams[{i}]"
        if not isinstance(item, dict):
            _err(errors, where, "must be an object")
            continue
        _require_keys(item, {"root_id", "stream_id", "arm_id", "history_namespace", "independent", "status"}, where, errors)
        raw_key = (item.get("root_id"), item.get("stream_id"), item.get("arm_id"))
        key = raw_key if all(isinstance(x, str) for x in raw_key) else None
        if key is not None:
            if key in seen:
                _err(errors, where, "duplicate root/stream/arm")
            seen.add(key)
            observed.add(key)
        if not isinstance(item.get("root_id"), str) or item.get("root_id") not in roots:
            _err(errors, where, "unknown root_id")
        if not isinstance(item.get("arm_id"), str) or item.get("arm_id") not in arms:
            _err(errors, where, "unknown arm_id")
        if not _nonempty(item.get("history_namespace")):
            _err(errors, where, "history_namespace must be non-empty")
        if item.get("independent") is not True:
            _err(errors, where, "independent must be true")
        if item.get("status") != "COMPLETE":
            _err(errors, where, "required stream must be COMPLETE")
    return observed


def _validate_arms(value: Any, errors: list[str]) -> set[str]:
    if not isinstance(value, list) or not value:
        _err(errors, "arms", "must be a non-empty list")
        return set()
    ids: set[str] = set()
    for i, item in enumerate(value):
        where = f"arms[{i}]"
        if not isinstance(item, dict):
            _err(errors, where, "must be an object")
            continue
        _require_keys(item, {"arm_id", "version", "qualified", "same_information", "history_namespace"}, where, errors)
        aid = item.get("arm_id")
        if not _nonempty(aid) or aid in ids:
            _err(errors, where, "arm_id must be non-empty and unique")
        if isinstance(aid, str):
            ids.add(aid)
        for key in ("qualified", "same_information"):
            if item.get(key) is not True:
                _err(errors, f"{where}.{key}", "must be true for CLOSED_FULL")
        if not _nonempty(item.get("version")) or not _nonempty(item.get("history_namespace")):
            _err(errors, where, "version and history_namespace must be non-empty")
    missing = REQUIRED_ARMS - ids
    if missing:
        _err(errors, "arms", f"missing required arms: {sorted(missing)}")
    return ids


def _validate_cells(value: Any, stream_keys: set[tuple[str, str, str]], root: Path, errors: list[str]) -> tuple[set[tuple[str, str, str]], set[str]]:
    observed: set[tuple[str, str, str]] = set()
    hypotheses: set[str] = set()
    if not isinstance(value, list) or not value:
        _err(errors, "target_cells", "must be a non-empty list")
        return observed, hypotheses
    seen: set[str] = set()
    for i, item in enumerate(value):
        where = f"target_cells[{i}]"
        if not isinstance(item, dict):
            _err(errors, where, "must be an object")
            continue
        keys = {"cell_id", "root_id", "stream_id", "arm_id", "future_assignment_id", "y_status", "hypothesis", "pre_run_sealed", "execution_status", "observed_regime", "falsifier_status", "estimate", "interval", "independent_verdict"}
        _require_keys(item, keys, where, errors)
        cid = item.get("cell_id")
        if not _nonempty(cid) or cid in seen:
            _err(errors, where, "cell_id must be non-empty and unique")
        if isinstance(cid, str):
            seen.add(cid)
        triple = (item.get("root_id"), item.get("stream_id"), item.get("arm_id"))
        if not all(isinstance(x, str) for x in triple):
            _err(errors, f"{where}.root/stream/arm", "must be strings")
        else:
            if triple not in stream_keys:
                _err(errors, where, "cell root/stream/arm is absent from the pre-run stream manifest")
            hypothesis = item.get("hypothesis")
            cell_key = (*triple, hypothesis) if isinstance(hypothesis, str) else None
            if cell_key is not None and cell_key in observed:
                _err(errors, where, "duplicate root/stream/arm cell")
            if cell_key is not None:
                observed.add(cell_key)
        if not _nonempty(item.get("future_assignment_id")):
            _err(errors, f"{where}.future_assignment_id", "must be non-empty")
        hypothesis = item.get("hypothesis")
        if not isinstance(hypothesis, str) or hypothesis not in {"H1", "H2", "H3", "safety"}:
            _err(errors, f"{where}.hypothesis", "must identify H1/H2/H3/safety")
        else:
            hypotheses.add(hypothesis)
        if hypothesis == "H2":
            if item.get("y_status") != "KNOWN":
                _err(errors, f"{where}.y_status", "ArtifactRole H2 requires a known future Y; absent Y is UNSTUDIED")
            _artifact_ref(item.get("y_artifact"), f"{where}.y_artifact", root, errors)
        elif item.get("y_status") != "NOT_APPLICABLE":
            _err(errors, f"{where}.y_status", "non-H2 cells must explicitly declare NOT_APPLICABLE")
        if item.get("pre_run_sealed") is not True:
            _err(errors, f"{where}.pre_run_sealed", "must be true")
        if item.get("execution_status") != "COMPLETE":
            _err(errors, f"{where}.execution_status", "required cell is not complete")
        if item.get("observed_regime") not in {"favorable", "neutral", "adverse"}:
            _err(errors, f"{where}.observed_regime", "must be favorable, neutral, or adverse")
        if item.get("falsifier_status") != "PASS":
            _err(errors, f"{where}.falsifier_status", "must be PASS")
        if item.get("independent_verdict") != "PASS":
            _err(errors, f"{where}.independent_verdict", "must be PASS")
        if not isinstance(item.get("interval"), list) or len(item["interval"]) != 2:
            _err(errors, f"{where}.interval", "must be a two-sided reported interval")
        if not isinstance(item.get("estimate"), (int, float)) or isinstance(item.get("estimate"), bool) or not math.isfinite(item.get("estimate", math.nan)):
            _err(errors, f"{where}.estimate", "must be a numeric observed estimate")
        elif isinstance(item.get("interval"), list) and len(item["interval"]) == 2:
            lo, hi = item["interval"]
            if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in (lo, hi)):
                _err(errors, f"{where}.interval", "bounds must be finite numbers")
            elif lo > hi or not (lo <= item["estimate"] <= hi):
                _err(errors, f"{where}.interval", "must be ordered and contain estimate")
    if not {"H1", "H2", "H3", "safety"} <= hypotheses:
        _err(errors, "target_cells", "must include H1, H2, H3 and safety cells")
    observed_triples = {key[:3] for key in observed}
    if stream_keys - observed_triples:
        _err(errors, "target_cells", "every pre-run root/stream/arm tuple requires an observed cell")
    return observed_triples, hypotheses


def validate_receipt(receipt: Any, root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(receipt, dict):
        return ["receipt: top-level JSON must be an object"]
    required = {
        "closure_scope", "guide_version", "goal_sha256", "goal_ref", "evaluation_sha256", "evaluation_ref",
        "pre_run_manifest_sha256", "pre_run_manifest_ref", "gates", "track_manifest", "roots", "streams",
        "arms", "minimum_streams_per_arm", "holdout", "target_cells", "artifactrole", "hard_fail_sentinels", "real_api_calls", "stop_receipt",
        "denominator_reconciliation", "cost_reconciliation", "independent_review", "clean_replay",
        "same_information_parity", "blind_scorer", "independent_environment", "policy_state_masked",
        "method_outcome", "readiness_level", "status",
    }
    _require_keys(receipt, required, "receipt", errors)
    if receipt.get("closure_scope") != SCOPE:
        _err(errors, "closure_scope", f"must equal {SCOPE}")
    if receipt.get("guide_version") != VERSION:
        _err(errors, "guide_version", f"must equal {VERSION}")
    for key in ("goal_sha256", "evaluation_sha256", "pre_run_manifest_sha256"):
        _hash(receipt.get(key), key, errors)
    for key in ("goal_ref", "evaluation_ref", "pre_run_manifest_ref"):
        ref = receipt.get(key)
        if _artifact_ref(ref, key, root, errors) and receipt.get(key.removesuffix("_ref") + "_sha256") != ref.get("sha256"):
            _err(errors, key, "sha256 does not match top-level digest")
    status = receipt.get("status")
    if not isinstance(status, str) or status not in RECEIPT_STATUSES:
        _err(errors, "status", f"must be one of {sorted(RECEIPT_STATUSES)}; CLOSED_BOUNDED is forbidden")
    outcome = receipt.get("method_outcome")
    if not isinstance(outcome, str) or outcome not in OUTCOMES:
        _err(errors, "method_outcome", f"must be one of {sorted(OUTCOMES)}")
    readiness = receipt.get("readiness_level")
    if not isinstance(readiness, str) or readiness not in READINESS:
        _err(errors, "readiness_level", f"must be one of {sorted(READINESS)}")

    gates = receipt.get("gates")
    if not isinstance(gates, list):
        _err(errors, "gates", "must be a list of exactly seven objects")
        gate_ids: list[str | None] = []
    else:
        if len(gates) != 7:
            _err(errors, "gates", "must contain exactly seven entries")
        gate_ids = [_validate_gate(g, i, root, errors) for i, g in enumerate(gates)]
        if set(gate_ids) != GATES or len(set(gate_ids)) != len(gate_ids):
            _err(errors, "gates", "must contain each of B1..B7 exactly once")

    tm = receipt.get("track_manifest")
    if not isinstance(tm, dict):
        _err(errors, "track_manifest", "must be an object")
    else:
        _require_keys(tm, {"primary_track", "secondary_track", "manifest"}, "track_manifest", errors)
        if tm.get("primary_track") != "ArtifactRole" or tm.get("secondary_track") != "PeerSelect":
            _err(errors, "track_manifest", "must declare ArtifactRole primary and PeerSelect secondary")
        _artifact_ref(tm.get("manifest"), "track_manifest.manifest", root, errors)

    roots = receipt.get("roots")
    _validate_roots(roots, readiness if isinstance(readiness, str) else "", root, errors, receipt.get("precision_justification"))
    root_ids = {x.get("root_id") for x in roots if isinstance(x, dict) and isinstance(x.get("root_id"), str)} if isinstance(roots, list) else set()
    arms = _validate_arms(receipt.get("arms"), errors)
    min_streams = receipt.get("minimum_streams_per_arm")
    if not _nonnegative_int(min_streams, "minimum_streams_per_arm", errors) or min_streams < 2:
        _err(errors, "minimum_streams_per_arm", "must be at least two for a closure receipt")
    stream_keys = _validate_streams(receipt.get("streams"), arms, root_ids, errors)
    if isinstance(min_streams, int) and not isinstance(min_streams, bool):
        for arm in arms:
            count = sum(1 for _, _, a in stream_keys if a == arm)
            if count < min_streams:
                _err(errors, "streams", f"arm {arm} has {count} streams; requires {min_streams}")
    holdout = receipt.get("holdout")
    if not isinstance(holdout, dict):
        _err(errors, "holdout", "must be an object")
    else:
        _require_keys(holdout, {"kind", "sealed", "artifact"}, "holdout", errors)
        if holdout.get("kind") not in {"structural_root", "temporal", "support_query"}:
            _err(errors, "holdout.kind", "must identify a structural, temporal or support/query holdout")
        if holdout.get("sealed") is not True:
            _err(errors, "holdout.sealed", "must be true")
        _artifact_ref(holdout.get("artifact"), "holdout.artifact", root, errors)
    _validate_cells(receipt.get("target_cells"), stream_keys, root, errors)

    ar = receipt.get("artifactrole")
    if not isinstance(ar, dict):
        _err(errors, "artifactrole", "must be an object")
    else:
        _require_keys(ar, {"future_assignment_y_complete", "evidence", "cell_count"}, "artifactrole", errors)
        if ar.get("future_assignment_y_complete") is not True:
            _err(errors, "artifactrole.future_assignment_y_complete", "must be true for CLOSED_FULL")
        _artifact_ref(ar.get("evidence"), "artifactrole.evidence", root, errors)
        if not _nonnegative_int(ar.get("cell_count"), "artifactrole.cell_count", errors) or ar.get("cell_count", 0) < 1:
            _err(errors, "artifactrole.cell_count", "must be positive")

    sentinels = receipt.get("hard_fail_sentinels")
    if not isinstance(sentinels, dict) or set(sentinels) != SENTINELS:
        _err(errors, "hard_fail_sentinels", "must report every registered sentinel exactly once")
    elif any(not isinstance(v, dict) or v.get("status") != "PASS" or v.get("executed") is not True or not _nonempty(v.get("reason")) or not isinstance(v.get("evidence"), dict) for v in sentinels.values()):
        _err(errors, "hard_fail_sentinels", "every sentinel must be executed, PASS, justified and carry evidence")
    elif any(not _artifact_ref(v.get("evidence"), f"hard_fail_sentinels.{k}.evidence", root, errors) for k, v in sentinels.items()):
        pass

    api = receipt.get("real_api_calls")
    if not isinstance(api, dict):
        _err(errors, "real_api_calls", "must be an object")
    else:
        _require_keys(api, {"attempted", "charged", "successful", "raw_receipt", "post_stop_calls"}, "real_api_calls", errors)
        for k in ("attempted", "charged", "successful", "post_stop_calls"):
            _nonnegative_int(api.get(k), f"real_api_calls.{k}", errors)
        _artifact_ref(api.get("raw_receipt"), "real_api_calls.raw_receipt", root, errors)
        if api.get("post_stop_calls") != 0:
            _err(errors, "real_api_calls.post_stop_calls", "must be zero")
        if isinstance(api.get("attempted"), int) and api.get("attempted", 0) <= 0:
            _err(errors, "real_api_calls.attempted", "must be positive for scientific closure")
        if all(isinstance(api.get(k), int) and not isinstance(api.get(k), bool) for k in ("attempted", "charged", "successful")):
            if api["successful"] > api["attempted"] or api["charged"] > api["attempted"]:
                _err(errors, "real_api_calls", "successful/charged calls cannot exceed attempted calls")

    stop = receipt.get("stop_receipt")
    if not isinstance(stop, dict):
        _err(errors, "stop_receipt", "must be an object")
    else:
        _require_keys(stop, {"stop_rule", "pre_run_sealed", "triggered", "stop_time", "attempted_calls", "charged_calls", "post_stop_calls", "rerun_policy"}, "stop_receipt", errors)
        for k in ("stop_rule", "stop_time", "rerun_policy"):
            if not _nonempty(stop.get(k)):
                _err(errors, f"stop_receipt.{k}", "must be non-empty")
        for k in ("attempted_calls", "charged_calls", "post_stop_calls"):
            _nonnegative_int(stop.get(k), f"stop_receipt.{k}", errors)
        if stop.get("pre_run_sealed") is not True or stop.get("triggered") is not True:
            _err(errors, "stop_receipt", "pre_run_sealed and triggered must be true")
        if stop.get("post_stop_calls") != 0:
            _err(errors, "stop_receipt.post_stop_calls", "must be zero")
        if isinstance(api, dict):
            for stop_key, api_key in (("attempted_calls", "attempted"), ("charged_calls", "charged"), ("post_stop_calls", "post_stop_calls")):
                if stop.get(stop_key) != api.get(api_key):
                    _err(errors, "stop_receipt", f"{stop_key} must equal real_api_calls.{api_key}")

    for key in ("clean_replay", "same_information_parity", "blind_scorer", "independent_environment", "policy_state_masked"):
        if receipt.get(key) is not True:
            _err(errors, key, "must be true for closure")
    for key in ("denominator_reconciliation", "cost_reconciliation"):
        item = receipt.get(key)
        if not isinstance(item, dict):
            _err(errors, key, "must be an object with a verified ledger artifact")
        else:
            _require_keys(item, {"verified", "ledger"}, key, errors)
            if item.get("verified") is not True:
                _err(errors, key, "verified must be true")
            _artifact_ref(item.get("ledger"), f"{key}.ledger", root, errors)

    review = receipt.get("independent_review")
    if not isinstance(review, dict):
        _err(errors, "independent_review", "must be an object")
    else:
        _require_keys(review, {"identity", "independent", "scientific_review_passed", "report"}, "independent_review", errors)
        if not _nonempty(review.get("identity")) or review.get("independent") is not True or review.get("scientific_review_passed") is not True:
            _err(errors, "independent_review", "identity, independent=true and scientific_review_passed=true are required")
        _artifact_ref(review.get("report"), "independent_review.report", root, errors)
        verifier_ids = {g.get("verifier", {}).get("identity") for g in gates if isinstance(g, dict) and isinstance(g.get("verifier"), dict) and isinstance(g.get("verifier", {}).get("identity"), str)}
        if review.get("identity") in verifier_ids:
            _err(errors, "independent_review.identity", "must be distinct from every gate verifier")

    # Cross-field closure invariant. These conditions deliberately do not require a favorable sign.
    if status == "CLOSED_FULL":
        if any(g.get("status") != "PASS" for g in gates if isinstance(g, dict)):
            _err(errors, "status", "CLOSED_FULL requires all B1..B7 statuses PASS")
        for i, gate in enumerate(gates if isinstance(gates, list) else []):
            if isinstance(gate, dict) and isinstance(gate.get("denominator"), dict):
                denom = gate["denominator"]
                if denom.get("attempted", 0) <= 0 or denom.get("completed", 0) <= 0:
                    _err(errors, f"gates[{i}].denominator", "CLOSED_FULL cannot use a zero or empty evidence denominator")
        if readiness != "proceedings_ready":
            _err(errors, "status", "CLOSED_FULL requires proceedings_ready")
        if outcome == "insufficient":
            _err(errors, "status", "insufficient method outcome cannot close the gate")
        api_for_closure = receipt.get("real_api_calls")
        if not isinstance(api_for_closure, dict) or api_for_closure.get("successful", 0) <= 0:
            _err(errors, "real_api_calls.successful", "CLOSED_FULL requires at least one successful real API call")
        ar = receipt.get("artifactrole")
        if not isinstance(ar, dict) or ar.get("future_assignment_y_complete") is not True or not isinstance(ar.get("evidence"), dict):
            _err(errors, "artifactrole.future_assignment_y_complete", "must be true; absent future Y is UNSTUDIED")
        if isinstance(receipt.get("target_cells"), list) and any(c.get("execution_status") != "COMPLETE" for c in receipt["target_cells"] if isinstance(c, dict)):
            _err(errors, "target_cells", "CLOSED_FULL requires every required target cell COMPLETE")
    elif status == "OPEN" and readiness == "proceedings_ready" and outcome in {"positive", "neutral", "adverse"}:
        # An open receipt is valid, but the reason must be explicit rather than silently omitted.
        if not _nonempty(receipt.get("open_reason")):
            _err(errors, "open_reason", "OPEN receipt must explain the unresolved closure condition")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        receipt = json.loads(args.receipt.read_text())
    except Exception as exc:  # fail closed, and keep message deterministic
        print(f"INVALID receipt: cannot read JSON: {exc}", file=sys.stderr)
        return 2
    try:
        errors = validate_receipt(receipt, args.project_root.resolve())
    except Exception as exc:  # malformed hostile input must fail closed, never traceback
        print(f"INVALID receipt: validator rejected malformed input: {exc}", file=sys.stderr)
        return 2
    if errors:
        print(f"INVALID receipt: {len(errors)} error(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    status = receipt.get("status")
    print(f"STRUCTURALLY_VALID status={status}; independent scientific review remains required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
