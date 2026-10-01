"""Public PIPE2 runtime driver used inside the qualified sandbox.

The worker receives only public CSV rows or a public delivery artifact.  It
contains no expected output, tests, labels, or scorer logic.  The parent keeps
those values outside the worker and evaluates the returned artifact.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import json
from pathlib import Path
import sys


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _extract(source: Path, request: dict) -> dict:
    csv_text = request["csv_text"]
    if not isinstance(csv_text, str) or len(csv_text.encode()) > 64 * 1024:
        raise ValueError("csv_text exceeds public input limit")
    input_path = source.parent / "scratch" / "source.csv"
    input_path.write_text(csv_text, encoding="utf-8")
    module = _load(source / "pipeline" / "extract.py", "pipe2_candidate_extract")
    rows = module.extract(str(input_path))
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise TypeError("extract must return a list of dictionaries")
    return {"rows": rows, "source_path": "pipeline/extract.py"}


def _transform_load(source: Path, request: dict) -> dict:
    artifact = request["artifact"]
    if not isinstance(artifact, dict) or artifact.get("schema") != "pipe2-extracted-rows-v1":
        raise ValueError("recipient requires a sealed PIPE2 artifact")
    rows = artifact["rows"]
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise TypeError("rows must be a list of dictionaries")
    if len(json.dumps(rows, ensure_ascii=False)) > 64 * 1024:
        raise ValueError("rows exceed public input limit")
    transform = _load(source / "pipeline" / "transform.py", "pipe2_candidate_transform")
    load = _load(source / "pipeline" / "load.py", "pipe2_candidate_load")
    transformed = transform.transform(rows)
    if not isinstance(transformed, list) or any(not isinstance(row, dict) for row in transformed):
        raise TypeError("transform must return a list of dictionaries")
    output_path = source.parent / "scratch" / "output.csv"
    load.load(transformed, str(output_path))
    output_text = output_path.read_text(encoding="utf-8")
    # Parse in the worker only to make malformed CSV an explicit transport
    # failure.  The parent still performs the authoritative comparison.
    parsed = list(csv.DictReader(io.StringIO(output_text)))
    return {"output_csv": output_text, "parsed_rows": parsed,
            "source_paths": ["pipeline/transform.py", "pipeline/load.py"]}


def main() -> None:
    source = Path(sys.argv[1]).resolve()
    for line in sys.stdin:
        try:
            request = json.loads(line)
            op = request["op"]
            if op == "extract":
                value = _extract(source, request)
            elif op == "transform_load":
                value = _transform_load(source, request)
            else:
                raise ValueError("unknown PIPE2 operation: " + str(op))
            answer = {"ok": True, "value": value}
        except Exception as exc:
            answer = {"ok": False, "error_type": type(exc).__name__, "message": str(exc),
                      "errno": getattr(exc, "errno", None)}
        print(json.dumps(answer, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
