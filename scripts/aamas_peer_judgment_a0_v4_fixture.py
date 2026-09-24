#!/usr/bin/env python3
"""Zero-LLM native AppWorld guard/state fixture for prospective A0."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys
import traceback

import aamas_peer_judgment_a0_v4 as a0
import aamas_real_probe as prior
import aamas_peer_judgment_smoke_v4 as base


def main() -> None:
    cfg = a0.load_config()
    root = a0.ROOT / cfg["preflight"]["paths"]["native_fixture"]
    root.mkdir(parents=True, exist_ok=True)
    attempts = root / "attempts"
    attempts.mkdir(exist_ok=True)
    # Preserve a fixture failure as its own attempt; `result.json` is the
    # latest machine-readable preflight pointer, never the only evidence.
    if (root / "result.json").exists():
        first = attempts / "attempt_0001"
        if not first.exists():
            first.mkdir()
            for name in ("raw.jsonl", "result.json"):
                old = root / name
                if old.exists():
                    shutil.move(str(old), str(first / name))
    attempt_number = len([p for p in attempts.iterdir() if p.is_dir()]) + 1
    attempt_dir = attempts / f"attempt_{attempt_number:04d}"
    attempt_dir.mkdir(exist_ok=False)
    raw = attempt_dir / "raw.jsonl"
    secrets = base.Secrets()
    a0.safe_log(secrets)
    task_id = cfg["episodes_in_order"][0]["task_id"]
    config_hash = prior.digest(a0.CONFIG)
    runner_hash = prior.digest(a0.__file__)
    suffix = hashlib.sha256((task_id + config_hash + f":fixture:{attempt_number}").encode()).hexdigest()[:16]
    producer_name = "pa0_fix_prod_" + suffix
    consumer_name = "pa0_fix_cons_" + suffix
    result = {"ok": False, "config_sha256": config_hash, "runner_sha256": runner_hash,
              "task_id": task_id, "seed": cfg["world_seed"], "llm_api_calls": 0,
              "native_guard_enabled": None, "producer_write_blocked": False,
              "consumer_write_allowed": False, "producer_state_unchanged": False,
              "initial_model_hashes_equal": False, "initial_public_probe_equal": False,
              "producer_api_calls": 0, "consumer_api_calls": 0, "error": None,
              "attempt_number": attempt_number}
    prior.log(raw, "fixture_config", config_sha256=config_hash, runner_sha256=runner_hash,
              task_id=task_id, seed=cfg["world_seed"], llm_api_calls=0,
              experiment_names=[producer_name, consumer_name])
    deferred: list[tuple[str, dict]] = []
    sources: dict[str, dict] = {}
    try:
        AppWorld, _ = prior.initialize_runtime()
        for name in (producer_name, consumer_name):
            native = prior.APP / "experiments/outputs" / name
            if native.exists():
                raise a0.InfrastructureError("Refuse native fixture output overwrite")
        with AppWorld(task_id=task_id, experiment_name=producer_name,
                      load_ground_truth=False, random_seed=cfg["world_seed"],
                      raise_on_extra_parameters=True) as producer:
            base.install_native_log_scrubber(producer,
                prior.APP / "experiments/outputs" / producer_name, secrets)
            if producer.task.ground_truth is not None or not producer.raise_on_unsafe_execution:
                raise a0.InfrastructureError("Unsafe native producer fixture world")
            result["native_guard_enabled"] = True
            before = a0.task_state_hashes(producer)
            producer_probe = a0.initial_public_probe(producer, "producer_fixture", "A",
                                                      secrets, raw, deferred, sources)
            context = {"step": 1}
            audit = a0.api_guard(producer, "producer", "A", secrets, raw, deferred,
                                 context, sources)
            docs = producer.execute("print(apis.api_docs.show_app_descriptions())")
            a0.flush(raw, deferred)
            context["step"] = 2
            datum = producer.execute("print(apis.phone.get_current_date_and_time())")
            a0.flush(raw, deferred)
            context["step"] = 3
            auth_read = producer.execute(
                "profile = apis.supervisor.show_profile()\n"
                "passwords = apis.supervisor.show_account_passwords()\n"
                "venmo_password = next(p['password'] for p in passwords if p['account_name']=='venmo')\n"
                "venmo_token = apis.venmo.login(username=profile['email'], password=venmo_password)['access_token']\n"
                "fixture_feed = apis.venmo.show_social_feed(access_token=venmo_token, page_index=0, page_limit=5)\n"
                "print({'feed_count': len(fixture_feed)})")
            a0.flush(raw, deferred)
            context["step"] = 4
            rejected = producer.execute("print(apis.supervisor.complete_task(answer=None))")
            a0.flush(raw, deferred)
            prior.log(raw, "fixture_observations", docs=docs, task_get=datum,
                      authenticated_venmo_get=auth_read, blocked_write=rejected)
            result["producer_write_blocked"] = (
                "Read-only actor attempted a task write" in rejected or
                "Direct write transport blocked" in rejected)
            after = a0.task_state_hashes(producer)
            result["producer_state_unchanged"] = before == after
            result["producer_api_calls"] = len(audit)
            result["producer_docs_ok"] = "Execution failed" not in docs
            result["producer_public_get_ok"] = (
                "Execution failed" not in datum and
                any(call.get("public_read_observation") for call in audit))
            result["producer_authenticated_venmo_get_ok"] = (
                "Execution failed" not in auth_read and
                any(call["app"] == "venmo" and call["api"] == "show_social_feed"
                    and call.get("ok") for call in audit))
            result["producer_initial_model_hashes_sha256"] = a0.sha_text(a0.canonical(before))
            result["producer_after_model_hashes_sha256"] = a0.sha_text(a0.canonical(after))
            producer.save()
        base.sanitize_native_logs(prior.APP / "experiments/outputs" / producer_name, secrets)
        with AppWorld(task_id=task_id, experiment_name=consumer_name,
                      load_ground_truth=False, random_seed=cfg["world_seed"],
                      raise_on_extra_parameters=True) as consumer:
            base.install_native_log_scrubber(consumer,
                prior.APP / "experiments/outputs" / consumer_name, secrets)
            if consumer.task.ground_truth is not None or not consumer.raise_on_unsafe_execution:
                raise a0.InfrastructureError("Unsafe native consumer fixture world")
            consumer_before = a0.task_state_hashes(consumer)
            result["initial_model_hashes_equal"] = before == consumer_before
            consumer_probe = a0.initial_public_probe(consumer, "consumer_fixture", "B",
                                                      secrets, raw, deferred, sources)
            result["initial_public_probe_equal"] = producer_probe == consumer_probe
            context = {"step": 1}
            audit = a0.api_guard(consumer, "consumer_action", "B", secrets, raw,
                                 deferred, context, sources)
            prepared = consumer.execute(
                "profile = apis.supervisor.show_profile()\n"
                "passwords = apis.supervisor.show_account_passwords()\n"
                "venmo_password = next(p['password'] for p in passwords if p['account_name']=='venmo')\n"
                "venmo_token = apis.venmo.login(username=profile['email'], password=venmo_password)['access_token']\n"
                "fixture_feed = apis.venmo.show_social_feed(access_token=venmo_token, page_index=0, page_limit=5)\n"
                "print({'feed_count': len(fixture_feed)})")
            a0.flush(raw, deferred)
            context["step"] = 2
            acted = consumer.execute(
                "print(apis.venmo.create_transaction_comment("
                "access_token=venmo_token, transaction_id=fixture_feed[0]['transaction_id'], "
                "comment='A0 native reset-world fixture'))")
            a0.flush(raw, deferred)
            result["consumer_prepare_ok"] = "Execution failed" not in prepared
            result["consumer_authenticated_venmo_write_ok"] = (
                "Execution failed" not in acted and
                any(call["app"] == "venmo" and call["api"] == "create_transaction_comment"
                        and call.get("ok") for call in audit))
            context["step"] = 3
            finalized = consumer.execute("print(apis.supervisor.complete_task(answer=None))")
            a0.flush(raw, deferred)
            completed = consumer.task_completed()
            a0.flush(raw, deferred)
            result["consumer_write_allowed"] = (
                result["consumer_authenticated_venmo_write_ok"] and
                "Execution failed" not in finalized and completed
                and any(call["app"] == "supervisor" and call["api"] == "complete_task"
                        and call.get("ok") for call in audit))
            prior.log(raw, "fixture_consumer_observations", prepared=prepared,
                      authenticated_write=acted, finalized=finalized)
            result["consumer_api_calls"] = len(audit)
            result["consumer_initial_model_hashes_sha256"] = a0.sha_text(a0.canonical(consumer_before))
            consumer.save()
        base.sanitize_native_logs(prior.APP / "experiments/outputs" / consumer_name, secrets)
        result["persisted_public_api_events"] = sum(
            json.loads(line)["event"] == "public_api_call" for line in raw.read_text().splitlines())
        result["persisted_write_block_events"] = sum(
            json.loads(line)["event"] == "write_blocked" for line in raw.read_text().splitlines())
        result["ok"] = all(result[key] for key in (
            "native_guard_enabled", "producer_write_blocked", "consumer_write_allowed",
            "producer_state_unchanged", "initial_model_hashes_equal", "initial_public_probe_equal",
            "producer_docs_ok", "producer_public_get_ok", "consumer_prepare_ok",
            "producer_authenticated_venmo_get_ok", "consumer_authenticated_venmo_write_ok")) and (
            result["persisted_public_api_events"] >= 12 and
            result["persisted_write_block_events"] >= 1)
        if not result["ok"]:
            raise AssertionError("Native fixture failed contract assertion")
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": secrets.scrub(str(exc)),
                           "traceback": secrets.scrub(traceback.format_exc())}
        prior.log(raw, "fixture_error", **result["error"])
    finally:
        a0.flush(raw, deferred)
        prior.save(attempt_dir / "result.json", secrets.scrub(result))
        prior.save(root / "result.json", secrets.scrub(result))
        prior.log(raw, "fixture_result", **result)
    print(a0.canonical(result))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
