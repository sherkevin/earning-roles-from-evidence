# Task report — PIPE2 derived CSV-writer authority probe (2026-10-01)

## Purpose and boundary

This is a decision-support probe for authority option A. It does not modify the
pinned TeamBench checkout, does not write an active benchmark fixture, and emits
no peer label. It reconstructs the generator's declared schema rows and
key-column filtering, serializes them with Python's standard `csv.writer`, and
records the resulting hashes and shape checks.

- Base TeamBench commit: `d185aef1916fd86a9ba554d581fd256319a973af` (clean).
- Generator hash:
  `8ecfde93d5e4a1631e3e86dea5864645463ef5a4efb106e4d2a66b478b06919c`.
- Overlay: `pipe2-csv-writer-probe-v1`.
- Derived root digest: `cd4a4b7f71782aa2d8098945995f2e368e8246416127a5bcb6f7903638aa6158`.
- Receipt: `experiments/logs/n03_pipe2_derived_fixture_probe_20261001_v2/`.
- LLM/API/GPU/native grader/candidate execution: all zero.

## Result

All seeds `0–9` produce shape-valid derived source and expected CSV. The logical
task content remains eight source rows, six rows after the public key-column
filter, and the same string truncation rule. For valid original seeds
`0,2,3,5,7,8`, the derived bytes are identical to the pinned generator bytes.
Only `1,4,6,9` change bytes, exactly the seeds previously rejected for
unescaped comma fields:

| seeds | original bytes | derived shape | interpretation |
|---|---|---|---|
| `0,2,3,5,7,8` | unchanged | valid | serialization repair is a no-op |
| `1,4,6,9` | changed | valid | standard quoting repairs the generator defect |

This is evidence that option A can preserve the declared logical task semantics
while changing the benchmark root identity. It is not evidence that the derived
root is already authoritative: the new generator/overlay hash, seed split,
neutral material, scorer/replay, baseline parity, independent histories, later
use and cost gates still require a separate freeze decision.

## Consequence for the authority choice

The probe makes option A technically concrete and limits its scope: a derived
root can repair the four malformed fixtures without excluding seeds or changing
the ETL contract. It also confirms why the original TeamBench root cannot be
silently rewritten—the four changed seeds have different source/expected bytes.
Until the author confirms option A (or another authority path), the active
benchmark manifest and Goal remain unchanged, and no real API/A800 experiment is
allowed.
