from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_material_payload_runtime_preflight import sandbox_sources  # noqa: E402


def test_sandbox_source_mapping_keeps_mqueue_paths_and_namespaces_other_roots():
    mapped = sandbox_sources({"producer.py": "x", "mqueue/queue.py": "y"})
    assert mapped == {"mqueue/payload/producer.py": "x", "mqueue/queue.py": "y"}
