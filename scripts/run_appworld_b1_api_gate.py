#!/usr/bin/env python3
"""Run the frozen AppWorld B1 API-backbone gate on the Mac runtime."""
from __future__ import annotations

import argparse
import json
import os
import platform
import time
from pathlib import Path


TASKS = ["6c2c621_1", "6c2c621_2", "6c2c621_3"]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def count_complete_calls(environment_log: Path) -> int:
    if not environment_log.exists():
        return 0
    text = environment_log.read_text(encoding="utf-8", errors="replace")
    return text.count("apis.supervisor.complete_task")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--appworld-root",
        default=str(Path.home() / "work" / "AppWorld"),
    )
    parser.add_argument(
        "--project-root",
        default=str(Path.home() / "work" / "earning-roles-from-evidence"),
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:8318/v1")
    parser.add_argument("--model", default="qwen3.8-max")
    parser.add_argument(
        "--experiment-name",
        default="aamas_b1_qwen38_api_gate_20260921",
    )
    args = parser.parse_args()

    appworld_root = Path(args.appworld_root).resolve()
    project_root = Path(args.project_root).resolve()
    os.environ["APPWORLD_ROOT"] = str(appworld_root)
    os.environ["MODEL_SERVER_URL"] = args.base_url

    # Import only after APPWORLD_ROOT is fixed.
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
            "temperature": 0.0,
            "cost_per_token": zero_cost,
            "retry_after_n_seconds": 2,
            "max_retries": 3,
            "use_cache": False,
        },
        "appworld_config": {
            "raise_on_extra_parameters": True,
        },
        "logger_config": {
            "color": False,
            "verbose": False,
        },
        "usage_tracker_config": {
            "max_cost_overall": 1000,
            "max_cost_per_task": 1000,
            "max_output_tokens_per_task": 200000,
        },
        "prompt_file_path": str(prompt_path),
        "ignore_multiple_calls": True,
        "max_prompt_length": None,
        "max_output_length": None,
        "max_steps": 40,
        "log_lm_calls": True,
        "skip_if_finished": False,
    }

    artifact_dir = (
        project_root
        / "artifacts"
        / "analysis"
        / "aamas2027"
        / "appworld_b1_20260921"
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()
    agent = Agent.from_dict(config)
    # AppWorld validates Responses kwargs against OpenAI's max_output_tokens,
    # but its non_cached_lm_call accepts max_completion_tokens and converts it.
    # Inject after construction to preserve the frozen 2048-token cap without
    # modifying the benchmark checkout.
    agent.language_model.generation_kwargs["max_completion_tokens"] = 2048
    agent.solve_tasks(
        task_ids=TASKS,
        experiment_name=args.experiment_name,
        num_processes=1,
        process_index=0,
    )
    elapsed = time.time() - start

    experiment_root = (
        Path(path_store.experiment_outputs) / args.experiment_name
    )
    task_results = []
    for task_id in TASKS:
        tracker = evaluate_task(
            task_id=task_id,
            experiment_name=args.experiment_name,
            suppress_errors=True,
            save_report=True,
        )
        evaluation = tracker.to_dict(stats_only=False)
        task_root = experiment_root / "tasks" / task_id
        complete_calls = count_complete_calls(
            task_root / "logs" / "environment_io.md"
        )
        usage_path = task_root / "misc" / "usage.json"
        usage = load_json(usage_path) if usage_path.exists() else {}
        official_success = bool(evaluation.get("success", False))
        gate_success = official_success and complete_calls > 0
        task_results.append(
            {
                "task_id": task_id,
                "official_success": official_success,
                "passed_tests": len(evaluation.get("passes", [])),
                "failed_tests": len(evaluation.get("failures", [])),
                "complete_task_calls": complete_calls,
                "gate_success": gate_success,
                "usage": usage.get("tokens", {}),
            }
        )

    gate_successes = sum(row["gate_success"] for row in task_results)
    result = {
        "status": (
            "B1_API_BACKBONE_GATE_PASS"
            if gate_successes >= 2
            else "B1_API_BACKBONE_GATE_FAIL"
        ),
        "experiment_name": args.experiment_name,
        "model": args.model,
        "base_url": args.base_url,
        "tasks": TASKS,
        "gate_successes": gate_successes,
        "gate_required": 2,
        "elapsed_seconds": round(elapsed, 3),
        "task_results": task_results,
        "raw_appworld_output": (
            f"experiments/outputs/{args.experiment_name}"
        ),
        "runtime": {
            "host": platform.node(),
            "python": platform.python_version(),
            "appworld_root": str(appworld_root),
            "private_experience": False,
            "evaluator_private_truth_visible_to_policy": False,
            "max_steps": 40,
            "max_output_tokens_per_turn": 2048,
            "temperature": 0.0,
        },
        "claim_boundary": (
            "Development backbone feasibility only. "
            "Not evidence for experience effects or workflow rebinding."
        ),
    }
    result_path = artifact_dir / "qwen38_api_gate_result.json"
    result_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("B1_GATE_RESULT")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
