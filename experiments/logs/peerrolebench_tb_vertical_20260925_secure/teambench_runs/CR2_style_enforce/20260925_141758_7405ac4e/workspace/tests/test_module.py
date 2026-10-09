"""Tests for API Client Library.

These tests verify correctness BEFORE and AFTER style fixes.
They must all pass without modification.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import api_client


@pytest.fixture
def sample_requests():
    return [
        {"url": "alpha", "status": 10, "headers": "cat_a"},
        {"url": "beta",  "status": 5,  "headers": "cat_b"},
        {"url": "gamma", "status": 20, "headers": "cat_a"},
    ]


def test_filter_items(sample_requests):
    processor = api_client.HttpClient(config={})
    result = processor.filter_items(sample_requests)
    assert len(result) == 3
    assert all("url" in r for r in result)


def test_filter_items_empty():
    processor = api_client.HttpClient(config={})
    result = processor.filter_items([])
    assert result == []


def test_process_count(sample_requests):
    processor = api_client.HttpClient(config={})
    count = processor.process(sample_requests)
    assert count == 3


def test_process_count_with_none():
    processor = api_client.HttpClient(config={})
    requests_with_none = [
        {"url": "x", "status": None, "headers": "c"},
        {"url": "y", "status": 1,    "headers": "c"},
    ]
    assert processor.process(requests_with_none) == 1


def test_validate_valid(sample_requests):
    validator = api_client.ResponseParser()
    assert validator.validate(sample_requests[0]) is True


def test_validate_missing_field():
    validator = api_client.ResponseParser()
    assert validator.validate({"url": "x", "status": 1}) is False


def test_load_data(sample_requests):
    result = api_client.load_data(sample_requests, threshold=8)
    values = [r["status"] for r in result]
    assert set(values) == {10, 20}


def test_load_data_no_results(sample_requests):
    result = api_client.load_data(sample_requests, threshold=100)
    assert result == []


def test_load_data_all_results(sample_requests):
    result = api_client.load_data(sample_requests, threshold=-1)
    assert len(result) == 3
