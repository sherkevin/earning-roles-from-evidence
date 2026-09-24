"""CPU-only v2 amendment checks; no provider calls or AppWorld task execution."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import aamas_peer_judgment_smoke_v2 as smoke


def proposal() -> dict:
    return {"summary": "One unpaid share", "requests": [
        {"recipient_email": "a@example.com", "amount_usd": 12.5,
         "basis": "public task-data record", "source_steps": [1]}], "uncertainties": []}


class FakeAPI:
    def __init__(self, answers):
        self.answers = list(answers)
        self.attempts = 0
        self.max_attempts = len(self.answers)

    def generate(self, messages, max_tokens):
        answer = self.answers[self.attempts]
        self.attempts += 1
        if isinstance(answer, Exception):
            raise answer
        return answer


class FakeParser:
    def extract_code_and_fix_content(self, answer):
        if "```python" in answer:
            return "print(apis.venmo.show_sent_payment_requests())", answer
        return "", answer


class FakeWorld:
    def __init__(self, audit):
        self.audit = audit

    def execute(self, code):
        self.audit.append({"method": "get", "app": "venmo", "api": "show_sent_payment_requests",
                           "public_read_observation": True})
        return "[]"


class FakeRequester:
    def __init__(self):
        self.response = {"message": "simulated API error"}

    def request(self, app, api, **kwargs):
        return self.response

    def _post(self, *args, **kwargs):
        return None

    def _put(self, *args, **kwargs):
        return None

    def _patch(self, *args, **kwargs):
        return None

    def _delete(self, *args, **kwargs):
        return None


class FakeGateWorld:
    def __init__(self):
        self.requester = FakeRequester()


def state():
    return {"timeout_retry_used": False, "world_execute_count": 0,
            "validation_rejections": {"producer": 0, "consumer_review": 0}}


class AmendmentTests(unittest.TestCase):
    def test_v1_artifact_hashes_and_fresh_population(self):
        cfg = smoke.load_config()
        self.assertEqual(cfg["native_task_ids_in_order"], ["22cc237_2", "3c13f5a_2"])
        self.assertEqual(cfg["global_attempt_cap"], 76)

    def test_unsupported_proposal_gets_charged_feedback_then_real_read(self):
        item = f"<proposal>{json.dumps(proposal())}</proposal>"
        api = FakeAPI([item, "```python\nprint(apis.venmo.show_sent_payment_requests())\n```", item])
        audit = []
        messages = [{"role": "user", "content": "produce"}]
        run_state = state()
        with tempfile.TemporaryDirectory() as temporary:
            accepted, steps = smoke.phase_loop(FakeWorld(audit), FakeParser(), api,
                messages, Path(temporary) / "raw.jsonl", "producer", "proposal", 2048,
                smoke.Secrets(), audit, run_state,
                lambda value, observed: smoke.validate_proposal_v2(value, observed, smoke.Secrets()))
        self.assertEqual(accepted, proposal())
        self.assertEqual(api.attempts, 3)
        self.assertEqual(run_state["validation_rejections"]["producer"], 1)
        self.assertEqual(run_state["world_execute_count"], 1)
        self.assertEqual(steps[0]["public_task_data_reads"], 1)
        self.assertTrue(any("Validation error" in message["content"] for message in messages))

    def test_docs_only_or_error_get_does_not_ground_proposal(self):
        candidate = proposal()
        with self.assertRaisesRegex(ValueError, "public task-data read"):
            smoke.validate_proposal_v2(candidate, [{"step": 1, "public_task_data_reads": 0}],
                                       smoke.Secrets())
        with self.assertRaisesRegex(ValueError, "must cite"):
            smoke.validate_proposal_v2(candidate, [
                {"step": 1, "public_task_data_reads": 0},
                {"step": 2, "public_task_data_reads": 1}], smoke.Secrets())
        world = FakeGateWorld()
        with tempfile.TemporaryDirectory() as temporary:
            audit = smoke.api_guard(world, "producer", smoke.Secrets(),
                                    Path(temporary) / "raw.jsonl")
            world.requester.request("venmo", "show_sent_payment_requests")
            self.assertFalse(audit[-1]["public_read_observation"])
            world.requester._pj_original_request.__self__.response = {"detail": "denied"}
            world.requester.request("venmo", "show_sent_payment_requests")
            self.assertFalse(audit[-1]["public_read_observation"])
            world.requester._pj_original_request.__self__.response = []
            world.requester.request("venmo", "show_sent_payment_requests")
            self.assertTrue(audit[-1]["public_read_observation"])

    def test_judgment_schema_repair_uses_remaining_review_cap(self):
        invalid = ('<judgment>{"verdict":"accept","intends_to_use_proposal":null,'
                   '"review_reason":"read","planned_repair":null}</judgment>')
        valid = ('<judgment>{"verdict":"accept","intends_to_use_proposal":true,'
                 '"review_reason":"read","planned_repair":null}</judgment>')
        api = FakeAPI([invalid, valid])
        messages = [{"role": "user", "content": "review"}]
        run_state = state()
        with tempfile.TemporaryDirectory() as temporary:
            judgment, _ = smoke.phase_loop(FakeWorld([]), FakeParser(), api,
                messages, Path(temporary) / "raw.jsonl", "consumer_review", "judgment",
                2048, smoke.Secrets(), [], run_state,
                lambda value, steps: smoke.validate_judgment(value, smoke.Secrets()))
        self.assertEqual(judgment["verdict"], "accept")
        self.assertEqual(api.attempts, 2)
        self.assertEqual(run_state["validation_rejections"]["consumer_review"], 1)
        self.assertEqual(run_state["world_execute_count"], 0)

    def test_one_timeout_retry_is_charged_before_world_execution_only(self):
        api = FakeAPI([TimeoutError("provider timed out"), "valid response"])
        run_state = state()
        old_sleep = smoke.time.sleep
        smoke.time.sleep = lambda seconds: None
        try:
            with tempfile.TemporaryDirectory() as temporary:
                answer = smoke.generate_with_retry(api, [], Path(temporary) / "raw.jsonl",
                                                   2048, run_state)
            self.assertEqual(answer, "valid response")
            self.assertEqual(api.attempts, 2)
            self.assertTrue(run_state["timeout_retry_used"])

            api = FakeAPI([TimeoutError("after read"), "must not run"])
            run_state = state()
            run_state["world_execute_count"] = 1
            with tempfile.TemporaryDirectory() as temporary:
                with self.assertRaises(TimeoutError):
                    smoke.generate_with_retry(api, [], Path(temporary) / "raw.jsonl",
                                              2048, run_state)
            self.assertEqual(api.attempts, 1)
        finally:
            smoke.time.sleep = old_sleep

    def test_attempted_proposal_use_is_distinct_from_created_request(self):
        calls = [{"app": "venmo", "api": "create_payment_request", "ok": True,
                  "arguments": {"user_email": "a@example.com", "amount": 12.5},
                  "payment_request_created": False}]
        use = smoke.actual_use(proposal(), calls)
        self.assertTrue(use["proposal_actually_used"])
        self.assertFalse(use["proposal_successfully_applied"])
        calls[0]["payment_request_created"] = True
        self.assertTrue(smoke.actual_use(proposal(), calls)["proposal_successfully_applied"])


if __name__ == "__main__":
    unittest.main()
