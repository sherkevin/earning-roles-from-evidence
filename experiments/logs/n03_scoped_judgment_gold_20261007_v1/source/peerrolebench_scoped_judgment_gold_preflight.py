"""Check exact prepared diagnostic sources with existing isolated P/Qr scorers.

No API, action generation, terminal rerun, or learning. Each unique component is
checked once; the four-cell gold projection is valid only if all pinned inputs
and all expected checks agree. This does not establish general scorer coverage.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import traceback

from peerrolebench_pipe3_material_adapter import digest_files
from peerrolebench_pipe3_producer_scorer_qualification import interfaces
from peerrolebench_pipe3_producer_scorer_v2 import run_producer_scorer
from peerrolebench_pipe3_recipient_scorer_v2 import run_scorer

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def run(prepared: Path, out: Path):
    out.mkdir(parents=True, exist_ok=False)
    scripts = [Path(__file__), ROOT / "scripts/peerrolebench_pipe3_producer_scorer_v2.py",
               ROOT / "scripts/peerrolebench_pipe3_producer_scorer_worker_v2.py",
               ROOT / "scripts/peerrolebench_pipe3_recipient_scorer_v2.py",
               ROOT / "scripts/peerrolebench_pipe3_recipient_scorer_worker_v2.py",
               ROOT / "scripts/peerrolebench_sandbox.py",
               ROOT / "scripts/peerrolebench_pipe3_producer_scorer_qualification.py"]
    config = {"purpose": __doc__, "frozen_before_execution": True,
              "started_at": datetime.now(timezone.utc).isoformat(),
              "prepared": str(prepared), "manifest_sha256": sha(prepared / "parent_manifest.json"),
              "command": [sys.executable, str(Path(__file__)), "--prepared", str(prepared), "--out", str(out)],
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "python": sys.version, "platform": platform.platform(),
              "source_sha256": {str(p.relative_to(ROOT)): sha(p) for p in scripts},
              "maximum_sandbox_executions": 4, "api_calls": 0, "gpu_jobs": 0,
              "scientific_claim_allowed": False,
              "limits": "non-adversarial existing code; finite scorer checks; same-process child instrumentation"}
    save(out / "config.json", config)
    snap = out / "source"; snap.mkdir()
    for script in scripts:
        shutil.copy2(script, snap / script.name)

    def log(event_type, payload):
        with (out / "raw.jsonl").open("a") as stream:
            stream.write(json.dumps({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                                     "event_type": event_type, "payload": payload}, ensure_ascii=False) + "\n")

    results = {}
    try:
        manifest = json.loads((prepared / "parent_manifest.json").read_text())
        if len(manifest["cases"]) != 4:
            raise ValueError("four cells required")
        cells = []
        for case in manifest["cases"]:
            request_path = prepared / case["request_path"]
            if sha(request_path) != case["request_sha256"]:
                raise ValueError("prepared request changed")
            request = json.loads(request_path.read_text())
            visible = json.loads(request["messages"][0]["content"].split("\n\nPublic task payload:\n", 1)[1])
            files = visible["public_source_files"]
            actual = {name: digest_files({name: source}) for name, source in files.items()}
            if actual != case["public_file_digests"]:
                raise ValueError("public file digest mismatch")
            if visible["producer_artifact_sha256"] != actual["producer.py"]:
                raise ValueError("producer binding mismatch")
            if digest_files({name: files[name] for name in ("models.py", "sink.py")}) != manifest["support_digest"]:
                raise ValueError("support differs across cells")
            cells.append((case, files))
        # Source identity, not the four Cartesian combinations, is the unit of
        # local correctness checking: Qr receives a canonical conforming input.
        for axis, filename, origin_key in (("producer", "producer.py", "producer_origin"),
                                           ("recipient", "processor.py", "recipient_origin")):
            for origin in ("historical", "native"):
                matching = [(case, files) for case, files in cells if case[origin_key] == origin]
                if len(matching) != 2 or matching[0][1][filename] != matching[1][1][filename]:
                    raise ValueError("factor changed with the other component")
                sources = {name: matching[0][1][name] for name in (filename, "models.py")}
                info = interfaces({"agent_payloads": {"producer": {"source_files": {
                    "models.py": sources["models.py"], "producer.py": matching[0][1]["producer.py"]}}}})
                key = axis + "_" + origin
                log("component_started", {"key": key, "source_sha256": digest_files(sources)})
                if axis == "producer":
                    result = run_producer_scorer(sources, info, "PIPE3_stream_processing", 0, out / key, log)
                else:
                    result = run_scorer(sources, info, "recipient", "PIPE3_stream_processing", 0, out / key, log)
                results[key] = result
                expected = "PASS" if origin == "historical" else "FAIL"
                if result.get("status") != expected or not result.get("coverage_complete"):
                    raise ValueError(f"component gold unsupported: {key}")
                if key == "producer_native" and result.get("failed_check_ids") != ["P2_iso_serialization"]:
                    raise ValueError("producer control has a different failure")
        projections = []
        for case, _ in cells:
            p = results["producer_" + case["producer_origin"]]
            r = results["recipient_" + case["recipient_origin"]]
            if (case["expected_producer_verdict"] != ("meets_contract" if p["status"] == "PASS" else "violates_contract")
                or case["expected_recipient_needs_change"] != (r["status"] == "FAIL")):
                raise ValueError("prepared gold differs from measured local label")
            projections.append({"case_id": case["case_id"], "producer_status": p["status"],
                                "recipient_self_status": r["status"], "other_axis_invariant": True})
        summary = {"status": "FINITE_COMPONENT_GOLD_SUPPORTED", "components": results,
                   "four_cell_projections": projections, "api_calls": 0, "gpu_jobs": 0,
                   "training_updates": 0, "scientific_readiness": False,
                   "scope": "Four fixed component artifacts; not population accuracy or exhaustive contract verification"}
    except Exception as exc:
        log("preflight_failed", {"exception": type(exc).__name__, "message": str(exc), "traceback": traceback.format_exc()})
        summary = {"status": "UNKNOWN", "components": results, "reason": str(exc), "api_calls": 0, "gpu_jobs": 0}
    save(out / "summary.json", summary)
    log("preflight_completed", {"status": summary["status"]})
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepared", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.prepared, args.out)
    print(json.dumps({"status": result["status"], "api_calls": 0, "gpu_jobs": 0}))
    sys.exit(0 if result["status"] == "FINITE_COMPONENT_GOLD_SUPPORTED" else 1)
