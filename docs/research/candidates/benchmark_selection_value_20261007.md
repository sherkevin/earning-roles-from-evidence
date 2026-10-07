# 什么样的任务值得研究 peer 选择

状态：`CANDIDATE / MATHEMATICAL_SCREEN`，2026-10-07。
用途：在花下一笔模型成本前，检查 benchmark 是否容许我们要证明的收益。
不替代唯一生效的 benchmark/method 文档，不改变 Goal，不构成新的算法贡献。

## 1. 第一原则：有判断差异，不等于有选择价值

一个判断即使能准确预测任务难度，只要所有情况下最好的协作者都相同，它仍不能
改善分派。我们需要的是 **事前可用的判断能帮助区分谁更适合下一项任务**，并且
收益足以支付取得和处理这些判断的成本。

当前 PIPE3 的局部格式差异可以被接收方规范化，终局 Y 因而相同。这不证明选择
不可能有效：修复时间、token 或 redo 成本仍可能不同。但 Qp 的差异本身不够，
而且无状态同模型 peer 的某一次不同输出不保证能预测其下一次输出。

## 2. 最小数学检查及具体实例

这里只看一个未来 assignment，冻结 recipient 执行策略。沿用方法合同的任务和
合法历史 `x`、候选 `a`、已完成源任务的评价 `J`、未来路由收益 `u(a)`。`u(a)` 是
如果把这次任务分给 a 时的质量减执行成本；实际只能观察选中路由。没有新增的
环境输入，下面的 `V` 与 `I` 都是这些量的函数。

| 量 | 本文的精确范围 | 实例（非实测） |
|---|---|---|
| x | 选择前任务、固定 recipient 策略与除本次待检 J 外的合法历史 | 下一个 ETL 字段映射任务，接收方 A，冻结版本与历史截止点 |
| a | J 到达前固定非空有限菜单中的 peer | B 或 C，两者都有正选择机会 |
| J | 源交付上的已到达评价，不能是目标的未来结果 | A 先前评 B 的规则说明是否完整；可含正负及不确定描述 |
| u(a) | 同执行规则下潜在的未来质量–成本收益 | 若选 B，最终检查成功且执行成本为0.2；未选 C 的本次收益不可观测 |

为避免把信息增加与行为干预混在一起，本节假定读取 J 仅改变 selector 的可见信息，
不改变菜单、producer/recipient 本次执行策略或潜在收益；这些改变要另做闭环实验。
所有 u(a) 可积，菜单有限；后续结论针对几乎每个有定义的 x，未计入获取 J 的
额外成本。这些是条件均值的性质，未假定模型能估计它们。

$$
V(x,J,a)=\mathbb E[u(a)\mid x,J].
$$

Case：x 固定为某个新任务，J 是一次此前已封存的“映射完整”评价；V(x,J,B)
表示在这种信息下选择 B 的期望路由效用。它不是 J 本身的分数，也不是 B 的因果功劳。

定义理想情况下增加 J 可以带来的单次分派价值：

$$
I(x)=\mathbb E_{J\mid x}\left[\max_a V(x,J,a)\right]
      -\max_a\mathbb E_{J\mid x}\left[V(x,J,a)\right]\ge 0.
$$

Case：不看 J 时只能按 x 选 B 或 C；看 J 后可以在不同分支选不同人。前项是在每个
J 分支选当时最优者再取平均，后项是先选一个人再对 J 平均。新增信息可以被忽略，
所以理想最优策略不会因此变差。这不说明实际 RLS/head/LLM selector 不会变差。

**何时这个值严格为零？** 存在一个只根据 x 选定的候选 a*，它在几乎所有 J 分支
都是最优者。允许并列，只要有一个共同最优候选即可；有限菜单下这也是必要条件。

证明：令 a* 最大化第二项中的条件平均，则：

$$
I(x)=\mathbb E_{J\mid x}\left[\max_a V(x,J,a)-V(x,J,a^*)\right].
$$

Case：括号中是“看到 J 再选”比“始终选 a*”多出的收益，每个分支都非负。平均为零
当且仅当它几乎处处为零；因此不需要增添模型结构就能检查这个必要的任务条件。

### 反例：预测变准，分派仍无收益

以下全为数学算例，不能填进论文结果表。J 的两个分支各占一半：

| 源评价 J | 选 B 的期望效用 | 选 C 的期望效用 | 最优选择 |
|---|---:|---:|---|
| 高 | 0.9 | 0.6 | B |
| 低 | 0.7 | 0.4 | B |
| 不读 J 的平均 | 0.8 | 0.5 | B |

J 对绝对收益有预测作用，但 I(x)=0。如果取得它还要额外支付0.02效用单位，净收益
变为−0.02。因此“J 与成功相关”或“预测误差更小”不足以证明角色学习改善团队。

### Y 饱和并不必然排除成本收益

另一个非实测算例：两条路线都成功；J 的两个分支分别令 B/C 的质量减执行成本为
(0.98,0.94) 和 (0.94,0.98)，各占一半。则 I(x)=0.98−0.96=0.02。若额外取得/处理 J
的代价大于0.02，完整方法仍不划算。只有提前固定资源权重，才能比较这种收益。

## 3. 它能决定什么，不能决定什么

1. **这是任务可检验性的筛查，不是 RARE 特有的理论优势。** 同信息 contextual
   baseline 也读取 J，理想信息价值同样属于它。RARE 是否更会利用 J 必须直接与
   该强对照比较，不能用 J-masked/no-J 的差值替代。
2. 当前 selected-only 日志只看到所选 a 的 u(a)。把观测到的 J 与 Y 做相关，或者
   在同一数据上拟合再取 max，不能识别 I(x)，后者还有选择最大值的乐观偏差。
   需要合法条件下的随机探索/可交换性、正 propensity、稳定执行策略、独立验证流
   以及完整 Y/成本或预注册缺失分析。记录 propensity 本身不保证这些条件成立。
3. 若 J 会改变 actor 自己的执行经验、接收方处理方式或菜单，单步比较必须保持
   相应状态一致；完整动态过程的收益另由独立 live histories 检验。不得把此单步
   非负结论推广为长期学习、实时性、稳定性或少遗忘保证。
4. 同模型同 prompt、无持久经验的 fresh peers 若对身份可交换，历史不能稳定预测
   某个 ID 的下次表现。固定两份好坏代码只验证“选交付物”。不能靠预设专家、给
   某个 peer 更好的规则、挑 seed 或故意削弱接收方来制造角色形成。

## 4. 当前材料的取舍

| 材料 | 已知 | 下一步可辨别的问题 |
|---|---|---|
| PIPE3 四格判断卡 | 修复后的公开合同与固定组件标签已核验；新判断尚未调用 | 能否分开评 producer 与 recipient，自身不识别 I(x) |
| 现有 C1 | 静态交付、四份最终代码相同、终局 Y 饱和；未完成完整成本和自然 peer 持续性 | 保留协议/测量诊断，不扩大同配置效果竞赛 |
| PIPE1 原生 Planner→Executor | 完整转换规则原本只给 Planner；Executor 接消息后修 ETL | peer 传达的规则是否影响实测未来质量/成本，经验是否带来可重复差异 |

PIPE1 可借用原生的 **peer 生成规则说明 → recipient 执行 → output.json** 路径，
不把 generator 预置的 source_sample 当成 peer 的交付。Planner 合法拥有完整规则，
不是把 hidden gold 泄给 actor；expected records 和评分器仍只属于 evaluator。
删掉 Planner 本来有权看的规范，反而会改变原生任务。

原生 grader 只抽查部分值、格式和非空，不能称完整正确性 oracle；Executor 也可能
从样本和旧代码推断不少规则。因此目前只收集原生材料与职责，不选定它、不修改
主矩阵或宣称其必然优于 PIPE3。任何补充 exact-value scorer 应单列为 derived
diagnostic，不能静默替换原生指标。四个业务域仍只算一个 structural root。

### 必须先比较的简单做法：原样转发规则

原生 Planner 已持有完整规范，`send_message` 未设置内容长度上限，Executor 会
读取完整消息。因此直接转发规范是一个合法、便宜、必须纳入的任务机制对照。
它尚未运行，也不是已发表的 peer-selector baseline；它检验的是“生成计划”相对
“传递已有规则”是否有额外价值，不能替代同信息 contextual selector。

| 任务机制对照（均未运行） | Executor 收到什么 | 可回答的问题 |
|---|---|---|
| 无消息 | 原生 brief 和工作文件 | 信息交付有没有必要；信息不同，不用于宣称算法公平优越性 |
| 原样转发 | Planner 原本合法持有的完整 spec | 直接传递规则是否已足够；记录消息 token 与执行成本 |
| 真实 peer 计划 | 同一 spec 上实际生成的消息 | 解释、压缩或组织是否帮助执行；计入生成与传递的完整成本 |

3782–4051 是本次四份 spec 的 UTF-8 **字节数**，不是 token 数。工具 stdout 的
4000 字符截断不适用于初始 spec 或消息；后端输出上限仍可能限制实际复制。
因此源码只支持“接口允许转发”，不证明模型一定完整转发或 Executor 一定成功。
不能仅为制造方法优势而人为禁止转发或压低对照的通信预算。

原生流程还有第三位 Verifier：它读取完整 spec，并可触发最多两轮返修。已捕获的
Planner/Executor 文件只是**两角色静态投影**，没有重现这个闭环。完整原生比较要
保留 Verifier 及其成本；若研究两角色切片，必须单独命名，不能称完整原生复现。

### 跨机器标签一致性必须先解决

已保存的 healthcare 和 financial 样本各10条。在显式 UTC 与 Asia/Shanghai 下
转换同一时间戳，**20/20 日期不同**；保存的 parent expected 均匹配后者。原生
generator 使用不带 tz 的 `datetime.fromtimestamp`，故日期标签依赖进程环境。
这次是对保存记录的静态计算，0 API/0 grader；不证明模型错误，也不能据此断言
此前 capture 进程的具体 TZ 配置。

若继续该候选，生成器、执行容器和评分容器必须冻结并记录相同 TZ，actor 也应
能知道任务所用的转换约定；不能用本地生成的日期去暗中惩罚另一时区的合法实现。
先记录环境约定，不修改历史 expected，不把 UTC/本地转换差异算成学习效果。
该问题、原生值覆盖不足、直接转发对照及自然 peer 持续性未解决前，不激活 PIPE1。
即使 relay、Verifier 和 TZ 的资格都通过，也只说明任务有可研究的信息交付路径。
还须验证 fresh 多候选在合法持久经验下存在可预测差异，以及后续 Y/完整成本能
辨别选择收益；仅给同模型无状态 Planner 换几个 ID 不满足这个条件。

## 来源和边界

- [现有真实流审查](../../coordination/task_reports/20261007_scientific_next_step_reconciliation.md)
- [终端诊断与后续合同解释更正](../../coordination/task_reports/20261007_independent_y_integration_audit_v2.md)
- [已封存四次判断卡](scoped_judgment_four_call_card_20261007.md)
- [原生材料及固定来源](../../../references/aamas/task_signal_materials_20261007/README.md)
- [四域原生视图捕获](../../../experiments/logs/n03_pipe1_native_material_audit_20261007_v1/summary.json)
- [逐记录时区核查](../../../experiments/logs/n03_pipe1_timezone_audit_20261007_v1/summary.json)
- [原生 harness 来源与哈希](../../../references/aamas/task_signal_materials_20261007/native_harness/manifest.json)：
  orchestrator 的 Planner/Verifier 路径、agent_interface 的消息写入及 agent_loop 的完整消息读取。
- [PIPE1 generator](../../../references/aamas/task_signal_materials_20261007/upstream/generators/gen_pipe1_etl_fix.py)
  的规则/视图见690–863行；[原生 grader](../../../references/aamas/task_signal_materials_20261007/upstream/tasks/PIPE1_etl_fix/grade.sh)
  的值覆盖见69–190行。

上述最大值与条件期望性质是普通数学筛查，不提出优先权/新定理主张。推导由独立
Codex 方法审查者核查，未以多数意见当有效性证据；所有数值均标明为算例。
