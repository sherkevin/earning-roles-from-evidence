"""Repo paths and merged experiment config (defaults from configs/huggingface.yaml)."""
from pathlib import Path
from typing import Any

import yaml


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_hf_defaults() -> dict[str, Any]:
    path = repo_root() / "configs" / "huggingface.yaml"
    if not path.is_file():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def merge_experiment_config(config_path: Path) -> dict[str, Any]:
    """Later keys win: huggingface.yaml < experiment yaml."""
    base = load_hf_defaults()
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    override = raw if isinstance(raw, dict) else {}
    return {**base, **override}
