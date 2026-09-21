#!/usr/bin/env python3
"""Run one frozen v4 alternative-backbone screen candidate on Mac."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from pathlib import Path

TASKS = ["530b157_1", "530b157_2", "530b157_3"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_complete_calls(environment_log: Path) -> int:
    if not environment_log.exists():
        return 0
    text = environment_log.read_text(encoding="utf-8", errors="replace")
    return text.count("apis.supervisor.complete_task")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appworld-root", default=str(Path.home() / "work" / "AppWorld"))
    parser.add_argument(
        "--project-root",
        default=str(Path.home() / "work" / "earning-roles-from-evidence"),
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8318/v1")
    parser.add_argument("--model", default="MiniMax-M3")
    parser.add_argument(
        "--experiment-name",
        default="aamas_b1_minimax_m3_530b157_screen_20260921",
    )
    args = parser.parse_args()

    appworld_root = Path(args.appworld_root).resolve()
    project_root = Path(args.project_root).resolve()
    artifact_dir = (
        project_root
        / "artifacts"
        / "analysis"
        / "aamas2027"
        / "appworld_b1_20260921"
    )
    contract_path = artifact_dir / "backbone_screen_530b157_contract_v4.json"
    contract = load_json(contract_path)
    assert contract["benchmark"]["tasks"] == TASKS
    assert args.model in contract["candidate_order"]

    os.environ["APPWORLD_ROOT"] = str(appworld_root)
    os.environ["MODEL_SERVER_URL"] = args.base_url

    from appworld.common.path_store import path_store
    from appworld.evaluator import evaluate_task
    from appworld_agents.code.simplified.agent import Agent
    from appworld_agents.code.simplified import react_code_agent  # noqa: F401

    zero_cost = {
        "input_cache_miss": 0.0,
        "input_cache_hit": 0.0,
        "input_cache_write": 0.0,
        "output": 0.0,
    }
    prompt_path = (
        appworld_root
        / "experiments"
        / "prompts"
        / "react_code_agent"
        / "instructions.txt"
    )
    config = {
        "type": "simplified_react_code_agent",
        "model_config": {
            "name": args.model,
            "client_name": "openai",
            "api_type": "responses",
            "base_url": args.base_url,
            "api_key": "local-router",
            "temperature": contract["shared_runtime"]["temperature"],
            "cost_per_token": zero_cost,
            "retry_after_n_seconds": 2,
            "max_retries": 3,
            "use_cache": False,
        },
        "appworld_config": {"raise_on_extra_parameters": True},
        "logger_config": {"color": False, "verbose": False},
        "usage_tracker_config": {
            "max_cost_overall": 1000,
            "max_cost_per_task": 1000,
            "max_output_tokens_per_task": 200000,
        },
        "prompt_file_path": str(prompt_path),
        "ignore_multiple_calls": True,
        "max_prompt_length": None,
        "max_output_length": None,
        "max_steps": contract["shared_runtime"]["max_steps"],
        "log_lm_calls": True,
        "skip_if_finished": False,
    }

    experiment_root = Path(path_store.experiment_outputs) / args.experiment_name
    if experiment_root.exists():
        raise SystemExit(f"Refusing to overwrite existing experiment: {experiment_root}")

    agent = Agent.from_dict(config)
    agent.language_model.generation_kwargs["max_completion_tokens"] = contract["shared_runtime"][
        "max_output_tokens_per_turn"
    ]

    start = time.time()
    agent.solve_tasks(
        task_ids=TASKS,
        experiment_name=args.experiment_name,
        num_processes=1,
        process_index=0,
    )
    elapsed = time.time() - start

    rows = []
    for task_id in TASKS:
        tracker = evaluate_task(
            task_id=task_id,
            experiment_name=args.experiment_name,
            suppress_errors=True,
            save_report=True,
        )
        evaluation = tracker.to_dict(stats_only=False)
        passes = len(evaluation.get("passes", []))
        failures = len(evaluation.get("failures", []))
        total = passes + failures
        task_root = experiment_root / "tasks" / task_id
        complete_calls = count_complete_calls(task_root / "logs" / "environment_io.md")
        usage_path = task_root / "misc" / "usage.json"
        usage = load_json(usage_path) if usage_path.exists() else {}
        rows.append(
            {
                "task_id": task_id,
                "official_success": bool(evaluation.get("success", False)),
                "passed_tests": passes,
                "failed_tests": failures,
                "passed_test_fraction": (passes / total) if total else 0.0,
                "complete_task_calls": complete_calls,
                "usage": usage.get("tokens", {}),
            }
        )

    successes = sum(int(row["official_success"]) for row in rows)
    mean_fraction = sum(row["passed_test_fraction"] for row in rows) / len(rows)
    none_completed = all(row["complete_task_calls"] == 0 for row in rows)

    if successes == 3:
        decision = "CEILING_REJECT"
    elif successes == 0 and mean_fraction <= 0.30 and none_completed:
        decision = "FLOOR_REJECT"
    else:
        decision = "USABLE_SELECT"

    result = {
        "status": decision,
        "condition": "backbone_screen_no_experience",
        "experiment_name": args.experiment_name,
        "contract_sha256": sha256(contract_path),
        "model": args.model,
        "base_url": args.base_url,
        "successes": successes,
        "out_of": len(rows),
        "mean_passed_test_fraction": mean_fraction,
        "elapsed_seconds": round(elapsed, 3),
        "task_results": rows,
        "runtime": {
            "host": platform.node(),
            "python": platform.python_version(),
            "appworld_root": str(appworld_root),
            "private_experience": False,
            "max_steps": contract["shared_runtime"]["max_steps"],
            "max_output_tokens_per_turn": contract["shared_runtime"][
                "max_output_tokens_per_turn"
            ],
            "temperature": contract["shared_runtime"]["temperature"],
        },
        "raw_appworld_output": f"experiments/outputs/{args.experiment_name}",
        "claim_boundary": (
            "Alternative-backbone development screen only. "
            "No donor acquisition or capability-difference treatment has run."
        ),
    }

    safe_model = args.model.lower().replace("/", "_").replace(".", "_").replace("-", "_")
    out_path = artifact_dir / f"screen_{safe_model}_530b157_result.json"
    out_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("B1_530B157_BACKBONE_SCREEN_RESULT")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
