# 观察桥与路由训练目标 — 2026-10-07

状态：`PARTIAL`。对应 ER-G1/ER-G2/ER-G4；`goal_change_requested=false`。

## 目的与衡量标准

落实用户确认的 ADR0049，使完整正负观察能引用真实 native 完成回执进入未来分派，
同时防止被旧接口误当 producer 奖惩。再明确合法后续训练目标，为真实小流解除语义
障碍。成功标准是三种合法 J/action 的绑定路径可达、错误主体/版本/时序拒绝、旧
归因和 credit 入口拒绝 observation-only 回执，以及 reward 数学目标和实现范围一致。
这些是工程/设计标准，不能替代三份科学验收。

## 已完成与尚未接通

- 新 [observation bridge](../../../scripts/peerrolebench_observation_bridge.py)复用 native
  ledger，用专用版本 `noisy-observation-completion-v1` 写入一条中性完成回执。
  observation 的辅助 ID 与 native evidence ID 分开；一组 J/action 仍只有一条回执。
  它不生成 reward，不调用 updater，不执行目标任务。
- 旧 role offer、ledger credit、peer-history 入口显式拒绝该版本命名空间。
  [25 项定向检查](../../../experiments/logs/n03_observation_legacy_isolation_20261007_v1/)
  通过，包括 native replay 合法但语义必须拒绝的反例。旧历史行为回归通过不说明
  旧 target-J 标签已经合法；该路线仍仅是诊断。
- [候选路由收益与评价对象卡](../../research/candidates/route_utility_and_scoped_judgment_v0.1_20261007.md)
  明确独立后续 Y 训练任务–producer–recipient 路由价值，Qp 只表示局部合同合规。
  正常 recipient 修改和 redo 留在结果分母及成本中，不能被记成 producer 缺陷。
  新 prompt 将 producer 合同评价与 recipient 集成计划分开封存；尚未运行新 prompt。

## 独立审查过程改变了什么

使用 Codex `gpt-6-sol` 分开实现与只读审查；下面是协调者对原始消息的整理，
不是投票或方法有效性证明。

| 原提议/疑点 | 审查证据与处理 |
|---|---|
| “真实后续 Y 可以更新选中的 producer” | 可更新该上下文中的路由价值，不能变成 producer 能力或因果责任。ACTIVE 方法 v1.3 已允许这个目标，无需再改 Goal |
| recipient 改了自己的文件就拒绝所有更新 | 会排空 PIPE3 的正常任务；责任门拒绝的是 producer attribution，不能机械套用到团队路由测量 |
| native receipt 能直接接旧 offer/credit | 旧消费者没有版本语义；已加显式拒绝，不依赖调用方自觉 |
| v1 的 B→B assignment 通过等于 selector 接通 | v1 由调用方填概率，并手动追加匹配选择；仅证明同主体 native lineage，不证明真实 preview 被执行 |
| receipt 自带 hash 足以锁定 observation | 自算 hash 不能阻止更改后重算；需要 operator 先封存的外部 receipt pin |
| dummy policy dict 没变化就证明发布不更新 | dict 未传进函数，不是证据；删除该断言，限于桥函数无 updater 接口的代码性质 |
| u=Y−λC 可以原样送现有 Feedback | 当前标签只接受 [0,1]，失败成本可使 u<0；候选独立有符号回归入口，不裁剪、不伪装 J |
| C 包含本次 updater 所有成本 | 标签先于更新，产生时间循环；训练用已封存执行成本，完整方法比较另计更新/存储/共享成本，明示两目标不必等价 |
| 条件期望最大就证明最优分派 | 还需封存历史后的随机化/可交换性、正概率支持、执行一致性与接收方策略稳定；当前没有这些实验证据 |

v1 16 项桥测试及原始源码保留在
[`n03_observation_bridge_20261007_v1`](../../../experiments/logs/n03_observation_bridge_20261007_v1/)。
v1 的上述不足不能被“测试通过”遮盖；复核不把它称 selector-qualified。

[v2](../../../experiments/logs/n03_observation_bridge_20261007_v2/)加入独立 receipt pin、
实际 `BaselinePolicy.choose()` 的 Selection 预览与独立预览 pin，绑定菜单/所选候选/
版本/概率；23 项通过。重算被篡改 receipt 的内部 hash、选择另一 peer、非零但不同的
propensity 均拒绝。三条合法路径到达的是 **target selection**，尚未执行 target。
它没有接真实 `Pipe3SelectionBoundary` commit、多 peer 观察聚合或收益更新。
日志里的 `full_native_chains=3` 仅指这一受限测试链，不能读成完整任务或学习闭环。

v2 测试默认不写持久日志，只有显式指定新目录才记录逐例事件；默认重跑后原 raw
摘要不变，避免后续 pytest 悄悄改历史。所有版本都有自己的源码快照。外部 pin 仍
须由可信 operator 在相应边界封存，它不抵御 operator 将记录和所有 pin 一起改写。

终审认为两处 v1 漏洞在上述 offline 范围内已补，没有发现新的直接实现错误。
候选 reward 的随机化前提与执行/完整成本边界也通过本轮逻辑复核；这不是效能评判。
[最终联合核验](../../../experiments/logs/n03_observation_bridge_integration_20261007_v1/)
的 48 项测试、语法、六类唯一生效登记、文档/科学 gate 一致性及改动空白检查通过。
机器 gate 仍为 `scientific_readiness=false`；未将任何科学 requirement 改成 VERIFIED。

## 饱和任务之外可复用什么

另一位只读 Codex 协作者检查了 pinned TeamBench 的两个生成器，没有执行 generator
或 grader。完整未修改材料与 MIT 许可证已保存到
[材料索引](../../../references/aamas/task_signal_materials_20261007/README.md)，共 118187
字节，原仓库 clean、commit `d185aef1916fd86a9ba554d581fd256319a973af`。

- **PIPE1 ETL**：可借用公开信息分割、字段/类型/缺省规则和逐记录终端核对。
  grader 真正运行 ETL 并读 output.json；但原生 producer 主要是预置源数据/Planner
  信息，还没有独立 peer 交付质量与未来分派资格。值得做下一轮独立材料审查，
  不能直接替换当前 benchmark，也不能仅凭机制不同计为第二合格 root。
- **PIPE3 message queue**：可借用 envelope、ack、dedup、DLQ 状态协议与真实消费测试。
  源码出现 `queue.py`/`queue_impl` 名称不一致，producer 专项检查还含静态字符串规则；
  目前不进入 live 卡。导入冲突是静态风险，尚未运行确认。

协作者一度把 PIPE2 已知 CSV 问题套到 PIPE1，随后自行纠正；这里明确保留这次纠正，
不将 PIPE2 缺陷作为 PIPE1 的拒绝依据。材料是待资格化的 operator 参考，hidden tests
及 expected 不能进入模型任务输入。该审查没有修改 benchmark 选型。

## 对主线和三份标准的实际贡献

| 标准 | 本轮推进 | 仍缺什么 |
|---|---|---|
| 故事线/创新点 | 区分 producer 责任与团队分派收益，避免“返工＝producer 错误” | 原创在线机制、最接近方法区分、未见任务收益仍无实证 |
| 方法论 | 打通中性完成身份，隔离旧 credit；写清可执行 label 时序 | 真实 selector commit、独立 Y/成本训练接口、经验状态、更新后真实任务 |
| benchmark/baseline | 保留正常集成/redo 与 UNKNOWN 分母，定位饱和任务风险 | 两个合格 root、自然信号支持度、全强对照、独立确认流 |

本轮新增 API/GPU 均为 0；不重复五次已知饱和的同 root/seed producer 测试，不把
协议输入当科学数据。正文结果表继续留空；本轮不覆盖并行绘图任务正在修改的正文。
最近已验证的八页正文仍是
[`observation_split_20261007_v2/main.pdf`](../../../artifacts/aamas2027/observation_split_20261007_v2/main.pdf)。

## 下一单元

先完成真实 policy preview 与 typed observation 的接线边界，再把候选新判断 schema、
独立终端评分、执行成本切点、实际 actor experience 接入一张有信息增益的小卡。
λ、成本单位、有限资源界限、未知结果处理、任务表与停止条件须先冻结。
选择器应先消费 source 观察，再执行后续任务、更新并真正执行更新后的任务。
若自然支持度仍为常数，先修任务测量或选材；不增大调用数制造“学习”曲线。
三份科学标准和投稿 gate 继续未通过；最终 backbone/updater 也未锁定。
