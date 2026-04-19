"""Export HotpotQA slices to JSONL for offline runs when Hub cache is flaky.

Usage:
  python scripts/export_hotpot_seed.py [N]           # validation[:N], default from config sample_size
  python scripts/export_hotpot_seed.py full          # entire validation split (~7.4k distractor)
  python scripts/export_hotpot_seed.py train-full  # entire train split (large; ~90k+ distractor)
  Add --force to force re-download from Hub.
"""
import json
import os
import sys
from pathlib import Path

from datasets import DownloadMode, load_dataset

import idea04_paths


def _write_jsonl(out_path: Path, rows: list[dict], split_label: str) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    n = len(rows)
    # 统一宽度，避免 9999→10000 时字符串排序错乱
    width = max(4, len(str(n - 1)) if n else 1)
    with out_path.open("w", encoding="utf-8") as f:
        for idx, row in enumerate(rows):
            passages: list[str] = []
            for title, sentences in zip(row["context"]["title"], row["context"]["sentences"]):
                passage_text = " ".join(sentences)
                passages.append(f"[{title}] {passage_text}")
            rec = {
                "task_id": f"hotpotqa-{idx:0{width}d}",
                "question": row["question"],
                "answer": row["answer"],
                "context_passages": passages[:10],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {out_path} ({len(rows)} rows, {split_label})")
    return len(rows)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = idea04_paths.merge_experiment_config(root / "configs" / "round1_hotpotqa.yaml")
    ep = (cfg.get("hf_endpoint") or "").strip()
    if ep and not os.environ.get("HF_ENDPOINT"):
        os.environ["HF_ENDPOINT"] = ep.rstrip("/")

    argv = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    download_mode = DownloadMode.FORCE_REDOWNLOAD if force else DownloadMode.REUSE_CACHE_IF_EXISTS

    out_dir = root / "artifacts" / "seed"

    if not argv:
        n = int(cfg.get("sample_size", 100))
        split_spec = f"validation[:{n}]"
        out_path = out_dir / f"hotpotqa_validation_{n}.jsonl"
        label = f"validation[:{n}]"
    else:
        first = argv[0].strip().lower()
        if first in ("full", "all", "--full-validation"):
            split_spec = "validation"
            out_path = out_dir / "hotpotqa_validation_full.jsonl"
            label = "validation (full)"
        elif first in ("train-full", "train_full", "train"):
            split_spec = "train"
            out_path = out_dir / "hotpotqa_train_full.jsonl"
            label = "train (full)"
        else:
            n = int(first)
            split_spec = f"validation[:{n}]"
            out_path = out_dir / f"hotpotqa_validation_{n}.jsonl"
            label = f"validation[:{n}]"

    dataset = load_dataset(
        "hotpot_qa",
        "distractor",
        split=split_spec,
        download_mode=download_mode,
    )
    rows = list(dataset)
    _write_jsonl(out_path, rows, label)


if __name__ == "__main__":
    main()
