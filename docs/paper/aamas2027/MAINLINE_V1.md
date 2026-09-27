# AAMAS 主线 v1：Learning Roles from Situated Peer Judgments

日期：2026-09-27
状态：内部研究稿的主线、方法合同和实验设计；不是投稿结论。

## 1. 论文只回答一个问题

在没有预先指定专家身份的协作流中，实际接收并使用交付物的 agent，对该交付的
情境化判断，能否形成**可归因的生产者角色证据**，改变后续任务开始前的责任分派，
并在相同信息与完整成本下改善团队质量？

这里的“角色”不是 prompt 中的标签，也不是一次选择后的分数。它必须满足三个可观测
条件：

1. 判断来自有真实依赖的 recipient/owner，并指向一份具体交付物；
2. 判断经过责任归属规则进入 producer 的角色证据；
3. 证据在下一次执行前改变一个合法的选择，并在未见任务上产生可测的质量或成本后果。

论文不同时声称能力学习、贡献分配、信誉传播、workflow 搜索和角色涌现。agent 的
技能与 workflow 可以按共同规则自然变化，但论文的唯一目标机制是：

```text
recipient 的 situated judgment
  -> responsibility-aware role evidence
  -> pre-execution peer choice
  -> later quality / cost
```

如果这个链条无法成立，结论收窄为“协议与失败边界”；不会用角色熵、接受率或一次
终局成功替代它。

## 2. 观察边界和最小事件

每轮只把下列对象作为原始输入：任务上下文 `x`、本轮候选 producer 集合 `C`、
实际选择 `a`、交付物 `o`、实际 recipient `j`。选择发生在任务开始前，只有 `a`
执行；候选的版本号和决策时快照随事件封存。

recipient 的反馈保存为结构化记录：

```text
judgment = {accept, integrate, upstream_fix, reject, unknown}
evidence = recipient 实际读取/使用/拒绝的交付片段或动作
action   = {use, modify_delivery, own_integration, redo, unknown}
delay    = feedback 到达选择器的时间
```

`judgment` 是意见，`action` 是行为，独立 producer contract check 是交付覆盖，
最终 scorer 是团队结果；四者不合并成一个“repair=0.5”标签。消费者正常完成自己
负责的 integration 不自动算作 producer 缺陷。若责任或用量无法识别，记录 `unknown`
并从该次更新中排除，不能为了训练方便改成 0。

在线更新只能读到已经到达的记录、决策时上下文和公开权限内的交付；gold、隐藏
grader、未来任务结果只能作为训练后的独立评估或预先声明的监督服务，不能泄漏到
选择、重试、停止或当轮更新。

## 3. 候选方法：责任安全的角色证据更新

当前锁定的是**方法合同**，不是已经证明有效的算法。候选方法称为
`Responsibility-Aware Role Evidence (RARE)`，其核心只有一个更新操作。

对 producer `v` 和情境 `c`，维护公共角色状态

```text
R(v,c) = (n(v,c), q(v,c), u(v,c))
```

其中 `n` 是有效证据量，`q` 是由 recipient judgment 产生的贡献证据，`u` 是
未能归因或被独立检查否定的证据量。一次事件只有在满足以下条件时才写入 `q`：

* recipient 确实看到了并采取了可审计动作；
* 交付物与 producer、任务上下文、版本和动作一一绑定；
* 动作不是 recipient 自己原本就要完成的正常 integration；
* 责任归因没有被最终团队失败替代。

否则事件写入 `u` 或保持 `unknown`，不会惩罚 producer。

选择器用决策时冻结的上下文表示 `h(x,v,c)` 计算角色分数：

$$
s(v\mid x,c)=w^\top h(x,v,c)+\beta\,
\frac{q(v,c)-u(v,c)}{n(v,c)+\alpha}.
$$

只执行候选集合中的一个 producer，按带最小探索概率的 softmax 选择。反馈到达后，
只对对应的 `(v,c,version)` 做一次增量更新；乱序反馈要么合并为可交换统计量，
要么按封存事件重放并记录 watermark。旧情境 holdout 上的风险上升超过信赖域时，
拒绝本次写入并保留事件。该保护是为了可测稳定性，不把“忘得少”写成未经验证的
定理。

这一定义把 `RARE` 与三个可混淆对象分开：

* `raw-acceptance`：直接把接受/拒绝计入 producer 分数；
* `private trust`：只让直接判断过该 producer 的 owner 使用自己的信任；
* `terminal-only`：只用最后任务成功/失败，不保留 recipient 的 situated judgment。

若 RARE 在相同信息、相同探索和相同成本下不能超过 raw-acceptance 或 contextual
trust，论文不得宣称它发现了新的 role-learning 机制。RLS、online logistic/SGD 和
周期性 refit 是训练方式的强比较，不是 RARE 的创新来源。

## 4. 基准与任务资格

主候选是 TeamBench-derived `PeerRoleBench-TB`。PIPE3 seed 0/1/2 的前置检查已经
通过了 payload、责任路径、hidden score、事件账本和列举的隔离检查；这只是进入真实
开发流的条件，不是最终 benchmark 冻结。科学资格仍需满足：

* 至少两个结构不同的 task root；当前 PIPE3 是第二 root 的条件性主候选，DIST1
  只保留开发诊断；
* producer 的公开交付义务由父进程或独立检查测量；recipient 的正常 integration、
  对交付的修改和 sink adoption 分开计账；
* recipient 真正执行依赖 producer 交付的行为，而不是脚本给两个 agent 贴角色名；
* source、tests、expected、scorer 和候选 workspace 的权限边界在运行前冻结；
* task root 级别划分 development / confirmation，改名 seed 不当作独立泛化样本。

TeamBench、DIST1、PIPE3 和现有 consumer worker 是可复用工程资产，不等于已经通过
科学 benchmark 锁定。若 PIPE3 或隔离资格失败，转 MULTI3；不继续修补一个没有真实
下游依赖的 root。

## 5. 必须比较的条件

首轮比较只保留能解释主问题的条件：

| 条件 | 读取的信息 | 作用 |
|---|---|---|
| random/local-uniform | 当前候选集合 | 选择下界与探索上界 |
| no-update | 初始先验、当前任务 | 判断单纯执行是否已足够 |
| raw acceptance | recipient 接受/拒绝 | 检验 RARE 的责任分离是否有增量 |
| contextual trust/bandit | 同一上下文、判断和 propensity | 最强同信息解释 |
| terminal-only | 独立最终结果 | 检验 situated judgment 是否比终局奖励多信息 |
| RARE | 责任安全的 recipient evidence | 主候选机制 |
| pooled controller | 全部允许的公共历史与同等预算 | 检验集中控制上界 |

训练更新另列为实现比较：RLS、online SGD/logistic、周期性 refit 和 RARE 的增量
更新使用同一表示、同一事件流、同一探索和同一旧任务 holdout。不能让 RARE 拿到
别的条件没有的记忆、gold 或更多调用。

## 6. 实验问题和停止规则

* **RQ1：信息价值。** recipient 的 situated judgment 是否能预测独立 producer
  contract / later-use 结果，超过 raw acceptance 和 terminal-only？
* **RQ2：角色闭环。** 反馈进入后，是否在下一次执行前改变未直接评价候选者的 owner
  的选择，并在新 root 上改变质量或完整成本？
* **RQ3：实时更新。** 在 selected-only、延迟和乱序反馈下，RARE 是否同时满足
  prequential utility、update p50/p95、状态大小和旧任务遗忘约束？
* **RQ4：边界。** 责任不清、consumer 自身出错、候选版本替换和任务漂移时，
  `unknown` 与保护更新是否比错误惩罚更稳健？

开发阶段先做零 LLM 的任务/评分/隔离资格和现有产物的离线责任回归；资格通过后，
在剩余 N03 开发预算内只开一批最小真实流，至少覆盖两个 root、两个独立 reset stream
和 no-update / RARE / same-information trust 三个条件。确认实验必须在看到开发结果后
冻结任务、种子、预算、更新器、失败规则和主指标。任何流无法形成真实 recipient
judgment、责任标签或未来 assignment，记为 UNKNOWN 并触发诊断，不补写成失败或成功。

主指标不是单一成功率，而是：未来责任选择后的官方质量、完整 API/token/tool/返工
成本、角色选择改变比例、judge-to-service 生效延迟、旧任务峰值遗忘。结果按独立
stream 汇总，不能把同一 stream 的多个 episode 当成独立样本。

## 7. 当前证据能写进论文什么

可写：协议已修复了“先生成所有候选再挑选”“记录 assignment 却不消费”“把消费者
自己的 integration 归责给 producer”等测量错误；两条真实 v3 链证明真实 API、选择、
判断、消费源码和后续 assignment 可以连起来；同时暴露了 priority 交付错误被四项
consumer 分数漏掉、更新概率没有变化、peer 没有持续个人经验等限制。

不可写：RARE 已经有效、实时训练已经实现、peer 已形成专长、TeamBench 已冻结、
A800 结果支持方法，或 v3 的两个限定 episode 足以证明跨 root 泛化。当前稿件应是
`internal pre-results`，主结果表留空，直到 RQ1–RQ3 有可审计的独立流证据。

## 8. 论文结构

1. **Introduction：** 真实依赖中的静态/全局选择为何丢失 consumer context；提出
   situated judgment→role evidence 的单一问题。
2. **Problem and protocol：** 事件、信息边界、责任切分、延迟和版本语义。
3. **RARE：** 一个可执行更新规则；明确它与 raw acceptance / trust / terminal-only
   的区别和可被推翻的条件。
4. **Benchmark and evaluation：** PeerRoleBench-TB 资格、同信息基线、成本、流级
   不确定性和四个 RQ。
5. **Results：** 先报告资格和信息质量，再报告未来责任闭环，最后报告实时性/遗忘；
   失败和 UNKNOWN 独立成表。
6. **Related work and limitations：** Meta-Team、RAPS、Sero/RepuNet、C3、
   contextual trust/bandit 等只作为近邻和解释边界，不把“别人评价 agent”本身写成创新。
