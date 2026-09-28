# 2026-09-28 factorial 设计审计与口径修正

- 状态：`PARTIAL`
- 对应 Goal：ER-G1（故事线可识别）、ER-G2（方法可验证）、ER-G4（主张与证据一致）
- `goal_change_requested=false`
- 真实 API：0；GPU：0。

## 为什么要修正

上一版零调用脚本把“ledger 能记录事件”称为四因素可表达，并把四个未实现的条件标成了部分可支持。独立方法审查发现这会混淆三件事：协议里存在事件、policy 收到该事件、policy 的状态改变后影响了下一次 decision。这个混淆会让后续 factorial 结果失去因果解释，因此在启动真实实验前必须修正。

## 修正后的因素合同

四个因素现在定义为对同一 immutable episode stream 的正交干预：

- J 只控制 situated judgment/action 是否进入 policy projection；recipient action 在所有条件都执行并记录；
- A 只控制 responsibility/UNKNOWN eligibility gate；不改变原始事件；
- U 只控制 versioned、幂等、watermark/interleaving 的 state transition；不改变 feedback 输入；
- F 只控制执行前 assignment 是否读取封存 evidence/state；candidate menu、propensity 和 exploration 固定。

raw acceptance、terminal-only、contextual trust/bandit 和 matched composition 另列 baseline，不伪装成二值 factorial 因素。主效应和二阶交互改用完整 `2^4` 均值对比；full-corner 留一只保留为局部诊断。

## 零调用复核结果

保留初版 v1/v2/v3 日志，不删除或改写。修正后的 v4 日志位于 [summary.json](../../../experiments/logs/n03_factorial_mapping_qualification_20260928_v4/summary.json)，状态为 `SCHEMA_CAPABILITY_ONLY`：

- 两个 episode 的 protocol hash-chain replay 为 `PASS`；
- ledger 能记录 J/A/U/F 相关事件；
- assignment 与下一 selection 的 agent/propensity 一致，但没有 assignment/evidence consumption attestation，不能证明 policy 读取了 evidence；
- U 只有 arrival metadata，尚未资格化 version replacement、correction、watermark interleaving、后续 decision 影响和延迟成本；
- A 没有 producer-score policy projection；
- 当前 scientific factorial cell 数为 **0/16**。

脚本和单测已把旧的 `QUALIFIED_OFFLINE` 标签改成 capability audit；`python3 -m pytest -q tests/test_peerrolebench_factorial_mapping.py` 通过 2 项。该结果是测量口径修正，不是 Goal 降级。

## 方法论影响

现有 replay 先注册全部 decision，再按 arrival 回放 feedback，最多证明可重放，不能证明 feedback 在下一次 decision 前生效。因此下一道资格门必须构造 event-time interleaving：在 `t+1` decision watermark 前分别注入/不注入 `t` feedback，比较 probability/state digest；迟到事件只能影响后续 decision 或进入预定义 correction queue。

## 下一步

1. 写出 typed policy projection，严格阻断 scorer payload、raw attribution 字段向 policy 泄漏；
2. 增加 producer-score/attribution sidecar 和 assignment/evidence consumption attestation；
3. 实现 U 的 source-index watermark、重复/校正/版本替换和 interleaved replay；
4. 做零调用 mutation 矩阵，只有 16 个 cell 的输入、状态转移和后续 decision 都可审计时，才冻结真实 factorial card。

方法当前仍是算法候选合同，未达到 Findings-ready 或 Proceedings-ready；不启动真实 API/A800。
