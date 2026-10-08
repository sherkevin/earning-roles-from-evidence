"""Zero-call qualification for the strict consumer response envelope."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_pipe3_consumer_response_contract import extract_consumer_sources  # noqa: E402


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=False, exist_ok=False)
    paths = ["processor.py", "models.py", "sink.py", "producer.py"]
    files = {path: f"# {path}\n" for path in paths}
    cases = [
        ("valid_envelope", {"source_files": files}, "PASS"),
        ("bare_file_dict", files, "UNKNOWN"),
        ("extra_metadata", {"source_files": files, "rationale": "x"}, "UNKNOWN"),
        ("missing_path", {"source_files": {"processor.py": files["processor.py"]}}, "UNKNOWN"),
        ("non_text_source", {"source_files": {**files, "sink.py": 7}}, "UNKNOWN"),
    ]
    results = []
    for name, value, expected in cases:
        try:
            extracted = extract_consumer_sources(value, paths)
            observed = {"case": name, "status": "PASS", "path_count": len(extracted)}
        except ValueError as exc:
            observed = {"case": name, "status": "UNKNOWN", "error": str(exc)}
        observed["expected"] = expected
        results.append(observed)
    summary = {
        "qualification_version": "pipe3-consumer-response-qualification-v1",
        "schema_version": "pipe3-consumer-response-v1",
        "required_paths": paths, "llm_calls": 0, "gpu_jobs": 0,
        "native_grader_invoked": False, "scientific_claim_allowed": False,
        "passed": all(item["status"] == item["expected"] for item in results),
        "results": results, "consumer_contract_qualified": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "remaining_gates": ["run a new real card after versioning the runner envelope parser"],
    }
    (out / "config.json").write_text(json.dumps({key: summary[key] for key in
                                                   ("qualification_version", "schema_version",
                                                    "required_paths", "llm_calls", "gpu_jobs",
                                                    "native_grader_invoked", "scientific_claim_allowed")},
                                                  indent=2, ensure_ascii=False) + "\n")
    (out / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    with (out / "raw.jsonl").open("w", encoding="utf-8") as handle:
        for item in results:
            handle.write(json.dumps({"timestamp_utc": summary["created_at_utc"],
                                     "event_type": "consumer_response_case", "payload": item},
                                    ensure_ascii=False) + "\n")
    print(json.dumps({"passed": summary["passed"], "consumer_contract_qualified": False,
                      "scientific_claim_allowed": False}, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
