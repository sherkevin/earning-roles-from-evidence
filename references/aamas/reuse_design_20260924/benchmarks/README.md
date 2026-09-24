# 可复用 benchmark 选择：原始 peer-judged role formation

**日期：2026-09-24。范围：官方仓库/论文的只读审计、少量公开任务文件保存和零模型完整性检查。没有调用 LLM API、没有安装 Docker、没有跑完整 benchmark。** 原始仓库提交、URL、许可证和本地文件 SHA-256 见 [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)；完整性检查见 [INTEGRITY_CHECK_CONFIG.json](INTEGRITY_CHECK_CONFIG.json) 与 [INTEGRITY_CHECK_RESULTS.json](INTEGRITY_CHECK_RESULTS.json)。

## 先给选择

**主 benchmark：CooperBench（固定提交 `63b9d44d9f39a02fccf5bf0052db48a917a011fd`）。**

原因是它的核心产物天然是可交付、可集成、可测试的代码补丁：一个 producer 可以提交 patch 和说明，另一个实际 owner 可以决定接收、修改、拒绝或重新实现；官方 sandbox 直接提供 `test_merged`、`test_solo`、`evaluate_merge`，能把最终功能质量从“接收者说有用”中分离出来。原仓库的 `runner_coop.py` / `runner_team.py` 还会保留每个 agent 的 patch、trajectory、conversation 和成本字段。它最适合把我们的故事变成一个可审计的 **producer → recipient judgment/use/repair → objective integration result → later responsibility** 流程。

**次 benchmark：AgentWorld（固定提交 `df5237da96a3ef00f602950baa362d14d3a618fe`）。**

它的优势是原生存在多 agent、状态世界、聊天、资源转移和多轮协作，并有 100 级任务风格的任务文件、轨迹记录和程序化 `task_verifier.py`。现成 `agents/experiment.py` 已有 single-agent upper bound、no-communication、shared-plan、no-roles 和 random-agent 等开发对照。它适合在 CooperBench 代码交付实验完成后验证：我们的更新规则是否只对代码 patch 有效，还是也能在有状态、多步骤、资源交接环境中改变后续职责。

**MARBLE / MultiAgentBench 不作为主或次 benchmark。** 它可以借用 agent graph、共享 memory、coding environment 和配置格式，但其公开 coding config 明确规定 agent1 必须创建、agent2/3 必须修改，且动作集合和顺序被 profiles 预先写死；`metrics.evaluate_llm` 还使用 LLM evaluator。它适合拿来拼装 workflow/agent adapter，不适合直接承担“角色由 peer judgment 形成”的主要证据。

现有 AppWorld 仍保留为本机开发和协议调试环境；它有很好的离线 state evaluator，但 producer-consumer 依赖和后续角色状态都是我们新增的，因此不能单独称为天然多 agent benchmark。

## 为什么 CooperBench 最匹配原故事

我们的核心因果链是：

```text
producer 产生 patch/说明
  → recipient 在看到或没看到部分信息时封存 accept / reject / repair 及拟采取动作
  → recipient 实际集成、返工或独立重做
  → 官方测试与合并状态提供终局事实
  → 该事件形成 producer 的角色证据
  → 未直接评价该 producer 的后续 owner 选择下一责任
```

CooperBench 已经提供其中成本最高的三块：

| 所需功能 | 可直接复用的上游结构 | 仍需我们加的协议 |
|---|---|---|
| 真实可交付物 | `runner_coop.py`、`runner_team.py` 保存每人 patch、trajectory、conversation | 结构化交付 manifest、引用文件、前行动作计划 |
| 客观结果 | `eval_sandbox.py::test_merged` 合并两份 patch 后分别跑两套 feature tests；`test_solo` 给单人上界 | 记录 merge status/strategy，并禁止把 solo fallback 当成双人协作成功 |
| 交互日志 | 每 agent 的消息、patch、调用/步数和 token 结果 | recipient 的 accept/reject/repair 必须在终局测试前封存 |
| 强基线 | 原生 `solo`、`coop`、`team` | 加 raw acceptance、terminal-only、local-trust、same-info bandit、no-handoff control |
| 跨任务角色 | 数据集提供多个 task/repository 根 | 身份注册表、第三方 owner、跨 root 的未来职责选择 |

需要明确的风险是：CooperBench 原生 `coop` 将 agent 预分配到 feature，且 `test_merged` 在合并冲突时可以走 `solo-agent1` fallback；两个 agent 甚至可以各自独立完成 feature。因此，直接报告 `both_passed=true` 不能证明 recipient 使用了 producer 交付。每一条结果必须同时报告 `merge.status`、`merge.strategy`、双方 patch 的贡献、recipient 行为和独立重做成本。既有固定样本 `pallets_click_task/task2800` 的 feature 1/7 只能作工程 smoke：它们来自 `flash_10`，不能作未见确认数据。

## AgentWorld 为什么只排第二

AgentWorld 更接近“真实协作环境”：任务文件明确要求多 agent 通过聊天和资源转移完成链式目标。例如 `task_01_magic_staff.yaml` 让 lumberjack agent 采集 logs，woodworker agent 制 sticks，再由 wizard agent 组装 staff；`task_00_combined_workshop.yaml` 有十个 agent、三个并行生产链。`task_verifier.py` 会读取最终 inventory、HP、agent username 和 trajectory，并输出程序化 0/1 结果。`agents/experiment.py` 已包含可复用的 communication/no-role/solo/random 对照开关。

但它有四个会伤害主问题识别的缺口：

1. 任务中的 username、skill level、spawn location 和 success criteria 预先定义了角色；`no_roles` 只去掉提示语，不能消除能力和资源的不对称。
2. `new_character: true` 会在登录时创建或重置角色；跨任务持续身份需要我们自己实现 account lifecycle，不能把一次运行中的 username 当成已学角色。
3. 多数 verifier 只核对最终库存或存活状态，不能证明某个 recipient 采纳了某个 producer 的交付；少数按 username 检查的 verifier 仍然是预设责任，而不是学习后的责任。
4. 完整环境需要 Node/Yarn、AgentWorld server，可能还要 MongoDB；模型调用和轨迹成本比 CooperBench 开发样本更难先做小批量控制。

所以 AgentWorld 适合作为第二阶段的外部有效性检验，而不是先拿来锁定方法。若 CooperBench 证明不了“判断改变后续职责”，AgentWorld 也不能救回故事；它只能让一个已经成立的更新规则接受更丰富的状态环境测试。

## 不从头写：需要拼装的功能块

第一阶段只实现一个薄适配层，保留上游 runner/evaluator，不重写 benchmark：

1. **`IdentityRegistry`**：保存 `persistent_id → CooperBench agent profile / AgentWorld username / task-root history`。同一身份可以跨 episode 继续，但初始代码、仓库状态、资源和当前任务必须独立 reset。
2. **`ArtifactReceipt`**：把 patch、diff、测试命令、引用文件和 producer 观察写成一条不可变 receipt；记录 recipient 在 judgment 时看到的字节范围。
3. **`JudgmentGate`**：在 recipient 首次修改或执行集成前写入 `accept`、`reject`、`repair`、`independent_redo` 和拟使用 artifact IDs；判断事件不能读终局 evaluator 输出。
4. **`ConsumerExecutor`**：沿用 CooperBench sandbox 或 AgentWorld transfer/action API，执行 accepted handoff、repair、拒绝后独立重做；日志要记录实际采用的行/文件和返工次数。
5. **`RoleEvidenceLedger`**：每条证据挂在 `producer_id × responsibility_context × recipient_id × task_root` 上，单独保存 outcome、visibility、cost 和 provenance；不要把 owner 的私有信任直接冒充公共角色。
6. **`ThirdPartyAssigner`**：下一任务由没有直接评价该 producer 的 owner 选责任，使用同信息条件下的静态、raw acceptance、local trust、contextual bandit 和 proposed ledger 对照。
7. **`ObjectiveAdapter`**：CooperBench 调用 `test_merged` / `test_solo` 并保存 merge strategy；AgentWorld 调用 `verify_task` / `process_folder`，把原始 verifier 输出和最终任务成功分开。
8. **`CostLedger`**：每 episode 记录 LLM calls、input/output/cache tokens、wall time、tool actions、通信量、sandbox 时间和返工次数，避免把质量提升与无限增加调用混在一起。

这些都是围绕公开项目现有函数做 wrapper；方法创新应集中在 `JudgmentGate → RoleEvidenceLedger → ThirdPartyAssigner`，而不是重复实现环境、patch sandbox 或游戏服务器。

## Benchmark 与任务划分

### CooperBench 主线

- `pallets_click_task/task2800` feature 1/7：只用于零模型/低模型工程 smoke，不能用于确认结果。
- 开发集：按完整 `task root`（至少包含同一 base repository、commit 和 feature pool）分组抽取少量任务；同一 root 内的 feature pair 不得跨 train/dev/test。
- 确认集：按 repository 留出，至少让确认 repo 不出现在开发集；如果样本太少，报告 task-root split，并明确这是开发级而非完整泛化结论。
- 每个 episode 先运行 recipient-only control，再运行 handoff 组；recipient-only 必须有同样的任务、预算和工具，只缺 producer artifact。否则无法估计交付的边际贡献。
- 所有 CooperBench 原生 `solo-agent1` fallback 单列为失败的协作事件或单人上界，不能并入协作成功率。

### AgentWorld 次线

- 先选 3-agent `task_01_magic_staff` 做 runner/verifier smoke，再选 10-agent `task_00_combined_workshop` 做多轮压力测试；都不直接当确认集。
- 将原任务的技能和 inventory 设为可交换或按 episode 随机置换，保持总资源、总行动预算和世界状态相同；否则“角色学习”其实只是读取了预设 skill。
- 跨 episode 复用 persistent identity，但每个任务用独立世界 seed；记录角色身份、资源状态、观察权限和通信历史的边界。
- `task_verifier.py` 的程序化结果是终局质量标签；recipient 的 accept/use/repair 仍需我们的事件协议，不能用 verifier 输出替代 peer judgment。

## 需要报告的基线

主 benchmark 最小比较集：

- `solo`：单 agent 处理两个 feature，给出能力和成本上界；
- `fixed-coop`：CooperBench 原生预分配双 agent，保持其默认 communication；
- `recipient-redo`：recipient 不看 producer artifact，独立重做；
- `raw-acceptance`：只用历史接受比例，不校正 recipient 语境；
- `local-trust`：只有当前 owner 的私有信任；
- `same-info contextual bandit`：使用同样可见事件，检验我们的更新/选择是否只是普通在线学习；
- `proposed peer-judged role ledger`：完整 judgment→evidence→third-party assignment；
- `terminal-only`：只在终局 evaluator 后更新，检验行动前判断是否带来额外价值。

AgentWorld 只需加 `single_agent_upper_bound`、`no_communication`、`no_roles`、`random_agent` 四个开发对照，并保持任务资源和 identity roster 一致。不要把 LLM judge 的主观通信分数当主要质量指标。

## 工程停止条件

在花更多模型调用以前，先完成以下零模型门：

1. CooperBench 官方 Docker scorer 能在固定 smoke 样本上输出 apply、merge、两套测试和 fallback strategy；
2. `ArtifactReceipt`、`JudgmentGate` 和 `RoleEvidenceLedger` 的日志可以重放，并且评估标签不泄露给 actor；
3. recipient-only 与 handoff 两组能在相同 task root、预算、工具和可见性下运行；
4. 第三方 owner 的下一次职责选择确实可以改变，且选择没有直接读到其评价过候选人的私有记录；
5. 以上条件通过后，才用“内部”模型跑 2–4 个开发 task root，保存逐样本 JSONL 和失败。

如果 CooperBench 在这些门上无法完成 recipient 顺序交接，立即降级为“客观代码集成基底”，把 AppWorld 作为协议开发环境；不要把它包装成角色学习 benchmark。如果 AgentWorld 的身份重置、任务角色随机化或 server 依赖无法控制，它只保留作定性压力测试。

## 许可证与复用边界

- CooperBench：固定提交的 `pyproject.toml` 和 dataset frontmatter 声明 MIT，但仓库根目录没有独立 `LICENSE` 文件；正式分发前应保留声明并再次核查上游许可。
- MARBLE：MIT；保存的配置仅作为 workflow/agent graph 参考，不把其 LLM evaluator 当客观标签。
- AgentWorld：仓库提供 MPL-2.0；若分发修改后的源代码，需要保留许可、版权和相应源代码提供义务。它还继承 Kaetram 的许可/notice，不能把 AgentWorld 代码静默改成项目自己的许可证。

本次审计保存的官方文件均在本目录下；没有把 API key、模型响应或确认任务答案写入 source archive。
