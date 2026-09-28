# 2026-09-28 候选在线更新方法：有界窗口与稳定锚点

- 状态：`PARTIAL`
- 对应 Goal：ER-G2（实时、时效、稳定、责任安全）
- `goal_change_requested=false`
- 真实 API：0；GPU：0；方法效果：未测。

## 这次推进什么

独立方法审查给 active method v1.0 的严格合同覆盖度约 38/100，论文方法准备度约 25–30/100。最大缺口不是再写一个名称，而是没有可重放的初始化、更新、correction、容量和恢复语义。为解决这个缺口，新建了候选 [method v1.1-candidate](../../research/versions/method/method_v1.1_candidate_20260928.md)，但没有替换 active method。

## 候选方法的具体化

候选方法 RARE-Anchor（暂名）固定：

- 一个唯一 typed sealed event 作为全部原始输入，并给每个符号配 JSON case；
- `d=64` 的固定 bounded hash feature、局部候选集合和封存 propensity；
- 最近 `B=256` 个 eligible feedback 的逐维充分统计量；
- 稳定锚点、半径 `ρ=2.0` 的投影和 `K=128` 的旧事件 reservoir；
- key 去重、窗口内 inverse correction、超窗 correction queue、版本隔离、snapshot/restore；
- selection `O(|C|d)`、feedback/correction `O(d)`、有界内存 `O(d(B+K))`。

这些是候选合同和可检验预测，不是结果。它把实时性、时效性和稳定性放进同一个状态转移中，但是否优于同信息 RLS、contextual trust 或周期 refit 尚未知道。

## 与 Goal 对照

- 已部分满足：方法现在有可供审查的具体状态、伪代码顺序、参数上限、复杂度和典型事件实例；不再把 `U` 留作空接口。
- 未满足：责任 sidecar、event-time interleaving、correction、checkpoint/restore、old-root forgetting 和真实延迟尚未通过测试；最终 backbone/updater 未锁定。
- 未满足：closest-method 实证、J/A/U/F 正交 factorial、独立 live stream、质量—完整成本结果、selection bias/calibration 尚未开始。

原因是方法合同此前未具体化，属于实现与可识别性缺口；不是实验失败，也不构成 Goal 降级。

## 零调用 reference qualification

已新增 [reference state](../../scripts/peerrolebench_raresafe_candidate.py) 和 [qualification runner](../../scripts/peerrolebench_raresafe_candidate_qualification.py)。它用 `d=4` 的小 fixture 检查：正常更新、duplicate、UNKNOWN no-op、窗口内 correction、超 watermark 事件进入 queue、anchor 半径约束、snapshot/restore，以及 event-time interleaving（早到反馈改变下一 decision，已封存 decision 不被迟到反馈改写）。首轮 digest 把 audit counter 与 policy state 混在一起而失败，后续 event-time 初始化也单独失败，原始日志均保留；修正 semantic digest 和初始化后 v4 通过，见 [summary.json](../../../experiments/logs/n03_raresafe_candidate_invariants_20260928_v4/summary.json)。14 项相关单测通过。

这只证明候选状态的离线不变量，不证明选择质量、真实实时性、遗忘或创新性；`d=4` 也不是最终实验维度。

## 下一步

1. 对候选状态实现零调用不变量：一次更新、UNKNOWN no-op、窗口 eviction、窗口内 correction、超窗 queue、version replacement、snapshot/restore；
2. 将 A/F typed projection 接到 sidecar，并用 event-time interleaving 验证 feedback 是否影响后续 decision；
3. 用合成已知漂移和已知 correction 做数学/离线回放，再比较同表示 RLS、contextual trust 和周期 refit；
4. 只有这些资格门通过，才把候选方法提交为 active method v1.1，并设计新的真实 API 小流。
