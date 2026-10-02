# PIPE3 feedback-channel and arm-qualification gate — 2026-10-02

状态：`PARTIAL`。本轮没有调用 LLM API、没有提交 GPU/Nebula 任务，也没有改变 Goal、active benchmark 或三份验收标准。

## 触发原因

独立 baseline parity review 发现，PIPE3 composition v1.3 虽然已经把 `policy_factory` 和
`policy_name` 暴露出来，但通过条件只检查 `credit_committed`。因此一个声明消费
`recipient_judgment` 或 `raw_acceptance` 的 arm，仍可能收到 runner 固定构造的
`terminal_outcome` 事件并被报告为 `QUALIFIED_OFFLINE`。这会把“延迟 credit 已提交”错误地当成
“该 arm 的反馈通道已正确更新”。

同一审查还确认，当前 qualification 的目标选择使用 hand-authored base-score overlay，并且
role evidence 只验证被选 candidate 确实有 published evidence；它没有测量 evidence 改变
decision digest。因此该 composition 只能证明 lineage、assignment-before-task-start 和 delayed
credit 的工程边界，不能证明 evidence 被 selector 有效消费，也不能识别 update 到 future choice
的因果效果。

## 实施修复

`peerrolebench_pipe3_two_stage_composition.py` v1.3 现在把
`policy_update_expected` 定义为 policy 声明的反馈源集合是否非空，并要求：

```text
feedback_contract_ok
  = credit_committed
    ∧ (¬policy_update_expected ∨ policy_update_applied)
```

所以：

- `no_update` 可以提交 later credit，但零 policy update，并通过其工程 negative-control
  qualification；
- `terminal_only` 只有在 terminal event 真正改变 policy 时才可通过；
- `raw_acceptance`、`contextual_trust`、`pooled_controller` 和 `RARE` 在尚未接入各自合法
  public feedback adapter 前会返回 `UNKNOWN`，不能借用 terminal event 假通过。

候选卡同步将激活阻塞项改为：七个 arm 的 feedback-channel adapter 未资格化、role-evidence
consumption decision 尚未识别、live measured-cost gate 尚未接入 runner。候选卡仍为
`DESIGN_ONLY`，不是 active manifest。

## 验证

- composition 定向回归：`8 passed`；
- baseline root-contract 与 cost gate 定向回归：`11 passed`；
- 新增负向测试明确验证 contextual arm 在收到 terminal event 时为 `UNKNOWN`，且
  `policy_update_expected=true`、`policy_update_applied=false`；
- JSON 语法与候选卡字段校验通过。

所有验证均为本地零调用工程测试，不能作为 benchmark、baseline parity、角色学习或模型效果证据。

## 当前结论与下一步

这一步关闭了一个会制造假通过的 P0，而不是完成七 arm runner。下一步只能先实现并逐一资格化
每个 arm 的合法 public feedback projection，并把 evidence consumption 变成可识别的
decision-digest mutation test；在此之前不启动 live parity cell、不选择第二 root、不进入
A800 或论文效果结论。
