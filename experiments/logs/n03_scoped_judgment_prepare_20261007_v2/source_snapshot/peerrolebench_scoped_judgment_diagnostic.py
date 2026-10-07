#!/usr/bin/env python3
"""Prepare four offline, scoped PIPE3 judgment requests; never call a model.

The parent manifest is private operator material. Only request_*.json may be sent
to a judgment model. Preparation does not execute candidates, score outcomes, or
claim that a model has answered. A separate, newly authorized run is required.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import random
import shutil
import subprocess
import sys
import traceback
from typing import Any

from peerrolebench_pipe3_material_adapter import digest_files, strip_comments_and_docstrings
from peerrolebench_pipe3_public_contract_v2 import CLAUSES, build_materials
from peerrolebench_pipe3_task_qualification import load_pipe3


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = ("producer.py", "processor.py", "models.py", "sink.py")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _event(path: Path, event: str, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                 "event": event, "payload": payload}, ensure_ascii=False, sort_keys=True) + "\n")


def _pinned(path_text: str, expected_sha256: str) -> Path:
    path = (ROOT / path_text).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f"missing or outside-project source: {path_text}")
    actual = sha256_file(path)
    if actual != expected_sha256:
        raise ValueError(f"source pin mismatch: {path_text}; expected {expected_sha256}, got {actual}")
    return path


def _sanitized(source: str, name: str) -> str:
    if not isinstance(source, str):
        raise ValueError(f"non-text source: {name}")
    return strip_comments_and_docstrings(source)


def _materials(card: dict[str, Any]) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
    sources = card["source_inputs"]
    delivery_path = _pinned(sources["delivery"]["path"], sources["delivery"]["sha256"])
    action_path = _pinned(sources["action"]["path"], sources["action"]["sha256"])
    _pinned(sources["public_contract"]["path"], sources["public_contract"]["sha256"])
    _pinned(sources["material_adapter"]["path"], sources["material_adapter"]["sha256"])
    _pinned(sources["qualification"]["path"], sources["qualification"]["sha256"])
    bench = (ROOT / card["native_generator"]["repository"]).resolve()
    actual_pin = subprocess.check_output(["git", "-C", str(bench), "rev-parse", "HEAD"], text=True).strip()
    if actual_pin != card["native_generator"]["commit"]:
        raise ValueError("native generator commit mismatch")
    porcelain = subprocess.check_output(["git", "-C", str(bench), "status", "--porcelain"], text=True).strip()
    if porcelain:
        raise ValueError("native generator checkout is dirty: " + porcelain)

    native = build_materials(load_pipe3(card["native_generator"]["seed"]))
    if native["manifest"]["public_contract_version"] != card["public_contract_version"]:
        raise ValueError("public contract version mismatch")
    producer_payload = native["agent_payloads"]["producer"]
    recipient_payload = native["agent_payloads"]["recipient"]
    if producer_payload["task_text"] != recipient_payload["task_text"]:
        raise ValueError("role-specific public spec")
    task_text = producer_payload["task_text"]
    if set(task_text) != {"spec_md", "brief_md"}:
        raise ValueError("unexpected public task text")
    nfiles = {name: _sanitized(
        (producer_payload if name != "processor.py" else recipient_payload)["source_files"][name], name)
        for name in PUBLIC_PATHS}
    delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
    action = json.loads(action_path.read_text(encoding="utf-8"))
    if set(delivery) != {"producer.py"} or set(action["source_files"]) != set(PUBLIC_PATHS):
        raise ValueError("unexpected historical file set")
    if action["source_files"]["producer.py"] != delivery["producer.py"]:
        raise ValueError("historical action does not match delivery")
    if action["changed_paths"] != ["processor.py"]:
        raise ValueError("historical recipient action changed unexpected paths")
    pplus = _sanitized(delivery["producer.py"], "historical producer.py")
    rplus = _sanitized(action["source_files"]["processor.py"], "historical processor.py")
    for name in ("models.py", "sink.py"):
        if _sanitized(action["source_files"][name], f"historical {name}") != nfiles[name]:
            raise ValueError(f"historical support differs from native: {name}")
    if pplus == nfiles["producer.py"] or rplus == nfiles["processor.py"]:
        raise ValueError("diagnostic axis collapsed")
    return task_text, nfiles, {"producer.py": pplus}, {"processor.py": rplus}


def _request(case_id: str, task_text: dict[str, str], files: dict[str, str]) -> dict[str, Any]:
    producer_digest = digest_files({"producer.py": files["producer.py"]})
    instruction = (
        "You are the recipient responsible for processor.py in the public PIPE3 task. "
        "Before acting, return exactly one JSON object "
        "with producer_contract_assessment and recipient_integration_plan. Assess producer.py "
        "against the public producer contract using only the provided public sources. "
        "For recipient_integration_plan, decide whether processor.py itself must change to meet "
        "its public responsibilities when paired with a conforming producer. Do not assign a "
        "producer defect to processor.py. Do not execute code or propose an action on the files. "
        "Use only public contract clause IDs for contract_clause_refs. "
        "producer_contract_assessment must contain verdict (meets_contract, violates_contract, "
        "or uncertain), observed_artifact_sha256 (copy the supplied producer digest), "
        "contract_clause_refs (array of clause ID strings), and rationale (string). "
        "recipient_integration_plan must contain needs_change (boolean), target_paths "
        "(array, either [] or [\"processor.py\"]), and rationale (string). "
        "If needs_change is false, target_paths must be empty; if true, target_paths must be "
        "[\"processor.py\"]. No markdown or extra keys."
    )
    visible = {
        "case_id": case_id,
        "task_id": "PIPE3_stream_processing",
        "public_task_text": task_text,
        "public_source_files": files,
        "producer_artifact_sha256": producer_digest,
        "public_contract_clauses": CLAUSES,
    }
    # Match the existing /v1/messages transport's single user-prompt shape.
    return {"messages": [{"role": "user", "content": instruction + "\n\nPublic task payload:\n"
                           + json.dumps(visible, ensure_ascii=False, sort_keys=True)}]}


def prepare(card_path: Path, output_dir: Path) -> Path:
    """Create an immutable-style, new-directory offline preparation record.

    This deliberately has no model transport or execution flag. The operator
    must review the private parent manifest before authorizing a separate run.
    """
    if output_dir.exists():
        raise FileExistsError(f"preparation directory already exists: {output_dir}")
    card_path = card_path.resolve()
    card = json.loads(card_path.read_text(encoding="utf-8"))
    if card["real_api_runs_allowed"] is not False or card["budget"]["prior_attempted_episodes"] <= card["budget"]["original_cap_episodes"]:
        raise ValueError("card must retain the exhausted budget stop")
    if card["max_judgment_requests"] != 4 or card["max_episodes"] != 4 or card["retries"] != 0:
        raise ValueError("bounded diagnostic dimensions changed")
    output_dir.mkdir(parents=True, exist_ok=False)
    # First output is the attempt configuration, before source loads/preflight.
    config = {"schema_version": "n03-scoped-judgment-prepare-v1", "card": card,
              "card_path": str(card_path), "card_sha256": sha256_file(card_path),
              "command": [sys.executable, str(Path(__file__).resolve()), "prepare", "--card", str(card_path), "--out", str(output_dir)],
              "python": platform.python_version(), "started_utc": datetime.now(timezone.utc).isoformat(),
              "api_calls": 0, "gpu_runs": 0, "candidate_executions": 0}
    _write_json(output_dir / "config.json", config)
    snapshot = output_dir / "source_snapshot"
    snapshot.mkdir()
    shutil.copy2(Path(__file__).resolve(), snapshot / Path(__file__).name)
    raw_path = output_dir / "raw.jsonl"
    _event(raw_path, "preflight_started", {"card_sha256": config["card_sha256"]})
    try:
        task_text, native, pplus, rplus = _materials(card)
        _event(raw_path, "source_pins_verified", {"source_sha256": {k: v["sha256"] for k, v in card["source_inputs"].items()},
                                                  "native_commit": card["native_generator"]["commit"]})
        variants = {
            "producer": {"native": native["producer.py"], "historical": pplus["producer.py"]},
            "recipient": {"native": native["processor.py"], "historical": rplus["processor.py"]},
        }
        cells = [(p, r) for p in ("historical", "native") for r in ("historical", "native")]
        rng = random.Random(card["shuffle_seed"])
        rng.shuffle(cells)
        used_ids: set[str] = set()
        parent_cases: list[dict[str, Any]] = []
        requests_dir = output_dir / "requests"
        requests_dir.mkdir()
        for order, (p, r) in enumerate(cells):
            case_id = hashlib.sha256(f"{card['shuffle_seed']}|{p}|{r}|{rng.getrandbits(128)}".encode()).hexdigest()[:20]
            if case_id in used_ids:
                raise ValueError("case ID collision")
            used_ids.add(case_id)
            files = {"producer.py": variants["producer"][p], "processor.py": variants["recipient"][r],
                     "models.py": native["models.py"], "sink.py": native["sink.py"]}
            request = _request(case_id, task_text, files)
            request_path = requests_dir / f"request_{case_id}.json"
            _write_json(request_path, request)
            parent_cases.append({"order": order, "case_id": case_id,
                                 "request_path": str(request_path.relative_to(output_dir)),
                                 "request_sha256": sha256_file(request_path),
                                 "producer_origin": p, "recipient_origin": r,
                                 "public_file_digests": {name: digest_files({name: source}) for name, source in files.items()},
                                 "expected_producer_verdict": "meets_contract" if p == "historical" else "violates_contract",
                                 "expected_recipient_needs_change": r == "native",
                                 "expected_recipient_target_paths": ["processor.py"] if r == "native" else []})
            _event(raw_path, "request_prepared", {"order": order, "case_id": case_id,
                                                   "request_sha256": sha256_file(request_path)})
        manifest = {"schema_version": "n03-scoped-judgment-parent-manifest-v1",
                    "scope": "fixed four-cell diagnostic; constructed gold, no model results",
                    "public_contract_version": card["public_contract_version"],
                    "public_task_text_sha256": hashlib.sha256(canonical_bytes(task_text)).hexdigest(),
                    "support_digest": digest_files({name: native[name] for name in ("models.py", "sink.py")}),
                    "sanitizer": "strip_comments_and_docstrings applied uniformly to all public files",
                    "cases": parent_cases,
                    "decision_rule": card["decision_rule"],
                    "api_calls": 0, "candidate_executions": 0, "gpu_runs": 0}
        _write_json(output_dir / "parent_manifest.json", manifest)
        for key in ("delivery", "action", "public_contract", "material_adapter", "qualification"):
            source = card["source_inputs"][key]
            shutil.copy2(ROOT / source["path"], snapshot / Path(source["path"]).name)
        shutil.copy2(Path(__file__).resolve(), snapshot / Path(__file__).name)
        _write_json(output_dir / "summary.json", {"status": "PREPARED_OFFLINE", "requests": len(parent_cases),
                                                   "api_calls": 0, "gpu_runs": 0,
                                                   "parent_manifest_sha256": sha256_file(output_dir / "parent_manifest.json"),
                                                   "source_snapshot_sha256": {p.name: sha256_file(p) for p in snapshot.iterdir()}})
        _event(raw_path, "prepare_completed", {"status": "PREPARED_OFFLINE", "requests": 4})
        return output_dir
    except Exception as exc:
        _event(raw_path, "prepare_failed", {"type": type(exc).__name__, "message": str(exc),
                                            "traceback": traceback.format_exc()})
        _write_json(output_dir / "summary.json", {"status": "UNKNOWN", "api_calls": 0,
                                                   "gpu_runs": 0, "error_type": type(exc).__name__})
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("prepare", help="prepare four offline prompts; no API transport")
    run.add_argument("--card", required=True, type=Path)
    run.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    prepare(args.card, args.out)


if __name__ == "__main__":
    main()
