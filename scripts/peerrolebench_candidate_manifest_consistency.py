"""Compare candidate benchmark cards before any live activation.

This is a zero-call guard against silently mixing the older two-root manifest,
the newer same-information parity card, and the bounded C1 live card.  A
reported mismatch is evidence that the scientific split is not yet frozen; it
must not be repaired by choosing whichever config is easiest to run.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
OLD_CARD = ROOT / "configs/aamas2027/n03_benchmark_baseline_candidate_v2.json"
PARITY_CARD = ROOT / "configs/aamas2027/n03_baseline_live_parity_candidate_v0.2.json"
C1_CARD = ROOT / "configs/aamas2027/n03_c1_parent_source_live_v2_signal_channels.json"
RUNNER = ROOT / "scripts/peerrolebench_policy_matrix_runner_v1.py"


def _load(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _runner_constants() -> tuple[tuple[str, ...], tuple[str, ...]]:
    spec = importlib.util.spec_from_file_location("peerrolebench_matrix_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load policy matrix runner")
    module = importlib.util.module_from_spec(spec)
    # dataclasses with postponed annotations resolve their module through
    # sys.modules; register the transient module before executing it.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return tuple(module.ARM_NAMES), tuple(module.CANDIDATE_EXECUTABLE_ARM_NAMES)


def audit(old: Mapping[str, Any], parity: Mapping[str, Any], c1: Mapping[str, Any]) -> dict[str, Any]:
    old_roots = {str(item.get("task_id")): str(item.get("split"))
                 for item in old.get("roots", []) if isinstance(item, Mapping)}
    parity_root = str(parity.get("primary_root"))
    old_primary_development = next(
        (task for task, split in old_roots.items() if split == "development"), None
    )
    old_arms = tuple(str(item) for item in old.get("baselines", []))
    parity_arms = tuple(str(item) for item in parity.get("arms", []))
    c1_arms = tuple(str(item) for item in c1.get("arms", []))
    legacy_arms, executable_arms = _runner_constants()

    blockers: list[dict[str, Any]] = []
    if old_primary_development != parity_root:
        blockers.append({
            "id": "root_split_disagreement",
            "old_manifest_development_root": old_primary_development,
            "parity_card_primary_root": parity_root,
            "impact": "development/confirmation assignment is not frozen",
        })
    if "contextual_trust" in old_arms and "contextual_trust_linear" in parity_arms:
        blockers.append({
            "id": "strongest_control_name_disagreement",
            "old_manifest": "contextual_trust",
            "parity_card": "contextual_trust_linear",
            "impact": "same-information control cannot be identified across cards",
        })
    missing_from_c1 = [name for name in executable_arms if name not in c1_arms]
    if missing_from_c1:
        blockers.append({
            "id": "c1_arm_coverage_gap",
            "candidate_executable_arms": list(executable_arms),
            "c1_arms": list(c1_arms),
            "missing": missing_from_c1,
            "impact": "C1 cannot be promoted to the parity matrix without new arm adapters",
        })
    if "Meta-Team-L2-public" not in parity.get("arms", []):
        blockers.append({
            "id": "closest_adapter_row_missing",
            "impact": "closest published adapter must be explicit NO-GO or independently executable",
        })
    if tuple(name for name in legacy_arms if name != "contextual_trust") != tuple(
        name for name in executable_arms if name != "contextual_trust_linear"
    ):
        blockers.append({
            "id": "runner_legacy_candidate_order_difference",
            "legacy_arms": list(legacy_arms),
            "candidate_executable_arms": list(executable_arms),
            "impact": "historical and candidate receipts require separate arm manifests",
        })

    return {
        "status": "BLOCKED_PRE_EXECUTION" if blockers else "CONSISTENT_CANDIDATE",
        "scientific_claim_allowed": False,
        "api_runs_allowed": False,
        "gpu_runs_allowed": False,
        "old_manifest": {
            "path": str(OLD_CARD.relative_to(ROOT)),
            "manifest_version": old.get("manifest_version"),
            "roots": old_roots,
            "baselines": list(old_arms),
        },
        "parity_card": {
            "path": str(PARITY_CARD.relative_to(ROOT)),
            "manifest_version": parity.get("manifest_version"),
            "primary_root": parity_root,
            "arms": list(parity_arms),
        },
        "c1_card": {
            "path": str(C1_CARD.relative_to(ROOT)),
            "manifest_version": c1.get("manifest_version"),
            "arms": list(c1_arms),
        },
        "runner": {
            "path": str(RUNNER.relative_to(ROOT)),
            "legacy_arms": list(legacy_arms),
            "candidate_executable_arms": list(executable_arms),
        },
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = audit(_load(OLD_CARD), _load(PARITY_CARD), _load(C1_CARD))
    result["source_sha256"] = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (OLD_CARD, PARITY_CARD, C1_CARD, RUNNER)
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["status"] == "CONSISTENT_CANDIDATE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
