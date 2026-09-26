# Peer-role protocol causality audit

> Date: 2026-09-25
> Scope: `references/aamas/peer_role_protocol_20260925.py`, its tests, and `peerrolebench_tb_gate_manifest_20260925.json`.
> This is a contract audit. Passing the existing protocol tests is not evidence that role learning improves task outcomes.

> Historical record: the findings and minimum tests below describe the 2026-09-25 implementation. Current status is in the dated resolution section appended below. In particular, the old requirement that a later assignment must name the same agent as the cited evidence is withdrawn by ADR 0015: negative evidence can justify assigning a different peer. G0–G7 definitions and scientific closure remain governed by [AAMAS_TASKS](../coordination/AAMAS_TASKS.md).

## Findings

### 0. The initial assignment event is missing

The gate manifest requires `assignment → artifact → judgment → terminal grade → ledger update → next assignment`, but the ledger only models `LaterAssignment`, which is recorded after evidence. There is no initial routing/selection event that links a selector decision to the producer delivery. The adapter must represent both boundaries; otherwise the required order is not executable or auditable.

### 1. Selection and selected-only attribution are not represented

`Delivery` has a producer but no selection event, candidate set, propensity, assignment id, or agent version. A delivery can therefore be inserted without proving that the selector chose that producer. The ledger also has no notion of unselected candidates, so it cannot enforce selected-only feedback.

The adapter must record a selection event first, bind the delivery to it, and verify that `delivery.producer_id` is the chosen eligible candidate. The updater must receive only the chosen peer's feedback; candidate probabilities and versions must be logged for replay and IPS/DR analysis.

### 2. Judgment is separated from terminal truth, but visibility is not auditable

The public call order makes it difficult to record an outcome before judgment because action requires judgment and outcome requires action. However, `terminal_outcome_available=False` is supplied by the caller, not derived from an observation boundary. The protocol does not record which fields were visible to the recipient or selector.

The adapter must seal the judgment before running the terminal grader and log a visibility manifest. Hidden tests, expected score, and terminal output must not be in the judgment or selector observation. The terminal score must be independently retained for calibration/effect analysis and must never be used to rewrite the judgment.

### 3. Judgment/action inconsistency is silently accepted

`record_action` checks identity and artifact digest but does not compare the action with the judgment. For example, `reject_redo` followed by `use` is accepted. This may be a valid human behavior, but it must be explicit: either enforce a documented decision-to-action mapping or log a mismatch as its own observable event and analyze it. `used_artifact=True` is currently a self-report, not proof of workspace adoption; adoption must be backed by artifact/state lineage. A repair action should carry the repaired artifact hash (or an explicit no-output reason).

### 4. Evidence can arrive before terminal outcome

`record_evidence_update` permits `outcome_id=None`, while the gate manifest declares terminal grading before ledger update. The main delayed-feedback condition must reject a role update until the terminal outcome has arrived. If a judgment-only update is desired, it must be a separately named baseline and cannot be called terminal-feedback learning.

### 5. Later assignment can be retroactive or weakly attributed

`record_assignment` checks only that evidence ids exist and that its `task_index` is greater than the cited delivery index. It does not prove that the assignment happened before execution of the next task, that the task id is a new root, or that the assigned agent is the subject of the cited evidence. Add an explicit task-start/assignment boundary and a subject-agent field or enforce producer linkage. An assignment made after the next delivery must be rejected.

### 6. Exactly-once episode semantics are missing

Different ids allow multiple judgments, actions, outcomes, and updates for one delivery. `ConsumerAction` also carries no `judgment_id`, so an action cannot be attributed to one of several judgments. Contradictory labels can therefore enter the role history. Either enforce one sealed judgment, one recipient action, one terminal outcome, and versioned evidence updates per delivery, or make supersession and the judgment/action link explicit and auditable.

### 7. Objective score and cost lineage are underspecified

`TerminalOutcome` stores only a boolean and scorer version. For TeamBench the adapter must retain raw partial score, grader run id, artifact/state diff, test output hash, and measured API/tool cost separately from the recipient label. Otherwise a terminal success cannot support calibration or causal attribution.

## Minimum adapter tests

1. A delivery whose producer was not the chosen candidate is rejected; unselected peers produce no updater event.
2. Judgment is recorded before the terminal grader; selector input excludes terminal fields, and a tampered visibility manifest fails.
3. A judgment/action mismatch follows an explicit policy and is not silently treated as agreement.
4. Main role update before terminal outcome is rejected; a judgment-only baseline is separately named.
5. Duplicate judgment/action/outcome for one delivery is rejected (or supersession is explicit and auditable).
6. Assignment after the next task starts is rejected; assignment before next task start cites evidence for the assigned subject.
7. Claimed adoption/repair is checked against the actual artifact or workspace state hash.
8. Tests are reported as protocol/contract sanity only; no score or learning claim follows from them.

## 2026-09-26 resolution and remaining requirements

这次修复让过去反馈真正约束下一次执行前的选择，也让消费者动作产生被评分的实际产物。它解决了协议会测错问题的几处错误，没有建立真实角色学习的效果。原始发现保留在上方；以下状态以 [ADR 0015](../user/decisions/0015-select-before-execution-and-bind-later-assignment.md)、当前协议/runner 和现有原始日志为依据。

| 原发现 | 当前状态与证据 | 尚缺或适用边界 |
|---|---|---|
| 0：缺少初始分派 | 已增加 `PeerSelection`，strict 模式要求选择先于 task start，交付绑定对应 selection。runner 在执行前选择且只运行选中 peer | causal_v2 仅保存 ledger snapshot；完整选择/开始事件尚未导出到 raw，不能仅凭 snapshot 声称独立重放已验证 |
| 1：selected-only 无法归因 | 交付必须属于被选中的候选；16 条 raw 每条只有一个候选标记执行。随机条件用 seeded `rng.choice`，四条 propensity 均为 1/3 | 真实模型/候选版本仍需冻结并由运行时验证；日志中的 fixture version 不是版本漂移处理的证据 |
| 2：判断可见性不可审计 | runner 封存判断后才调用 grader；探针 prompt 未包含终局字段 | **未关闭**：`terminal_outcome_available` 和 `reports_hidden_from_recipient` 仍由调用方提供。candidate source 仍能读取 sibling reports；只读 tests/expected 与哈希检查不是完整文件/网络隔离 |
| 3：判断与动作可不一致 | strict 模式校验 decision→action；use/repair/redo 生成消费产物，grader 复制其源文件。16 条记录的源文件与 evaluator source digest 一致 | 动作由硬编码判断驱动；真实消费者是否检查、使用并从交付中获益仍未验证。所有 repair/redo 调用同一修复函数，不能作为效果归因 |
| 4：终局前更新 | `require_terminal_outcome=True` 时，更新必须引用已记录且属于同交付的 outcome；runner 启用此模式 | 兼容模式仍允许无终局更新，不得混为主实验。fixture `arrived_at` 是事件序号，未测真实延迟到达或墙钟时效 |
| 5：分派事后补写或不用 | 当前协议拒绝 task start 后、也拒绝已记录下一轮 selection 后补写 assignment；下一次选择必须消费已记录对象并保留概率。causal_v2 的 8 次后续选择都消费了 assignment | **修正原审计意见**：不能要求分配对象与被评价者相同；证据可以支持负面判断后改选他人。独立 task root 与跨消费者的信息共享尚需在任务契约中保证 |
| 6：重复反馈 | 每份交付限制一个 judgment/action/outcome；本轮追加修复按 judgment/action 来源拒绝换 evidence ID、版本或到达时间重复更新。每任务 episode 限一个 assignment | 当前无“新证据修订旧证据”的版本化语义；如将来需要，必须单独设计，不能绕过去重。现有 runner 正常路径不等于所有持久化恢复路径已测 |
| 7：分数与成本来源不完整 | outcome 加入 partial score 与 score payload digest；raw 保存原生逐项评分、产物/评分目录和源文件完整性审计 | **未关闭**：repair cost 仍是 0/1 占位。必须实测调用、token、工具、返工与训练成本，并分别记录交付质量和最终质量 |

### 当前协议测试与历史运行分开计量

协议修复者记录的两份协议测试结果已从历史 9 项增至 15 项通过。新增回归覆盖重复 evidence 来源以及 selection 后补写 assignment；负反馈测试明确允许把未来任务派给另一位 peer，并保留 assignment 的采样概率。测试文件为 [基础协议测试](../../references/aamas/test_peer_role_protocol_20260925.py) 和 [strict 协议测试](../../references/aamas/test_peer_role_protocol_strict_20260925.py)。

重跑命令：

```bash
python3 -m pytest references/aamas/test_peer_role_protocol_20260925.py references/aamas/test_peer_role_protocol_strict_20260925.py -q
```

历史 [causal_v2 config](../../experiments/logs/peerrolebench_tb_vertical_20260926_causal_v2/config.json) 保存的 protocol SHA256 是 `f34d2a0277c893a199bc42fdb48e01504bc5a08aa335307be21f7caa5bf63a71`，runner SHA256 是 `c79a29aeedcce99427cc62575f3c4bf636e0f7e54e4ab16d28bb9a4ad49381f1`。该运行早于本轮两项入口加固；保留历史哈希和日志，不以最新测试覆盖其来源。raw 只有逐 episode 字段、ledger snapshot 与末尾哈希，没有完整 `ledger.events`，下一轮必须导出实际事件并冻结可取回的运行源码。

### 现有结果的科学边界

[causal_v2 raw](../../experiments/logs/peerrolebench_tb_vertical_20260926_causal_v2/raw.jsonl) 有 16 条完成记录、0 次 LLM 调用。消费者动作为 use 5、repair 9、redo 2，均分 0.8958；同任务/seed 的四个条件终局分数完全相同。判断依赖 fixture peer 身份，修复统一来自手写函数，返工成本只记 0/1，因此结果不支持 peer selection 收益、角色学习、实时更新或遗忘控制。

旧 secure_v4 的评分与因果问题、CR2 首次资格失败、DIST1 缺少 pytest-timeout 的环境问题、causal_v1 丢失 random propensity 的错误均保留原日志，修复依据见 [vertical-slice 报告](peerrolebench_tb_vertical_slice_20260925.md)。主台账的 G2 科学门仍开放；TeamBench 仍是候选任务基底，benchmark、baseline 与方法未锁。

下一步 N01 的验收应聚焦正常/错误产物评分与越权读取负例、完整事件持久化、实际上下游工作和 task-root 划分。这些条件满足后才开始预算内真实接入，避免继续用夹具通过数量代替原始故事需要的证据。
