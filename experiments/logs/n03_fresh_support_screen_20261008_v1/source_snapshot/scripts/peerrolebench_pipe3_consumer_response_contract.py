"""Strict parser for the PIPE3 consumer actor response envelope."""
from __future__ import annotations


def extract_consumer_sources(value, required_paths):
    if not isinstance(value, dict) or set(value) != {"source_files"}:
        raise ValueError("consumer response must contain only source_files")
    files = value.get("source_files")
    if not isinstance(files, dict) or set(files) != set(required_paths):
        raise ValueError("consumer source_files must match the contracted public paths")
    if not all(isinstance(source, str) for source in files.values()):
        raise ValueError("consumer source_files values must be text")
    return dict(files)
