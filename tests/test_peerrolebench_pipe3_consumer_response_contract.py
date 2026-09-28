from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from peerrolebench_pipe3_consumer_response_contract import extract_consumer_sources


PATHS = ["processor.py", "models.py", "sink.py", "producer.py"]
FILES = {path: "source" for path in PATHS}


def test_exact_envelope_is_accepted():
    assert extract_consumer_sources({"source_files": FILES}, PATHS) == FILES


@pytest.mark.parametrize("payload", [
    FILES,
    {"source_files": FILES, "rationale": "x"},
    {"source_files": {"processor.py": "source"}},
])
def test_non_exact_envelope_is_rejected(payload):
    with pytest.raises(ValueError):
        extract_consumer_sources(payload, PATHS)
