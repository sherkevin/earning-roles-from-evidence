# S-518 -> Engineer: AAMAS evidence and runtime rebuild

Status: actionable design, execution pending. Owner of runtime/code/experiments: engineer. This handoff does not claim execution or silently modify the historical core. The prior no-paid-API decision remains in force. Use existing authorized local/server resources after verifying their current availability; do not infer a current GPU allocation from old logs.

## Objective and governing hypothesis

Implement and evaluate the proposed local persistent delegation protocol in `article/aamas2027/main.tex`. The hypothesis is that attributable task-conditioned history improves subsequent allocation at fixed resource budgets. The current historical adaptive routers do not establish this.

Keep the old EMNLP branch, data, predictions, source snapshots, and checkpoints untouched. Work in an isolated engineering checkout under the project convention. Freeze the experiment manifest before confirmatory runs. Do not re-open paid inference, synchronize the whole paper repository, or launch a full benchmark merely because a small pilot looks positive.

## Ordered experiment cards

### AAMAS-E01: provenance, scorer, and execution semantics (P0)

Inputs: S-518 audit JSON and failure trace; current `workspace/idea04_core/{runner,methods,evaluation}.py`; archived historical configs.

1. Recover the exact historical runtime commits/hashes and identify differences from the dirty current checkout. Recover the HotpotQA direct-baseline predictions at the archived E130 reference location if available, validating ID and content identity before reuse.
2. Pin official dataset versions, splits, native IDs, scorer code, and licenses. Check the 4,834-row MuSiQue composition, answerability setting, and context conversion explicitly rather than assuming its rows mean the same as the standard answerable subset. Label old converted populations accurately.
3. Reproduce official-score comparisons on both method and baseline outputs. Test punctuation/article order, yes/no/noanswer, empty answers, and multi-answer handling against the official functions.
4. Remove gold labels from all policy-facing inputs. A `gold_answer` argument currently exists at the method boundary; this is an API hazard, not evidence that the headline policy used the value. Verify call graphs and label-shuffling invariance of routing/answers.
5. Audit whether every non-acceptance outcome produces its specified transition. Reproduce `hotpotqa-0000` from stored events without a new LLM call. Ensure final acceptance cannot silently override a reroute request.

Acceptance: a schema and provenance report; focused offline tests pass; no claim of global runtime parity without actual matching hashes. Stop incompatible comparisons rather than silently normalizing away missing records.

### AAMAS-E02: minimal persistent protocol and complete accounting (P0)

- Separate task memory from neighbor/task-type allocation records. Persist the latter across tasks in a stream, reset between streams. The present task-local stores must not be presented as persistent learning.
- Use initially identical worker prompts/model/tool interfaces. Remove role-name-dependent competence priors in the primary condition. Record graph/topology asymmetry separately.
- Implement one task-type taxonomy and one policy shared across datasets. Remove benchmark-name routing from the primary condition. Keep old heuristic router as an explicit baseline.
- Apply completed audit observations (including rejection) only to the responsible local edge/task type. Distinguish observed acceptance from external correctness. Log state before/after and the actual next route chosen because of it.
- Start with the mean-update/cost/exploration policy from the draft and a simple bandit alternative. Do not add seven personality axes or a broad new framework without a demonstrated need.
- Enforce atomic pre-call reservations for every answer, decomposition, audit, aggregator, retry, and failed request. Track prompt/completion/total tokens and missing usage, tool time, start/end times, concurrency, and actual model/checkpoint. Record budget exhaustion as an outcome. Do not derive call totals from outer hops.

Required event fields: stream ID, task/native ID, order index, local actor/executor, task type, evidence references, state version before/after, selected action, audit result, enforced transition, request ID, attempt/retry IDs, success/error, token usage/missingness, monotonic start/end, model/config hashes.

Acceptance: frozen/shuffled/reset controls change only allocation state; label access and unauthorized non-neighbor reads fail tests; budget property holds with nested calls, failures, and concurrency; a local smoke run produces a complete ledger. Smoke numbers are debugging evidence, not paper results.

### AAMAS-E03: primary causal and budget comparison (P0)

Primary variants:

1. Correct persistent EDO state.
2. Frozen state, identical task memory and execution interface.
3. Worker-shuffled state within task type, identical exposure budget.
4. State reset after each task.
5. Uniform delegation.
6. Cost-aware contextual bandit using the same observations.
7. Static team with identical tools and role-free worker prompts.
8. Direct model with self-consistency/revise-and-check allowed to spend the same budget.
9. Historical dataset-specific adaptive router, explicitly labeled as a heuristic comparator.

Primary endpoint: held-out task success/score under fixed calls AND tokens. Initial call grid: 4/8/16. Freeze actual token caps on development data after verifying prompt lengths; no post-result changes. Include best development-selected fixed baseline, not per-test-item oracle choice. Report quality--cost curves, absolute deltas, realized total usage, task-conditioned allocation, and audit error. Include all predeclared comparisons regardless of sign.

Use at least five independently reset task streams with recorded order seeds for the primary contrast. Evaluate paired methods on the same order per stream; the independent unit for persistent learning is a stream, not an adaptively connected task. Use development variance for sample-size/power planning; five streams alone does not guarantee power. If intervals remain wide, report uncertainty rather than declaring equivalence.

Acceptance: correct history improves a predeclared utility criterion relative to the relevant state controls and budget-matched alternatives, or the result is recorded as a negative/bounded finding and the manuscript revised. Allocation differences must mediate a real output/cost difference; an entropy plot is not sufficient.

### AAMAS-E04: closest external baselines (P0/P1)

Prioritize AgentNet and Dynamic Role Assignment, with ReAcTree where task-compatible. Use official implementations and pin revisions; record adapter fidelity and unavoidable differences. Add RepuNet as a conceptual comparator if an output-correctness adaptation changes its original cooperation problem too much for a fair numerical comparison. GPTSwarm is relevant if graph optimization is affordable and its development cost can be accounted for. MoRSE uses learned experts and is not a free same-backbone drop-in; record that distinction.

Charge candidate-selection/meta-debate calls to deployment, offline optimization to development, and give every comparable runtime the same observable task information and tool library. A weak quick adaptation does not license a broad claim against its published system.

Acceptance: at least the nearest task-compatible dynamic comparator and a strong simple history-based comparator under a documented matched contract. If external reproduction fails, disclose the failure and narrow comparison claims; do not substitute eight general frameworks as equivalent coverage.

### AAMAS-E05: audit noise, topology, and failure recovery (P1)

- Audit noise: predeclare false-accept/reject settings that include informative, uninformative, and inverted observations. Distinguish synthetic observation-model tests from real LLM auditing. Include worker-dependent error to challenge the ranking assumption.
- Worker swap: at a fixed stream position, permute capabilities/tool access. Measure cumulative utility and tasks to recover relative to frozen/reset policies. Keep the evaluator's correct assignment hidden from the router.
- Topology: compare a fixed sparse graph with an equal-budget centralized alternative; vary degree/team size in a small predeclared grid. Report messages and observed non-neighbor reads. Do not promise scalability from four agents.
- Sensitivity: development-selected update rate, exploration, cost weight; evaluate a small surrounding grid without selecting test winners. Example candidate rates 0.05/0.2/0.5, exploration 0/0.1/0.2; freeze the final grid after pilot feasibility and before confirmatory outcomes.

Acceptance: failure conditions align with the stated assumptions or contradict them openly. No general convergence claim from a stationary synthetic test.

### AAMAS-E06: stronger backbone and external non-QA task (P1, essential for broad scope)

Verify available hardware/models first. Choose one materially stronger open-weight instruction model (for example a feasible 8--14B-class model) and lock the checkpoint before evaluation. Do not substitute another similarly small checkpoint and call the scale concern closed.

Preferred new task: a public coordination/planning environment with executable outcomes and partial local information; assess ReAcTree/WAH-NL or ALFRED adaptation feasibility before committing. If setup cost is prohibitive within the deadline, use a fixed external executable coding task and narrow the claim accordingly. Existing BBH conversion is ready as a secondary reasoning check, but BBH alone does not establish interactive multiagent coordination. Old MBPP public-test repairs are development history, not new held-out evidence.

Acceptance: a frozen public split/protocol, task-grounded scorer, matched tools/budgets, and all primary controls on the stronger model and second task family, or explicit scope reduction. Do not manufacture breadth by renaming synthetic operational QA as a distinct public benchmark.

### AAMAS-E07: clean release (P1)

Package a minimal anonymous code/data manifest, exact environment, configs, scorer pins, trace examples, and reproduction commands. Separate remote machine names, credentials, local paths, and author identity from released files. Final supplement ZIP <=25 MB; large evidence should use a venue-compatible anonymous access route during review and an archival location after acceptance. Verify the final PDF and ZIP against the same frozen evidence set.

## Schedule and decision points

| Date (Asia/Shanghai planning date) | Deliverable |
|---|---|
| Sep 16--18 | Author accounts; E01 and E02 offline correctness; identify actual available resources |
| Sep 19--22 | Freeze benchmark/baseline contract, protocol, pilot feasibility, and primary statistical plan |
| Sep 23--28 | Run E03/E04 primary comparisons and stronger-model feasibility; preserve every outcome |
| Sep 29--30 | Decide supported title/abstract and contribution; no claims ahead of available evidence |
| Oct 1 | Internal abstract submission target, ahead of official Oct 1 AoE end |
| Oct 1--5 | E05/E06, result reconciliation, independent author review, release material |
| Oct 6--7 | Format/citation/anonymity/replication checks and conservative submission decision |
| Oct 8 | Internal full-paper upload target, ahead of official Oct 8 AoE end |

The dates are a proposed work schedule, not a promise that resources or results will cooperate. If primary causal evidence is not available by Sep 29, reduce the submission ambition or choose a later cycle; formatting does not substitute for the missing experiment.

## Reply requested

Write an engineer reply with (a) current resource inventory, (b) exact code checkout and source hashes, (c) the E01/E02 findings, (d) feasible public non-QA and external-baseline adapters, and (e) a frozen run-cost estimate. Return raw outputs and unsuccessful controls, not only promotable summaries. This is a written project handoff; no external message or remote experiment was dispatched in S-518.
