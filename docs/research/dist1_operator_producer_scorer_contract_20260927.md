# DIST1 operator-only producer scorer contract (2026-09-27)

Status: design finding for review; not a qualified benchmark scorer and not a learning result.

## What the current task actually provides

`TeamBench@d185aef1916fd86a9ba554d581fd256319a973af` generates `DIST1_queue_race` from one structural root. Seeds rename the domain/classes/modules and vary capacity; they do not create independent task roots. The producer owns `mqueue/queue.py` and `mqueue/priority.py`; the recipient owns `mqueue/consumer.py`; `mqueue/config.py` and package files are operator-held support. The current adapter therefore cannot treat the final consumer artifact as producer correctness.

The native `grade.sh` has twelve checks. It parses `consumer.py` in C1 and runs whole-workspace tests in several checks. Calling it on the live recipient workspace would mix responsibility and would make a repair to `consumer.py` look like evidence against the selected producer. It must remain a reference only until a separate scorer is qualified.

The current live runner evaluates only `sealed_consumer.json` using `dist1-consumer-behavior-v2`; it records `producer_objective_quality: null`. It has no producer score path yet.

## Minimal operator-only boundary

The operator launches one fresh scorer worker after a producer delivery is sealed. The candidate source is copied into a read-only public tree. A trusted worker and hidden tests stay in a private driver tree; no grade script, expected values, or hidden test source enters either agent payload. The worker receives only the source tree and a public request:

This boundary is suitable for the current non-adversarial source contract, not for a malicious candidate: the pinned sandbox and Python worker share the candidate address space/instrumentation. The qualification record must therefore avoid claiming hostile-code secrecy.

```json
{
  "op": "score_producer",
  "schema_version": "dist1-producer-score-request-v1",
  "task_id": "DIST1_queue_race",
  "seed": 0,
  "artifact_sha256": "<digest of sorted mqueue/queue.py + mqueue/priority.py>",
  "scorer_version": "dist1-producer-objective-v1"
}
```

`producer_id`, `recipient_id`, ledger IDs, and controller state stay in the parent process; they are not scorer inputs. The trusted launch configuration may derive the generated queue and priority class names from the operator-held seed, but must not pass hidden expected answers or test source in the request. The worker should verify that its source digest equals `artifact_sha256` before running checks.

The first version should use an explicit producer-only inventory, rather than invoking native `grade.sh`:

| ID | Producer contract | Evidence type |
| --- | --- | --- |
| `P1_source_parse` | queue and priority source parse/import under the generated public names | deterministic source/runtime |
| `P2_capacity` | concurrent `put` never exceeds declared capacity | behavior |
| `P3_ack_receipt` | `get` returns a receipt and `ack` removes only acknowledged work | behavior |
| `P4_nack_recovery` | `nack` re-delivers unacknowledged work, including multiple in-flight items | behavior |
| `P5_priority_type_safety` | equal-priority dict/list payloads never enter payload comparison errors | behavior |
| `P6_priority_order` | lower priority value is dequeued first and equal priorities have deterministic ordering | behavior |
| `P7_zero_loss` | the public 10,000-message/20-thread contract completes with no loss | behavior |

`P1` must not parse or execute `consumer.py`. `P2`–`P7` may use operator-held generated support/test drivers but must not use recipient source. Each check runs from a fresh queue/module state; no check may silently skip. A weighted score is only meaningful after the inventory and weights are frozen and the scorer is qualified against known buggy, correct, and near-miss controls.

## Exact worker response

A successful RPC always returns an object, even if the candidate fails a check:

```json
{
  "ok": true,
  "value": {
    "schema_version": "dist1-producer-score-response-v1",
    "scorer_version": "dist1-producer-objective-v1",
    "task_id": "DIST1_queue_race",
    "seed": 0,
    "artifact_sha256": "<echoed verified digest>",
    "status": "PASS",
    "label": 1,
    "quality_score": 1.0,
    "coverage_complete": true,
    "checks": [
      {"id": "P1_source_parse", "status": "PASS"},
      {"id": "P2_capacity", "status": "PASS"},
      {"id": "P3_ack_receipt", "status": "PASS"},
      {"id": "P4_nack_recovery", "status": "PASS"},
      {"id": "P5_priority_type_safety", "status": "PASS"},
      {"id": "P6_priority_order", "status": "PASS"},
      {"id": "P7_zero_loss", "status": "PASS"}
    ],
    "failed_check_ids": [],
    "observed_check_count": 7,
    "required_check_ids": ["P1_source_parse", "P2_capacity", "P3_ack_receipt", "P4_nack_recovery", "P5_priority_type_safety", "P6_priority_order", "P7_zero_loss"]
  }
}
```

For a complete candidate result, every required check must be exactly `PASS` or `FAIL`. A source-owned assertion or deterministic contract violation is `FAIL`, with `label: 0`; all checks passing is `PASS`, with `label: 1`. `quality_score` is the frozen weighted fraction of `PASS` checks and is retained for a future graded update. The scorer response should contain only stable check IDs and short operator-side reasons; never forward hidden assertion text to agents.

For any incomplete or infrastructure result, the worker returns `ok: false` or a response with `status: "UNKNOWN"`, `label: null`, `quality_score: null`, and `coverage_complete: false`. Parent-side UNKNOWN causes include timeout, transport/JSON failure, unexpected process exit, permission or sandbox denial, resource limit, missing/duplicate/ skipped check, missing source, or scorer-version/schema mismatch. A mixed vector with one observed source failure and one unknown check is still UNKNOWN and must not update a role model. The parent records exit code, timeout, response digest, and stderr separately; it never converts these into a negative capability label.

## Attribution and protocol boundary

The producer label refers only to the immutable delivery digest and the producer-owned files. Recipient integration edits, declared `repair`, final consumer behavior, and repair cost are separate observations. Do not overload the existing `TerminalOutcome` (which currently requires a prior consumer action) with producer quality. Introduce a versioned operator-side producer-score record or a protocol event only after deciding its causal order; at minimum it must reference `delivery_id`, producer artifact digest, scorer version, score payload digest, and the hidden check inventory version. The scorer result can be computed after delivery and kept private until recipient judgment/action are sealed, but the recipient must never see it.

For the paper's situated-judgment story, this objective score is a ground-truth/evaluation signal for whether the recipient's sealed judgment predicted the delivered artifact. It must not silently replace the recipient judgment as the learned evidence. Preserve the pair `(recipient judgment, objective producer score)` and report any direct use of the objective score as an explicit oracle-label ablation. The final recipient artifact has its own integration score and cannot be used as `Q_p` after recipient edits.

## Qualification required before live integration

Live integration is **not scientifically safe yet**. Before using this score for role updates, run a zero-LLM scorer qualification matrix with the same sandbox and worker:

1. original generated buggy source: expected deterministic `FAIL` on targeted checks;
2. independently authored correct control: expected `PASS` on all checks;
3. one near-miss per requirement: expected failure only on the targeted check(s);
4. malformed source, timeout, permission, and transport mutations: expected `UNKNOWN`, never `FAIL`;
5. candidate read attempts against the private driver path: denied and logged;
6. exact digest, check inventory, response-digest, and no-hidden-data assertions.

Only after this matrix passes should the runner call the producer scorer. Even then, this establishes scorer validity, not role-learning efficacy or benchmark qualification. A second independent structural task root and persistent non-exchangeable agent state remain open requirements.
