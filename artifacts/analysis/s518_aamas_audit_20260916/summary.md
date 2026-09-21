# S-518 preserved-evidence audit

No new model calls. All 24,815 headline predictions have unique IDs and reproduce the stored project-scored F1/EM.

| Dataset | n | Recomputed F1 | EM | Paired delta | Archived 95% CI | Raw baseline pairing verified |
|---|---:|---:|---:|---:|---|---|
| HotpotQA | 7405 | 0.432403 | 0.325456 | 0.004470 | [0.0024855578062870443, 0.006547806608576358] | False |
| MuSiQue | 4834 | 0.338877 | 0.242449 | 0.012980 | [0.002994691701252238, 0.02278542118977006] | True |
| 2Wiki | 12576 | 0.554537 | 0.496501 | 0.085668 | [0.07631095585647175, 0.095393178125644] | True |

HotpotQA router/direct token ratio: 1.417246 (41.72% more recorded API tokens).

The CIs above are read from archived bootstrap outputs, not newly estimated and not corrected for model selection. Missing total calls and elapsed time stay missing.

Component usage totals in JSON count available usage records, not independently verified attempted-call totals.

The actual worked failure shows a split, a REJECT_REROUTE audit label, then acceptance of an incorrect answer. A logged label is not proof that its prescribed control action was enforced.

Hashes cover inspected files. This does not establish that the current working-tree implementation is identical to each historical runtime.
