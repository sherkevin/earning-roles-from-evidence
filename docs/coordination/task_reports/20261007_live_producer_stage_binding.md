# 个人经历进入真实 producer 请求：入口实现与绑定审查

日期：2026-10-07。状态：`BOUNDED_SOFTWARE_CHECKS_PASSED / NO_LIVE_EXECUTION`。
不改变 Goal、六份生效标准或方案 B；没有新增模型调用或实验授权。

## 目的与验收范围

上轮发现个人经历没有生产调用者，C1 的 producer 又是固定文件。本轮实现独立的
producer stage，复用现有真实 API transport，使同一生成策略可以读取个人旧经历并
产生新交付。它不修改历史 runner，不包含完整 recipient、assignment 或收益更新。

本轮衡量的是请求和状态绑定：历史不得串 actor/arm 或来自未来；真实请求必须先有
外部预算授权；策略版本与单次产物分开；失败不得生成完成经验；完成记录必须绑定
同一请求的真实响应。软件检查通过也不能说明模型效果好或完整闭环已可运行。

## 实现与复用

- [新入口](../../../scripts/peerrolebench_live_producer_stage.py)复用 `ActorExperience`、
  `CandidateRegistryEntry`、native `Delivery`、PIPE3 v2 公开条款和原有 `call_api`。
- 给 actor 的历史只有此前自己的基础任务和答复；operator metadata 不进入 prompt，
  完整已拼接历史的 prompt 不再递归写回记忆。实际请求与审计快照另外保存。
- 生成策略/模型配置固定身份；每次历史与产物各自封存。任何 source/model/template
  更换均需新版本，正常经历增加不会将同一个 peer 重命名。
- 实际 API 入口默认关闭；本轮不创建 enabled 实验卡或有效预算授权。外层累计预算
  的发行与审批仍是独立前置，局部 `.claimed` 或自报累计数不构成全局预算控制。

## 失败与审查过程

[首次静态版本](../../../experiments/logs/n03_live_producer_static_review_20261007_v1/review.json)
有格式模板花括号、旧 v1 payload schema、memory 容量和命名空间未绑定等问题。
这些问题在执行测试或 API 前被发现；源码留存，先修复再做软件测试。

[首轮软件检查](../../../experiments/logs/n03_live_producer_stage_checks_20261007_v1/summary.json)
11项通过，但独立审查揭示其覆盖不充分：

1. 同一预算 reservation 复制到别处，会绕过路径旁的 claim 标记。
2. `finalize` 接受任意 parsed/metadata，未证明它们来自这一次请求。
3. 返回模型身份未与注册身份核对，可能错记到原模型的经历下。

这些属于实现缺口，不是模型实验失败。原 passing 回执与
[后续独立审查](../../../experiments/logs/n03_live_producer_stage_checks_20261007_v1/post_test_review.json)
共同保留，不能只引用11项通过来声称入口安全。

## 修复、验证和实际边界

修复后，reservation 只认项目内由 ID 决定的唯一绝对路径，调用前原子写入 claim。
完成时重新检查封存的卡、请求、原始响应、解析结果、成本和模型身份；SSE 使用
现有解析器重读，而非仅验证文件各自有 hash。已封存但互相矛盾的文件也必须拒绝。
同一个输出目录只能写入一次完成记录；失败不把本次答复添加到个人经历。

[v2 配置和源码快照](../../../experiments/logs/n03_live_producer_stage_checks_20261007_v2/config.json)
在执行前保存，定向三文件软件检查 **20项通过**。检查覆盖历史身份/时间、配置、
不同交付共享稳定策略、禁用入口、reservation 复制/重用、模型错配、解析结果与原始
响应不一致、文件篡改和重复完成；源码在检查前后未变化。独立 Codex 审查认为此前
三个入口级问题已修复；[审查回执](../../../experiments/logs/n03_live_producer_stage_checks_20261007_v2/review.json)
与测试一起保存。未扩大到全仓回归，因为本轮没有修改既有执行器或协议。

所有 wire-format 文件均为明确标注的手写软件 fixture，测试不调用或模拟成功的
API transport。这证明文件间的约束被检查，**不证明服务端真实生成过这些内容**。
真实执行仍需实际 `call_api` 请求日志及原始响应。新增模型调用、候选执行、GPU 均为0。

仍有三个外部前置，不由该模块解决：

1. 可信预算发行者需要跨实验卡核对总尝试数、失败和唯一编号。局部 claim 不能阻止
   发行者重新命名同一预算；自报 `prior_attempted_episodes` 不是审批记录。
2. 当前摘要固定 provider 加载代码，不固定运行时实际 provider 配置或后端 checkpoint。
   真实卡须事前封存非敏感的 endpoint/provider 身份和模型约定；不记录凭证。
3. 公开 payload 检查结构和条款引用，不能证明自由文本无隐藏答案或语义完整。
   输入资格、完整 ledger、recipient、独立后续收益及成本仍由上层实验卡保证。

本模块返回新的经历快照，由调用者串行持久化；它不是跨进程数据库事务，也没有
偷偷替换旧 C1 的固定产物路径。未生成可用的项目级 reservation 或启用实验卡。

## 与三份标准对照

本轮缩小的是方法可执行性的一个缺口。故事线的创新增量、两个合格 root、完整公平
基线、真实后续收益、实时性与遗忘结果均未获得新证据。固定状态软件 fixture 不是
真实 agent 学习；本轮未模拟成功 API 后声称跑过模型。

完整 source→judgment→assignment→fresh target→合法 reward→再次真实任务仍待接通。
追加四次判断预算仍未确认，也不覆盖本 producer stage。科学投稿 gate 保持关闭。

| 三份标准 | 本轮关闭的具体缺口 | 没有关闭的要求 |
|---|---|---|
| 故事线与创新 | 可以将“有经历的同一 peer”接入新生成请求，不再只能讨论静态产物 | J 是否改善未来选人、相对强基线的增量创新 |
| 方法论 | 有界历史投影、稳定策略与实际交付分离、请求/响应一致性的软件入口 | 完整 live 闭环、合法 reward、最终 backbone/训练、实时性与遗忘 |
| Benchmark + baseline | 保留已修公开条款、独立 arm/actor 状态的接入条件 | 有辨别力的任务、两 root 资格、公平 live 矩阵、实测收益与完整成本 |

下一步只围绕能改变科学判断的条件：把已存真实输出和 native 材料用于冻结 source–target
任务与测量卡，明确任务/规则重叠、收益对象和所有对照的共同权限。当前四次判断诊断
即使获批也只检验评价对象是否分开；它不能证明自然 peer 差异、角色学习或训练收益。
不继续泛化此入口为新框架，不把20项软件通过写入论文效果表。
