import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from datasets import DownloadMode, load_dataset

import idea04_paths

sys.path.append(str(Path("workspace").resolve()))
from idea04_core.runner import RoundRunner


ROUND0_METHODS = [
    "fixed_static_roles", 
    "fixed_self_claim", 
    "fixed_peer_calibrated",
    "central_orchestrator_with_reflection",
    "fixed_self_calibrated"
]


def apply_hf_hub_endpoint(config: dict[str, Any], cli_endpoint: str | None) -> None:
    """Use a Hub mirror (e.g. https://hf-mirror.com) before load_dataset. huggingface_hub reads HF_ENDPOINT."""
    if cli_endpoint and cli_endpoint.strip():
        os.environ["HF_ENDPOINT"] = cli_endpoint.strip().rstrip("/")
        return
    if os.environ.get("HF_ENDPOINT"):
        return
    ep = (config.get("hf_endpoint") or "").strip()
    if ep:
        os.environ["HF_ENDPOINT"] = ep.rstrip("/")


def load_samples_from_jsonl(path: Path, sample_size: int | None) -> list[dict[str, Any]]:
    """Replay a prior run's raw_inputs.jsonl when HuggingFace dataset cache is unavailable."""
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    if sample_size is not None:
        rows = rows[:sample_size]
    return rows


def load_hotpot_samples(sample_size: int, force_redownload: bool = False) -> list[dict[str, Any]]:
    download_mode = DownloadMode.FORCE_REDOWNLOAD if force_redownload else DownloadMode.REUSE_CACHE_IF_EXISTS
    dataset = load_dataset(
        "hotpot_qa",
        "distractor",
        split=f"validation[:{sample_size}]",
        download_mode=download_mode,
    )
    samples: list[dict[str, Any]] = []
    for idx, row in enumerate(dataset):
        # Build context passages (title + sentences) for the agent to use
        passages: list[str] = []
        for title, sentences in zip(row["context"]["title"], row["context"]["sentences"]):
            passage_text = " ".join(sentences)
            passages.append(f"[{title}] {passage_text}")
        samples.append(
            {
                "task_id": f"hotpotqa-{idx:04d}",
                "question": row["question"],
                "answer": row["answer"],
                "context_passages": passages[:10],  # limit to 10 passages to control token budget
            }
        )
    return samples


def collect_summary_rows_from_run_dir(run_root: Path) -> list[dict[str, Any]]:
    """Build summary from each method subfolder that has metrics.json (supports partial runs)."""
    rows: list[dict[str, Any]] = []
    for method_name in ROUND0_METHODS:
        metrics_path = run_root / method_name / "metrics.json"
        if not metrics_path.is_file():
            continue
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        rows.append({"method": method_name, **metrics})
    return rows


def write_round0_summary(
    output_root: Path,
    run_id: str,
    summary_rows: list[dict[str, Any]],
    summary_prefix: str,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    round0_main_table = output_root / f"{summary_prefix}_main_table.csv"
    fieldnames = list(summary_rows[0].keys()) if summary_rows else ["method"]
    with round0_main_table.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in summary_rows:
            writer.writerow(row)

    routing_examples = output_root / f"{summary_prefix}_routing_examples.md"
    routing_examples.write_text(
        "\n".join(
            [
                f"# {summary_prefix}_routing_examples",
                "",
                f"- run_id: {run_id}",
                "- See each method folder `routing_traces.jsonl` and `handoff_packets.jsonl`.",
            ]
        ),
        encoding="utf-8",
    )

    logging_check = output_root / f"{summary_prefix}_logging_check.md"
    logging_check.write_text(
        "\n".join(
            [
                f"# {summary_prefix}_logging_check",
                "",
                "- Required files are generated per method run:",
                "  - run_config.yaml",
                "  - sample_ids.json",
                "  - raw_inputs.jsonl",
                "  - routing_traces.jsonl",
                "  - handoff_packets.jsonl",
                "  - competence_snapshots.jsonl",
                "  - raw_model_outputs.jsonl",
                "  - parsed_predictions.jsonl",
                "  - metrics.json",
                "  - main_table.csv",
                "  - failure_cases.md",
                "  - case_studies.md",
                "  - run_notes.md",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Round0/Round1 HotpotQA smoke for idea04.")
    parser.add_argument("--config", default="configs/round0_hotpotqa.yaml")
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Override config sample_size (default: use config).",
    )
    parser.add_argument(
        "--artifacts-root",
        default="artifacts/round0",
        help="Output directory for this round (e.g. artifacts/round1).",
    )
    parser.add_argument(
        "--samples-jsonl",
        default=None,
        help="Load samples from raw_inputs.jsonl (skips HuggingFace). Caps length by --sample-size / config.",
    )
    parser.add_argument(
        "--hf-endpoint",
        default=None,
        help="Hub mirror for this run, e.g. https://hf-mirror.com (overrides env/config).",
    )
    parser.add_argument(
        "--hf-force-redownload",
        action="store_true",
        help="Re-download dataset via Hub (use when local HF dataset cache is corrupted).",
    )
    parser.add_argument(
        "--methods",
        default=None,
        help="Comma-separated subset of methods to run (default: all Round0 methods).",
    )
    parser.add_argument(
        "--resume-run-dir",
        default=None,
        help="Existing run_* folder under artifacts; write only listed methods there (no new run id).",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path
    config = idea04_paths.merge_experiment_config(config_path)
    apply_hf_hub_endpoint(config, args.hf_endpoint)
    sample_size = args.sample_size if args.sample_size is not None else int(config.get("sample_size", 50))
    if args.samples_jsonl:
        samples = load_samples_from_jsonl(Path(args.samples_jsonl), sample_size=sample_size)
        if not samples:
            sys.exit(f"No samples loaded from {args.samples_jsonl}")
    else:
        force_dl = bool(args.hf_force_redownload or config.get("hf_force_redownload", False))
        samples = load_hotpot_samples(sample_size=sample_size, force_redownload=force_dl)

    output_root = Path(args.artifacts_root)
    summary_prefix = output_root.name

    if args.resume_run_dir:
        run_root = Path(args.resume_run_dir).resolve()
        if not run_root.is_dir():
            sys.exit(f"--resume-run-dir is not a directory: {run_root}")
        run_id = run_root.name
    else:
        run_id = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
        run_root = output_root / run_id
        run_root.mkdir(parents=True, exist_ok=True)

    methods_to_run = ROUND0_METHODS
    if args.methods:
        methods_to_run = [m.strip() for m in args.methods.split(",") if m.strip()]
        for m in methods_to_run:
            if m not in ROUND0_METHODS:
                sys.exit(f"Unknown method {m!r}; allowed: {ROUND0_METHODS}")

    for method_name in methods_to_run:
        method_config = dict(config)
        method_config["method_name"] = method_name
        runner = RoundRunner(topology=config["topology"], max_handoff=config["max_handoff"])
        method_dir = run_root / method_name
        runner.run(
            method_name=method_name,
            samples=samples,
            run_config=method_config,
            run_dir=method_dir,
        )

    summary_rows = collect_summary_rows_from_run_dir(run_root)
    write_round0_summary(
        output_root=output_root,
        run_id=run_id,
        summary_rows=summary_rows,
        summary_prefix=summary_prefix,
    )
    print(f"Smoke completed: {run_root} (summary in {output_root})")


if __name__ == "__main__":
    main()
