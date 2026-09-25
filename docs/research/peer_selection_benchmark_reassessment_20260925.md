# Peer selection benchmark 重新评估：从任务基底转向真实 selector benchmark

> 日期：2026-09-25  
> 状态：替代“TeamBench 作为主 benchmark”的上一版建议；尚未写入 Accepted ADR。  
> 触发：上一版虽然找到可复用任务环境，但仍然没有找到真正测量 peer selection 的 benchmark。

## 结论

如果当前论文的第一科学问题是：

> 一个 agent 在无向局部图中，依据邻居的历史交互结果选择 peer，并用 selected-only 的反馈实时更新选择器，是否能在变化环境中获得更高收益、较低遗憾和更好的探索/稳定性权衡？

那么主 benchmark 应改为 **shMARL / graph-ipd 的 partner-selection track**，而不是 TeamBench。

官方仓库固定到 `00ef417f60053569175b2b50d0f0e25ff8eb7007`，MIT 许可：[graph-ipd](https://github.com/geronest/graph-ipd)。对应论文明确把每个 agent 作为图节点，把邻居作为候选 opponent，并让 partner-selection module 输出每个候选的选择概率：[论文](https://arxiv.org/abs/2608.28977)。

这是目前找到的第一个真正满足 peer-selector 核心数学形式的公开 benchmark：它不是把固定角色任务外面包一层 selector，而是把 partner selection 本身作为环境的一部分。

## 它与我们的数学问题逐项对应

| 我们的概念 | graph-ipd 中的实例 |
|---|---|
| agent 图 \(G=(V,E)\) | `agentnet.py` 生成 ER、Watts–Strogatz、Barabási–Albert 等图；邻接矩阵是局部候选约束 |
| persistent agent | 一个节点在整个训练/评估过程中持续存在 |
| 候选集合 \(C_t(i)\) | 节点 \(i\) 的邻居集合 \(\mathcal N(i)\)，不是全体 agent |
| selector 输入 | 候选邻居的历史动作状态；可选 opponent identity |
| selector 输出 | `select_partner` 对候选集合输出选择概率并采样 partner |
| selected-only feedback | 选择后只执行该 pair 的 IPD，selector buffer 记录被选 partner 的状态/动作并接收该轮 payoff |
| objective label/reward | PD 的确定性 payoff 矩阵，terminal/round reward 可直接审计 |
| online update | SAC/DQN partner-selection network 按交互轨迹更新 |
| baseline | random matching、不同 history length、是否提供 identity、不同图拓扑 |
| temporal adaptation | 论文和代码已有长序列、多 seed、partner selection 与 random matching 对照 |

因此它直接支持我们要研究的四个量：选择概率、邻居局部性、selected-only 反馈、在线更新后的 cumulative return/regret。

## 为什么 TeamBench 不能继续作为主 selector benchmark

TeamBench 仍然有价值，但它验证的是另一层问题：artifact 交付、Verifier 判定和最终软件测试。它原生把 Planner/Executor/Verifier 角色固定好，selector 是我们额外加的协议；所以它适合回答：

> 在真实交付任务中，学习到的 peer policy 能否改变 artifact 的最终质量？

它不适合先回答：

> peer selection 机制本身是否有效？

如果一开始就用 TeamBench，任务难度、LLM 调用失败、workspace 修改、Verifier 误判和 selector 学习会同时变化，无法知道方法到底失败在哪一层。主 benchmark 应先用 graph-ipd 把 selector 的因果链跑通，再把同一个 selector 接到 TeamBench-derived `PeerRoleBench-TB` 做外部有效性。

## 主 benchmark 的正式定义

### Track A：PeerSelect-IPD（主机制 benchmark）

固定三类图：ring/line、ER、BA；每类至少 20 个 seeds。每个节点持久存在，候选只取邻居。每轮包含：

```text
观察邻居历史
→ 输出候选选择概率
→ 采样一个 partner
→ 与被选 partner 进行一轮/一局 IPD
→ 只把该 pair 的 payoff 和交互摘要写入 selected-only queue
→ 更新 selector
```

需要保留的原生 baseline：

- random matching；
- no-history selector；
- history-only selector；
- identity-aware selector；
- 原作者 SAC/DQN partner selector。

我们新增的 baseline：

- static score；
- OnlineRLS/linear bandit；
- residual fast-weight；
- 我们的实时更新器。

主指标：平均 payoff、cumulative regret、partner-selection precision、探索覆盖率、环境切换后的 recovery time、每步更新延迟和显存占用。

### Track B：ArtifactRole-TB（外部任务 benchmark）

使用 TeamBench 的 task/generator/grade.sh，但只在 Track A 机制通过后接入。这里增加：

- persistent peer id；
- candidate executor pool；
- recipient pre-terminal judgment；
- artifact adoption/repair/reject lineage；
- delayed ledger；
- later assignment。

Track B 的指标是最终 partial score、artifact adoption accuracy 和 later-assignment gain；它不能替代 Track A 的 selector 机制结果。

### Track C：Enterprise transfer

如果 EntCollabBench 的许可问题解决，再用其 MCP workflow 和 database state diff 做一次外部 transfer；目前不把它纳入主代码依赖。

## 已完成的真实性核查

已将 graph-ipd 拉到本地并固定 commit，源码中确认了：

- `create_network_*` 生成无向邻居图；
- `StateManager` 编码历史和可选 identity；
- `SACAgent.select_partner(cand_agents, states_op)` 对候选集合输出概率并采样；
- partner-selection buffer 保存 selected state/action/next-state，后续训练使用 reward。

依赖检查和 smoke 已经实际完成。第一次命令错误地把 `set_id` 写成了不存在的目录，第二次按官方 README 修正后，官方 `smoke_ps` 在隔离 Python 3.9 环境中完成了 **2 个 repetition × 200 steps、4 个 agent、SAC partner selector**，生成 selections、action pairs、selector reward summaries 和 network plots。上游 `bin/train_ray.py` 的 post-processing 还存在一个未定义 `results_dir` 的 NameError；我们只在本地验证副本中补了一个参数传递，随后 smoke 完整结束（`returncode=0`）。这不是我们的算法结果，只证明 benchmark 的 selector 训练/记录/汇总链路能跑。

可复核证据：[`graph_ipd_smoke_ps_patched_summary.json`](../../experiments/logs/benchmark_selection_20260925/graph_ipd_smoke_ps_patched_summary.json)、[`graph_ipd_smoke_ps_metrics.json`](../../experiments/logs/benchmark_selection_20260925/graph_ipd_smoke_ps_metrics.json)、[`graph_ipd_smoke_ps_patched_output.txt`](../../experiments/logs/benchmark_selection_20260925/graph_ipd_smoke_ps_patched_output.txt)。非 Ray 的 6 个仓库测试为 `6 passed in 2.07s`；完整测试在 Ray teardown 阶段耗时过长后中断，未把它写成通过，记录见 [`graph_ipd_test_log.jsonl`](../../experiments/logs/benchmark_selection_20260925/graph_ipd_test_log.jsonl)。

## 重新审查后排除的“看起来更贴近”的项目

搜索到的 Diagon 论文在概念上非常接近：它让 agent 发任务、竞标、选择 contractor、执行、评价交付物、结算并积累双边 reputation；论文也宣称代码和数据公开（[论文](https://arxiv.org/abs/2604.06688)）。但截至本次审查，论文给出的 `assassin808/diagon` GitHub URL 返回 404，无法固定 commit、下载代码或复现实验。因此它只能作为相关工作和设计启发，不能作为我们当前的 benchmark 依赖。

另外几个可下载的市场项目也不能替代 benchmark：`upwork/simploy` 的框架假设把任务完成写成自动 `success=True`，没有可审计的任务真值；`agenlon` 和 `agent-arena` 是可运行的编排/拍卖系统，但没有冻结任务集、held-out split 和独立 scorer。把这些项目叫 benchmark 会再次把系统 demo 和科学评测混为一谈。

## 这次选择的边界

graph-ipd 的优点是 peer selection 数学形式和反馈机制真实存在；它的缺点是反馈是博弈 payoff，不是“接收方对 artifact 的自然语言判断”。因此最终论文不能只用它声称已经解决了 learning roles from others' judgment。严谨的路线是：

```text
graph-ipd：证明 selector / online update / graph / selected-only feedback 机制
TeamBench-TB：证明 artifact judgment 能否转化为后续责任分派
```

所以当前不是再找一个万能仓库，而是冻结一个两层 benchmark contract：`PeerSelect-IPD` 负责先验可证的 selector/online-update 机制，`ArtifactRole-TB` 负责论文核心的 producer→recipient judgment→use/rework→terminal outcome→later assignment。两层共用同一个 candidate-set、selected-only event、delayed ledger 和 updater API；只有 Track A 的机制 sanity 通过，才启动 Track B 的真实 LLM 交付实验。

这比把一个固定角色 benchmark 改造成 selector 后直接称为主 benchmark 更干净，也能兼容 tool-select 项目：Track A 的 selector/ledger/update API 可以直接共享，Track B 只替换环境 adapter 和 label extractor。
