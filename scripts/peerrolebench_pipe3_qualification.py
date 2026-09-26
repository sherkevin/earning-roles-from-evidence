#!/usr/bin/env python3
"""Parent-side PIPE3 attribution qualification.

This is a deterministic scorer smoke test, not an agent experiment.  It
generates one fixed TeamBench instance and evaluates four controlled source
variants to check that producer quality, recipient-owned processing, and final
sink adoption are separable.  No LLM, GPU, network, pytest, or TeamBench
native grader is used.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_workspace(files, root: Path):
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")


def datetime_field(models_path: Path) -> str:
    tree = ast.parse(models_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            annotation = ast.unparse(node.annotation) if hasattr(ast, "unparse") else ""
            if annotation == "datetime" or annotation.endswith(".datetime"):
                return node.target.id
    raise RuntimeError("could not identify datetime field")


def id_field(models_path: Path) -> str:
    tree = ast.parse(models_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and any(isinstance(x, ast.Name) and x.id == "dataclass" for x in node.decorator_list):
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if "id" in item.target.id.lower():
                        return item.target.id
    return "event_id"


def patch_producer(root: Path):
    path = root / "producer.py"
    source = path.read_text(encoding="utf-8")
    ts = datetime_field(root / "models.py")
    old = "    return json.dumps(data, default=str)"
    new = "    data[\"%s\"] = event.%s.isoformat()\n    return json.dumps(data)" % (ts, ts)
    if old not in source:
        raise RuntimeError("producer patch anchor not found")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def patch_processor(root: Path):
    path = root / "processor.py"
    source = path.read_text(encoding="utf-8")
    source = source.replace('open(output_path, "w", encoding="latin-1")', 'open(output_path, "w", encoding="utf-8")', 1)
    old = '            envelope = {"data": processed}\n            fout.write(json.dumps(envelope, ensure_ascii=False) + "\\n")'
    new = '            fout.write(json.dumps(processed, ensure_ascii=False) + "\\n")'
    if old not in source:
        raise RuntimeError("processor envelope patch anchor not found")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def fresh_import(module_names, root: Path):
    for name in module_names:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(root))
    try:
        return [importlib.import_module(name) for name in module_names]
    finally:
        try:
            sys.path.remove(str(root))
        except ValueError:
            pass


def producer_quality(root: Path):
    producer, models = fresh_import(["producer", "models"], root)
    classes = [obj for obj in vars(models).values() if isinstance(obj, type) and hasattr(obj, "__dataclass_fields__")]
    if not classes:
        raise RuntimeError("no generated dataclass")
    cls = classes[0]
    ts = datetime_field(root / "models.py")
    fields = {}
    for name in cls.__dataclass_fields__:
        if name == ts:
            from datetime import datetime
            fields[name] = datetime(2023, 11, 14, 22, 13, 20)
        elif "id" in name.lower():
            fields[name] = "evt-001"
        else:
            fields[name] = "sample"
    raw = producer.serialize_event(cls(**fields))
    data = json.loads(raw)
    timestamp = data[ts]
    return {
        "pass": isinstance(timestamp, str) and "T" in timestamp and " " not in timestamp,
        "timestamp": timestamp,
        "keys": sorted(data.keys()),
    }


def recipient_own_work(root: Path):
    producer, processor, sink, models = fresh_import(["producer", "processor", "sink", "models"], root)
    classes = [obj for obj in vars(models).values() if isinstance(obj, type) and hasattr(obj, "__dataclass_fields__")]
    cls = classes[0]
    ts = datetime_field(root / "models.py")
    identifier = id_field(root / "models.py")
    fields = {}
    for name in cls.__dataclass_fields__:
        if name == ts:
            fields[name] = "2023-11-14T22:13:20"
        elif name == identifier or "id" in name.lower():
            fields[name] = "evt-canonical"
        elif "user" in name.lower() or "name" in name.lower():
            fields[name] = "Müller"
        elif "value" in name.lower() or "amount" in name.lower():
            fields[name] = "Price: €99.99"
        else:
            fields[name] = "sample"
    source = root / "canonical.jsonl"
    target = root / "recipient.jsonl"
    source.write_text(json.dumps(fields, ensure_ascii=False) + "\n", encoding="utf-8")
    processor.process_events(str(source), str(target))
    loaded = sink.load_processed_events(str(target))
    return {
        "pass": len(loaded) == 1 and loaded[0].get(identifier) == "evt-canonical" and "Müller" in json.dumps(loaded, ensure_ascii=False),
        "loaded_count": len(loaded),
        "loaded": loaded,
    }


def pipeline_adoption(root: Path):
    producer, processor, sink, models = fresh_import(["producer", "processor", "sink", "models"], root)
    classes = [obj for obj in vars(models).values() if isinstance(obj, type) and hasattr(obj, "__dataclass_fields__")]
    cls = classes[0]
    ts = datetime_field(root / "models.py")
    fields = {}
    for name in cls.__dataclass_fields__:
        if name == ts:
            from datetime import datetime
            fields[name] = datetime(2023, 11, 14, 22, 13, 20)
        elif "id" in name.lower():
            fields[name] = "evt-pipeline"
        elif "user" in name.lower() or "name" in name.lower():
            fields[name] = "Müller"
        elif "value" in name.lower() or "amount" in name.lower():
            fields[name] = "Price: €99.99"
        else:
            fields[name] = "sample"
    from datetime import datetime
    event = cls(**fields)
    produced = root / "produced.jsonl"
    processed = root / "processed.jsonl"
    producer.produce_events([event], str(produced))
    # The task contract explicitly requires a T-separated ISO timestamp.  The
    # Python runtime accepts a space here, so this boundary check must happen
    # before processor parsing; otherwise an upstream contract violation is
    # silently masked by datetime.fromisoformat().
    first_line = produced.read_text(encoding="utf-8").splitlines()[0]
    serialized = json.loads(first_line)
    ts = datetime_field(root / "models.py")
    if not isinstance(serialized.get(ts), str) or "T" not in serialized[ts] or " " in serialized[ts]:
        return {
            "pass": False,
            "reason": "producer_boundary_contract_rejected",
            "timestamp": serialized.get(ts),
        }
    processor.process_events(str(produced), str(processed))
    loaded = sink.load_processed_events(str(processed))
    return {"pass": len(loaded) == 1, "loaded_count": len(loaded)}


def changed_files(root: Path, baseline):
    result = []
    for rel, before in baseline.items():
        path = root / rel
        after = sha256(path)
        if after != before:
            result.append(rel)
    return sorted(result)


def run_variant(generated, name: str, patches, tmp_root: Path):
    root = tmp_root / name
    root.mkdir(parents=True)
    write_workspace(generated.workspace_files, root)
    baseline = {rel: sha256(root / rel) for rel in ("producer.py", "processor.py", "sink.py", "models.py")}
    for patch in patches:
        patch(root)
    record = {"variant": name, "changed_files": changed_files(root, baseline)}
    try:
        record["producer_quality"] = producer_quality(root)
    except Exception as exc:
        record["producer_quality"] = {"pass": False, "error": repr(exc)}
    try:
        record["recipient_own_work"] = recipient_own_work(root)
    except Exception as exc:
        record["recipient_own_work"] = {"pass": False, "error": repr(exc)}
    try:
        record["pipeline_adoption"] = pipeline_adoption(root)
    except Exception as exc:
        record["pipeline_adoption"] = {"pass": False, "error": repr(exc)}
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--teambench", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    repo = args.teambench.resolve()
    sys.path.insert(0, str(repo))
    from generators.gen_pipe3_stream_processing import Generator
    generated = Generator().generate(args.seed)
    generated_hashes = {}
    for rel, content in generated.workspace_files.items():
        data = content if isinstance(content, bytes) else content.encode("utf-8")
        generated_hashes[rel] = hashlib.sha256(data).hexdigest()
    config = {
        "experiment_id": args.output_dir.name,
        "source_commit": subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(),
        "task_id": generated.task_id,
        "seed": args.seed,
        "scientific_claim_allowed": False,
        "candidate_execution": False,
        "llm_calls": 0,
        "gpu_jobs": 0,
        "network": False,
        "native_grader": False,
        "variants": ["baseline", "producer_only", "recipient_only", "both"],
        "generated_workspace_sha256": generated_hashes,
    }
    (args.output_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")
    with tempfile.TemporaryDirectory(prefix="pipe3_qualification_") as temp:
        tmp_root = Path(temp)
        variants = [
            ("baseline", []),
            ("producer_only", [patch_producer]),
            ("recipient_only", [patch_processor]),
            ("both", [patch_producer, patch_processor]),
        ]
        records = []
        raw_path = args.output_dir / "raw.jsonl"
        with raw_path.open("w", encoding="utf-8") as raw_handle:
            for name, patches in variants:
                started = time.time()
                record = run_variant(generated, name, patches, tmp_root)
                record["wall_seconds"] = round(time.time() - started, 6)
                raw_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
                raw_handle.flush()
                records.append(record)
    matrix = []
    for record in records:
        matrix.append({
            "variant": record["variant"],
            "changed_files": record["changed_files"],
            "producer_quality": bool(record.get("producer_quality", {}).get("pass")),
            "recipient_own_work": bool(record.get("recipient_own_work", {}).get("pass")),
            "pipeline_adoption": bool(record.get("pipeline_adoption", {}).get("pass")),
        })
    expected = [
        {"variant": "baseline", "producer_quality": False, "recipient_own_work": False, "pipeline_adoption": False},
        {"variant": "producer_only", "producer_quality": True, "recipient_own_work": False, "pipeline_adoption": False},
        {"variant": "recipient_only", "producer_quality": False, "recipient_own_work": True, "pipeline_adoption": False},
        {"variant": "both", "producer_quality": True, "recipient_own_work": True, "pipeline_adoption": True},
    ]
    passed = matrix == [{**item, "changed_files": matrix[i]["changed_files"]} for i, item in enumerate(expected)]
    summary = {
        **config,
        "status": "pass" if passed else "fail",
        "matrix": matrix,
        "expected_boolean_matrix": expected,
        "attribution_separable": passed,
        "interpretation": (
            "PIPE3 remains a candidate only: the parent probes separate producer quality, recipient work, and final adoption."
            if passed else
            "PIPE3 is not qualified: at least one control conflates producer quality, recipient work, or final adoption."
        ),
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": summary["status"], "matrix": matrix, "attribution_separable": passed}, ensure_ascii=False, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
