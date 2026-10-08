# 决策输入落盘：复用核查

日期：2026-10-08。目的：保留实际选择时的输入供延迟反馈重放，避免事后重新计算特征。

## 已有能力

- `peerrolebench_pipe3_runner_v1.SelectionSeal` 已持有策略选择、原生选择、完整 `DecisionSidecar` 和消费证明；`choose_and_seal` 创建它们时已绑定原生记录、注册表与状态摘要。
- `DecisionSidecar.payload()` 已包含全部候选的 `captured_features`、encoder/schema、分数、概率及选中索引，不需要新特征协议。
- `AssignmentEvidenceOffer.operator_binding_payload()`、`DecisionConsumptionAttestation` 及 `verify_consumption_attestation` 可重放公开输入/读切关系。
- role evidence 是独立公开输入，`commit_role_evidence_selection` 在 auxiliary rows 中保存其 read link；不能只保存普通 feedback offer 就声称覆盖该输入。
- C1 在 source/target seal 后才调用 `_run_episode`，可在此处保存输入，不改变模型调用或选择算法。

## 实际缺口与实现范围

旧 C1 只把选择绑定摘要写出，完整sidecar/offer仍留在内存；失败前后未必有完整ledger。哈希证明不了已丢失向量的数值。原封保存上述已有对象，并在执行前完成不可覆盖的文件写入，比再建一套延迟reward协议更直接。

本轮仅增加原对象的序列化/恢复与执行前保存；保留选中向量并验证原有绑定。来源/结果标签不变、诊断执行限制不变、历史输出不改写。当前one-hot仍是one-hot，原始任务文字没有被现有头消费，不能把它一并存档说成模型已使用。后续task-conditioned adapter必须另行接入相同输入链。

保存完整role offer是审计来源，不能等同于把其所有字段提供给新模型；当前公开评分投影只消费 source J，未消费的终局字段须保持这一差别。校验是可信runner下的数据一致性检查，不是针对恶意重写全部文件的安全证明，也不授权reward更新。

结论来自两个独立Codex对上述本地实现的核查。复用项目已有类型和Python标准文件操作；没有引入新第三方协议框架。
