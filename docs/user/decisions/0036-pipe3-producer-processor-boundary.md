# ADR 0036 — PIPE3 producer scoring stops at semantic JSON delivery

日期：2026-09-27
状态：Accepted
范围：PIPE3 producer objective scorer；recipient/processor outcome remains separate

## Context

PIPE3 has three different defects: producer timestamp serialization, processor output
envelope, and processor file encoding. A first producer scorer prototype required the raw
JSONL bytes to contain literal non-ASCII characters. That incorrectly rejected a correct
producer using JSON's default ASCII escaping, even though `json.loads` restored the original
Unicode value. It would also have assigned a processor encoding responsibility to the
producer.

## Decision

The producer quality objective `Q_p` checks only the sealed producer artifact:

1. public import and API availability;
2. timestamp serialization uses a strict `T` separator with no space;
3. bounded JSONL output preserves record count/order and field values after parsing, and the
   bytes are valid UTF-8.

The scorer may inspect decoded JSON values for non-ASCII semantic preservation, but it does
not require literal Unicode bytes. Processor envelope shape and UTF-8 write/read behavior are
recipient-self or final adoption objectives (`Q_r`/`TerminalOutcome`) and cannot change `Q_p`.
Candidate import failures use ADR 0035; worker, digest, schema and resource failures remain
`UNKNOWN`. This decision applies to the new PIPE3 scorer version only; failed v1/v2 matrices
are preserved and not reinterpreted.

## Consequences

The producer scorer has a clean ownership boundary and can distinguish the timestamp defect
from downstream processor defects. A later PIPE3 qualification must add separate canonical
processor and producer→processor→sink controls, with Qp recorded before recipient judgment
and adoption evaluated on the post-action snapshot. Passing this producer matrix alone does
not qualify PIPE3 as a benchmark or establish role-learning efficacy.
