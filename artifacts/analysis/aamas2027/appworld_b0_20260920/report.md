# AppWorld B0 benchmark/task-contract audit — 2026-09-20

## Verdict

**B0 PASS. AppWorld replaces OfficeBench as the primary benchmark candidate.**
This is a structural/integrity decision, not yet \`benchmark_status=locked\`; B1 model feasibility remains open.

Pinned source:
- AppWorld commit: \`42b5bcf3cd334fee33f0c37c02070a9f5807add5\`
- data version: \`0.2.0\`
- audit script: \`scripts/audit_appworld_b0.py\`

The official minimal bundle was used. Hidden test ground truth is not used for method design.

## Integrity and split structure

Official public split sizes are:
- train: 90 instances / 30 generator families
- dev: 57 / 19
- test-normal: 168 / 56
- test-challenge: 417 / 139

Every family has three scenarios. Generator-family overlap is zero for every pair of splits.
Thus the benchmark supplies family-level OOD evaluation rather than randomly splitting variants of the same generator.

All 90 train and all 57 dev tasks contain at least one evaluator requirement labeled \`no_op_fail\`.
Across train there are 492 evaluator assertions; across dev there are 291.
A direct no-action world probe on representative train/dev tasks returned \`success=False\`.
The official end-to-end verifier was run with the benchmark's compiled solutions and evaluators:

\`\`\`
appworld verify tasks --num-processes 1
=> Passed 147/147 tasks
\`\`\`

This is materially cleaner than the OfficeBench candidate, where the audit found zero-action passes and evaluator errors.

## Primitive reuse and family novelty

After removing supervisor bookkeeping and login calls, train exposes 56 distinct API primitives.
32/57 dev scenarios require only primitives already present somewhere in train.

16/19 dev families keep the same required-API signature across all three scenarios.
Under the frozen structural rule:

1. all target primitives occur in train;
2. the three target scenarios share one invariant API signature;
3. no single train family contains the whole target signature;
4. at most three train families can cover it;

four dev families qualify as strict composition candidates:

- \`530b157\`
- \`4ec8de5\`
- \`6bdbc26\`
- \`6c2c621\`

API set cover is only a feasibility proxy. The final workflow slots must be typed subprocedures with explicit I/O, not bags of APIs.
## Recommended primary causal family: 530b157

Representative task: recover an owed grocery amount from a phone conversation, send the money on Venmo, then send an acknowledgement text.

Properties:
- difficulty 3;
- apps: Phone + Venmo;
- invariant target primitives across all three scenarios;
- 10 evaluator assertions, 9 of which are \`no_op_fail\`;
- exact state checks cover both the payment and acknowledgement.

Proposed typed workflow:

\`\`\`
S1 Context extraction
  input: user identity + task instruction
  output: {friend_phone_id, friend_venmo_id, owed_amount}

S2 Payment execution
  input: {friend_venmo_id, owed_amount, note}
  output: payment_receipt

S3 Acknowledgement
  input: {friend_phone_id, acknowledgement_text, payment_receipt}
  output: message_receipt
\`\`\`

The dependency graph is \`S1 -> S2 -> S3\`; S3 is guarded by successful S2 completion.

Relevant train donor families:
- \`29caf6f\`: phone contact/text retrieval and phone reply;
- \`60d0b5b\`: contact resolution plus Venmo transaction creation;
- \`d0b1f43\`: current-time/contact filtering plus Venmo transaction inspection.
The donors contain extra operations. Experience extraction must therefore scope evidence to the contributed subprocedure, not transfer an entire donor trajectory wholesale.

The target evaluator supplies natural contribution partitions:
- S2: exactly one Venmo transaction, correct receiver, note and amount;
- S3: exactly one global text message, correct receiver and content;
- global safety: expected changed-model set and no deletion of user text records.

This makes 530b157 suitable for testing binding, rebinding and local repair rather than only final-answer accuracy.

## Recommended feasibility/sanity family: 6c2c621

Representative task: export every Simple Note note as a Markdown file in a requested backup directory.

Properties:
- difficulty 2;
- apps: Simple Note + File System;
- 8 evaluator assertions, 7 \`no_op_fail\`;
- exact file paths, contents, extension and collateral-change checks.

Natural slots are:
1. enumerate/read notes;
2. deterministic title-to-path transformation;
3. create files with the corresponding content.

Train donor families:
- \`cf6abd2\`: Simple Note search/show procedure;
- \`6104387\`: file creation/export procedure.

Use this family first in B1 because the two-role dependency is simpler than 530b157.
## Probe-only composition families

\`4ec8de5\` combines Spotify library retrieval with current-time filtering.
\`6bdbc26\` combines current-player state with artist lookup.

Both are useful frozen capability probes, but they are read-only answer tasks with only two evaluator assertions.
They should not carry the main workflow-rebinding claim.

## Confirmatory boundary

Train is the only acquisition source.
Dev may be used for benchmark/mechanism development until the design is frozen.
Test-normal and test-challenge remain untouched by method selection and hyperparameter choices.

Evaluator-only private truth may be used for offline audit/scoring but never exposed to the execution policy.

## B0 decision

AppWorld passes the structural and evaluator-integrity gates needed for A-T03.
OfficeBench is retained only as optional external evidence; it is rejected as the primary benchmark because its evaluator/runtime noise would confound the mechanism.

B1 must still establish:
- a non-floor solvability regime with the chosen backbone/harness;
- measurable exposure-induced capability differences;
- a clean no-experience versus private-experience contrast on the sanity family;
- then feasibility on 530b157 before the benchmark is locked.
