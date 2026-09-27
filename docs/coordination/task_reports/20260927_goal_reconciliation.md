# Task report：Goal reconciliation / 2026-09-27

状态：`PARTIAL`。`goal_change_requested=false`。本报告不修改 Goal v1.0。

## 本次任务

从当前主线、ADR、任务账本、真实 API 记录、PIPE3 资格报告和 LaTeX 草稿中重建项目
目标，并把证据逐项映射到 [`GOAL.md`](../GOAL.md)。本轮没有新增 LLM 推理或 A800
作业；新增的材料/IPC 检查均是零 LLM 工程资格检查。

## 逐项对照

| Goal 条目 | 当前状态 | 证据与已完成内容 | 未完成原因/边界 |
|---|---|---|---|
| ER-G1 科学链条与论文产出 | `PARTIAL` | 主线、RARE 合同、责任/UNKNOWN 语义已写入 [MAINLINE_V1](../../paper/aamas2027/MAINLINE_V1.md) 和 ADR0022 | N02 两条完整限定链中反馈没有改变概率/选人；没有未见 root 的质量—成本收益 |
| ER-G1 recipient 真实使用与归因 | `PARTIAL` | 协议已区分 judgment、action、producer contract、final score；发现 consumer4/4 漏掉 priority 缺陷，正常 integration 不再自动归责 producer | scorer 覆盖和 upstream correctness 仍需真实 runner 验证；部分已有数据只能保留为诊断 |
| ER-G3 非 oracle、双 root、可复现 benchmark | `OPEN` | TeamBench pin、PIPE3 静态契约/ledger fixture、材料适配器 seed0/1/2、单 producer IPC probe 已完成 | 原 PIPE3 文本泄露三个 bug；recipient、hidden scorer、真实 ledger replay、第二独立 root 和 root split 未完成 |
| ER-G2 新的在线训练/更新机制 | `OPEN` | RARE 仅是候选方法合同；已声明 RLS、SGD、周期 refit、trust/bandit 等强对照 | 尚未确定最终 backbone/表示/更新器；没有每条反馈实时更新、时延、状态大小、遗忘和准确率证据 |
| ER-G2 实时性、时效性、稳定性 | `OPEN` | Goal 已冻结测量项；历史 linear/RLS 只作探索或比较，不能支持结论 | 没有合法学习信号和纵向 peer state，不能开始有意义的实时训练比较 |
| ER-G3 强 baseline 与同信息公平比较 | `PARTIAL` | baseline 矩阵已预先写入主线 | 尚未在合格 benchmark 上执行；不能从程序夹具的同分数结果推断方法无效或有效 |
| ER-G4 真实 API/逐事件可审计实验 | `PARTIAL` | N02 使用真实 API；保留 4 次 episode 尝试、2 条完整限定链、token/错误/哈希日志；材料/IPC preflight 也有 config/raw/summary | N02 信号无效且预算已关闭；N03 合格小流尚未启动 |
| ER-G4 A800 训练准入 | `OPEN` | 明确延后到真实信号和训练瓶颈成立后 | 现在启动会把 scorer 缺陷和 exchangeable peer 当成训练信号，违反 Goal gate |
| ER-G1 论文包 | `PARTIAL` | 主线、claim-evidence matrix、AAMAS LaTeX internal pre-results 草稿已建立并编译 | 没有主结果、benchmark lock、方法效果和确认实验；不能称投稿完成 |

## 当前真正完成的部分

1. 研究问题已经从旧 allocation/router 草稿收敛为一个问题：真实 recipient 的
   situated judgment 能否形成可归因角色证据并改变未来责任。
2. 执行前选择、实际交付、消费行为、判断、终局评分、assignment 和 UNKNOWN 的协议
   边界已被代码与回归测试约束。
3. N02 的真实运行没有被包装成成功：四次 episode 尝试已关闭，transport UNKNOWN、
   scorer blind spot、错误责任归因、概率不变和 peer 无持久状态均被保留。
4. PIPE3 现在有静态任务契约、非 oracle 材料适配器和一次单 producer IPC 可见性探针；
   这些是进入下一资格门的工程资产，不是 benchmark 结果。
5. 论文草稿已经按证据边界留空结果表，能够继续写作而不提前声称方法有效。

## 没有完成的部分及原因

- **方法没有定型**：缺少合法、可归因、可纵向学习的标签；不是因为模型效果不好而放弃，
  而是因为先验 scorer/任务无法测出该问题。
- **benchmark 没锁定**：原 PIPE3 task text 暴露答案，且真实 runner/scorer/ledger 边界
  尚未验证；因此不能把 seed 变成样本数。
- **peer 没有个体差异**：N02 的 fresh peers 同构且没有持久个人经历，无法学习 peer
  suitability；继续调用只会增加无效成本。
- **baseline 没有结果**：基线合同已经确定，但必须等同一真实事件流和合法 scorer，
  否则比较没有解释力。
- **A800 没启动**：当前没有值得训练的信号或具体瓶颈；这是遵守 Goal gate，不是降级。

## 下一步顺序

1. 完成 PIPE3 recipient payload、delivery attachment、hidden scorer/operator ledger
   的真实 IPC 边界和 exact-once lineage replay。
2. 在不泄露答案的 task root 上完成多事件、缺字段、异常、正常 integration 覆盖，并
   确认第二个结构 root 或正式转向新的候选；不把失败数据改成正例。
3. 明确每个 agent 合法持久经历如何进入未来行为，并加入 identity-renaming、no-update、
   raw acceptance、same-information contextual trust/bandit 对照。
4. 只在上述资格通过后冻结 N03 真实 API 小流；每条反馈、延迟、成本和 UNKNOWN 全量记录。
5. 根据真实瓶颈选择 backbone/update challenger，再决定是否需要 Nebula A800；最后做
   独立 confirmation 和论文结果填充。

## Goal 变更检查

本次没有提出任何 Goal 修改或降级。实验失败、数据缺陷、预算消耗和尚未完成的证据均
被记录为任务状态与下一步工程问题；如果未来认为研究问题本身应改变，必须由用户明确
同意并新增 ADR，不能由本报告自动完成。
