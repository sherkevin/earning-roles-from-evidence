# 后续分派收益与评价对象：候选实现卡 v0.1

日期：2026-10-07。状态：`CANDIDATE / NOT_RUN`。依据：用户确认的
[ADR0049](../../user/decisions/0049-separate-judgment-observation-from-credit.md)。
本卡细化 ACTIVE 方法 v1.3 已允许的“未来分派质量/完整成本”目标；不修改 Goal、
六份生效文档，不把团队收益当成 producer 能力或边际贡献。没有新增 API/GPU 结果。

**合同前置补充：** [后续公开输入审查](../../coordination/task_reports/20261007_public_contract_and_budget_repair.md)
发现旧材料删掉了 Qp 要求的 T 格式。下文“不合规”的一般例子以 actor 看得到对应
义务为前提，不能直接套在旧 sanitized payload。先做版本化公开合同的判断对象
诊断；新增 API 尚未授权，不直接开始收益训练。

## 1. 先确定我们训练的对象

选择器要回答的是：**在这个任务、这位接收方及当前可见经验下，把工作交给谁，
最终能得到更好的团队结果，并少花资源？** 这与“谁违反了自己的交付合同”不同。

| 信号 | 能证明/训练什么 | 不能直接证明什么 |
|---|---|---|
| 封存的 producer 合同评价 | 接收方当时对交付的有噪声判断 | 客观 producer 正误 |
| Qp：独立检查原始交付 | 指定合同的局部合规性 | 下游不能使用、团队收益、通用能力 |
| recipient integration plan / action | 接收方计划与实际做了什么 | 这些工作由 producer 错误造成 |
| 独立后续 Y 与完整成本 | 实际执行的任务–producer–recipient 路由收益 | producer 对团队成败的因果责任 |

三种候选标签：直接用 J 最省事，但已混入接收方集成计划，拒绝作为主 reward；
Qp 更清楚，但把局部合规当团队目标，保留辅助 endpoint；**本卡选择独立后续 Y 与
完整成本作为 route utility**。这属于 B 的实现选择，不是新的创新结论。

## 2. 最小数学对象与逐式实例

沿用生效方法的任务上下文 x、候选 a、结果 Y 和成本，不增加一个全局“Agent 好坏分”。
x 必须包含执行前可见的任务/角色、接收方身份与版本、行动策略和经验快照版本。
候选 a 是 producer 的注册身份/版本。不能用尚未发生的动作或结果定义 x。

$$
u_j=\mathbf 1\{Y_j=\mathrm{PASS}\}-\lambda C_{\mathrm{exec},j}.
$$

Case：未来 assignment `as1` 将序列化任务交给 `peer-b@v1`，接收方为 `peer-a@v1`。
它修改自己的 `processor.py`，最终独立检查 PASS。若按预先固定单位测得更新前执行成本 0.2，
示意 λ=0.1，则 u=0.98。**0.2 和 0.1 仅为算例，不是实测值或冻结超参。**
无论 J 是 accept 还是 rework，这次路由都有结果；不因此写入 producer 正/负能力标签。

$$
V(x,a)=\mathbb E[u_j\mid x_j=x,a_j=a]
      =\Pr(Y_j=\mathrm{PASS}\mid x,a)-\lambda\mathbb E[C_{\mathrm{exec},j}\mid x,a].
$$

Case：同一公开任务条件下比较 B 与 C，接收方策略保持相同；收益模型预测的是各条
路由成功率减成本。B 的不合规时间戳可被接收方便宜地规范化，B 的 Qp 可 FAIL 而
路由收益高。两项并列报告，不能以终局 PASS 改写 Qp。
此等式由期望的线性性得到，不要求成功与成本独立，也不证明模型能准确估计 V。
V 首先是观测条件均值；解释成未来路由价值还需给定封存历史后的受控随机化/序贯
可交换性、候选正概率支持、执行一致性和接收方策略稳定。记录 propensity 本身不能
消除遗漏上下文；这些条件失败时不能据此声称选择产生因果收益。

$$
\mathbb E[(f(x,a)-u)^2\mid x,a]
 =(f(x,a)-V(x,a))^2+\operatorname{Var}(u\mid x,a).
$$

Case：用执行前封存的特征和所选路由的 u 更新一个小 head；在有限二阶矩条件下，
条件平方损失的最优预测是 V。这个常规性质只说明标签与预测目标一致，**不证明**
few-shot 泛化、实时性、稳定性或我们有创新。当前 RLS/RARE 的候选身份 one-hot
与 `recipient_judgment` 接口不满足完整路由语义，不能把 source 名字换掉就算接通。

若在合法菜单内有统一预测误差上界 ε，且严格选择预测值最大的候选，则：

$$
V(x,a^*)-V(x,\hat a)\le 2\varepsilon,
\quad a^*=\arg\max_a V(x,a),\quad \hat a=\arg\max_a f(x,a).
$$

Case：B/C 的收益预测都在真实条件均值 ±0.05 内，则该确定性选择的期望损失至多
0.10。证明是在两端各加减 f，中间项非正。**当前没有这个误差上界**；探索抽样也
不享有该确定性结论。实际实验须测预测误差、探索成本与未来效用，不能引用此式
替代数据。相同 scorer/接收方策略、可见状态充分性与环境变化仍是模型适用条件。

## 3. 责任约束仍在哪里

route utility 只进入明确标注为 `route_utility` 的上下文选择头，不写入
`producer_quality`、producer 缺陷标签或全局技能描述。完整的 recipient-only/mixed
任务可以有路由收益，但不能因此获得 producer attribution。Qp、J、实际改动和 Y
保留各自来源。正常集成与 independent redo 都保留在任务分母，并计入全部执行成本。

| 后续实际情况 | 路由更新 | producer 结论 |
|---|---|---|
| Qp PASS；只改 recipient；Y FAIL；成本完整 | 合法低 route utility | 不能说 producer 失败 |
| Qp FAIL；recipient 修复；Y PASS；成本完整 | 合法质量–成本值 | 原始交付仍不合规；修复不变成 producer 功劳 |
| 拒绝并 redo；Y PASS；成本完整 | 计 redo 成本，保留路由结果 | 不能说原始交付被采用 |
| Y 或必要成本缺失 | 不更新；UNKNOWN 与已发生成本留在分母 | 不补负例、不删记录 |
| source 观察刚发布，目标尚未执行 | 不更新 | 源观察不能成为后续收益 |

如果所有 producer 都被接收方完全重做、Y 和成本无差异，那么 route value 本来就
无法区分 producer。应停止扩大这类任务的模型调用，找有真实依赖和自然差异的任务；
不能事后剔除 redo 或挑 seed 制造选择收益。这不是 Goal 降级。

## 4. 成本与缺失不能留给实现者随意补值

训练标签中的 C_exec 是 **本次更新开始前**已经实测并封存的成本：producer 生成、
recipient 判断/集成/redo、工具、终端验证及当时已发生的通信/失败成本。不能把本次
更新的耗时放进该标签，否则“先知道标签才能更新，先更新才能知道标签”形成时间循环。

本次 update、后续持久化/存储和共享源开销照常实测，按固定归属在 policy/stream 总账
计入完整成本。完整收益比较为：

$$
U_{\mathrm{full}}=\frac{1}{N}\sum_{j=1}^{N}\mathbf 1\{Y_j=\mathrm{PASS}\}
                    -\frac{\lambda}{N}C_{\mathrm{total}}.
$$

Case：计划两次任务都完成；目标执行费用共 0.4，在线更新及持久化 0.1，共享源费用
0.2，则完整成本 C_total=0.7，两次都成功时 U_full=1−λ·0.7/2。数值仅解释计账；
N 是预先计划的任务分母，不是事后成功数。存在 UNKNOWN 时不能把它代成零或从 N
中删掉，上式点值不确定，使用下述缺失分析。尚未尝试的计划任务也不冒充实测失败。

因此 u 是可因果执行的**训练代理目标**，U_full 才是方法选择与论文主比较的完整目标。
二者一般不等价；若更新开销随候选/结果变化，最大化 u 不保证最大化 U_full。须测量
该差距，不能只报训练收益或低估昂贵 updater。原生 `repair_cost` 只是局部费用。
不同资源的金额/时间权重、预算归一化、成本切点与 λ 在新 live 卡之前固定；不按结果调权重。

同一共享源调用在 policy/stream 总成本中只计一次；若摊入每个 assignment，摊销规则
和计划步数须事前固定，不能按成功样本数分摊。主结果同时给未合成的质量与成本分量、
Pareto 图及全部开发成本，防止一个任意权重遮住结果。

不因 UNKNOWN 更新不合法就把 UNKNOWN 从效果比较中删去。按 arm/candidate 报告
attempted、完整、缺 Y、缺成本、transport/parse/scorer 失败数。选中概率须大于零并
封存；propensity 不是缺失机制的修复。完整样本训练仍可能有选择偏差。
确认卡须预定 outcome/cost 有界时的最坏–最好敏感性范围；无可信有限成本上界时
不声称有限范围。上述条件未冻结前，不启动带该标签的新训练。

**现有训练接口的实际不兼容：** `Feedback` 和 RARE 只接受 `[0,1]` label，而失败且
耗费资源的 u 可以小于零。候选实现使用独立版本的 `route_utility` 有符号回归入口，
不把 u 冒充 `recipient_judgment` 或截断到零；同信息 comparator 必须接受相同的目标。
该入口尚未实现，因此当前代码不能训练本卡的 u。

2026-10-08 实现增量：[有符号完整岭回归数值核心](signed_ridge_comparator_v0.1_20261008.md)
已完成独立数值检查，能计算负u；但没有接入合法reward、selected-only绑定或真实runner。
它不改变上述“训练入口尚未实现”的状态，也不锁定最终算法或成本权重。

同日补齐[任务条件对照](task_conditioned_ridge_v0.1_20261008.md)：按候选版本保存独立岭回归统计量，输入封存的同一任务向量。它修正身份one-hot不能表达任务交叉偏好的表示缺口；仍无真实合法收益接入，未开放训练入口或冻结最终encoder。

若将来能事前保证所有 C_exec 都有相同真实硬上界 Cmax，也可采用：

$$
\tilde u_j=\frac{u_j+\lambda C_{\max}}{1+\lambda C_{\max}}\in[0,1].
$$

Case：仅在 Cmax=1 被实际强制且 λ=0.1 时，耗尽预算的失败 u=−0.1 映射为 0；
零成本成功 u=1 映射为 1。这是固定正仿射变换，保留路由期望收益排序；不允许按
batch/arm 的观测最大值归一化。现阶段完整资源硬上界未证明，不采用这一捷径。
溢出必须留痕并使冻结合同失效，不能静默裁剪或丢弃高成本样本。

## 5. 下一请求怎样拆开，避免再次问错问题

对一次真实交付，用同一 recipient 在行动前生成一个封存 JSON，分开两个对象：

```json
{
  "producer_contract_assessment": {
    "verdict": "meets_contract | violates_contract | uncertain",
    "observed_artifact_sha256": "digest of the delivered producer files",
    "contract_clause_refs": ["public producer obligation"],
    "rationale": "assessment restricted to producer-owned delivery"
  },
  "recipient_integration_plan": {
    "decision": "accept | accept_with_rework | reject_redo",
    "target_paths": ["processor.py"],
    "rationale": "work needed to finish recipient-owned integration"
  }
}
```

上述值为 schema 示意，不是模型输出。只提供公开合同、明确的路径所有权和交付，
不提供 hidden test、Qp 或后来 Y。旧 native `decision` 仍保留为实际动作计划及其合法
配对；新增的 contract assessment 作为另一个 noisy 字段，不能重新解释历史 J。
需要接通这一 schema 的新 runner/card 后再观察自然支持度，不把提示词更清楚当作
模型判断更准的证据。

## 6. 可执行前置与最小停止规则

1. observation→native completion→assignment 合法桥和旧 credit 隔离先通过；
   此步骤不产生 reward，不需要再测 API 连通性。
2. 复用独立 Y worker、原始交付 Qp 与已有完整成本组件；补 producer API 成本。
   预注册 cost/λ、路由特征与状态隔离、三类判断字段及 selected-only 标签通道。
3. 用既有原生任务检查真实依赖和可区分输出，复用已存在的“合规/可用”控制。
   不重跑已知饱和的五次同 root/seed 任务来追求正面结果。
4. 冻结最小真实卡：先检验交付合同判断与自身集成计划是否分开、自然 J/Qp/Y 支持度
   是否存在，再执行 observation→assignment→真实后续任务→合法更新→再次真实任务。
   只改变概率而不执行最后一步不算闭环收益。

当前没有冻结成本换算/切点、λ、任务表或新 prompt 的 live 行为，因此本卡还不能启动
实训。最后这一步仍须强同信息 contextual、count/J-masked、no-update、terminal-only
等对照与独立流，两个 root、跨任务泛化、完整训练矩阵和 A800 门没有取消。
