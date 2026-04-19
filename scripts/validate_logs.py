"""
Log integrity validator for idea04 Round0.
Checks:
  1. All required files exist
  2. Sample coverage = 100% (every sample_id has routing trace, handoff packet, prediction)
  3. Every sample has at least one competence snapshot (before + after)
  4. Routing chain can be fully reconstructed per sample
"""
import argparse
import json
import sys
from pathlib import Path


REQUIRED_FILES = [
    "run_config.yaml",
    "sample_ids.json",
    "raw_inputs.jsonl",
    "routing_traces.jsonl",
    "handoff_packets.jsonl",
    "competence_snapshots.jsonl",
    "raw_model_outputs.jsonl",
    "parsed_predictions.jsonl",
    "metrics.json",
    "main_table.csv",
    "failure_cases.md",
    "case_studies.md",
    "run_notes.md",
]


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def validate_run_dir(run_dir: Path) -> list[str]:
    errors: list[str] = []

    # 1. File existence
    for fname in REQUIRED_FILES:
        if not (run_dir / fname).exists():
            errors.append(f"MISSING_FILE: {fname}")

    if errors:
        return errors

    # 2. Load artefacts
    sample_ids: list[str] = json.loads((run_dir / "sample_ids.json").read_text(encoding="utf-8"))
    traces = read_jsonl(run_dir / "routing_traces.jsonl")
    packets = read_jsonl(run_dir / "handoff_packets.jsonl")
    snaps = read_jsonl(run_dir / "competence_snapshots.jsonl")
    raw_outs = read_jsonl(run_dir / "raw_model_outputs.jsonl")
    predictions = read_jsonl(run_dir / "parsed_predictions.jsonl")

    sample_id_set = set(sample_ids)

    # 3. Sample coverage in predictions
    predicted_ids = {p["task_id"] for p in predictions}
    missing_pred = sample_id_set - predicted_ids
    if missing_pred:
        errors.append(f"MISSING_PREDICTIONS for {len(missing_pred)} samples: {sorted(missing_pred)[:5]}")

    coverage = len(predicted_ids & sample_id_set) / len(sample_id_set) if sample_id_set else 0.0
    if coverage < 1.0:
        errors.append(f"COVERAGE_BELOW_100: {coverage:.2%}")

    # 4. Sample coverage in routing traces
    traced_ids = {t["task_id"] for t in traces}
    missing_traces = sample_id_set - traced_ids
    if missing_traces:
        errors.append(f"MISSING_ROUTING_TRACES for {len(missing_traces)} samples")

    # 5. Sample coverage in handoff packets
    packet_ids = {p["task_id"] for p in packets}
    missing_packets = sample_id_set - packet_ids
    if missing_packets:
        errors.append(f"MISSING_HANDOFF_PACKETS for {len(missing_packets)} samples")

    # 6. Sample coverage in competence snapshots
    snap_ids = {s["task_id"] for s in snaps}
    missing_snaps = sample_id_set - snap_ids
    if missing_snaps:
        errors.append(f"MISSING_COMPETENCE_SNAPSHOTS for {len(missing_snaps)} samples")

    # 7. Every snapshot has before + after keys
    for snap in snaps:
        upd = snap.get("update", {})
        if "before" not in upd or "after" not in upd:
            errors.append(
                f"SNAPSHOT_MISSING_BEFORE_AFTER: task={snap.get('task_id')} hop={snap.get('hop_index')}"
            )
            break

    # 8. Routing chain reconstruction: each sample's traces are contiguous hops starting from 0
    traces_by_sample: dict[str, list[dict]] = {}
    for t in traces:
        traces_by_sample.setdefault(t["task_id"], []).append(t)

    for sid, sid_traces in traces_by_sample.items():
        hops = sorted(t["hop_index"] for t in sid_traces)
        expected = list(range(len(hops)))
        if hops != expected:
            errors.append(f"ROUTING_CHAIN_GAP: task={sid} hops={hops}")

    # 9. Raw model outputs cover every trace hop
    raw_by_sample: dict[str, set] = {}
    for r in raw_outs:
        raw_by_sample.setdefault(r["task_id"], set()).add(r["hop_index"])

    for sid, sid_traces in traces_by_sample.items():
        trace_hops = {t["hop_index"] for t in sid_traces}
        raw_hops = raw_by_sample.get(sid, set())
        uncovered = trace_hops - raw_hops
        if uncovered:
            errors.append(f"RAW_OUTPUT_MISSING_HOPS: task={sid} hops={sorted(uncovered)}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Round0 log integrity.")
    parser.add_argument("run_dir", nargs="?", default=None, help="Path to a specific run directory.")
    parser.add_argument(
        "--all-methods",
        action="store_true",
        help="Scan all method subdirs inside a run directory.",
    )
    args = parser.parse_args()

    if args.run_dir is None:
        print("Usage: validate_logs.py <run_dir> [--all-methods]", file=sys.stderr)
        sys.exit(1)

    root = Path(args.run_dir)
    if not root.exists():
        print(f"ERROR: {root} does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.all_methods:
        method_dirs = [d for d in root.iterdir() if d.is_dir()]
    else:
        method_dirs = [root]

    all_ok = True
    for mdir in sorted(method_dirs):
        errors = validate_run_dir(mdir)
        if errors:
            print(f"\n[FAIL] {mdir.name}")
            for e in errors:
                print(f"  - {e}")
            all_ok = False
        else:
            sample_ids = json.loads((mdir / "sample_ids.json").read_text(encoding="utf-8"))
            print(f"[OK]   {mdir.name}  ({len(sample_ids)} samples, 100% coverage)")

    if not all_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
