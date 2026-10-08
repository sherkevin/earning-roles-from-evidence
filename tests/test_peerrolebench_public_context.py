"""Software-stub checks only; these do not test model quality or public provenance."""

from __future__ import annotations

import json
import hashlib
import math
from pathlib import Path
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from peerrolebench_public_context import encode_public_context, restore_public_context  # noqa: E402


class TokenizerStub:
    def __init__(self):
        self.calls = []

    def encode(self, text, *, add_special_tokens, truncation):
        assert add_special_tokens is True and truncation is False
        self.calls.append(text)
        return list(range(len(text.split()) + 2))


class EncoderStub:
    max_seq_length = 8

    def __init__(self, values=None):
        self.values = [[3.0, 0.0], [0.0, 4.0]] if values is None else values
        self.calls = []

    def encode(self, texts, *, normalize_embeddings):
        assert normalize_embeddings is True
        self.calls.append(list(texts))
        return self.values


def _encode(**overrides):
    arguments = dict(
        task_contract="public task text", recipient_contract="recipient public duty",
        recipient_id="peer-a", declared_recipient_version="recipient-v1", read_cut=4,
        tokenizer=TokenizerStub(), encoder=EncoderStub(), encoder_version="frozen-model-rev",
        max_seq_length=8,
    )
    arguments.update(overrides)
    return encode_public_context(**arguments)


def _reseal(receipt):
    body = {key: value for key, value in receipt.items() if key != "payload_digest"}
    receipt["payload_digest"] = hashlib.sha256(json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()
    return receipt


def test_full_text_receipt_roundtrip_and_equal_weight_geometry():
    tokenizer, encoder = TokenizerStub(), EncoderStub()
    vector, receipt = _encode(tokenizer=tokenizer, encoder=encoder)
    radius = 1.0 - 1e-12
    np.testing.assert_allclose(vector, [radius / math.sqrt(2), 0, 0, radius / math.sqrt(2)])
    assert encoder.calls == [["public task text", "recipient public duty"]]
    assert tokenizer.calls == ["public task text", "recipient public duty"]
    assert receipt["token_counts"] == {"task_contract": 5, "recipient_contract": 5}
    assert receipt["task_contract"] == "public task text"
    restored = restore_public_context(json.loads(json.dumps(receipt)),
                                      expected_payload_digest=receipt["payload_digest"], read_cut=4,
                                      recipient_id="peer-a", declared_recipient_version="recipient-v1",
                                      encoder_version="frozen-model-rev")
    assert restored == vector


@pytest.mark.parametrize("field", ["task_contract", "recipient_contract"])
def test_overlength_contract_is_rejected_before_encoder(field):
    encoder = EncoderStub()
    with pytest.raises(ValueError, match="max_seq_length"):
        _encode(encoder=encoder, **{field: "one two three four five six seven"})
    assert encoder.calls == []


@pytest.mark.parametrize("values", [
    [[1.0, 0.0]],
    [[1.0], [1.0, 2.0]],
    [[float("nan"), 0.0], [0.0, 1.0]],
    [[0.0, 0.0], [0.0, 1.0]],
    [[float("inf"), 0.0], [0.0, 1.0]],
])
def test_invalid_encoder_shape_or_values_are_rejected(values):
    with pytest.raises(ValueError):
        _encode(encoder=EncoderStub(values))


def test_tamper_and_identity_mismatch_are_rejected():
    vector, receipt = _encode()
    changed = json.loads(json.dumps(receipt))
    changed["vector"][0] = 0.25
    with pytest.raises(ValueError, match="digest"):
        restore_public_context(changed, expected_payload_digest=receipt["payload_digest"],
                               read_cut=4, recipient_id="peer-a",
                               declared_recipient_version="recipient-v1")
    for kwargs in ({"read_cut": 5, "recipient_id": "peer-a", "declared_recipient_version": "recipient-v1"},
                   {"read_cut": 4, "recipient_id": "peer-b", "declared_recipient_version": "recipient-v1"},
                   {"read_cut": 4, "recipient_id": "peer-a", "declared_recipient_version": "recipient-v2"}):
        with pytest.raises(ValueError, match="identity or read cut"):
            restore_public_context(receipt, expected_payload_digest=receipt["payload_digest"], **kwargs)
    assert restore_public_context(receipt, expected_payload_digest=receipt["payload_digest"],
                                  read_cut=4, recipient_id="peer-a",
                                  declared_recipient_version="recipient-v1") == vector


def test_another_valid_task_receipt_cannot_replace_sealed_task_context():
    _, original = _encode(task_contract="public task alpha")
    _, other = _encode(task_contract="public task beta")
    with pytest.raises(ValueError, match="digest"):
        restore_public_context(other, expected_payload_digest=original["payload_digest"],
                               read_cut=4, recipient_id="peer-a",
                               declared_recipient_version="recipient-v1")


@pytest.mark.parametrize("field,value", [
    ("task_contract", " "), ("recipient_contract", ""), ("encoder_version", ""),
    ("read_cut", True), ("read_cut", -1), ("max_seq_length", 0),
    ("token_counts", {"task_contract": True, "recipient_contract": 5}),
    ("token_counts", {"task_contract": 9, "recipient_contract": 5}),
    ("vector", [2.0, 0.0, 0.0, 0.0]),
])
def test_self_consistent_receipt_with_invalid_bounds_or_content_is_rejected(field, value):
    _, original = _encode()
    changed = json.loads(json.dumps(original))
    changed[field] = value
    _reseal(changed)
    with pytest.raises(ValueError):
        restore_public_context(changed, expected_payload_digest=changed["payload_digest"],
                               read_cut=4, recipient_id="peer-a",
                               declared_recipient_version="recipient-v1")


def test_opaque_identity_and_declared_version_do_not_enter_semantic_encoder_input():
    left_encoder, right_encoder = EncoderStub(), EncoderStub()
    left, left_receipt = _encode(encoder=left_encoder)
    right, right_receipt = _encode(encoder=right_encoder, recipient_id="opaque-other",
                                  declared_recipient_version="revision-other", read_cut=9)
    assert left == right
    assert left_encoder.calls == right_encoder.calls
    assert left_receipt["payload_digest"] != right_receipt["payload_digest"]


def test_declared_limit_must_match_injected_encoder():
    encoder = EncoderStub()
    with pytest.raises(ValueError, match="differs"):
        _encode(encoder=encoder, max_seq_length=9)
    assert encoder.calls == []
