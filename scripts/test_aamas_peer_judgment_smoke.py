"""CPU-only contract tests; these never initialize a task world or call a model."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import aamas_peer_judgment_smoke as smoke


class FakeRequester:
    def __init__(self) -> None:
        self.calls = []

    def request(self, app: str, api: str, **kwargs):
        self.calls.append((app, api, kwargs))
        return {"ok": True}

    def _post(self, url: str, *args, **kwargs):
        return {"posted": url}

    def _put(self, url: str, *args, **kwargs):
        return {"put": url}

    def _patch(self, url: str, *args, **kwargs):
        return {"patched": url}

    def _delete(self, url: str, *args, **kwargs):
        return {"deleted": url}


class FakeWorld:
    def __init__(self) -> None:
        self.requester = FakeRequester()


class FakeAPI:
    def __init__(self, answers):
        self.answers = list(answers)
        self.attempts = 0
        self.max_attempts = len(self.answers)

    def generate(self, messages, max_tokens):
        answer = self.answers[self.attempts]
        self.attempts += 1
        return answer


class FakeParser:
    def extract_code_and_fix_content(self, answer):
        return "print(1)", answer


class FakeExecutionWorld:
    def execute(self, code):
        return "1"

    def task_completed(self):
        return False


class GuardTests(unittest.TestCase):
    def test_review_gate_blocks_write_then_action_gate_restores_it(self) -> None:
        world = FakeWorld()
        secrets = smoke.Secrets()
        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary) / "raw.jsonl"
            review = smoke.api_guard(world, "consumer_review", secrets, raw)
            world.requester.request("venmo", "show_sent_payment_requests")
            self.assertEqual(review[0]["method"], "get")
            with self.assertRaises(PermissionError):
                world.requester.request("venmo", "create_payment_request")
            with self.assertRaises(PermissionError):
                world.requester._post("/payment_requests")
            self.assertEqual(len(world.requester.calls), 1)

            action = smoke.api_guard(world, "consumer_action", secrets, raw)
            world.requester.request("venmo", "create_payment_request",
                                    user_email="a@example.com", amount=12.5)
            self.assertEqual(action[0]["method"], "post")
            self.assertEqual(world.requester._post("/payment_requests"),
                             {"posted": "/payment_requests"})
            self.assertEqual(len(world.requester.calls), 2)

    def test_secret_values_are_removed_even_when_repeated_in_code(self) -> None:
        secrets = smoke.Secrets()
        secrets.observe({"access_token": "realToken123456", "password": "Pass123456"})
        payload = {"code": "apis.venmo.show_users(access_token='realToken123456')",
                   "output": '{"password": "Pass123456"}'}
        cleaned = secrets.scrub(payload)
        self.assertNotIn("realToken123456", str(cleaned))
        self.assertNotIn("Pass123456", str(cleaned))
        with tempfile.TemporaryDirectory() as temporary:
            native = Path(temporary)
            log_dir = native / "tasks" / "task" / "logs"
            log_dir.mkdir(parents=True)
            markdown = log_dir / "environment_io.md"
            markdown.write_text("access_token='realToken123456'\n")
            smoke.sanitize_native_logs(native, secrets)
            self.assertNotIn("realToken123456", markdown.read_text())

    def test_proposal_requires_observed_sources_and_no_credentials(self) -> None:
        secrets = smoke.Secrets()
        proposal = {"summary": "Two outstanding shares", "requests": [
            {"recipient_email": "a@example.com", "amount_usd": 12.5,
             "basis": "public note and paid record", "source_steps": [1, 2]}],
            "uncertainties": []}
        self.assertEqual(smoke.validate_proposal(proposal, {1, 2}, secrets), proposal)
        with self.assertRaises(ValueError):
            smoke.validate_proposal(proposal, {1}, secrets)
        secrets.observe({"access_token": "realToken123456"})
        proposal["summary"] = "realToken123456"
        with self.assertRaises(ValueError):
            smoke.validate_proposal(proposal, {1, 2}, secrets)

    def test_public_repl_guard_blocks_private_paths_and_requester(self) -> None:
        smoke.safe_code("print(apis.api_docs.show_app_descriptions())")
        with self.assertRaises(ValueError):
            smoke.safe_code("requester.request('venmo', 'create_payment_request')")
        with self.assertRaises(ValueError):
            smoke.safe_code("open('/tmp/private_data', 'r')")

    def test_actual_use_survives_missing_amount(self) -> None:
        proposal = {"requests": [{"recipient_email": "a@example.com", "amount_usd": 12.5}]}
        calls = [{"app": "venmo", "api": "create_payment_request", "ok": True,
                  "arguments": {"user_email": "a@example.com", "amount": None}}]
        use = smoke.actual_use(proposal, calls)
        self.assertFalse(use["proposal_actually_used"])
        self.assertEqual(use["proposal_rows_reworked_in_action"][0]["actual_amounts"], [None])
        calls[0]["arguments"]["amount"] = 12.5
        use = smoke.actual_use(proposal, calls)
        self.assertTrue(use["proposal_actually_used"])

    def test_judgment_stays_in_consumer_history_and_action_budget_seals(self) -> None:
        secrets = smoke.Secrets()
        messages = [{"role": "user", "content": "review"}]
        judgment_text = ('<judgment>{"verdict":"accept","intends_to_use_proposal":true,'
                         '"review_reason":"checked public data","planned_repair":null}</judgment>')
        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary) / "raw.jsonl"
            artifact, steps = smoke.phase_loop(FakeExecutionWorld(), FakeParser(),
                FakeAPI([judgment_text]), messages, raw, "consumer_review", "judgment",
                2048, secrets, [])
            self.assertEqual(artifact["verdict"], "accept")
            self.assertFalse(steps)
            self.assertEqual(messages[-1], {"role": "assistant", "content": judgment_text})
            _, action_steps = smoke.phase_loop(FakeExecutionWorld(), FakeParser(),
                FakeAPI(["```python\nprint(1)\n```", "```python\nprint(1)\n```"]),
                messages, raw, "consumer_action", None, 2048, secrets, [])
            self.assertEqual(len(action_steps), 2)


if __name__ == "__main__":
    unittest.main()
