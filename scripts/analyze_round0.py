"""Quick analysis of Round0 results for the report."""
import json
import sys
from pathlib import Path


def analyze_run(run_dir: Path) -> None:
    methods = sorted([d.name for d in run_dir.iterdir() if d.is_dir()])
    print(f"\n=== Run: {run_dir.name} ===")
    print(f"{'Method':<28} {'EM':>6} {'F1':>6} {'PAR':>6} {'MHC':>6} {'Token':>7} {'FAR':>6}")
    print("-" * 70)
    for method in methods:
        m = run_dir / method / "metrics.json"
        if not m.exists():
            continue
        d = json.loads(m.read_text(encoding="utf-8"))
        print(
            f"{method:<28} {d['answer_em']:>6.3f} {d['answer_f1']:>6.3f} "
            f"{d['premature_accept_rate']:>6.3f} {d['mean_handoff_count']:>6.3f} "
            f"{d['token_cost_per_sample']:>7.1f} {d['forward_after_correction_rate']:>6.3f}"
        )

    print("\n--- Delegation proxy: per-hop breakdown (peer_calibrated) ---")
    preds_path = run_dir / "fixed_peer_calibrated" / "parsed_predictions.jsonl"
    if preds_path.exists():
        preds = [json.loads(l) for l in preds_path.open(encoding="utf-8")]
        hop1 = [p for p in preds if p["hop_count"] == 1]
        multi = [p for p in preds if p["hop_count"] > 1]
        avg_f1_h1 = sum(p["answer_f1"] for p in hop1) / len(hop1) if hop1 else 0.0
        avg_f1_multi = sum(p["answer_f1"] for p in multi) / len(multi) if multi else 0.0
        print(f"  hop=1 (accepted early): n={len(hop1)}, avg_F1={avg_f1_h1:.3f}")
        print(f"  hop>1 (forwarded):      n={len(multi)}, avg_F1={avg_f1_multi:.3f}")

        # competence trajectory
        snaps_path = run_dir / "fixed_peer_calibrated" / "competence_snapshots.jsonl"
        post_snaps = [
            json.loads(l) for l in snaps_path.open(encoding="utf-8")
            if "post_sample" in l
        ]
        decomp_scores = [
            s["update"]["after"].get("decomposer", None)
            for s in post_snaps
            if s.get("node_name") == "decomposer"
        ]
        print(f"\n--- Decomposer competence trajectory (post-sample) ---")
        print(f"  First 10: {[round(x, 2) for x in decomp_scores[:10] if x is not None]}")
        print(f"  Last 10:  {[round(x, 2) for x in decomp_scores[-10:] if x is not None]}")
        below_thresh = sum(1 for x in decomp_scores if x is not None and x < 0.62)
        print(f"  Samples where decomposer competence dropped below 0.62: {below_thresh}")

    print("\n--- 3 delegation correction case studies ---")
    traces_path = run_dir / "fixed_peer_calibrated" / "routing_traces.jsonl"
    preds_path = run_dir / "fixed_peer_calibrated" / "parsed_predictions.jsonl"
    if traces_path.exists() and preds_path.exists():
        traces = [json.loads(l) for l in traces_path.open(encoding="utf-8")]
        preds = {p["task_id"]: p for p in [json.loads(l) for l in preds_path.open(encoding="utf-8")]}
        by_sample: dict[str, list] = {}
        for t in traces:
            by_sample.setdefault(t["task_id"], []).append(t)
        shown = 0
        for tid, trace_list in by_sample.items():
            if len(trace_list) > 1 and shown < 3:
                pred = preds.get(tid, {})
                path = " -> ".join(t["node_name"] for t in sorted(trace_list, key=lambda x: x["hop_index"]))
                print(f"\n  [{tid}] hops={pred.get('hop_count')}, F1={pred.get('answer_f1',0):.3f}")
                print(f"    Route: {path}")
                print(f"    Q: {pred.get('question', '')[:80]}")
                print(f"    Gold: {pred.get('gold_answer')} | Pred: {pred.get('final_answer', '')[:50]}")
                for t in sorted(trace_list, key=lambda x: x["hop_index"]):
                    print(f"    [{t['node_name']}] {t['decision']} -> {t['chosen_target'] or 'END'} | {t['reason'][:60]}")
                shown += 1


def main() -> None:
    if len(sys.argv) > 1:
        run_dir = Path(sys.argv[1])
    else:
        candidates = sorted(Path("artifacts/round0").glob("run_*"))
        if not candidates:
            print("No runs found.")
            return
        run_dir = candidates[-1]
    analyze_run(run_dir)


if __name__ == "__main__":
    main()
