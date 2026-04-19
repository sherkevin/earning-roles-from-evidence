# 04: 思想通信与位置适应拓扑短文实验设计文档

## 基本信息

- 代码工作目录：`D:\Codes\idea04\`
- 代码侧同步文件：
  - `D:\Codes\idea04\idea.md`
  - `D:\Codes\idea04\experiment.md`
- 当前目标：先按 `EMNLP short paper` 的证据标准，验证 `peer-calibrated accept-or-forward delegation` 是否能在固定拓扑多智能体问答中稳定减少委派失准，并在相近成本下改善答案质量与协作稳定性

## 强制执行原则

### 0.1 Short-Paper-Only
当前阶段只允许服务于一个窄 claim：

> 在固定拓扑下，由同伴反馈更新的专长向量，是否比自我声明专长和静态角色更能减少 delegation miscalibration？

当前不允许把实验扩展成：

- 长文级的大而全多任务系统；
- 跨多种 backbone 的大规模横评；
- 真正的 latent thought 对齐训练；
- 多模型异构协作；
- 复杂图搜索或在线学拓扑；
- GUI agent、代码 agent、tool-use agent 的统一大框架。

### 0.2 Fork-Not-Build
本项目必须继续严格遵守：

> 不从零实现多智能体框架，不从零写 benchmark，不从零做评测系统；只允许在现成多 agent orchestration 框架和现成问答 benchmark 上增加轻量 delegation 逻辑、结构化通信和日志分析层。

允许的工作：

- clone / fork 现有多智能体 orchestration repo；
- 使用官方数据集或官方评测脚本；
- 增加固定拓扑约束；
- 增加 `accept-or-forward` 策略层；
- 增加 `peer-calibrated competence vector` 更新逻辑；
- 增加结构化 handoff packet；
- 增加日志、分析与汇总脚本。

不允许的工作：

- 自写新的多智能体运行时；
- 自建新的问答 benchmark；
- 训练新的 foundation model；
- 为了讲故事重做完整 long-context QA 管线；
- 先做复杂 thought latent channel 再回头想论文是否成立。

### 0.3 全量留档
所有实验必须默认“可以被复盘检查”，因此每一轮都必须保留：

- 原始输入样本；
- 每个 agent 的原始提示词；
- 每步路由决策；
- 每次 handoff 的结构化 packet；
- 每轮 competence vector 快照；
- 原始模型输出；
- 解析后的预测结果；
- 每个样本的评测结果；
- 汇总表格与失败案例。

任何没有原始过程文件支撑的结果，一律视为无效结果。

### 0.4 先打穿冒烟再扩样本
只有当最小冒烟实验已经证明：

- 框架可跑；
- 固定拓扑不死锁；
- 路由日志完整；
- `Ours` 至少在一个关键 proxy 指标上优于 cheap baseline；

才允许进入主实验。

## 0. 当前论文故事与实验落点

当前短文故事必须统一成：

- failure mode：`LLM 在多智能体协作中存在严重的委派幻觉（高估自己），且无法通过 Self-Reflection 进行自我纠正。`
- method object：`peer-calibrated competence vector + accept-or-forward policy`
- deployment value：`利用 LLM 挑剔同伴的鉴赏力进行 Peer-Calibration，打破冷启动盲区，从无序中收敛出类似 Static Roles 的帕累托最优状态。`
- paper scope：`固定拓扑多智能体问答 short paper`

当前不允许的写法：

- 论文已证明固定拓扑普遍优于所有动态编排；
- 论文已证明 latent thought communication 是新通用范式；
- 论文已证明多智能体能在所有语言任务上稳定自组织；
- 论文需要大规模训练 specialized adapters 才能成立。

## 1. Backbone 锁定

### 1.1 当前唯一主 orchestration backbone
当前唯一主框架为：

- `AutoGen`
- GitHub：`https://github.com/microsoft/autogen`

原因：

1. 已有成熟的多 agent 对话与消息传递抽象；
2. 容易加固定拓扑约束和受限邻接关系；
3. 易于插入结构化消息和日志；
4. 不需要重写运行时，最符合 short paper 的小改策略。

### 1.2 第一备选 orchestration backbone
若 `AutoGen` 的固定 speaker 约束或日志接口阻塞实现，则 fallback 到：

- `LangGraph`
- GitHub：`https://github.com/langchain-ai/langgraph`

启用条件：

- `AutoGen` 在 `0.5` 天内无法稳定实现固定拓扑与路由日志；
- 或其消息控制点过深，改动复杂度明显超过 short paper 范围。

启用 fallback 后同样必须遵守：

- 不重写 agent runtime；
- 只在 graph node 层和 message schema 层做小改；
- 保持实验主故事仍是 delegation calibration，而不是框架工程。

### 1.3 当前唯一主 benchmark
当前唯一主 benchmark 为：

- `HotpotQA`
- 优先使用官方 dev 集或 HuggingFace 上与官方评测兼容的版本；
- 优先复用官方 evaluation script。

原因：

1. 它天然需要多跳信息整合，容易暴露错误委派；
2. 社区熟悉，便于短文评审快速理解；
3. 可先在子集上快速冒烟，不需要大规模训练。

### 1.4 Next-Gen 动态验证集 (防守策略与扩写储备)
只有在 `HotpotQA` 主实验跑通其收敛特性后，为了应付审稿人“HotpotQA 过于静态线性”的质疑或筹备 Long Paper 升级，启动以下轻量 transfer：

- **MuSiQue**（真实下载：已包含高达 4800+ 复合多跳段落）

作用：相比平滑的 HotpotQA，MuSiQue 的多跳检索具有极强的前后位置不定性（Agent 无法依赖单行流处理）。此处转测的目标不仅是为了迁移测试，而是为了证明：在强不确定场景下，只有 `Peer-Calib` 的高跳脱能力能够避免死锁。这是彻底击溃 Static 分配优越性的后手王牌。

## 2. 当前唯一推荐的系统落地形态

### 2.1 固定拓扑先锁死
短文阶段只允许两种拓扑：

1. `chain`
2. `star`

不允许首发就比较树、双环、随机图、动态图重连。

原因：

- 先把 failure mode 讲清楚；
- 先证明固定结构下的 delegation 是否更稳；
- 避免拓扑搜索把实验面做散。

### 2.2 agent 角色先锁死
短文阶段默认 4 类节点：

1. `decomposer`
2. `evidence seeker`
3. `verifier`
4. `synthesizer`

可以允许多个节点共享同一基础角色模板，但不允许第一版就做十几个 agent 的复杂社会。

### 2.3 当前推荐的通信形态
短文阶段不做真正 latent thought 学习，统一用：

- `structured handoff packet`

最小 schema 必须包含：

- `task_id`
- `question`
- `current_subgoal`
- `evidence_so_far`
- `uncertainty`
- `reason_for_forward`
- `recommended_next_skill`

原因：

- 更容易把“高保真中间状态”落到可检查对象；
- 更适合 short paper；
- 避免方法滑向“我们训练了 thought space”这种长文叙事。

### 2.4 当前推荐的专长向量实现
首发只允许轻量 competence vector：

- 输入：任务特征、问题类型、历史接受结果、同伴修正信号；
- 更新：规则更新或极简统计更新；
- 存储：每个 agent 一个小维度向量或字典；
- 使用：只作用于 `accept-or-forward` 决策。

当前不允许首发：

- 训练复杂 router 网络；
- 训练 GNN 学全图路由；
- 联合训练强化学习委派策略。

## 3. 方法实现约束

### 3.1 `Ours` 的最小实现必须满足

1. 没有全局 orchestrator 决定最终分配；
2. 每个节点只能看本地消息和邻居信息；
3. 是否接单由本地 competence vector 与 packet 决定；
4. competence 更新必须来自同伴反馈与结果信号，而不是纯自报；
5. 所有路由决策必须落日志。

### 3.2 短文首发不要求的部分
以下内容全部延后到长文阶段，当前禁止成为阻塞项：

- 跨模型异构 specialization；
- adapter / LoRA 级位置专化；
- 真正 latent state 注入；
- 在线学习拓扑；
- 理论收敛分析；
- 大规模多任务统一表。

### 3.3 路由循环保护
固定图协作必须加：

- 最大 handoff 次数；
- 已访问节点记录；
- 死循环终止原因；
- 强制升级到 `synthesizer` 的保底策略。

没有这四项保护，不允许跑主实验。

## 4. Baseline 锁定

### 4.1 必跑 baseline

1. `Single-Agent`
2. `Central Orchestrator (带有 Self-Reflection 机制)`
3. `Fixed Topology + Static Roles (作为帕累托最优的参考组)`
4. `Fixed Topology + Self-Claim Competence`
5. `Fixed Topology + Self-Calibrated (基于自省自我更新置信度)`
6. `Fixed Topology + Peer-Calibrated Delegation (Ours)`

### 4.2 baseline 设计原则
这些 baseline 不是凑表，而是正面回答：

- 我们是否真的优于单 agent？
- 我们距离“静态角色分配”的帕累托最优状态（F1 上限）还有多近？能通过动态收敛学得类似结构吗？
- 对比 `Self-Claim` 和 `Self-Calibrated`：LLM 是不是真的不会认错（Self-Reflection 失效），只能被同伴（Peer）教做人？
- 我们是否能用去中心化网络持平或逼近带有 Reflection 的 Central Orchestrator？

如果 `Ours` 打不过 `Self-Calibrated`，或者完全无法逼近 `Static Roles` 的表现，就不应该继续扩实验。

## 5. 指标与验收口径

### 5.1 主结果指标

- `Answer EM`
- `Answer F1`

### 5.2 协作过程指标

- `mean handoff count`
- `dead-end rate`
- `premature accept rate`
- `forward-after-correction rate`
- `token cost per sample`
- `cost-normalized F1`

### 5.3 delegation 相关代理指标
由于“真实最优路由”难以直接观测，短文阶段统一使用以下 proxy：

- `first-accept success rate`
  - 第一个接单节点最终是否支持正确答案
- `avoidable handoff rate`
  - 是否出现明显多余转发（如 Ping-Pong 现象，必须被 TTL 或 Max Handoff 截断）
- `repair-needed rate`
  - 是否必须靠 verifier 或下游节点纠错
- `competence convergence dynamics` (新增)
  - 随样本轮次增加，盲目自信接单是否稳定下降，职责化收敛曲线是否清晰。

### 5.4 日志完整性验收标准
每轮实验只有同时满足以下条件才算有效：

1. 样本级日志覆盖率 `= 100%`
2. 每次 handoff 都有结构化 packet
3. 每个样本都能恢复完整路由链
4. 每个节点的 competence 更新前后都有快照

缺一项则该轮结果无效，必须重跑。

## 6. 强制输出目录结构

所有文件统一落到：

- `D:\Codes\idea04\artifacts\round0\`
- `D:\Codes\idea04\artifacts\round1\`
- `D:\Codes\idea04\artifacts\round2\`

每轮至少保留：

- `run_config.yaml`
- `sample_ids.json`
- `raw_inputs.jsonl`
- `prompt_templates/`
- `routing_traces.jsonl`
- `handoff_packets.jsonl`
- `competence_snapshots.jsonl`
- `raw_model_outputs.jsonl`
- `parsed_predictions.jsonl`
- `metrics.json`
- `main_table.csv`
- `failure_cases.md`
- `case_studies.md`
- `run_notes.md`

如果后续做 transfer，再额外增加：

- `transfer_table.csv`

### 6.1 不允许覆盖旧结果
同一轮不同运行必须按时间戳或 run id 新建目录，不允许覆盖旧结果。

### 6.2 必须缓存原始模型输出
不允许只保留最终解析答案；原始响应必须缓存，便于后续检查：

- packet 是否失真；
- verifier 如何纠错；
- competence 更新是否合理。

## 7. 最小执行计划

### Round 0: 两小时冒烟
目标：

- 用 `HotpotQA` 的 `50` 个样本子集；
- 跑通 `Static Roles`、`Self-Claim`、`Ours` 三个版本；
- 验证固定拓扑不死锁；
- 验证日志与 packet 留档完整；
- 初步看 `Ours` 是否降低 `dead-end rate` 或 `premature accept rate`。

执行步骤：

1. 选定 `chain` 拓扑；
2. 固定 4 类节点与 prompt；
3. 实现结构化 packet；
4. 实现 `self-claim` 和 `peer-calibrated` 两个决策版本；
5. 跑 `50` 个样本；
6. 生成最小分析表。

必须产出：

- `round0_main_table.csv`
- `round0_routing_examples.md`
- `round0_logging_check.md`

通过标准：

1. 三个版本都能稳定跑完；
2. 无死循环或死循环率低于可控阈值；
3. 日志完整性满足第 `5.4` 节；
4. `Ours` 至少在一个 delegation proxy 指标上优于 `Self-Claim`。

若不满足，先修系统，不进入 Round 1。

### Round 1: 短文主实验
目标：

- 在 `HotpotQA` 上跑 `300-500` 个样本；
- 比较 6 个 baseline；
- 给出主表、协作过程表、案例分析；
- 判断 short paper 是否成立。

执行步骤：

1. 先锁定一个基础模型与统一 API 配置；
2. 先跑 `Single-Agent` 和 `Central Orchestrator`；
3. 再跑固定图 4 个版本；
4. 汇总答案指标与 delegation proxy；
5. 抽取最典型的正确改善和失败案例。

必须产出：

- `round1_main_table.csv`
- `round1_process_metrics.csv`
- `round1_case_study.md`
- `round1_failure_taxonomy.md`
- **`round1_convergence_dynamics_chart.png/.csv` (重要：专长更新收敛曲线)**

Round 1 验收标准：

满足以下任意两条，即可认为 short paper 主结论成立，允许进入 Round 2：

1. `Ours` 成功从冷启动收敛，最终 F1 和 Cost 逼近 `Static Roles`
2. `Ours` 显著且稳定地优于 `Self-Calibrated` 和 `Self-Claim`，坐实“LLM 自反思幻觉”
3. `Ours` 在 `cost-normalized F1` 上不劣于 `Central Orchestrator (with Reflection)`
4. `Ours` 明显降低 `dead-end rate` 或 `premature accept rate`
5. 案例和收敛图表能清晰显示：强的人置信度上升，不懂装懂的被同伴打压。

如果一条都不满足，直接止损，不扩展。

### Round 2: 动态交叉领域与轻量 transfer
前提：

- 只有 Round 1 (HotpotQA) 通过才允许执行。

目标：

- 在更具不确定性的深层多跳 Benchmark（`MuSiQue`）上做 `200` 样本 transfer；
- 证明目标：“当传统的 Static Pipeline 流水线因为题目动态性过高而陷入逻辑死锁时，基于 Peer-Calibrated 的自学习小网络能大面积幸存”。

必须产出：

- `round2_transfer_table.csv`
- `round2_transfer_failures.md`

通过标准：

- `Ours` 至少保留相对 `Self-Claim` 的方向性优势；
- 日志与案例能够复现 Round 1 中的 delegation 改善模式。

## 8. 论文最小证据包

短文要成立，至少需要以下证据同时出现：

1. 固定拓扑设置下确实存在可观察的 delegation failure；
2. `Self-Claim` 相比 `Static Roles` 不能可靠解决该问题；
3. `Peer-Calibrated Delegation` 在答案质量或过程稳定性上提供非偶然收益；
4. 优势不是单纯靠多转发或更多 token 堆出来的；
5. 失败案例能说明本方法仍受什么限制，而不是只报喜不报忧。

## 9. 快失败条件

### 继续推进
满足任意两条即可继续：

- `Ours` 稳定优于 `Self-Claim`
- `Ours` 稳定优于 `Static Roles`
- `Ours` 在成本近似条件下接近 `Central Orchestrator`
- 案例中可清楚看到 delegate calibration 改善

### 立即止损
满足任意一条就停止：

- `Ours` 与 `Self-Claim` 长期无差别；
- 结果只能靠更高 token 成本换来；
- competence vector 更新看起来与实际路由质量无关；
- 日志无法稳定支撑“错误接单/错误转发”这个 failure mode；
- 为了得到结果被迫引入复杂训练或大规模框架改造。

## 10. 当前最重要的执行提醒

1. 先证明 `delegation calibration`，不要先证明“大规模自组织”。
2. 先把 `structured handoff packet` 跑通，不要先追求真正 latent thought。
3. 先在 `HotpotQA` 上打穿，别一开始铺多 benchmark。
4. 所有中间文件必须保留，后续审查优先看过程证据而不是总分。
5. 能 patch 现有 repo 就 patch，绝不在第一阶段自造新框架。
