"""A-T02: offline, read-only diagnostics of preserved AAMAS revision evidence.

No runtime, network client, or model provider is imported. Outputs are diagnostic
and never replace historical scores, source snapshots, or experiment artifacts.
"""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import re
from statistics import mean
import string

OFFICIAL_SHA256 = "d35fc91a6db21d791dbdda11daf3856e9359f5701d54e3eefba20d88fecc02c0"
OFFICIAL_REL = "references/aamas/official/hotpot_evaluate_v1.py"
SNAPSHOT = "artifacts/submission/edo_anonymous_supplement_20260526/code/edo_core"
JOBS = (
    ("HotpotQA", "e155_qwen_hotpotqa_fullval_adaptive_20260510_auto",
     "hotpotqa/seed_42/edo_adaptive_protocol_router_backbone",
     "e155_qwen_fullval_bootstrap/paired_bootstrap.json",
     "edo_adaptive_protocol_router_backbone_minus_single_agent_fullval", 7405),
    ("MuSiQue", "e170_qwen_musique_role_pool_guarded_fullval_20260512_0030",
     "musique_role_pool_guarded/seed_42/edo_adaptive_protocol_router_musique_role_pool_guarded",
     "posthoc_baseline_compare/e170_musique_qwen_baseline_bootstrap.json", "agentverse_mas", 4834),
    ("2Wiki", "e182_qwen_2wiki_bridge_tool_v6_fullval_20260514_1310",
     "2wiki_fullval/seed_42/edo_adaptive_protocol_router_tool_pool_bridge_gated_v6",
     "posthoc_final_mad_compare_20260515_110641/e179_2wiki_qwen_baseline_bootstrap.json",
     "mad_final", 12576),
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonicalize_rows(rows):
    """Explicit aliases for the two preserved runner schemas; retain values."""
    canonical = []
    for original in rows:
        row = dict(original)
        for target, alias in (("gold_answer", "answer_gold"), ("final_answer", "answer_pred")):
            if target in row and alias in row and row[target] != row[alias]:
                raise ValueError(f"conflicting schema aliases: {target}/{alias}")
            if target not in row and alias in row:
                row[target] = row[alias]
        canonical.append(row)
    return canonical


def index_rows(rows):
    if not rows:
        raise ValueError("empty population")
    indexed = {}
    for row in rows:
        key = row["task_id"]
        if key in indexed:
            raise ValueError(f"duplicate task_id: {key}")
        if not isinstance(key, str) or not key:
            raise ValueError("invalid task_id")
        if not isinstance(row.get("gold_answer"), str):
            raise ValueError(f"missing/non-string gold_answer: {key}")
        indexed[key] = row
    return indexed


def align_rows(left, right):
    """Fail closed: no intersection pairing or normalized-away label mismatch."""
    a, b = index_rows(left), index_rows(right)
    if a.keys() != b.keys():
        raise ValueError("unequal ID populations")
    pairs = []
    for key, row in a.items():
        if row["gold_answer"] != b[key]["gold_answer"]:
            raise ValueError(f"gold mismatch: {key}")
        if "question" in row and "question" in b[key] and row["question"] != b[key]["question"]:
            raise ValueError(f"question mismatch: {key}")
        pairs.append((row, b[key]))
    return pairs


class _WithoutDocstrings(ast.NodeTransformer):
    def generic_visit(self, node):
        super().generic_visit(node)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body.pop(0)
        return node


def source_comparison(current: Path, snapshot: Path):
    a = current.read_text(encoding="utf-8-sig")
    b = snapshot.read_text(encoding="utf-8-sig")
    at = _WithoutDocstrings().visit(ast.parse(a))
    bt = _WithoutDocstrings().visit(ast.parse(b))
    dump = lambda tree: ast.dump(tree, include_attributes=False)
    def functions(tree):
        found = {}
        def visit(node, prefix=""):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    key = prefix + child.name
                    if not isinstance(child, ast.ClassDef):
                        found[key] = dump(child)
                    visit(child, key + ".")
                else:
                    visit(child, prefix)
        visit(tree)
        return found
    af, bf = functions(at), functions(bt)
    return {"byte_equal": current.read_bytes() == snapshot.read_bytes(),
            "normalized_text_equal": a == b,
            "normalized_ast_equal": dump(at) == dump(bt),
            "changed_functions": [n for n in sorted(af.keys() | bf.keys()) if af.get(n) != bf.get(n)],
            "normalized_source_diff": list(difflib.unified_diff(ast.unparse(bt).splitlines(), ast.unparse(at).splitlines(), fromfile="submitted_snapshot", tofile="current", n=1)),
            "boundary": "AST comparison ignores BOM, line endings, comments and docstrings. Ignoring docstrings is a diagnostic assumption: Python can inspect __doc__, so this does not establish all observational equivalence. Structural differences are not a proof of changed numerical behavior or experiment-time runtime identity."}


def load_official_hotpot(path: Path):
    if sha256(path) != OFFICIAL_SHA256:
        raise ValueError("official scorer hash mismatch; review changed source before execution")
    source = ast.parse(path.read_text(encoding="utf-8-sig"))
    names = {"normalize_answer", "f1_score", "exact_match_score"}
    selected = [n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in selected} != names:
        raise ValueError("official scorer function set mismatch")
    namespace = {"re": re, "string": string, "Counter": Counter}
    # Execute only the three reviewed, hash-pinned pure scoring definitions.
    # Imports, pickle/CLI and all other downloaded code are excluded.
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)
    return namespace


def project_f1(prediction: str, gold: str) -> float:
    def normalize(text):
        text = re.sub(r"\b(a|an|the)\b", " ", text.lower())
        return text.translate(str.maketrans("", "", string.punctuation)).split()
    a, b = normalize(prediction), normalize(gold)
    common = sum((Counter(a) & Counter(b)).values())
    return 2 * common / (len(a) + len(b)) if common and a and b else 0.0


def summarize_scores(rows, official=None):
    index_rows(rows)
    values = [project_f1(r["final_answer"], r["gold_answer"]) for r in rows]
    if any(abs(value - row["answer_f1"]) > 1e-10 for value, row in zip(values, rows)):
        raise ValueError("stored project F1 mismatch")
    result = {"n": len(rows), "project_f1": mean(values), "stored_project_f1_reproduced": True}
    if official:
        f1 = [official["f1_score"](r["final_answer"], r["gold_answer"])[0] for r in rows]
        em = [float(official["exact_match_score"](r["final_answer"], r["gold_answer"])) for r in rows]
        result.update(official_answer_f1=mean(f1), official_answer_em=mean(em),
                      changed_f1_rows=[{"task_id": r["task_id"], "project_f1": p, "official_f1": f}
                                       for r, p, f in zip(rows, values, f1) if abs(p-f) > 1e-12])
    return result


def audit_acceptance_conflicts(traces):
    conflicts = []
    for row in traces:
        audit = row.get("routing_features", {}).get("edo_stage2_audit_decision")
        if audit in {"REJECT_REROUTE", "REJECT_RESPLIT"} and row.get("decision") == "accept":
            conflicts.append({"task_id": row["task_id"], "hop_index": row["hop_index"],
                              "audit": audit, "decision": row["decision"],
                              "chosen_target": row.get("chosen_target", "")})
    return conflicts


def token_fallback_counterexample(usage):
    prompt = completion = legacy = per_event = 0
    for row in usage:
        p, c = int(row.get("prompt_tokens") or 0), int(row.get("completion_tokens") or 0)
        prompt += p
        completion += c
        total = row.get("total_tokens")
        legacy += int(total) if total is not None else prompt + completion
        per_event += int(total) if total is not None else p + c
    return {"legacy_cumulative_fallback": legacy, "per_event_sum": per_event,
            "boundary": "Synthetic reproduction of inspected arithmetic, not a correction to historical totals; missing all usage remains unknown."}


def line_evidence(path: Path, needles):
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    result = {}
    for needle in needles:
        found = [{"line": i+1, "text": line.strip()} for i, line in enumerate(lines)
                 if " ".join(needle.split()) in " ".join(line.split())]
        if not found:
            raise ValueError(f"source anchor not found: {needle}")
        result[needle] = found
    return result


def build_report(root: Path):
    inputs = {}
    def record(path):
        path = path.resolve()
        rel = path.relative_to(root).as_posix()
        inputs[rel] = {"path": rel, "sha256": sha256(path), "bytes": path.stat().st_size}
        return rel
    def load(path, jsonl=False):
        record(path)
        return read_jsonl(path) if jsonl else read_json(path)
    official_path = root / OFFICIAL_REL
    record(official_path)
    official = load_official_hotpot(official_path)
    comparisons = []
    for name in ("runner.py", "methods.py", "evaluation.py"):
        current, snapshot = root / "workspace/idea04_core" / name, root / SNAPSHOT / name
        comparisons.append({"file": name, "current": record(current), "submitted_snapshot": record(snapshot),
                            **source_comparison(current, snapshot)})

    headline = []
    for dataset, stem, subdir, archive, comparison, expected_n in JOBS:
        run = root / "artifacts/emergence" / stem
        rows = load(run / subdir / "parsed_predictions.jsonl", True)
        if len(rows) != expected_n:
            raise ValueError(f"{dataset}: unexpected population")
        archive_path = run / archive
        prior = next(r for r in load(archive_path)["rows"] if r["comparison"] == comparison)
        baseline = root / prior["baseline_dir"].split("/idea04/", 1)[1] / "parsed_predictions.jsonl"
        item = {"dataset": dataset, "method": summarize_scores(rows, official if dataset == "HotpotQA" else None),
                "comparison": comparison, "baseline_expected_path": baseline.relative_to(root).as_posix(),
                "archived_project_delta": prior.get("delta_f1", prior.get("mean_delta_f1")),
                "archived_ci95": prior.get("f1_ci95", [prior.get("ci95_low_f1"), prior.get("ci95_high_f1")]),
                "ci_boundary": "Archived CI only; not newly estimated or corrected for historical selection."}
        if baseline.is_file():
            original_baseline = load(baseline, True)
            other = canonicalize_rows(original_baseline)
            pairs = align_rows(rows, other)
            delta = mean(a["answer_f1"]-b["answer_f1"] for a, b in pairs)
            if abs(delta-item["archived_project_delta"]) > 1e-10:
                raise ValueError(f"{dataset}: paired delta mismatch")
            item.update(pairing="exact_ids_gold_and_available_questions_match", paired_n=len(pairs),
                        recomputed_project_delta=delta, baseline=summarize_scores(other, official if dataset == "HotpotQA" else None),
                        baseline_schema_aliases={"answer_gold": "gold_answer", "answer_pred": "final_answer"} if "answer_gold" in original_baseline[0] else {})
        else:
            item.update(pairing="unavailable_at_recorded_path", paired_n=None,
                        official_paired_delta=None)
        headline.append(item)

    components = []
    for model, stem in (("Qwen2.5-3B", "e432_qwen_hotpotqa_component_matrix_20260524"),
                        ("Phi-4-mini", "e433_phi4_hotpotqa_component_matrix_20260524")):
        directory = root / "artifacts/emergence" / stem
        summary = load(directory / "e432_component_matrix_summary.json")
        row_cache = {}
        output = {"backbone": model, "rows": [], "boundary": "Historical single-seed development component evidence; official answer rescoring does not correct adaptive selection or recover missing call attempts."}
        for row in summary["rows"]:
            run = root / row["run_dir"]
            rows = load(run / "parsed_predictions.jsonl", True)
            if len(rows) != row["sample_count"]:
                raise ValueError("component population mismatch")
            score = summarize_scores(rows, official)
            if abs(score["project_f1"] - row["answer_f1"]) > 0.000051:
                raise ValueError("component summary mismatch")
            row_cache[row["label"]] = rows
            result = {"label": row["label"], **score, "archived_comparisons": row["comparisons"]}
            raw = run / "raw_model_outputs.jsonl"
            if raw.exists():
                usage = [u for event in load(raw, True) for u in event.get("usage_calls", [])]
                result["observed_usage_records"] = len(usage)
                result["usage_records_missing_total_tokens"] = sum(u.get("total_tokens") is None for u in usage)
            else:
                result["observed_usage_records"] = None
            output["rows"].append(result)
        output["full_minus_controls"] = []
        for label in ("stage2_chain", "frame_no_memory", "frame_all_tools", "frame_random_tools", "frame_no_tool_history"):
            paired = align_rows(row_cache["frame_full"], row_cache[label])
            full_comparisons = next(r for r in output["rows"] if r["label"] == "frame_full")["archived_comparisons"]
            direct_key = f"vs_{label}_f1"
            direct = direct_key in full_comparisons
            archived = full_comparisons[direct_key] if direct else next(r for r in output["rows"] if r["label"] == label)["archived_comparisons"]["vs_frame_full_f1"]
            difference = mean(a["answer_f1"]-b["answer_f1"] for a,b in paired)
            if abs(difference - (archived["mean"] if direct else -archived["mean"])) > 1e-10:
                raise ValueError("archived component contrast mismatch")
            output["full_minus_controls"].append({"control": label, "paired_n": len(paired),
                "project_delta": difference, "archived_project_ci95": archived["ci95"] if direct else [-archived["ci95"][1], -archived["ci95"][0]],
                "archived_ci_source": f"frame_full/{direct_key}" if direct else f"{label}/vs_frame_full_f1 (sign reversed)",
                "ci_boundary": "Archived interval; not a new bootstrap or selection correction. Independently bootstrapped opposite directions can differ slightly.",
                "official_answer_delta": mean(official["f1_score"](a["final_answer"], a["gold_answer"])[0] - official["f1_score"](b["final_answer"], b["gold_answer"])[0] for a,b in paired)})
        components.append(output)

    runner = root / "workspace/idea04_core/runner.py"
    methods = root / "workspace/idea04_core/methods.py"
    method_ast = ast.parse(methods.read_text(encoding="utf-8-sig"))
    method_function = next(n for n in method_ast.body if isinstance(n, ast.FunctionDef) and n.name == "run_method_step")
    unused = {name: {"signature_line": method_function.lineno,
                     "load_references_in_function": sum(isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id == name for n in ast.walk(method_function))}
              for name in ("gold_answer", "answer_f1_feedback")}
    static = {"runner": record(runner), "methods": record(methods), "method_arguments": unused,
              "runner_locations": line_evidence(runner, ["_STATEFUL_METHODS =", "gold_answer=gold_answer", "after_val = apply_peer_post_sample_competence(prev_self, pred[\"answer_f1\"])", "if pred[\"answer_f1\"] > 0.0:", "for future in as_completed(future_map):", "for p in sorted(", "st += int(tt) if tt is not None else sp + sc"]),
              "method_locations": line_evidence(methods, ["def _adaptive_protocol_choice(", "if hint in {\"2wiki\", \"2wikimultihopqa\"} or q_type == \"comparison\":"]),
              "findings": ["Gold-derived answer_f1 updates the fixed_peer_calibrated historical baseline; this is not evidence that headline adaptive policies read gold.", "The runner's consecutive-zero-F1 stopping rule reads evaluator labels.", "Gold arguments exist but have zero Load references in run_method_step; this limited check does not prove global noninterference.", "Completion-order concurrent updates differ from original-input-order resume replay; no replay-equivalence guarantee follows from locks.", "Primary adaptive routes rebuild state per task and use dataset/question heuristics. Existing self-calibrated state updates require further behavioral audit."],
              "boundary": "Source facts about inspected current checkout; not a dynamic taint analysis or proof about original experiment-time code."}
    trace_path = root / "artifacts/analysis/s518_aamas_audit_20260916/worked_failure_trace.json"
    trace = load(trace_path)
    conflicts = audit_acceptance_conflicts(trace["routing_traces.jsonl"])
    failure = {"source": record(trace_path), "conflicts": conflicts,
               "predictions": trace["parsed_predictions.jsonl"],
               "boundary": "One stored trajectory: rejection audit co-occurs with terminal acceptance and a wrong final answer. Rejection targets the prior contribution; this demonstrates the logged mismatch, not a population failure rate or complete causal replay."}
    appendix = root / "article/latex/edo_appendix_content.tex"
    record(appendix)
    appendix_rows = line_evidence(appendix, ["Phi-4 HotpotQA & full EDO", "neutral controls; Phi-4"])
    for code in (Path(__file__), Path(__file__).parents[1] / "tests/test_aamas_forensics.py"):
        record(code)
    return {"task": "A-T02", "kind": "offline_historical_forensics", "model_calls": 0, "network_calls": 0,
            "counts": {"headline_method_rows": sum(r["method"]["n"] for r in headline), "available_headline_baseline_rows": sum(r.get("paired_n") or 0 for r in headline), "component_rows": sum(r["n"] for model in components for r in model["rows"])},
            "source_comparisons": comparisons, "official_hotpot_scorer": {"source": OFFICIAL_REL, "sha256": OFFICIAL_SHA256, "scope": "Answer F1/EM only; support-fact/joint metrics not evaluated."},
            "headline": headline, "components": components, "static_control_findings": static,
            "audit_trace": failure, "token_fallback_counterexample": token_fallback_counterexample([{"prompt_tokens": 100, "completion_tokens": 20}, {"prompt_tokens": 50, "completion_tokens": 10}]),
            "historical_phi4_appendix_lines": appendix_rows,
            "repository_boundary": "codes/evidence_tools is currently in the flattened parent checkout; no nested Git history asserted or initialized.",
            "remaining_limits": ["No historical runtime identity established from submitted-source snapshots.", "HotpotQA direct full-validation comparator missing at archived reference path; no official paired headline delta.", "MuSiQue/2Wiki official native scorer parity and data population provenance remain open.", "Historical selection/development exposure is not removed by rescoring; no confirmatory evidence generated.", "No new protocol implementation, label-isolation proof, cost-fairness certification, or new model evaluation."],
            "inputs": sorted(inputs.values(), key=lambda r:r["path"])}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    report = build_report(root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    destination = args.output_dir / "report.json"
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({"report": str(destination.resolve()), "headline_rows": sum(r["method"]["n"] for r in report["headline"]), "component_rows": sum(r["n"] for model in report["components"] for r in model["rows"]), "hashed_inputs": len(report["inputs"]), "model_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
