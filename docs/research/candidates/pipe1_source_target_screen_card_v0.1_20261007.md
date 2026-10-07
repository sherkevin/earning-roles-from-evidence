# PIPE1 source–target 先行筛查卡 v0.1

日期：2026-10-07。状态：`CANDIDATE / NOT_ACTIVE / NO_API_AUTHORIZED`。
本卡只把已有原生材料整理成一个可审查的先行筛查，不冻结 benchmark，不改变六份
生效文档，也不把不同域的四个 seed 宣称成独立 structural roots。

## 目的

检查“同一个有经历的 Planner 是否能在新的规则任务上产出更有用的交接”是否有
可测条件。这个问题必须同时保留 Planner 的合法完整规范、Executor 的真实工作和
Verifier 的原生介入；只比较静态消息或最终通过率不能回答它。

## 证据先决条件

当前 C1 保存的三条可读 judging 请求中，`no_update` 与 `RARE` 的 source/target
public payload 都是 seed 0、完整任务合同相同，producer 文件也相同；
`contextual_trust_linear` 只有 source 请求，因为它在源证据后没有启动 target。
材料审计见 [`n03_task_distinctness_audit_20261007_v2`](../../../experiments/logs/n03_task_distinctness_audit_20261007_v2/summary.json)。
历史 runner 还显式把 `generated_target = generated_source`，不能用 target scorer 收到
的 seed 字段替代真实 target material。上述历史结果不重写，只标成不可用于未见任务泛化的证据。

PIPE1 原生生成器的 seed 0 是 ecommerce、seed 3 是 logistics；两组 `field_map`、
类型转换、嵌套字段、枚举和空值规则的整组摘要不同，且没有共享的整组规则。两域仍
只是同一 structural root 的不同业务参数；它们可以做先行筛查，不能单独证明跨 root
泛化。生成器的 Planner 规范和 Executor 视图均来自固定 TeamBench commit，不能用
手写“专家总结”代替。

## 预注册路由

1. 两个候选 Planner 从同一空历史、同一模型/template、同一 source material 和相同
   API/时区配置开始；随机化只决定哪个候选接到后续任务。不能预置 B 为专家，不能
   按源结果挑候选。
2. source 使用原生 seed 0。Planner 读取完整 spec，真实生成一条给 Executor 的
   消息；封存消息、交付 digest、Executor 输出、Verifier 介入前后结果和逐阶段成本。
3. target 预注册为 seed 3 logistics，使用独立生成的完整 target material。被选
   Planner 只能读取自己的 source 输入/答复历史和 target 合法完整 spec；不得读取
   expected、hidden tests、Verifier、其他 Planner 或 selector 状态。
4. 使用相同 Executor/Verifier 策略、相同 action/retry 上限和同一时区。Verifier 看到
   完整 spec 是原生权限；报告 Executor 在它介入前的结果以及最终结果，避免 Verifier
   把 Planner 消息的差异完全抹平。

## 必须的对照

| route | 消息来源 | 解释 |
|---|---|---|
| `no_message` | Executor 只有 brief/workspace | 依赖诊断，不是 selector baseline |
| `generated_planner` | Planner 实际生成消息 | 候选 peer route；历史可进入 Planner 请求 |
| `full_spec_relay` | operator 将同一完整 spec 原样作为 Planner 消息 | 合法的消息生成绕过/任务必要性对照，计通信和执行成本 |

`full_spec_relay` 仍使用原生 Planner→Executor 消息接口，不增加 Executor 文件权限。
它绕过的是 Planner 的语言生成策略，属于不同 policy family；不能冒充与候选同信息的
selector baseline。若它明显更好，只能说明此配置下付费选择 Planner 的应用价值可疑。

## 结果和停止规则

每条 route 必须同时报告 Executor 介入前的输出、Verifier 后的 output/attestation、
最终 exact correctness、是否返工/重做、通信/模型/工具/Verifier/返工完整成本和
UNKNOWN 原因。只要 target material、时区、源/目标 overlap、消息 lineage 或成本不
完整，整条 route 为 UNKNOWN，不补标签。

若同初态 Planner 产生相同消息/历史，这是真实的“无可重复身份差异”结果，不能挑 seed
或改 prompt 制造专家；小样本只记 `INCONCLUSIVE`。若 `full_spec_relay` 与生成消息
质量—完整成本相同或更好，本卡停止，不把该配置写成 peer 选择有效。只有在 source
历史差异自然出现、target 结果和成本完整且候选路由相对合法对照有预注册增量时，才
值得另行设计 selected-only judgment→assignment→later outcome 闭环。

## 当前结论

本卡可复用现有原生材料和 actor-history 入口，但 **尚不可执行**：此前累计 episode
已超过原开发预算，外部预算发行者、运行时 provider pin、source/target 任务执行和
完整 ledger 尚未提供。待批准的四次 judgment-only 诊断也不包含本卡的 producer/Executor/
Verifier 路由，不能借用。没有这张卡的真实结果，不能宣称 PIPE1 已成为 benchmark，
也不能据此选择 backbone 或启动 A800。
