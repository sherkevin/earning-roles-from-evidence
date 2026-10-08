"""Explicit v1 runtime qualification for the PIPE2 derived candidate root.

The pinned runtime qualification remains available unchanged as v2.  This
wrapper patches only its material loader and version labels, so the same
parent-side responsibility/adoption checks and already-qualified sandbox are
applied to the CSV-writer-derived bytes.  It is still engineering evidence:
zero LLM calls, no native grader, no GPU, and no benchmark or efficacy claim.
"""

from __future__ import annotations

import sys
import json

import peerrolebench_pipe2_runtime_qualification as pinned_runner
from peerrolebench_pipe2_derived_material_adapter import load_derived_pipe2
from peerrolebench_pipe2_derived_material_adapter import RECIPE_PATH


pinned_runner.load_pipe2 = load_derived_pipe2
pinned_runner.RUNNER_VERSION = "pipe2-derived-runtime-adoption-qualification-v1"
pinned_runner.SCHEMA_VERSION = "pipe2-derived-runtime-result-v1"
pinned_runner.MATERIAL_ADAPTER = "peerrolebench_pipe2_derived_material_adapter"
pinned_runner.MATERIAL_ROOT_DIGEST = json.loads(
    RECIPE_PATH.read_text(encoding="utf-8"))["root_digest"]


if __name__ == "__main__":
    raise SystemExit(pinned_runner.main())
