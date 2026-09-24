#!/usr/bin/env python3
"""Deterministic zero-LLM replay of the actual A0 v4 55-page source burst."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

import aamas_bounded_source_receipts as bounded
from aamas_peer_judgment_smoke_v4 import Secrets


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "artifacts/experiments/aamas2027/peer_judgment_a0_v4_20260923/episodes/2a163ab_1/raw.jsonl"


def replay_step_six():
    rows, sources, observation = [], {}, None
    for line in RAW.read_text().splitlines():
        event = json.loads(line)
        payload = event["payload"]
        if event["event"] == "public_api_call" and payload.get("step") == 6:
            rows.append(payload)
            identifier = payload.get("source_id")
            if identifier:
                sources[identifier] = {
                    "kind": "api_observation", "value": payload["response"],
                    "world": payload["world"], "app": payload["app"],
                    "api": payload["api"], "method": payload["method"],
                    "response_sha256": payload["response_sha256"],
                }
        elif event["event"] == "environment_observation" and payload.get("step") == 6:
            observation = payload["observation"]
    if observation is None:
        raise AssertionError("Actual v4 step-six observation is missing")
    return rows, sources, observation


class BoundedSourceReceiptTests(unittest.TestCase):
    def test_actual_55_page_replay_is_bounded_and_exactly_lookupable(self):
        raw_sha_before = hashlib.sha256(RAW.read_bytes()).hexdigest()
        rows, sources, observation = replay_step_six()
        world = rows[0]["world"]
        secrets = Secrets()
        self.assertEqual(len(rows), 56)  # 55 task GETs plus one login call.
        self.assertEqual(len(sources), 55)
        self.assertGreater(sum(len(bounded.canonical(x["response"]).encode()) for x in rows), 300_000)

        feedback = bounded.bounded_observation_feedback(
            observation, rows, sources, world, secrets.scrub, max_bytes=4096)
        self.assertLessEqual(len(feedback.encode()), 4096)
        payload = json.loads(feedback)
        self.assertEqual(payload["source_count"], 55)
        self.assertEqual(payload["source_id_span_exact"], "p6.c20..p6.c74")
        self.assertTrue(payload["observation_truncated"])
        self.assertNotIn('"response":', feedback)  # No 55 response bodies are copied.

        seen = []
        offset = 0
        while True:
            page_text = bounded.source_index_page(rows, sources, world, secrets.scrub,
                                                  offset=offset, limit=8, max_bytes=4096)
            self.assertLessEqual(len(page_text.encode()), 4096)
            page = json.loads(page_text)
            seen.extend(item["source_id"] for item in page["sources"])
            if page["next_offset"] is None:
                break
            offset = page["next_offset"]
        self.assertEqual(seen, [row["source_id"] for row in rows if row.get("source_id")])

        last = seen[-1]
        actual_value = sources[last]["value"][0]["transaction_id"]
        exact = json.loads(bounded.lookup_public_source(
            last, "/0/transaction_id", sources, world, secrets.scrub, max_bytes=4096))
        self.assertEqual(exact["status"], "exact")
        self.assertEqual(exact["source_ref"], {
            "kind": "api_observation", "source_id": last,
            "path": "/0/transaction_id", "value": actual_value})
        self.assertEqual(exact["response_sha256"], sources[last]["response_sha256"])
        self.assertEqual(hashlib.sha256(RAW.read_bytes()).hexdigest(), raw_sha_before)

    def test_oversize_lookup_does_not_pretend_partial_value_is_evidence(self):
        rows, sources, _ = replay_step_six()
        identifier = next(row["source_id"] for row in rows if row.get("source_id"))
        result = json.loads(bounded.lookup_public_source(
            identifier, "", sources, rows[0]["world"], Secrets().scrub, max_bytes=512))
        self.assertEqual(result["status"], "requires_narrower_pointer")
        self.assertNotIn("source_ref", result)

    def test_secret_scrubbing_world_isolation_and_digest_integrity(self):
        secrets = Secrets()
        secret = "private-token-12345"
        secrets.observe({"access_token": secret})
        safe_value = secrets.scrub({"message": f"Bearer {secret}", "value": 7})
        source = {"p1.c1": {"kind": "api_observation", "value": safe_value,
                             "world": "world-A", "app": "venmo", "api": "get_item",
                             "method": "get", "response_sha256": bounded.digest(safe_value)}}
        row = {"source_id": "p1.c1", "ok": True, "app": "venmo", "api": "get_item",
               "response_sha256": source["p1.c1"]["response_sha256"]}
        feedback = bounded.bounded_observation_feedback(
            f"access_token={secret}", [row], source, "world-A", secrets.scrub,
            max_bytes=1024)
        lookup = bounded.lookup_public_source(
            "p1.c1", "/message", source, "world-A", secrets.scrub)
        self.assertNotIn(secret, feedback + lookup)
        self.assertIn("[REDACTED]", feedback + lookup)
        with self.assertRaises(bounded.SourceReceiptError):
            bounded.lookup_public_source("p1.c1", "/value", source, "world-B", secrets.scrub)
        bad = {"p1.c1": {**source["p1.c1"], "value": {"message": "tampered"}}}
        with self.assertRaises(bounded.SourceReceiptError):
            bounded.lookup_public_source("p1.c1", "/message", bad, "world-A", secrets.scrub)

    def test_noncontiguous_ids_have_no_invented_span(self):
        rows, sources, _ = replay_step_six()
        skipped = [row for row in rows if row.get("source_id") != "p6.c49"]
        feedback = json.loads(bounded.bounded_observation_feedback(
            "ok", skipped, sources, rows[0]["world"], Secrets().scrub))
        self.assertEqual(feedback["source_count"], 54)
        self.assertIsNone(feedback["source_id_span_exact"])


if __name__ == "__main__":
    unittest.main()
