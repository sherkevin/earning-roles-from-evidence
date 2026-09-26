"""Decode a recorded real SSE response and reject interrupted transports."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from peerrolebench_real_closed_loop import parse_sse

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "experiments/logs/n02_stream_transport_health_20260926/response.sse"


def test_recorded_real_sse_text_usage_and_model():
    result = parse_sse(RAW.read_text())
    assert result["content"] == [{"type": "text", "text": "OK"}]
    assert result["usage"]["input_tokens"] == 66
    assert result["usage"]["output_tokens"] == 25
    assert result["final_usage_observed"] is True
    assert result["model"] == "qwen3.8-max"
    assert result["stop_reason"] == "end_turn"


def test_incomplete_stream_cannot_be_success():
    raw = RAW.read_text()
    frames = [frame for frame in raw.split("\n\n") if '"type":"message_stop"' not in frame.replace(" ", "")]
    with pytest.raises(ValueError, match="Incomplete"):
        parse_sse("\n\n".join(frames))


def test_provider_error_is_not_empty_success():
    with pytest.raises(RuntimeError, match="Provider stream error"):
        parse_sse('data: ' + json.dumps({"type": "error", "error": {"type": "overloaded_error"}}) + '\n\n')


def test_provisional_zero_usage_not_claimed_as_final():
    raw = RAW.read_text()
    frames = [frame for frame in raw.split("\n\n") if '"type":"message_delta"' not in frame.replace(" ", "")]
    result = parse_sse("\n\n".join(frames))
    assert not result["final_usage_observed"]
