# Real AppWorld acquisition probe — observed results

The frozen memory package achieved 6/6 official successes; the identical agent without memory achieved 6/6. There were 0 paired wins and 0 paired losses.

Prospective development gate: **NOT PASSED**. This is a prerequisite experiment, not evidence of collaboration compatibility or role emergence.

Gate reasons: Fewer than two paired official-success wins; Unwaived infrastructure error in pair(s): 692c77d.

Official scores describe saved final states. The recovered HTTP200 response with no executable text in family 692c77d is still an unwaived infrastructure error; this pair is not silently promoted to a clean treatment comparison. Two separate path-only scoring failures were repaired using byte-identical saved databases and the unchanged evaluator, with no additional model calls.

| Native validation task | Empty success | Memory success | Empty calls | Memory calls |
|---|---:|---:|---:|---:|
| 692c77d_2 | 1 | 1 | 20 | 18 |
| aa8502b_2 | 1 | 1 | 15 | 14 |
| 6ea6792_2 | 1 | 1 | 20 | 18 |
| 771d8fc_2 | 1 | 1 | 14 | 15 |
| 7d7fbf6_2 | 1 | 1 | 15 | 26 |
| 287e338_2 | 1 | 1 | 12 | 8 |

The two unchanged-package controls had 0 success flips. They are limited variability diagnostics.

Empty/memory paired validation used 96/99 attempted calls, 739,410/886,460 known context tokens including cache, and 14,968/13,430 reported output tokens including reasoning.

Acquisition and induction separately cost 102 attempted calls, 723,371 known context tokens and 31,552 reported output tokens. This overhead is not excluded when evaluating reuse economics.

Including acquisition, its recorded infrastructure retry, induction, paired validation and unchanged controls, there are 329 real attempted LLM calls. 6 failed attempts have unknown token usage. Known token counts are lower bounds on full consumption, not an exact monetary bill. Provider prices were unavailable; USD cost remains unknown.

The provider returned total output above the requested text cap on 6 calls. This experiment matches requested settings and attempted-call limits; it cannot claim a hard equal actual-token budget.

Descriptive Wilson95 success intervals are [0.6096657120978346, 1] (empty) and [0.6096657120978346, 1] (memory). The paired exact discordance test is None; None means no discordant cases, not demonstrated equivalence. Six families and one acquired checkpoint cannot establish broad improvement or absence of an effect.

All tasks, package candidates, failures and costs are retained. Original failed acquisition is not mislabeled as a scientific failure; its one declared same-task replacement is explicit. No test-normal or test-challenge inference was performed.

The two API-health preflight attempts (one authentication-format error and one success) are recorded separately in preflight_raw.jsonl; they are not benchmark or induction attempts. Raw benchmark traces contain simulated accounts and remain local.

Reused assets: the verified named-provider adapter, official native prompt/runtime/scorer, hashed split selection, six actual training traces, six bounded source-linked procedural candidates, and an auditable paired runner. Candidate advice is not automatically semantically verified.

Reproduce analysis: `/Users/jingwu/work/AppWorld/.venv-b1-api/bin/python scripts/analyze_aamas_real_probe.py` from this project. The JSON analysis holds every raw log hash and separate task/cost statistics.
