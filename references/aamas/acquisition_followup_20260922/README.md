# Acquisition baseline audit and reusable sources

Retrieved 2026-09-22. [sources.json](sources.json) records each official URL,
timestamp, download result and SHA-256. Both arXiv HTML titles were checked.
This is a bounded comparison, not a literature-complete originality claim.

SkillMAS v2 (2026-05-16), [Sections 2.2–2.4 and Appendix A.1](https://arxiv.org/html/2605.09341v2),
already combines execution-supported skill utility, procedures extracted from
successful trajectories, limited repair for localizable failures, and a pending
skill pool. It permits deduplication, refinement, pruning and no update. The
inspected description leaves some promotion/structure thresholds unspecified;
we did not identify runnable official code in the inspected primary material.
Source-linked procedures, applicability conditions, safeguards and validation
steps therefore are not independent novelties of this project. Exact baseline
adaptations must disclose unresolved implementation details.

Meta-Team v1 (2026-05-28), [Sections 3.1–3.2 and Appendix D](https://arxiv.org/html/2605.29790v1#S3),
retains execution context and downstream feedback to revise individual skills,
collaboration records and team instructions. Its public implementation inspected
here is a later [commit](https://github.com/zz-haooo/Meta-Team/tree/36dc85d9dc2219d292fa180f347479738a84acb2),
dated 2026-07-25, not a verified publication-time snapshot. The code writes skills
after content/path checks, merges teammate profiles, persists collaboration notes,
and consumes these on subsequent tasks. The L3 validator checks text properties
and allows warning-only contradictions; the inspected write path does not supply
an independent held-out efficacy gate. Its later L1/L2 communication schedule
also differs from the broad paper description.

## Pinned implementation references

- [Skill updates, reflection.py lines 63–232](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/tools/reflection.py#L63).
- [Profile merges, lines 309–372](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/tools/reflection.py#L309), and [collaboration notes, lines 607–649](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/tools/reflection.py#L607).
- [Consumption and selective skill loading, agent.py lines 150–227](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/core/agent.py#L150).
- [L3 application, reflection_runner.py lines 219–308](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/core/reflection_runner.py#L219), and [text validator](https://github.com/zz-haooo/Meta-Team/blob/36dc85d9dc2219d292fa180f347479738a84acb2/core/reflection_validator.py#L43).

The named files and L1/L2 prompts are downloaded beside this index for practical
reference. These are inspected upstream sources, not a locally executed baseline.
Check the upstream license before incorporating code into a runtime.

## Consequence for the next controlled design

A competent comparison must maintain revisable, conditional procedures from
the same training evidence and load applicable material on demand. Allow pruning
and no update. If actual collaboration occurs, permit the comparator to retain
and consume the same lawful downstream feedback. The first probe's full-library
concatenation is a transparent acquisition prerequisite, not this strong baseline.

Evidence beyond common API documentation would identify an observed condition,
actual failure or downstream use, and an observed consequence of a correction.
Generic pagination advice or repeated API signatures is insufficient. Neither
prose validation nor structural checks certify task improvement. Any claimed
reusable qualification method still needs a specified finite-feedback algorithm,
unseen-combination evidence and equally funded testing controls.
