# 最小模型可实现性与合理性审查

日期：2026-09-25

## 结论

当前方案分成两个层次，结论不能合并：

1. **七元 selector/tool 核可以直接运行。** 现有 `OnlineRLSHead` 已经支持候选打分、探索采样、propensity 记录、selected-only 标签更新、延迟字段和状态快照；`StreamJEVCore` 已经支持一个小型 gated state 更新器。现有协议测试 `15 passed`。
2. **八元 peer-judged role 模型还不能端到端运行。** 真实 producer→consumer/judge 观察已经存在，但当前协议没有一等的 judge/source 字段，更新器也没有使用 judge 信息，更没有“角色证据影响下一次职责选择”的真实闭环。因此现在可以跑的是“选择器协议和更新器 smoke”，不能声称已经验证了 learning roles from others' judge。

## 变量到实现的核对

| 数学量 | 现有来源 | 当前状态 |
|---|---|---|
| `x_t` | `DecisionEvent.context`（`protocol.py:47–59`） | 有容器；`replay_adapter.py:49–52` 只保留分子任务字段，会丢掉 peer case 的 `task/stage`，需 peer adapter |
| `C_t` | `Candidate`（`protocol.py:37–44`） | 候选、版本、描述可表示；尚无局部 peer 图/邻域生成器 |
| `a_t` | `OnlineRLSHead.choose()`（`online_head.py:139–160`） | 可直接运行，返回采样动作和实际 propensity |
| `o_t` | producer proposal 或 tool output | 真实日志有输出；Stream-JEV 协议没有强制的 delivery→source-event 绑定 |
| `j_t` | 真实 AppWorld consumer 身份 | 目前只可放进 `FeedbackEvent.metadata`，不是必填字段，也不参与更新 |
| `y_t` | `FeedbackEvent.label`、`make_feedback_event()` | 可接二值/软标签；`use/accept` 与 objective task success 尚未分离 |
| `δ_t` | `arrived_at-selected_at`（`replay_adapter.py:71–90`） | 可计算；文档按 tick、adapter 按时间戳，必须冻结单位和边界 |
| `s_t` | `OnlineRLSHead.snapshot()` 或 `NeuralState` | 可更新的参数/记忆存在；尚不等于可审计的公共角色证据 |
| `B_k,U` | synthetic runner 的 `pending` 队列和 `head.update()` | 合成流能跑；真实 consumer 事件、持久化到达队列、事件 join、原子发布尚未接通 |

## 已验证的真实性边界

审查实际复跑：

```text
python3 -m pytest -q references/aamas/streamjev_20260924
15 passed
```

这证明协议、RLS head、neural fast state 和 replay 组件可以执行，不证明真实 peer
选择收益。已有 selected-only RLS 结果来自固定的隐藏合成流；其实际 Bernoulli 改善
约为 `+0.503 pp`，配对区间跨 0，不能写成稳定优越性。神经 A800 记录使用
`torch.randn` 缓存向量，只能支持 runtime probe，不能支持真实数据准确率或完整
端到端 p95 结论。

已有真实 AppWorld v4/v5 case `3c13f5a_3` 确实记录了 producer proposal、consumer
accept/use 和实际执行，但官方结果为 `5 assertions passed, 1 failed,
success=false`。它证明 `o_t,j_t,y_t` 可以采集；它没有证明 judge→online update→future
responsibility，也不能把 `use=1` 直接当成任务正确率。

## 合理性审查

当前依赖链是合理的：

$$
(x_t,C_t,s_t)
\rightarrow a_t
\rightarrow o_t
\rightarrow j_t
\rightarrow y_t
\rightarrow s_{t+1}.
$$

但需要四个明确修正：

1. `j_t` 应由任务 owner/consumer 规则产生并可追踪；若 owner 已在 `x_t` 中，优先写成 `j_t=owner(x_t)`，不要无来源地引入一个候选 judge 集合。
2. `y_t` 是预先冻结的标量评分协议。`use=1/rework=0.5/reject=0` 只是协作结果代理，不能直接称为客观任务正确率；真实 objective success 必须另行记录和报告。
3. `s_t` 要统一为在线选择器状态；公共角色证据是其中可传播的记录，不能把私有参数、judge 信念和公共证据混为同一个概念。
4. 到达反馈应保留 source decision index（有序事件列表），不能只用无序的同构 tuple；否则乱序反馈、重复事件和对应 propensity 无法审计。

固定旧任务约束也只能施加在语义未发生变化的回访切片。发生概念反转时，旧任务保持率和新任务适应率可能数学上互相冲突；这时必须报告恢复速度，而不能把旧准确率约束当作普适真理。

## 实时性、性能和准确率

- **实时性：** 小头的单事件更新在代码层面可执行；但文档中的 `4.1 ms p95` 是教学数值，不是当前端到端测量。必须测量 feedback receipt→state publish 的 p95，包含事件 join、序列化、队列和 checkpoint。
- **性能：** RLS 和 gated state 都是低维、可在线更新的候选实现；backbone 编码、候选扩展和真实 judge 延迟尚未纳入测量。
- **准确率：** 目前没有真实 peer role 的未来职责指标，也没有把 consumer use 与官方 task success 分开后的增益证据。公式不能推出准确率，必须通过预注册的小闭环实验测得。

## 最小闭环和停止条件

先不训练新 backbone。复用现有 runner、候选对象、RLS `choose/update/snapshot` 和
官方 evaluator，新增四个薄适配层：

1. peer context/candidate adapter，完整保留任务 JSON、候选版本和局部邻域；
2. delivery/judge provenance，强制记录 `producer_event_id`、`judge_id`、label source 和 actual-use；
3. durable delayed-arrival queue，按 source decision index 重放并原子发布 `s_{t+1}`；
4. role-assignment evaluator，验证更新后的公开证据是否改变下一次职责分配。

用一个冻结的小批量做三臂比较：静态 selector、RLS online selector、候选新更新器；
相同候选、探索率、预算和 judge 信息。至少同时报告：consumer use、official task
success、未来职责选择、旧语义切片保持率、概念变化后的恢复时间、更新端到端 p50/p95。
如果没有完整的 judge→update→future assignment 链，停止方法优越性结论，只报告协议接线结果。
