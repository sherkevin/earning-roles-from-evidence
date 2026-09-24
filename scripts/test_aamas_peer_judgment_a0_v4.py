#!/usr/bin/env python3
"""Synthetic-only A0 contract tests; no task outcomes or LLM calls."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import aamas_peer_judgment_a0_v4 as a0


WORLD = "synthetic_producer_world"


def ref(identifier: str, kind: str, path: str, value):
    return {"kind": kind, "source_id": identifier, "path": path, "value": value}


def sources():
    data = {"id": "tx1001", "transaction_id": 1001,
            "relationship": "roommate", "date": "today"}
    task = {"instruction": "Like all roommate transactions from today.", "supervisor": "Example"}
    doc = {"app_name": "venmo", "api_name": "like_transaction", "method": "POST"}
    return {
        "task_spec": {"kind": "task_spec", "value": task, "world": WORLD,
                      "actor": "A", "step": None, "response_sha256": "task"},
        "p1.c1": {"kind": "api_observation", "value": data, "world": WORLD,
                  "actor": "A", "step": 1, "app": "venmo", "api": "show_social_feed",
                  "method": "get", "response_sha256": "data"},
        "p1.c2": {"kind": "api_doc", "value": doc, "world": WORLD,
                  "actor": "A", "step": 1, "app": "api_docs", "api": "show_api_doc",
                  "method": "get", "doc_app": "venmo", "doc_api": "like_transaction",
                  "response_sha256": "doc"},
    }


def claim(field, value, path):
    return {"field": field, "value": value,
            "source_refs": [ref("p1.c1", "api_observation", path, value)],
            "derivation": None}


def proposal():
    return {"summary": "A synthetic example only", "candidate_actions": [{
        "action_id": "a1", "app": "venmo", "api": "like_transaction",
        "target": "tx1001", "arguments": {"transaction_id": 1001},
        "selection_claim": {"field": "selection", "value": "roommate today",
            "source_refs": [ref("p1.c1", "api_observation", "/relationship", "roommate"),
                            ref("p1.c1", "api_observation", "/date", "today")],
            "derivation": {"expression": "relationship is roommate and date is today",
                "operands": [
                    {"name": "relationship", "value": "roommate",
                     "source_refs": [ref("p1.c1", "api_observation", "/relationship", "roommate")]},
                    {"name": "date", "value": "today",
                     "source_refs": [ref("p1.c1", "api_observation", "/date", "today")]}
                ]}},
        "claims": [claim("target", "tx1001", "/id"),
                   claim("arguments.transaction_id", 1001, "/transaction_id")]
    }], "coverage": {"scope": "all synthetic matching transactions", "exhaustive": None,
                      "pagination_and_stopping_basis": "not asserted in this fixture",
                      "source_refs": [ref("p1.c1", "api_observation", "/date", "today")]},
            "no_action": None, "uncertainties": []}


class A0ContractTests(unittest.TestCase):
    def test_typed_claims_enrich_actual_public_source(self):
        value = a0.validate_proposal(proposal(), sources(), WORLD, a0.base.Secrets())
        source = value["candidate_actions"][0]["claims"][0]["source_refs"][0]
        self.assertEqual(source["world"], WORLD)
        self.assertEqual(source["response_sha256"], "data")
        self.assertEqual(value["provenance_status"],
                         "STRUCTURALLY_VERIFIED_ONLY_SEMANTIC_REVIEW_PENDING")

    def test_wrong_public_value_and_uncited_numeric_substring_fail(self):
        wrong = proposal()
        wrong["candidate_actions"][0]["claims"][1]["source_refs"][0]["value"] = 1
        with self.assertRaises(a0.ArtifactInvalid):
            a0.validate_proposal(wrong, sources(), WORLD, a0.base.Secrets())
        typed = sources()
        typed["p1.c1"]["value"]["transaction_id"] = True
        with self.assertRaises(a0.ArtifactInvalid):
            a0.source_ref(ref("p1.c1", "api_observation", "/transaction_id", 1), typed, WORLD)

    def test_selection_cannot_use_unrelated_get_without_derivation(self):
        bad = proposal()
        bad["candidate_actions"][0]["selection_claim"]["derivation"] = None
        with self.assertRaises(a0.ArtifactInvalid):
            a0.validate_proposal(bad, sources(), WORLD, a0.base.Secrets())

    def test_review_citation_requires_actual_public_task_get(self):
        judgment = {"verdict": "accept", "planned_action_ids": ["a1"],
                    "review_reason": "checked", "planned_repair": None,
                    "review_source_steps": [1]}
        with self.assertRaises(a0.ArtifactInvalid):
            a0.validate_judgment(judgment, proposal(), a0.base.Secrets(),
                                 [{"step": 1, "public_task_data_reads": 0}])
        a0.validate_judgment(judgment, proposal(), a0.base.Secrets(),
                             [{"step": 1, "public_task_data_reads": 1}])

    def test_one_write_cannot_match_two_rows_and_secret_is_redacted(self):
        artifact = proposal()
        second = copy.deepcopy(artifact["candidate_actions"][0])
        second["action_id"] = "a2"
        artifact["candidate_actions"].append(second)
        call = {"app": "venmo", "api": "like_transaction", "method": "post",
                "origin": "actor",
                "api_path": "/venmo/transactions/1001/likes",
                "arguments": {"transaction_id": 1001, "access_token": "secret-token-12345",
                              "raise_on_failure": None}, "ok": True,
                "response": {"message": "Liked transaction."}}
        result = a0.actual_use(artifact, [call], {"planned_action_ids": ["a1", "a2"]},
                               a0.base.Secrets())
        self.assertEqual(result["matched_attempted_action_ids"], ["a1"])
        self.assertEqual(result["not_matched_action_ids"], ["a2"])
        self.assertNotIn("secret-token-12345", a0.canonical(result))

    def test_extra_material_argument_prevents_exact_match(self):
        call = {"app": "venmo", "api": "like_transaction", "method": "post",
                "origin": "actor",
                "api_path": "/venmo/transactions/1001/likes",
                "arguments": {"transaction_id": 1001, "comment": "unexpected"},
                "ok": True, "response": {"message": "Liked transaction."}}
        result = a0.actual_use(proposal(), [call], {"planned_action_ids": ["a1"]},
                               a0.base.Secrets())
        self.assertEqual(result["matched_attempted_action_ids"], [])
        self.assertEqual(len(result["extra_or_modified_write_calls"]), 1)

    def test_timeout_after_prior_world_step_retries_same_request_once(self):
        cfg = a0.load_config()
        messages = [{"role": "user", "content": "synthetic transport test"}]

        class SyntheticTransport:
            def __init__(self, path, max_attempts, timeout_count):
                self.path, self.max_attempts = path, max_attempts
                self.attempts, self.timeout_count = 0, timeout_count
                self.requests = []

            def generate(self, history, max_tokens):
                self.attempts += 1
                request = {"model": cfg["model_request"], "messages": history,
                           "max_tokens": max_tokens, "temperature": cfg["temperature"],
                           "stream": False}
                self.requests.append(json.dumps(request).encode())
                a0.prior.log(self.path, "request_start", attempt=self.attempts,
                             request=request)
                if self.attempts <= self.timeout_count:
                    a0.prior.log(self.path, "request_error", attempt=self.attempts,
                                 error_type="TimeoutError")
                    raise TimeoutError("synthetic unreturned response")
                a0.prior.log(self.path, "response", attempt=self.attempts,
                             response={"content": [{"text": "ok"}]})
                return "ok"

        with tempfile.TemporaryDirectory() as folder, patch.object(a0.time, "sleep"):
            raw = Path(folder) / "raw.jsonl"
            state = {"world_execute_count": 3, "timeout_retry_used": False}
            api = SyntheticTransport(raw, 12, 1)
            self.assertEqual(a0.generate_with_retry(api, messages, raw, cfg, state), "ok")
            self.assertEqual(api.attempts, 2)
            self.assertEqual(api.requests[0], api.requests[1])
            self.assertTrue(state["timeout_retry_used"])
            events = [json.loads(line) for line in raw.read_text().splitlines()]
            retry = [row["payload"] for row in events
                     if row["event"] == "transport_backoff"]
            self.assertEqual(len(retry), 1)
            self.assertEqual(retry[0]["retry_kind"], "same_request_unreturned_timeout")
            self.assertEqual(retry[0]["world_execute_count_before"], 3)
            self.assertEqual(retry[0]["charged_attempts"], 1)

            raw2 = Path(folder) / "raw2.jsonl"
            state2 = {"world_execute_count": 2, "timeout_retry_used": False}
            api2 = SyntheticTransport(raw2, 12, 2)
            with self.assertRaises(a0.TransportUnknown):
                a0.generate_with_retry(api2, messages, raw2, cfg, state2)
            self.assertEqual(api2.attempts, 2)
            self.assertTrue(state2["timeout_retry_used"])

            raw3 = Path(folder) / "raw3.jsonl"
            state3 = {"world_execute_count": 2, "timeout_retry_used": False}
            api3 = SyntheticTransport(raw3, 1, 1)
            with self.assertRaises(a0.TransportUnknown):
                a0.generate_with_retry(api3, messages, raw3, cfg, state3)
            self.assertEqual(api3.attempts, 1)
            self.assertFalse(state3["timeout_retry_used"])


if __name__ == "__main__":
    unittest.main()
