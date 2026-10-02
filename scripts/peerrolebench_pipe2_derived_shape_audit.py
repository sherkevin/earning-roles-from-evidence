"""Run the existing PIPE2 shape audit against the explicit derived loader."""

from __future__ import annotations

import peerrolebench_pipe2_fixture_shape_audit as pinned_audit
from peerrolebench_pipe2_derived_material_adapter import RECIPE_PATH, load_derived_pipe2
import json


pinned_audit.load_pipe2 = load_derived_pipe2
pinned_audit.RUNNER_VERSION = "pipe2-derived-fixture-shape-audit-v1"
pinned_audit.MATERIAL_ROOT_DIGEST = json.loads(
    RECIPE_PATH.read_text(encoding="utf-8"))["root_digest"]


if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    args = parser.parse_args()
    result = pinned_audit.run(args.output, args.seeds)
    print(json.dumps({key: result[key] for key in (
        "status", "valid_seeds", "invalid_seeds", "public_invalid_count",
        "hidden_invalid_count")}, indent=2))
