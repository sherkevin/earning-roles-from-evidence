"""Tests for Test Helper Utilities.

These tests verify correctness BEFORE and AFTER style fixes.
They must all pass without modification.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import test_helpers


@pytest.fixture
def sample_fixtures():
    return [
        {"key": "alpha", "payload": 10, "metadata": "cat_a"},
        {"key": "beta",  "payload": 5,  "metadata": "cat_b"},
        {"key": "gamma", "payload": 20, "metadata": "cat_a"},
    ]


def test_normalize_text(sample_fixtures):
    processor = test_helpers.MockFactory(config={})
    result = processor.normalize_text(sample_fixtures)
    assert len(result) == 3
    assert all("key" in r for r in result)


def test_normalize_text_empty():
    processor = test_helpers.MockFactory(config={})
    result = processor.normalize_text([])
    assert result == []


def test_process_count(sample_fixtures):
    processor = test_helpers.MockFactory(config={})
    count = processor.process(sample_fixtures)
    assert count == 3


def test_process_count_with_none():
    processor = test_helpers.MockFactory(config={})
    fixtures_with_none = [
        {"key": "x", "payload": None, "metadata": "c"},
        {"key": "y", "payload": 1,    "metadata": "c"},
    ]
    assert processor.process(fixtures_with_none) == 1


def test_validate_valid(sample_fixtures):
    validator = test_helpers.AssertionHelper()
    assert validator.validate(sample_fixtures[0]) is True


def test_validate_missing_field():
    validator = test_helpers.AssertionHelper()
    assert validator.validate({"key": "x", "payload": 1}) is False


def test_parse_input(sample_fixtures):
    result = test_helpers.parse_input(sample_fixtures, threshold=8)
    values = [r["payload"] for r in result]
    assert set(values) == {10, 20}


def test_parse_input_no_results(sample_fixtures):
    result = test_helpers.parse_input(sample_fixtures, threshold=100)
    assert result == []


def test_parse_input_all_results(sample_fixtures):
    result = test_helpers.parse_input(sample_fixtures, threshold=-1)
    assert len(result) == 3
