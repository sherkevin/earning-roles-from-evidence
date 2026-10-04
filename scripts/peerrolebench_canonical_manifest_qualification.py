"""Zero-call qualification for the canonical nested manifest validator.

This is an engineering receipt only.  It reuses the synthetic manifest builder
from the focused test module, exercises one valid manifest and the registered
mutation cases, and writes config/raw/summary JSON.  It never starts a policy
runner, calls an API, allocates a GPU, or changes historical receipts.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_canonical_manifest import digest, validate_canonical_manifest  # noqa: E402
from tests.test_peerrolebench_canonical_manifest import _manifest  # noqa: E402


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reseal(manifest: dict[str, Any]) -> None:
    manifest["manifest_digest"] = digest({
        key: value for key, value in manifest.items() if key != "manifest_digest"
    })


def _cases() -> dict[str, Callable[[dict[str, Any]], None]]:
    def missing_channel(value: dict[str, Any]) -> None:
        del value["channels"][1]
        _reseal(value)

    def arm_mutation(value: dict[str, Any]) -> None:
        value["arm_specs"][0]["implementation_digest"] = "1" * 64

    def phi_mutation(value: dict[str, Any]) -> None:
        value["stream"]["public_phi"]["fields"].append("future_outcome")

    def missing_closest(value: dict[str, Any]) -> None:
        del value["closest_published"]
        _reseal(value)

    def live_with_blocked_closest(value: dict[str, Any]) -> None:
        value["status"] = "live"
        _reseal(value)

    def cell_disposition(value: dict[str, Any]) -> None:
        value["cells"][0]["expected_disposition"] = "ignored"

    def bad_envelope(value: dict[str, Any]) -> None:
        value["manifest_digest"] = "0" * 64

    def missing_root_metadata(value: dict[str, Any]) -> None:
        del value["root"]["task_id"]

    def arm_policy_field(value: dict[str, Any]) -> None:
        del value["arm_specs"][0]["policy_factory"]

    def bad_execution(value: dict[str, Any]) -> None:
        value["execution"]["selected_only"] = False

    def bad_cost_digest(value: dict[str, Any]) -> None:
        value["execution"]["cost_schema_digest"] = "0" * 64

    def bad_negative_digest(value: dict[str, Any]) -> None:
        value["execution"]["negative_cell_contract_digest"] = "0" * 64

    def bad_started_expectation(value: dict[str, Any]) -> None:
        value["cells"][0]["expected_runner_started"] = False

    def bad_update_expectation(value: dict[str, Any]) -> None:
        value["cells"][1]["expected_updates"] = 1

    return {
        "missing_channel": missing_channel,
        "arm_mutation": arm_mutation,
        "phi_mutation": phi_mutation,
        "missing_closest": missing_closest,
        "live_with_blocked_closest": live_with_blocked_closest,
        "cell_disposition": cell_disposition,
        "bad_envelope": bad_envelope,
        "missing_root_metadata": missing_root_metadata,
        "arm_policy_field": arm_policy_field,
        "bad_execution": bad_execution,
        "bad_cost_digest": bad_cost_digest,
        "bad_negative_digest": bad_negative_digest,
        "bad_started_expectation": bad_started_expectation,
        "bad_update_expectation": bad_update_expectation,
    }


def run(out_dir: Path) -> dict[str, Any]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=False, exist_ok=False)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    component_names = (
        "scripts/peerrolebench_canonical_manifest.py",
        "scripts/peerrolebench_baseline_contract.py",
        "scripts/peerrolebench_baseline_root_contract.py",
        "tests/test_peerrolebench_canonical_manifest.py",
    )
    config = {
        "experiment_id": out_dir.name,
        "kind": "zero_call_canonical_manifest_validator_qualification",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "python": platform.python_version(),
        "component_sha256": {name: _sha(ROOT / name) for name in component_names},
        "real_api_calls": 0,
        "gpu_jobs": 0,
        "scientific_claim_allowed": False,
        "benchmark_qualified": False,
    }
    (out_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    records: list[dict[str, Any]] = []
    valid = _manifest()
    try:
        validate_canonical_manifest(valid)
        records.append({"case": "valid", "status": "PASS", "runner_started": False, "policy_updates": 0})
    except Exception as exc:  # pragma: no cover - receipt failure path
        records.append({"case": "valid", "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
    for name, mutate in _cases().items():
        candidate = deepcopy(valid)
        try:
            mutate(candidate)
            validate_canonical_manifest(candidate)
        except Exception as exc:
            records.append({
                "case": name,
                "status": "UNKNOWN",
                "false_accept": False,
                "runner_started": False,
                "policy_updates": 0,
                "error": f"{type(exc).__name__}: {exc}",
            })
        else:
            records.append({
                "case": name,
                "status": "FAIL",
                "false_accept": True,
                "runner_started": None,
                "policy_updates": None,
            })
    with (out_dir / "raw.jsonl").open("w", encoding="utf-8") as raw:
        for record in records:
            raw.write(json.dumps(record, sort_keys=True) + "\n")
    positive_ok = records[0]["status"] == "PASS"
    negative_ok = all(
        record["status"] == "UNKNOWN"
        and record.get("false_accept") is False
        and record.get("runner_started") is False
        and record.get("policy_updates") == 0
        for record in records[1:]
    )
    summary = {
        **config,
        "status": "QUALIFIED_OFFLINE" if positive_ok and negative_ok else "FAILED_OFFLINE",
        "passed": bool(positive_ok and negative_ok),
        "case_count": len(records),
        "checks": {"valid_manifest": positive_ok, "all_mutations_fail_closed": negative_ok},
        "records": records,
        "ended_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, required=True)
    result = run(parser.parse_args().out_dir)
    print(json.dumps({key: result[key] for key in ("status", "passed", "case_count", "real_api_calls", "gpu_jobs")}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
