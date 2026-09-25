# Peer-role benchmark 候选复审与主 benchmark 选择

> 日期：2026-09-25  
> 状态：建议冻结，等待用户确认后写入新的 ADR
> 目的：为“从接收方判断中学习 peer role，并把证据用于后续分派”找到可复现、可比较、能直接跑小批量实验的 benchmark。

## 先给结论

之前把 CooperBench 当成完整 benchmark 是错误的。经过对公开代码、数据格式和运行链路的重新核查，目前最合适的主任务基底是 **TeamBench**，具体采用其 MIT 许可仓库的固定 commit `d185aef1916fd86a9ba554d581fd256319a973af`，并在外层加入一个很薄的 `PeerRoleBench-TB` 协议层。

这不是把 TeamBench 的原始结果冒充成我们的结果。准确说法是：

> TeamBench 提供隔离角色、可交付 workspace、隐藏规格、确定性 grader 和 held-out seed；PeerRoleBench-TB 只增加候选 peer、持久身份、接收方的终局前判断、判断/结果的延迟 ledger，以及下一任务的责任再分派。

这个选择的理由是：TeamBench 已经把最贵、最容易出错的任务环境和客观评分做完了；我们的新增代码只围绕“谁来做、谁判断、下一次怎么分派”展开，科学变量不会和重新造任务环境混在一起。

## 必须满足的 benchmark 条件

一个能支撑主论文的 benchmark 必须同时提供：

1. **真实可执行的交付物或状态变化**：不是只评最后一段文字。
2. **接收方可观察的中间结果**：接收方要能在 terminal scorer 之前给出 accept / repair / reject / redo 判断。
3. **独立客观的 terminal signal**：判断不能自己充当真值，最终仍由测试、状态 diff 或规则引擎给分。
4. **可追溯 lineage**：能回答哪个 peer 产出、哪个接收方采用/返工、最后分数如何归因。
5. **跨 episode 的身份和再分派**：否则无法研究“判断改变了未来责任”。
6. **公开代码、数据或明确许可**：没有许可的仓库不能作为可直接改造和发布的主实现。
7. **可做小批量、可做 held-out split**：先用 2–10 个任务验证协议，再扩大到正式评测。

## 候选逐项审查

| 候选 | 已有能力 | 缺口 | 许可/复现 | 结论 |
|---|---|---|---|---|
| **TeamBench** | Planner/Executor/Verifier 由 Docker 访问边界强制隔离；workspace 是真实交付物；每任务有 `grade.sh`，输出 `[0,1]` partial score；851 templates / 931 seeded instances；5 个 role ablation；支持 hidden seed | 原生角色固定；没有 persistent peer ledger、later assignment 和结构化 pre-terminal judgment | MIT；官方仓库和 HF 数据；本地 mock smoke 已通 | **主 benchmark substrate；改造最薄，主张边界清楚** |
| **EntCollabBench** | 11 个权限隔离的企业角色；160 workflow + 40 multi-step workflow + 80 approval + 20 multi-step approval；MCP 工具执行、数据库 state diff、确定性 policy adjudication；天然有多跳 delegation | 角色和 delegate 图固定；没有独立 producer artifact judgment；没有 later assignment；仓库未声明 license；Docker + 多服务运行成本高 | 代码公开、数据在 HF，但缺明确许可 | **第二真实 workflow；不作为主实现依赖** |
| **MECoBench** | MIT；VirtualHome；96 parallel + 96 sequential；sequential 需要跨空间 object handover；success/steps 等客观指标 | embodied 环境重；角色固定；handover 是物体转移，不是可审计的 peer artifact judgment | MIT；代码和数据公开 | **外部 handoff stress test，不作为主 benchmark** |
| **CoCoBench (AgibotGeneral)** | 897 oracle-validated embodied instances；D1 allocation、D2 precedence、D3 exclusion、D4 producer-buffer-consumer handoff；construct-level deterministic score | producer/consumer 由任务配置固定；没有 persistent identity、later assignment 和 quality judgment；环境依赖重；仓库许可需单独确认 | 代码公开；许可未核实 | **概念上最接近 handoff，工程上不适合作主线** |
| **AgentCollabBench** | 900 个任务；5 种拓扑；2–6 agent；RTD/CLC 有确定性过程指标；IDR/CPR 有独立 judge | 主要测约束丢失、错误传播、信息泄漏；没有 artifact use、terminal task quality 或 recipient adoption | 代码和 JSON 任务公开 | **诊断控制，不能支撑 role-learning 主结果** |
| **CoopEval** | 重复交互、随机换 peer、公开 reputation、payoff 和 partner history；游戏真值清晰；MIT 代码 | 没有 artifact、recipient judgment 和真实工作流；是社会困境而非交付任务 | 代码公开；适合低成本验证 selector 的 online update | **数学/机制 sanity benchmark，不替代主 benchmark** |
| **CooperBench** | 真实代码仓库、patch、merge pressure、native tests | 原生没有 recipient situated judgment、artifact adoption lineage、跨任务 identity；存在 `solo-agent1` fallback 风险 | 代码公开，但协议不匹配 | **仅保留 coding integration diagnostic** |
| **DecisionBench** | 离线异构候选选择、质量/成本/profile 数据 | 没有执行中接收方、artifact lineage 或后续责任 | 数据和代码公开 | **只做 selector-only baseline** |

公开来源： [TeamBench 仓库](https://github.com/ybkim95/TeamBench)、[TeamBench 论文](https://arxiv.org/abs/2605.07073)、[EntCollabBench 仓库](https://github.com/yutao1024/EntCollabBench)、[EntCollabBench 论文](https://arxiv.org/abs/2605.08761)、[MECoBench 仓库](https://github.com/q-i-n-g/MECoBench)、[CoCoBench 论文](https://arxiv.org/abs/2608.28266)、[AgentCollabBench 仓库](https://github.com/aritra741/AgentCollabBench)、[CoopEval 仓库](https://github.com/Xiao215/CoopEval)。

## 为什么主选 TeamBench

它不是因为任务数量最多，而是因为它同时满足四个关键要求：

- **交付物可见但权限受限**：Planner 只能看完整规格，Executor 修改 workspace，Verifier 只能读规格和 workspace。这使“接收方看到了什么”可控，避免模型绕过交付链。
- **判断与真值分离**：Verifier 的 attestation 是中间判断，`grade.sh` 是 terminal truth。我们的学习器可以只看判断和已到达的结果，不把隐藏测试泄漏给 selector。
- **任务生成和 held-out seed 已存在**：可按 task family/repository 分组做 train/stream/test，避免把某个 patch 记忆当成能力。
- **官方已有 ablation**：`oracle / restricted / full / team_no_plan / team_no_verify` 能直接作为环境控制和 sanity baseline，而不用重写 grader。

我们已经在本地固定 commit 上真实跑通了 `DIST1_queue_race / oracle / seed0 / mock`：harness、role runner、deterministic grader 和 `score.json` 全部连通，结果是 `passed=false, partial_score=0.08`。这只是运行链路 smoke，不是模型质量结论；原始 JSONL、summary 和 stdout 已保存到 [`experiments/logs/benchmark_selection_20260925/`](../../experiments/logs/benchmark_selection_20260925/)。

## PeerRoleBench-TB 的最小协议层

保留 TeamBench 原始 task、generator、Docker 边界和 `grade.sh`，只增加下面六件事：

```text
candidate peer roster with persistent agent_id/version
    -> selector chooses one eligible Executor (and, if enabled, Verifier)
    -> selected peer produces workspace artifact
    -> Verifier records accept / repair / reject / redo before grade.sh
    -> grade.sh returns terminal reward and artifact lineage is sealed
    -> delayed ledger update changes later-task assignment probabilities
```

每条 episode 至少记录：

```json
{
  "task_id": "DIST1_queue_race",
  "seed": 0,
  "selected_peer": "peer_02",
  "candidate_set": ["peer_01", "peer_02", "peer_03"],
  "artifact_hash": "...",
  "recipient_judgment": "repair",
  "judgment_time": "...",
  "terminal_score": 0.78,
  "used_after_judgment": true,
  "role_update_visible_at": "next_episode"
}
```

这里的 `recipient_judgment` 必须先封存，之后才能运行 terminal grader；selector 不能读取 `spec.md`、hidden tests 或 grader 的 expected JSON。`terminal_score` 只能在反馈到达后写入 ledger，不能在选择时泄漏。

## 第一轮不做大实验

先做一个完全可审计的 2-task gate：

- 选两个不同 task family、固定两个 seed；
- 3 个 persistent peer，先让他们都具备同一 Executor 接口；
- 比较 `random`、`static-best`、`terminal-only`、`recipient-judgment` 四个条件；
- recipient 在 grade 前输出 accept/repair/reject/redo，且记录是否真的采用/返工；
- 下一任务只允许使用已经到达的第一任务反馈；
- 统计 final partial score、cumulative regret、judgment calibration、later-assignment change 和 p95 routing overhead。

通过 gate 的条件不是“方法分数立刻最高”，而是必须能从日志中区分：

1. 交付物自身有用；
2. 接收方判断额外有用；
3. 判断确实改变了下一次责任分派。

如果这三点不能在 2-task gate 中区分，就不能扩大实验，也不能把结果写成 learning roles from others' judgment。

## 最终 benchmark 组合

论文主结果使用：

```text
PeerRoleBench-TB (TeamBench substrate)  — 主 benchmark
CoopEval                                  — selector/reputation 机制 sanity
EntCollabBench                            — 企业 workflow 外部有效性
AgentCollabBench                          — 拓扑与信息传递诊断控制
```

CooperBench 和 DecisionBench 不再承担主 benchmark 角色。这样既不把一个不具备完整因果链的现成环境硬说成 role-learning benchmark，也不从零重造任务、grader 和状态环境。

## 下一步实现顺序

1. 固定 TeamBench commit、90-task leaderboard 子集和 2-task gate manifest。
2. 写 `PeerRoleBench-TB` 外层 adapter，不修改原始 `grade.sh`。
3. 先用 deterministic/mock peer 跑通 lineage、delayed ledger 和 later assignment；这一步不调用 LLM。
4. 再接入真实 agent，比较四个最小 baseline。
5. 只有 gate 通过后，才在 A800 上跑真实 LLM 小批量；所有运行写入 JSONL 原始日志和 summary。
