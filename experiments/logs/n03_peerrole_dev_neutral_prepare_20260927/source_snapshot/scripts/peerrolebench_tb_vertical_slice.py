#!/usr/bin/env python3
"""Run a small, auditable TeamBench peer-selection protocol slice.

This is a contract/data-pipeline smoke test, not a benchmark result.  It uses
deterministic fixture peers so we can verify attribution, delayed feedback,
artifact lineage, and the native TeamBench scorer before paying for LLM calls.
The runner deliberately reports when the task set is too small for a scientific
claim.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import platform
import random
import shutil
import subprocess
import sys
import time
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEAMBENCH = ROOT / "references" / "benchmark_sources" / "TeamBench"
sys.path.insert(0, str(ROOT / "references" / "aamas"))
sys.path.insert(0, str(TEAMBENCH))

from harness.run_all import grade_run, setup_run  # noqa: E402
from peer_role_protocol_20260925 import (  # noqa: E402
    ConsumerAction,
    Delivery,
    LaterAssignment,
    PeerRoleLedger,
    PeerSelection,
    RecipientJudgment,
    RoleEvidenceUpdate,
    TerminalOutcome,
)


TASKS = ("CR2_style_enforce", "DIST1_queue_race")
PEERS = ("peer_01_noop", "peer_02_repair", "peer_03_partial")
CONDITIONS = ("random", "static_best", "terminal_only", "recipient_judgment")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_digest(root: Path) -> str:
    """Hash a workspace's relative paths and bytes in deterministic order."""
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        rel = path.relative_to(root).as_posix().encode()
        h.update(len(rel).to_bytes(8, "big"))
        h.update(rel)
        data = path.read_bytes()
        h.update(len(data).to_bytes(8, "big"))
        h.update(data)
    return h.hexdigest()


def json_digest(payload: Any) -> str:
    return sha256_bytes(json.dumps(payload, sort_keys=True).encode())


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_output(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def write_seeded_cr2_repair(workspace: Path, seed: int) -> None:
    """Generate the deterministic repair for the current CR2 task instance."""
    from generators.gen_cr2_style_enforce import DOMAINS, Generator

    generated = Generator().generate(seed=seed)
    expected = generated.expected
    domain = next(item for item in DOMAINS if item["name"] == expected["domain"])
    substitutions = {
        expected["class_bad"]: expected["class_good"],
        expected["class2_bad"]: expected["class2_good"],
        expected["fn1_bad"]: expected["fn1_good"],
        expected["fn2_bad"]: expected["fn2_good"],
        expected["var1_bad"]: expected["var1_good"],
        expected["var2_bad"]: expected["var2_good"],
    }
    module_file = expected["module_file"]
    source = generated.workspace_files[module_file]
    for old, new in substitutions.items():
        source = source.replace(old, new)
    source = source.replace("from typing import *", "from typing import Any, Dict, List")
    source = source.replace(
        expected["good_imports"].splitlines()[0],
        expected["good_imports"],
        1,
    )
    bad_import_lines = [
        line
        for line in source.splitlines()
        if line.startswith("import ") and line.split()[1] in {"functools", "math", "os", "re", "string"}
    ]
    if bad_import_lines:
        for line in bad_import_lines:
            source = source.replace(line + "\n", "", 1)
        marker = "from typing import Any, Dict, List"
        source = source.replace(marker, expected["good_imports"] + "\n" + marker, 1)

    source = source.replace("def __init__(self, config):", "def __init__(self, config: Dict[str, Any]) -> None:")
    source = source.replace("self.results = []", "self.results: List[Dict[str, Any]] = []")
    source = source.replace(
        f"def {expected['fn1_good']}(self, raw):",
        f"def {expected['fn1_good']}(self, raw: List[Dict[str, Any]]) -> List[Dict[str, Any]]:",
    )
    source = source.replace(
        f"def process(self, {domain['noun_plural']}):",
        f"def process(self, {domain['noun_plural']}: List[Dict[str, Any]]) -> int:",
    )
    source = source.replace(
        f"def validate(self, {domain['noun']}):",
        f"def validate(self, {domain['noun']}: Dict[str, Any]) -> bool:",
    )
    source = source.replace(
        f"def {expected['fn2_good']}(items, threshold):",
        f"def {expected['fn2_good']}(items: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:",
    )
    source = source.replace("def _internal_helper(value):", "def _internal_helper(value: Any) -> str:")
    source = source.replace(
        "        # No docstring here - this is also a violation\n        # Missing type hints on public method\n",
        f'        """Count {domain["noun_plural"]} with a non-null value."""\n',
    )
    source = source.replace(
        "        # Missing type hints\n        # Bad docstring style\n        \"\"\"validate a fixture dict. returns True if valid.\"\"\"",
        f'        """Validate one {domain["noun"]} against the required fields."""',
    )
    source = source.replace(
        "    # Missing type hints and Google-style docstring\n    \"\"\"filter items above threshold\"\"\"",
        f'    """Return {domain["noun_plural"]} above the threshold."""',
    )
    source = source.replace(",\n            }", ",\n            }")
    source = source.replace(f'            "{domain["field3"]}"\n', f'            "{domain["field3"]}",\n')
    source = source.replace(
        "# This is a very long comment that documents important behaviour of this module in detail.\n\n",
        "",
    )
    source = source.replace(
        f'                "{domain["field3"]}": item.get("{domain["field3"]}", "default")\n',
        f'                "{domain["field3"]}": item.get("{domain["field3"]}", "default"),\n',
    )
    (workspace / module_file).write_text(source, encoding="utf-8")


def write_dist1_repair(workspace: Path) -> None:
    """Apply a deterministic repair for the queue fixture."""
    (workspace / "mqueue" / "queue.py").write_text(
        '''"""Thread-safe task queue with explicit acknowledgement."""

import threading
import uuid
from collections import deque
from typing import Any, Dict, Optional, Tuple


class QueueFull(Exception):
    """Raised when the queue has reached its capacity."""


class QueueEmpty(Exception):
    """Raised when the queue is empty."""


class TaskQueue:
    """Thread-safe FIFO queue with ack/nack receipts."""

    def __init__(self, capacity: int = 500) -> None:
        self._capacity = capacity
        self._queue: deque[Any] = deque()
        self._in_flight: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def put(self, message: Any) -> None:
        """Atomically enqueue a message if capacity is available."""
        with self._lock:
            if len(self._queue) >= self._capacity:
                raise QueueFull(f"TaskQueue at capacity ({self._capacity})")
            self._queue.append(message)

    def get(self) -> Tuple[Optional[Any], Optional[str]]:
        """Return the next message and receipt, or ``(None, None)``."""
        with self._lock:
            if not self._queue:
                return None, None
            message = self._queue.popleft()
            receipt = uuid.uuid4().hex
            self._in_flight[receipt] = message
            return message, receipt

    def ack(self, receipt: str) -> None:
        """Commit a receipt and remove it from the in-flight set."""
        with self._lock:
            self._in_flight.pop(receipt, None)

    def nack(self, receipt: str) -> None:
        """Return an unacknowledged message to the front of the queue."""
        with self._lock:
            if receipt in self._in_flight:
                self._queue.appendleft(self._in_flight.pop(receipt))

    def size(self) -> int:
        """Return the number of queued messages."""
        with self._lock:
            return len(self._queue)

    def is_empty(self) -> bool:
        """Return whether no queued messages remain."""
        with self._lock:
            return not self._queue

    def is_full(self) -> bool:
        """Return whether the queue has reached capacity."""
        with self._lock:
            return len(self._queue) >= self._capacity
''',
        encoding="utf-8",
    )
    (workspace / "mqueue" / "priority.py").write_text(
        '''"""Priority-ordered task message wrapper."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PriorityTask:
    """Order tasks by urgency and a numeric sequence tie-breaker."""

    urgency: int
    seq: int
    message: Any = field(compare=False)
''',
        encoding="utf-8",
    )
    (workspace / "mqueue" / "consumer.py").write_text(
        '''"""Consumer interface for the task queue."""

import threading
import time
from typing import Any, Callable

from mqueue.queue import TaskQueue


class TaskConsumer:
    """Consume messages and acknowledge successful processing."""

    def __init__(
        self,
        queue: TaskQueue,
        handler: Callable[[Any], None],
        consumer_id: int = 0,
    ) -> None:
        self._queue = queue
        self._handler = handler
        self._consumer_id = consumer_id
        self._processed = []
        self._lock = threading.Lock()
        self._running = False

    def run_once(self) -> bool:
        """Process and acknowledge one queued task."""
        message, receipt = self._queue.get()
        if message is None or receipt is None:
            return False
        try:
            self._handler(message)
        except Exception:
            self._queue.nack(receipt)
            raise
        self._queue.ack(receipt)
        with self._lock:
            self._processed.append(message)
        return True

    def run_until_empty(self, max_idle_cycles: int = 10) -> None:
        """Drain the queue after a bounded number of empty polls."""
        idle = 0
        while idle < max_idle_cycles:
            if self.run_once():
                idle = 0
            else:
                idle += 1
                time.sleep(0.001)

    @property
    def processed_count(self) -> int:
        """Return the number of successfully processed messages."""
        return len(self._processed)

    @property
    def processed_messages(self) -> list:
        """Return a snapshot of successfully processed messages."""
        with self._lock:
            return list(self._processed)
''',
        encoding="utf-8",
    )


def apply_fixture_candidate(task: str, peer: str, workspace: Path, seed: int) -> None:
    if peer == "peer_02_repair":
        if task == "CR2_style_enforce":
            write_seeded_cr2_repair(workspace, seed)
        elif task == "DIST1_queue_race":
            write_dist1_repair(workspace)
    elif peer == "peer_03_partial" and task == "DIST1_queue_race":
        # A partial candidate fixes only the type-safe priority comparator.
        priority = workspace / "mqueue" / "priority.py"
        priority.write_text(
            '''from dataclasses import dataclass, field\nfrom typing import Any\n\n\n@dataclass(order=True)\nclass PriorityTask:\n    """Order messages without comparing arbitrary payloads."""\n\n    urgency: int\n    seq: int\n    message: Any = field(compare=False)\n''',
            encoding="utf-8",
        )


def fixture_judgment(peer: str) -> tuple[str, float]:
    if peer == "peer_02_repair":
        return "accept", 0.9
    if peer == "peer_03_partial":
        return "accept_with_rework", 0.5
    return "reject_redo", 0.2


def choose_peer(
    condition: str,
    scores: dict[str, float],
    rng: random.Random,
) -> tuple[str, float]:
    if condition == "random":
        return rng.choice(PEERS), 1.0 / len(PEERS)
    if condition == "static_best":
        # This is a fixture-only frozen arm.  A real benchmark must freeze this
        # choice on a disjoint calibration split, never on evaluation labels.
        return "peer_02_repair", 1.0
    return max(PEERS, key=lambda p: (scores.get(p, 0.0), p)), 1.0


def update_selector(condition: str, scores: dict[str, float], peer: str,
                    judgment_score: float, terminal_score: float) -> None:
    if condition == "terminal_only":
        scores[peer] = 0.5 * scores.get(peer, 0.0) + 0.5 * terminal_score
    elif condition == "recipient_judgment":
        scores[peer] = 0.5 * scores.get(peer, 0.0) + 0.5 * judgment_score


def write_attestation(run_dir: Path) -> None:
    (run_dir / "submission" / "attestation.json").write_text(
        json.dumps({"verdict": "pass", "verifier": "fixture-protocol"}),
        encoding="utf-8",
    )


def stable_policy_seed(task: str, condition: str, episode: int) -> int:
    payload = f"{task}|{condition}|{episode}|fixture-policy-v2".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def require_task_runtime(task: str) -> None:
    if task == "DIST1_queue_race" and importlib.util.find_spec("pytest_timeout") is None:
        raise RuntimeError(
            "DIST1_queue_race requires pytest-timeout; without it, every pytest "
            "check using --timeout is an environment failure"
        )


def assignment_for_episode(
    ledger: PeerRoleLedger,
    task: str,
    episode: int,
) -> LaterAssignment | None:
    matches = [
        assignment
        for assignment in ledger.assignments.values()
        if (assignment.task_id, assignment.task_index) == (task, episode)
    ]
    if len(matches) > 1:
        raise RuntimeError("multiple assignments recorded for one episode")
    return matches[0] if matches else None


def materialize_consumer_action(
    task: str,
    action_name: str,
    chosen_dir: Path,
    seed: int,
    runs_dir: Path,
) -> tuple[Path, str, bool]:
    """Create the workspace actually consumed and later graded."""
    if action_name == "use":
        return chosen_dir, tree_digest(chosen_dir / "workspace"), False

    _, consumer_dir_str, _ = setup_run(
        task,
        str(TEAMBENCH / "tasks"),
        str(runs_dir),
        seed=seed,
    )
    consumer_dir = Path(consumer_dir_str)
    if action_name == "repair":
        shutil.rmtree(consumer_dir / "workspace")
        shutil.copytree(chosen_dir / "workspace", consumer_dir / "workspace")
    elif action_name != "independent_redo":
        raise ValueError(f"unsupported fixture consumer action: {action_name}")

    apply_fixture_candidate(task, "peer_02_repair", consumer_dir / "workspace", seed)
    write_attestation(consumer_dir)
    return consumer_dir, tree_digest(consumer_dir / "workspace"), True


def secure_grade_candidate(task: str, candidate_dir: Path, seed: int,
                           runs_dir: Path) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    """Grade candidate source against a fresh evaluator workspace.

    TeamBench's native workspace includes writable tests.  This adapter keeps
    the generated gold tests/expected labels from a fresh run and copies only
    the candidate source tree, so a candidate cannot pass by editing tests.
    It does not claim to sandbox malicious source from reading sibling reports;
    that remains a benchmark hardening item for the containerized evaluator.
    """
    _, eval_dir_str, _ = setup_run(task, str(TEAMBENCH / "tasks"), str(runs_dir), seed=seed)
    eval_dir = Path(eval_dir_str)
    candidate_workspace = candidate_dir / "workspace"
    eval_workspace = eval_dir / "workspace"
    if task == "CR2_style_enforce":
        expected = json.loads((eval_dir / "reports" / "expected.json").read_text())
        module_file = expected["module_file"]
        source = candidate_workspace / module_file
        if not source.exists():
            raise FileNotFoundError(f"candidate source missing: {module_file}")
        shutil.copy2(source, eval_workspace / module_file)
        candidate_source_digest = file_digest(source)
        evaluator_source_path = eval_workspace / module_file
    elif task == "DIST1_queue_race":
        source = candidate_workspace / "mqueue"
        target = eval_workspace / "mqueue"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        candidate_source_digest = tree_digest(source)
        evaluator_source_path = target
    else:
        raise ValueError(f"no secure source allowlist for {task}")
    write_attestation(eval_dir)
    tests_dir = eval_workspace / "tests"
    tests_before = tree_digest(tests_dir)
    expected_path = eval_dir / "reports" / "expected.json"
    expected_before = sha256_bytes(expected_path.read_bytes()) if expected_path.exists() else None
    evaluator_source_before = (
        tree_digest(evaluator_source_path)
        if evaluator_source_path.is_dir()
        else file_digest(evaluator_source_path)
    )
    for path in tests_dir.rglob("*"):
        if path.is_file():
            path.chmod(0o444)
    if expected_path.exists():
        expected_path.chmod(0o444)
    score = grade_run(task, str(TEAMBENCH / "tasks" / task), str(eval_dir))
    tests_after = tree_digest(tests_dir)
    expected_after = sha256_bytes(expected_path.read_bytes()) if expected_path.exists() else None
    evaluator_source_after = (
        tree_digest(evaluator_source_path)
        if evaluator_source_path.is_dir()
        else file_digest(evaluator_source_path)
    )
    audit = {
        "secure_source_allowlist": True,
        "tests_sha256_before": tests_before,
        "tests_sha256_after": tests_after,
        "tests_unchanged": tests_before == tests_after,
        "expected_sha256_before": expected_before,
        "expected_sha256_after": expected_after,
        "expected_unchanged": expected_before == expected_after,
        "candidate_source_sha256": candidate_source_digest,
        "evaluator_source_sha256_before": evaluator_source_before,
        "evaluator_source_sha256_after": evaluator_source_after,
        "evaluator_executed_candidate_source": candidate_source_digest == evaluator_source_before,
        "evaluator_source_unchanged": evaluator_source_before == evaluator_source_after,
        "candidate_grader_sandboxed_from_sibling_reports": False,
    }
    return score, eval_dir, audit


def run_episode(
    task: str,
    condition: str,
    episode: int,
    runs_dir: Path,
    scores: dict[str, float],
    ledger: PeerRoleLedger,
) -> dict[str, Any]:
    seed = episode
    task_dir = TEAMBENCH / "tasks"
    pending_assignment = assignment_for_episode(ledger, task, episode)
    if pending_assignment is None:
        chosen, propensity = choose_peer(
            condition,
            scores,
            random.Random(stable_policy_seed(task, condition, episode)),
        )
        assignment_consumed = False
    else:
        chosen = pending_assignment.agent_id
        propensity = pending_assignment.decision_propensity
        assignment_consumed = True
    selection = PeerSelection(
        selection_id=f"sel-{task}-{condition}-{episode}",
        task_id=task,
        task_index=episode,
        selector_id="selector-01",
        role="producer",
        candidate_ids=PEERS,
        chosen_peer_id=chosen,
        propensity=propensity,
    )
    ledger.record_selection(selection)
    ledger.record_task_start(task, episode)

    _, candidate_dir, _ = setup_run(task, str(task_dir), str(runs_dir), seed=seed)
    chosen_dir = Path(candidate_dir)
    apply_fixture_candidate(task, chosen, chosen_dir / "workspace", seed)
    write_attestation(chosen_dir)
    artifact_hash = tree_digest(chosen_dir / "workspace")
    delivery = Delivery(
        delivery_id=f"del-{task}-{condition}-{episode}",
        task_id=task,
        producer_id=chosen,
        recipient_id="recipient-01",
        artifact_sha256=artifact_hash,
        source_event_id=f"produce-{task}-{condition}-{episode}",
        task_index=episode,
        selection_id=selection.selection_id,
    )
    ledger.record_delivery(delivery)
    decision, predicted_score = fixture_judgment(chosen)
    judgment = RecipientJudgment(
        judgment_id=f"jud-{task}-{condition}-{episode}",
        delivery_id=delivery.delivery_id,
        consumer_id="recipient-01",
        decision=decision,
        observed_artifact_sha256=artifact_hash,
    )
    ledger.record_judgment(judgment)
    action_name = {"accept": "use", "accept_with_rework": "repair",
                   "reject_redo": "independent_redo"}[decision]
    consumed_dir, consumed_hash, consumer_changed_artifact = materialize_consumer_action(
        task,
        action_name,
        chosen_dir,
        seed,
        runs_dir,
    )
    action = ConsumerAction(
        action_id=f"act-{task}-{condition}-{episode}",
        delivery_id=delivery.delivery_id,
        consumer_id="recipient-01",
        used_artifact=action_name in {"use", "repair"},
        input_artifact_sha256=artifact_hash,
        output_artifact_sha256=consumed_hash,
        repair_cost=1.0 if consumer_changed_artifact else 0.0,
        action=action_name,
    )
    ledger.record_action(action)
    before_grade_hash = tree_digest(consumed_dir / "workspace")
    score, eval_dir, grade_audit = secure_grade_candidate(
        task, consumed_dir, seed, runs_dir
    )
    after_grade_hash = tree_digest(consumed_dir / "workspace")
    score_payload = score.get("secondary", {})
    terminal_score = float(score_payload.get("partial_score", 0.0))
    outcome = TerminalOutcome(
        outcome_id=f"out-{task}-{condition}-{episode}",
        delivery_id=delivery.delivery_id,
        success=bool(score.get("pass", False)),
        scorer_version="teambench-native-d185aef",
        partial_score=terminal_score,
        score_payload_sha256=json_digest(score),
    )
    ledger.record_outcome(outcome)
    evidence = RoleEvidenceUpdate(
        evidence_id=f"ev-{task}-{condition}-{episode}",
        judgment_id=judgment.judgment_id,
        action_id=action.action_id,
        outcome_id=outcome.outcome_id,
        update_version="fixture-update-v1",
        arrived_at=float(len(ledger.events)),
    )
    ledger.record_evidence_update(evidence)
    update_selector(condition, scores, chosen, predicted_score, terminal_score)
    if episode + 1 < 2:
        next_peer, next_propensity = choose_peer(
            condition,
            scores,
            random.Random(stable_policy_seed(task, condition, episode + 1)),
        )
        ledger.record_assignment(LaterAssignment(
            assignment_id=f"assign-{task}-{condition}-{episode + 1}",
            task_id=task,
            task_index=episode + 1,
            agent_id=next_peer,
            role="producer",
            evidence_ids=(evidence.evidence_id,),
            decision_propensity=next_propensity,
        ))
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "episode_complete",
        "task_id": task,
        "condition": condition,
        "episode": episode,
        "seed": seed,
        "candidate_pool": [
            {
                "peer_id": peer,
                "producer_version": "fixture-v2",
                "executed": peer == chosen,
            }
            for peer in PEERS
        ],
        "selected_peer_id": chosen,
        "selection_propensity": propensity,
        "assignment_consumed": assignment_consumed,
        "assignment_id": pending_assignment.assignment_id if pending_assignment else None,
        "recipient_judgment": asdict(judgment),
        "consumer_action": asdict(action),
        "consumer_output_artifact_sha256": consumed_hash,
        "consumer_changed_artifact": consumer_changed_artifact,
        "terminal_outcome": asdict(outcome),
        "score": score,
        "secure_grade_audit": grade_audit,
        "evaluator_run_dir": str(eval_dir),
        "artifact_hash_before_grade": before_grade_hash,
        "artifact_hash_after_grade": after_grade_hash,
        "artifact_unchanged": before_grade_hash == after_grade_hash,
        "reports_hidden_from_recipient": True,
        "selector_state_after": copy.deepcopy(scores),
        "ledger": ledger.snapshot(),
        "producer_run_dir": str(chosen_dir),
        "consumed_run_dir": str(consumed_dir),
    }
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "experiments" / "logs" /
                                                    "peerrolebench_tb_vertical_20260925"))
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    runs_dir = out / "teambench_runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "fixture_protocol_smoke",
        "teambench_commit": "d185aef",
        "tasks": TASKS,
        "conditions": CONDITIONS,
        "peers": PEERS,
        "episodes_per_task_condition": 2,
        "policy_seed_scheme": "sha256(task|condition|episode|fixture-policy-v2)",
        "execution_timing": "select_then_execute",
        "consumer_action_materialized": True,
        "raw_log_streaming": True,
        "runtime_dependencies": {
            "pytest": importlib.util.find_spec("pytest") is not None,
            "pytest_timeout": importlib.util.find_spec("pytest_timeout") is not None,
        },
        "exact_command": " ".join(sys.argv),
        "git_head": git_output("rev-parse", "HEAD"),
        "git_status_porcelain_sha256": sha256_bytes(
            git_output("status", "--porcelain=v1", "-uall").encode()
        ),
        "source_sha256": {
            "runner": file_digest(Path(__file__).resolve()),
            "protocol": file_digest(ROOT / "references" / "aamas" / "peer_role_protocol_20260925.py"),
        },
        "python": sys.version,
        "platform": platform.platform(),
        "real_llm_calls": 0,
        "scientific_claim_allowed": False,
        "reason": "fixture peers and only two task families; used to validate the causal adapter",
    }
    (out / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    records: list[dict[str, Any]] = []
    started = time.time()
    raw_path = out / "raw.jsonl"
    with raw_path.open("w", encoding="utf-8", buffering=1) as fh:
        for task in TASKS:
            require_task_runtime(task)
            for condition in CONDITIONS:
                scores: dict[str, float] = {}
                ledger = PeerRoleLedger(require_selection=True, require_terminal_outcome=True)
                for episode in range(2):
                    try:
                        record = run_episode(
                            task,
                            condition,
                            episode,
                            runs_dir,
                            scores,
                            ledger,
                        )
                    except Exception as exc:
                        failure = {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "event": "episode_failed",
                            "task_id": task,
                            "condition": condition,
                            "episode": episode,
                            "error_type": type(exc).__name__,
                            "error": str(exc),
                            "traceback": traceback.format_exc(),
                        }
                        fh.write(json.dumps(failure, sort_keys=True) + "\n")
                        fh.flush()
                        raise
                    records.append(record)
                    fh.write(json.dumps(record, sort_keys=True) + "\n")
                    fh.flush()
    scores = [r["terminal_outcome"]["partial_score"] for r in records]
    summary = {
        "completed_episodes": len(records),
        "wall_seconds": round(time.time() - started, 3),
        "mean_terminal_score": round(sum(scores) / max(1, len(scores)), 4),
        "min_terminal_score": min(scores) if scores else None,
        "max_terminal_score": max(scores) if scores else None,
        "artifact_lineage_all_unchanged": all(r["artifact_unchanged"] for r in records),
        "all_followup_assignments_consumed": all(
            r["assignment_consumed"] for r in records if r["episode"] > 0
        ),
        "consumer_actions_materialized": all(
            r["consumer_action"]["output_artifact_sha256"]
            == r["consumer_output_artifact_sha256"]
            for r in records
        ),
        "all_ledgers_strict": all(
            r["ledger"]["evidence_count"] == 2 and r["ledger"]["assignment_count"] == 1
            for r in records if r["episode"] == 1
        ),
        "scientific_claim_allowed": False,
        "blocking_reasons": [
            "native grader is not a full sandbox; this wrapper protects tests but candidate source can read sibling reports",
            "two task families and two seeds are a protocol smoke slice, not a benchmark estimate",
            "fixture peers are not a trained selector or LLM agents",
        ],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
