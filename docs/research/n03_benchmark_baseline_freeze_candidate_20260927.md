# N03 benchmark / baseline freeze candidate

日期：2026-09-27。状态：`CANDIDATE`，不是 benchmark freeze，也不是结果。
目标依据：[`docs/coordination/GOAL.md`](../coordination/GOAL.md) v1.0。

本文件把下一条真实 API 小链开始前必须固定的对象写清楚。它不把现有 fixture、
两条 N02 链或 producer scorer 的 exploratory matrix 当作科学样本。

## 1. Benchmark 候选与 root split

主候选仍是 TeamBench-derived `PeerRoleBench-TB`。拟采用两个结构 root：

| root | 当前用途 | 允许进入真实链的条件 |
|---|---|---|
| `DIST1_queue_race` | development / 责任与 scorer 调试 | task text、producer contract、recipient contract、hidden scorer、UNKNOWN 和成本边界重新通过；当前 N02 只作 plumbing 诊断 |
| `PIPE3_stream_processing` | confirmation / 未见 root | 去 oracle 材料、真实 producer→recipient dispatch、独立 scorer/ledger IPC、sink adoption 和异常/成本覆盖通过 |

这只是候选 split。seed 改名或字段替换仍属于同一 root，不能增加独立样本数。若
DIST1 不能去除任务信息泄漏，必须在 freeze 前重新定义其为 development-only，另找
一个满足同样结构条件的 root；不能把 PIPE3 的三个 seed 当成替代的三个 root。

冻结前必须写入一张不可变 manifest：TeamBench commit、每个 root 的 generator/source
hash、seed 列表、development/confirmation 分区、角色可见文件、可写路径、scorer
版本、ledger schema、预算和停止规则。manifest 之后发生的任务、label、主指标或
split 改动都要新建版本并保留旧版本。

## 2. 共同执行信息

每个 policy 在同一条独立 stream 上共享：任务实例、候选集合、初始状态、模型/API
配置、探索随机数、请求预算、timeout、重试规则、recipient 可见 delivery、延迟/乱序
事件和完整成本口径。policy 只能读取自己的合法历史；producer private score、隐藏
测试、未来 outcome 和其他 policy 的状态不能进入选择或当轮 judgment。

每个选择都记录决策时 snapshot、候选版本、propensity、实际 selected peer、delivery
digest、recipient judgment、recipient action、producer contract score、sink/adoption
结果、token/tool/API/返工成本以及 UNKNOWN 原因。任何责任或覆盖不完整的 episode 只
能进入 UNKNOWN 流，不能转成负标签。

## 3. 首轮 baseline matrix

下面的条件使用完全相同的候选集合、探索和信息预算；区别只在于更新规则。

| 条件 | 在线可用信息 | 更新 | 作用 |
|---|---|---|---|
| `uniform` | 当前候选集合 | 固定均匀选择，不读历史 | 随机下界与探索上界 |
| `no_update` | 初始先验与当前任务上下文 | 不因反馈改变 | 判断任务/模型本身是否已足够 |
| `raw_acceptance` | 合法 recipient accept/reject | 直接计入 producer 分数 | 测量责任安全规则的增量 |
| `terminal_only` | 独立最终 outcome | 只更新终局奖励 | 检验 situated judgment 是否提供额外信息 |
| `contextual_trust` | 与 RARE 完全相同的 context、judgment、propensity 和延迟事件 | 同信息 trust/bandit 更新 | 最强非 RARE 解释 |
| `pooled_controller` | 允许公开的全部历史，但不读私有 scorer | 一个共享 controller | 集中控制上界，不代表个体角色学习 |
| `RARE` | 责任过滤后的 judgment/action/contract 事件 | 只对可归因 `(producer, context, version)` 增量更新 | 主候选 |

更新实现单独形成正交比较：同一表示、同一事件流、同一探索下比较 RLS、online
logistic/SGD、周期性 refit 和 RARE 的增量更新。RLS、Laya、AnyJev 或普通 SGD
不能在论文中被称为 RARE 的创新来源。

## 4. 主指标与停止规则

主指标在运行前固定为四组：

1. **信息价值**：recipient judgment 对独立 producer contract / later-use 结果的
   预测、校准和相对于 `raw_acceptance`/`terminal_only` 的增量；不把最终结果倒灌成
   当轮 label。
2. **闭环效果**：反馈到达后、下一次执行前的 assignment 改变，以及 confirmation
   root 上的质量、完整成本和返工成本；只按独立 stream 汇总。
3. **实时性**：每条合法反馈的 update p50/p95、选择端到端延迟、状态字节数、API/
   GPU/tool 成本；延迟 feedback 和乱序按预注册 replay 规则处理。
4. **稳定性**：旧 root holdout 的峰值/平均性能下降、漂移后的恢复窗口和 UNKNOWN
   率。单次没有观察到遗忘不构成稳定性结论。

停止规则：任何 root 的 task text、producer/recipient 归因、scorer isolation 或
ledger replay 失败，立即停止该 root 的真实链并保留 UNKNOWN；不得通过减少检查、改
label 或扩大 timeout 把它变成通过。若 RARE 与 `contextual_trust` 在相同信息和完整
成本下没有预先声明的增量，停止扩展模型和 A800，报告机制未被支持。

## 5. 当前决定

`PIPE3` 是条件性主候选，`MULTI3` 是低优先级 fallback；现在**不冻结 benchmark、
不启动新的 API 小链、不启动 A800**。下一步只有两项：补齐两个 root 的 manifest/信息
边界，随后在看不到 confirmation 结果的前提下冻结一张小批量开发卡。该门通过后才
执行新的真实链；失败只产生修复报告，不改变 Goal v1.0。
