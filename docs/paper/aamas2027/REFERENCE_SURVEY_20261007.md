# Reference survey and supplement — 2026-10-07

## Purpose and scope

This audit answers two questions before changing the bibliography:

1. How large are the reference lists in strong, directly relevant papers?
2. What kinds of sources do those papers actually cite, and how does that compare with the current AAMAS draft?

The audit uses the compiled reference list rather than the number of entries available in a source `.bib` file. Two ICML papers were counted from their arXiv source `.bbl`; the two AAMAS papers were counted from the highest numbered entry in the official proceedings PDF; MultiAgentBench was counted from the author–year entries in the official ACL PDF. The download URLs and count method are recorded in `experiments/logs/reference_supplement_round_20261007/config.json`.

This is a literature and manuscript audit. It uses no LLM experiment, GPU job, or synthetic result.

## Strong-paper sample

| Paper | Venue/sample status | Compiled references | Count evidence |
|---|---|---:|---|
| [CollabLLM: From Passive Responders to Active Collaborators](https://proceedings.mlr.press/v267/wu25i.html) | ICML 2025; local gallery marks the paper oral/best | 57 | 57 `\\bibitem` records in the source `main.bbl` |
| [Cross-environment Cooperation Enables Zero-shot Multi-agent Coordination](https://proceedings.mlr.press/v267/jha25b.html) | ICML 2025; local gallery marks the paper oral | 65 | 65 `\\bibitem` records in the source `example_paper.bbl` |
| [Learning Partner Selection Rules that Sustain Cooperation in Social Dilemmas with the Option of Opting Out](https://www.ifaamas.org/Proceedings/aamas2024/pdfs/p1110.pdf) | AAMAS 2024 full research paper | 38 | Highest numbered entry `[38]` in the official PDF |
| [Reputation as a Solution to Cooperation Collapse in LLM-based MASs](https://www.ifaamas.org/Proceedings/aamas2026/pdfs/UEHN4980.pdf) | AAMAS 2026 research paper | 55 | Highest numbered entry `[55]` in the official PDF |
| [MultiAgentBench: Evaluating the Collaboration and Competition of LLM Agents](https://aclanthology.org/2025.acl-long.421/) | ACL 2025 long paper | 59 | Author–year entries in the official PDF reference section; page-number false positive removed |

The sample range is **38–65**, with a median of **57**. The count is not a quality target: a short, sharp paper can need fewer references, while a benchmark or systems paper needs more space for tasks, infrastructure, and adjacent evaluation literature.

## What the sample papers cite

The sample is not a collection of “top-conference-only” bibliographies. Its recurring pattern is a deliberate mixture:

- **Nearest problem literature.** Partner selection, reputation, coordination, role assignment, and cooperation papers establish the exact neighboring question and the boundary of the claim.
- **Canonical foundations.** Bandits, multi-agent reinforcement learning, credit assignment, game theory, and cooperation papers provide definitions and comparison points even when they are older journal or conference work.
- **Benchmarks, datasets, and evaluators.** Benchmark papers and dataset/tool documentation explain what is measured, how success is judged, and which failure modes are visible. These are often ACL/ICLR/NeurIPS papers, but a dataset or maintained artifact can be the authoritative source even when it is not a top conference paper.
- **Adjacent evidence.** The best papers cite human–AI interaction, social science, economics, psychology, continual learning, and systems work when those sources support a specific assumption or evaluation choice.
- **Reproducibility and implementation sources.** LLM systems papers, technical reports, preprints, and project documentation appear when they define an implementation or a fast-moving baseline. Their status must be labelled accurately; an arXiv preprint is not silently upgraded to a peer-reviewed venue.

Thus, venue prestige is a filter for direct comparisons, not a substitute for relevance. A bibliography made only of recent top-conference papers would omit the classical bandit/delay/reputation results that define our estimands, and it would omit authoritative benchmark specifications.

## Current-manuscript audit

Before this round, `main.tex` cited **22** keys out of **28** BibTeX entries. Six entries were leftovers from an earlier benchmark direction (SCMRAG, ReAcTree, role-market work, and three multi-hop QA datasets) and were not cited by any current claim. They were removed from the active `references.bib`; the historical source and prior decisions remain untouched.

The 22 active citations already covered classical reputation/trust, partner selection, orchestration, credit assignment, contextual bandits, delayed feedback, and several benchmarks. The gaps were narrower:

- a direct AAMAS predecessor immediately before the 2025/2026 partner-selection results;
- canonical role-oriented collaboration frameworks;
- a stateful interactive-agent benchmark used to frame what current evaluators expose;
- direct LLM cooperation studies to distinguish social-game payoff from artifact attribution;
- continual-learning and multi-agent non-stationarity foundations for the explicitly promised forgetting/drift analysis.

After the supplement, the 30-entry active list has this venue mix: AAMAS proceedings 7,
ICLR 3, ICML proceedings 2, ACL/NAACL 3, NeurIPS 2, AAAI 1, WWW 1, peer-reviewed
journals 5, and arXiv/preprint records 6. The groups overlap with the paper's roles in a
useful way: AAMAS/ICLR/ICML/ACL/NAACL/NeurIPS provide the current nearest methods and
benchmarks; journals and older proceedings provide reputation, bandit, credit, continual
learning, and game/interaction foundations; preprints are retained only for fast-moving
baselines whose cited artifact is explicitly labelled as a preprint. This distribution is
closer to the sampled papers' logic than either an all-preprint list or an all-top-venue list.

## Supplement applied in this round

Eight verified entries were added and cited where they carry a sentence-level argument:

| Key | Source role | Where used |
|---|---|---|
| `leung2024partner` | AAMAS 2024 partner-selection predecessor | Introduction’s partner-selection boundary |
| `metagpt2024` | ICLR 2024 oral role-specialized collaboration framework | Orchestration positioning |
| `agentverse2024` | ICLR 2024 collaboration/emergent-behavior framework | Orchestration positioning |
| `appworld2024` | ACL 2024 interactive, stateful agent benchmark | Benchmark positioning |
| `piatti2024cooperate` | NeurIPS 2024 LLM-society cooperation study | Social cooperation boundary |
| `akata2025repeated` | Nature Human Behaviour 2025 repeated-game LLM study | Social cooperation boundary |
| `khetarpal2022continual` | JAIR review of continual reinforcement learning | RQ4 stability/forgetting motivation |
| `hernandezleal2017nonstationarity` | Multi-agent non-stationarity survey | RQ4 drift motivation |

The active bibliography now contains **30 entries, all cited in the manuscript**. The additions do not assert that any of these systems solves responsibility-aware role learning; they define the neighboring baselines and the evaluation risks against which the paper positions its narrower question.

## Editorial rule carried forward

We will not inflate the list to match 57 or 65 mechanically. Before submission, every entry must satisfy one of these tests:

1. it defines the nearest competing problem or mechanism;
2. it supplies a foundational definition or estimator used by the method;
3. it is the authoritative benchmark, dataset, evaluator, or software source used in the experiment; or
4. it supports an explicit limitation, safety, stability, or human/agent interaction claim.

A future reference round should add a source only when a new paragraph, baseline, benchmark, or measurement requires it. The next review is a claim-to-citation audit after the final method and benchmark are frozen, not a numerical chase for a larger bibliography.
