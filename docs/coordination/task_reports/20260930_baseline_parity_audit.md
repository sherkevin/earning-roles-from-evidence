# Baseline parity audit — 2026-09-30

## 结论先行

当前可以构造七个 policy arm，但还不能把 benchmark/baseline 标成冻结。统一
`Selection`/`Feedback` Python 接口只证明了对象能被实例化；它没有完成 root-level
runner、完整成本、later assignment、UNKNOWN 分母或 closest published adapter 的
公平比较。

## 已核对的共同接口

所有当前 policy 都经过同一个选择边界，记录候选版本、base score、实际概率与
propensity、state/encoder/schema 版本、selected time 和可选 captured features。反馈
记录 source、label、arrival time、delay、action、disposition、provenance、arrival index
和 correction reference。七个可构造 arm 是：

`uniform`, `no_update`, `raw_acceptance`, `terminal_only`, `contextual_trust`,
`pooled_controller`, `RARE`。

它们的合法信息通道仍然不同：raw 只读 raw accept/reject，terminal 只读独立终局，
contextual/pooled/RARE 读 recipient judgment；RARE 还要求每个候选的固定特征、
`hash64-v1` 和可处理 correction。这个差异是设计的一部分，但必须由同一个 runner
明确封存，不能把“共享 Python 构造器”当成同信息证明。

## 发现的公平性缺口

1. **没有统一 root-level live runner。** 现有 PIPE3 boundary 只到 selection、sidecar
   和有限反馈消费；没有统一的 scorer、later-assignment、执行前 assignment 和完整
   stream replay。
2. **时间轴还未对所有 arm 封存。** sidecar v4/RARE 已要求 event-time 与 frozen
   schedule；旧 arm 仍可走 v2/v3 wall-clock 兼容路径，PIPE3 boundary 也没有全局
   schedule digest 闸门。
3. **UNKNOWN 与分母没有成为结果字段。** policy 会 no-update，但不会持久化每条
   UNKNOWN 的 reason、selected/eligible/unknown 分母或 ITT/protocol denominator；这些
   必须由 runner 记录，不能在分析时猜。
4. **成本合同不存在。** 当前选择/反馈/replay 对象没有 producer、recipient、judge、
   scorer、retry、communication、repair、replay cost，无法声称同成本比较。
5. **closest published adapter 尚未实现。** DecisionBench 只能作为最近的 delegation
   参考，CooperBench 只能作为工程 substrate；当前没有固定 paper/code commit、完整
   public/private field map、selected-only/arrival/correction/assignment 映射和回放测试。
6. **RARE 与 contextual trust 不是同信息。** RARE 读取并验证 captured feature 与
   event-time correction；contextual 只用 context×candidate trust，correction 被当作
   不可用事件。若不把这些差异预注册为更新器差异，不能称为 strongest same-information
   control。

## 只读依据

审查对象是 active `benchmark_baseline_v1.1_20260930.md`、benchmark evaluation
v1.2、`scripts/peerrolebench_baseline_policies.py`、PIPE3 boundary、sidecar/replay
以及 RARE v6 零调用日志。没有 API、GPU 或 benchmark episode 被启动。

## 下一道门（不降低 Goal）

冻结 baseline 之前必须先交付一个 versioned root runner contract：

- 同一 global arrival schedule 和 schedule digest 对所有 arm 生效；
- 每条 feedback/UNKNOWN 都保存 reason、selected/eligible/unknown 分母与 source；
- producer、recipient、judge、scorer、retry、communication、repair、replay 成本进入
  同一 ledger；
- later assignment 在下一次执行前封存并可回放；
- closest published adapter 完成固定版本与信息/成本字段映射；
- contextual 与 RARE 的差异写成预注册更新器差异，而不是模糊地称“同信息”。

在这些门关闭前，`scientific_readiness` 保持 `false`，不启动真实效果 API 或 A800。
