# A real-data test of the first link in the proposed story

The first question is whether actual experience creates a useful behavioral
change. A coordination mechanism has nothing to qualify if the retained
experience does not change capabilities. This prerequisite is now executable;
the larger Q1 coordination hypothesis remains unproven.

## Story and innovation boundary

The intended story is: experience changes an executor; some changes help one
workflow but hurt another; task-grounded evidence determines where to adopt the
change; reusable handoff requirements reduce the cost of checking new bindings.
The current experiment measures only the first arrow.

Storing successful trajectories or summarizing API use is established practice.
Neither this runner nor a positive memory-versus-empty comparison is claimed as
the paper's innovation. The remaining potential contribution is a useful,
finite-feedback method for qualifying previously untested combinations. It
needs a natural interaction witness and comparisons with competent interfaces,
pairwise matching and equally funded regression tests.

## Frozen executable acquisition policy

The [prospective manifest](../../../configs/aamas2027/acquisition_probe_v1.json)
specifies all IDs, ordering, costs, failure handling and the continuation gate.
It was saved before any new benchmark inference. The real API health request
and its failed authentication-format predecessor are separately recorded.

1. Sort complete native train/dev family lists by the declared SHA-256 rule;
   retain the first six families from each split. No outcome/difficulty filtering.
2. Execute each selected train `_1` with the official ReAct prompt and a fresh
   native world, using the named idealab provider and qwen3.8-max.
3. Make one paid induction request per valid trajectory. Input is public
   actions/observations plus the terminal training success boolean. Output is a
   bounded JSON procedure with applicability, pitfalls and observed step IDs.
4. Retain syntactically valid candidates in the frozen order. The same full
   library is added to every memory arm. No target-specific retrieval or editing.
5. On each train `_2`, run empty and memory from independent identical initial
   worlds. Repeat two preselected empty cases to detect output instability.
6. Enter the six-family dev pairing only if there are at least two complete
   success wins, no losses, nondecreasing mean assertion fraction, no null
   success flips, and intact infrastructure. Complete all dev pairs if entered.

The threshold is a conservative spending/continuation heuristic, not statistical
significance. The maximum is 32 native episodes plus six induction requests;
the first decision occurs after 20 native episodes. All failed requests count
toward the common 30-attempt per-episode budget; each call requests a 2048-token
output limit. The provider's reported total can include additional reasoning,
as documented below. Full native history is preserved, as in the existing B1 harness.

## Feedback and provenance

The solver loads no ground truth. It receives only the native instruction,
public documentation and API observations. Official scoring runs after solving
stops. Assertion details never enter induction or target-solving prompts.

Schema/source-step checks validate provenance structure, not semantic truth.
The generated summary remains a candidate; manual inspection must check for
unsupported generalization and instance literals. The immutable raw response is
kept even if a candidate is rejected. No regeneration is allowed in this round.

Temperature zero and a returned model alias do not guarantee deterministic
weights/service. The two empty repeats are diagnostics, not a precise estimate
of all service variance. No claim is made about remote inference hardware.

## Result interpretation and reuse

A passing result warrants a separate, prospective test of a natural handoff.
A failed gate warrants failure analysis, not a renamed positive claim. Equal
task success with fewer calls can support an efficiency observation only after
including acquisition/induction cost; it cannot establish stronger capabilities.
Task-quality changes without a consumer intervention are generalization effects,
not collaboration incompatibility.

The reusable assets are the verified named-provider adapter, official native
prompt/runtime/scorer, hashed split selection, complete attempt ledger, actual
training trajectories, bounded learned artifacts and unchanged-package controls.
AppWorld database snapshots do not restore messages/REPL locals; this probe uses
fresh worlds and makes no faithful replay claim.

Live status and final evidence belong in the [single task ledger](../../coordination/AAMAS_TASKS.md)
and [experiment evidence directory](../../../artifacts/experiments/aamas2027/dev_20260922/).


## Recorded execution corrections

The immutable original contract remains available. Before any validation call,
a [transport amendment](../../../configs/aamas2027/acquisition_probe_v1_transport_amendment.json)
allowed one fresh-world replacement for an acquisition interrupted by HTTP429,
serialized calls, and added bounded retry backoff. The original attempt and its
cost remain in the evidence; no task/model selection or success-gate change occurred.
The new ceiling is 33 native episodes and six induction attempts.

The idealab service reports additional reasoning generation beyond the requested
text cap. Requested settings remain fixed, but actual token usage is the accounting
source and the nominal arithmetic ceiling is not a hard spend guarantee. Unknown
usage for failed requests remains unknown.

Pinned AppWorld treats any database path containing `memory` as an in-memory path.
Two completed treatment outputs therefore initially lacked valid scoring. Their
saved state files were copied byte-for-byte to neutral paths and scored with the
unchanged official evaluator, with no new model calls. Original scorer errors and
per-file hashes remain archived. Future physical paths use neutral hashes; arm
labels remain in metadata.

## Completed round and scientific decision

The [audited result](../../../artifacts/experiments/aamas2027/dev_20260922/report.md)
contains 21 native episodes (including the interrupted acquisition and its
declared replacement), six induction calls, and 329 real benchmark/induction
request attempts. Both arms scored 6/6 on the fixed independent training
instances; the two unchanged-package controls had no success flip. Validation
calls were 96 without memory and 99 with memory; known context tokens including
cache were 739,410 and 886,460. Acquisition/induction cost another 102 calls.

The gate did not pass: zero paired success wins, plus one unwaived empty-text
HTTP200 response in the first treatment pair. The recovered final state still
scored successfully; this does not erase the infrastructure defect. The original
conditional dev arms were not launched, and Q1 remains unestablished.

A [label-masked audit of all six pairs](../../../artifacts/experiments/aamas2027/dev_20260922/behavior_audit/review.md)
finds that both arms already perform most of the summarized procedures. Some
verification and scheduling changes are visible, including one treatment using
26 versus 15 calls after separating compression, existence checks and deletion.
This supports behavioral change, not a proven capability gain or collaboration
incompatibility. The small ceiling sample does not prove that all AppWorld tasks
are saturated or that every experience-learning method is ineffective.
