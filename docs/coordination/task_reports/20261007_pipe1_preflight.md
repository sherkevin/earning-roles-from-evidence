# PIPE1 source–target 路由执行前资格审查 — 2026-10-07

状态：`BLOCKED_PRE_EXECUTION`。本轮只读取已封存的原生材料和候选卡，未调用
模型、生成器、候选代码或 GPU；Goal、六份生效标准和方案 B 不改变。

## 目的和通过指标

这一步回答一个很具体的问题：PIPE1 候选卡是否已经具备进入昂贵的 source→target
真实路由实验的最低执行条件。审查对象是已保存的 Planner/Executor 投影、公共工作区、
原生消息/Verifier harness、候选卡中的 source/target 声明和运行前必要的审计字段。
审查不把静态材料完整性误报成科学效果。只有所有阻塞项关闭、ledger 能绑定真实消息到
Executor 介入前后结果、且成本/时区/provider 身份完整时，才允许进入 route call。

配置先于检查写入（v2 保留为可读性修订前的历史回执；v3 是独立审查后拆分 live
阻塞项的当前回执）：
[`n03_pipe1_preflight_20261007_v3`](../../../experiments/logs/n03_pipe1_preflight_20261007_v3/summary.json)。
脚本为 [`peerrolebench_pipe1_preflight.py`](../../../scripts/peerrolebench_pipe1_preflight.py)。

## 审查结果

修订后的回执共 22 项：11 项 `PASS`、10 项 `BLOCKED`、1 项 `OPEN`、0 项 `FAIL`。
API、generator、candidate、GPU 调用均为 0；`scientific_claim_allowed=false`，历史
结果未修改。

已通过的项目包括：

- seed 0 和 seed 3 的 Planner/Executor 投影只暴露各自的原生任务材料，expected 只在
  parent projection 中保存；
- 两个公共工作区可解析，且 source/target 的规则材料确实不同；
- 候选卡明确它们属于同一个 structural root，不能将这次筛查写成跨 root 泛化；
- 原生 Planner→Executor 消息接口以及包含 Verifier/remediation 的 harness 已保存。

静态材料层面的检查通过，并不代表 live route 已经放行。独立 Codex 只读审查进一步
确认 source→message→artifact→Executor→Verifier 的真实链尚不存在，因而把以下 live
边界单列为阻塞项。完整修订回执见
[`n03_pipe1_preflight_20261007_v3`](../../../experiments/logs/n03_pipe1_preflight_20261007_v3/summary.json)。

仍然阻塞执行的项目如下：

| 项目 | 目前不能声称什么 | 必须补齐的证据 |
| --- | --- | --- |
| exact outcome scorer | 现有 native grader 不是完整 target 终局 oracle | 固定 Executor 介入前输出、Verifier 前后结果、exact correctness、返工和 UNKNOWN 规则 |
| source-target artifact lineage | 只有静态 source/target view，没有真实交付、消息、artifact、Executor、Verifier 的 hash chain | 由同一 runner 封存每一段 digest、版本和父子关系 |
| actor visibility at runtime | 静态 projection 显示意图，但没有 live receipt 证明 target history/selector 隔离 | 记录 target prompt、history watermark、expected/hidden 拒绝和 selected-only 读取边界 |
| Verifier live attestation | 只保存了原生 Verifier 源码，没有介入前后 attestation 或 remediation 记录 | 运行时封存介入前输出、介入后结果、测试证据和返修次数 |
| timezone contract | 历史材料没有证明生成时区；UTC 与 Asia/Shanghai 的日期会不同 | 在生成、执行、评分三端固定并记录同一时区，旧材料不回填 |
| provider identity pin | 候选卡没有可执行的非秘密 provider/model 路由指纹 | 运行前固定 provider、model、endpoint/config digest，不记录凭据 |
| global budget issuer | 原开发预算已从 24 次累计到 31 episodes/68 requests | 为 PIPE1 单独发行并记录新的有界预算；不能以换卡清零 |
| source-target ledger runner | 尚无一条 runner 绑定 Planner history、message lineage、Executor 前后输出、Verifier 和全成本 | 先实现并零调用验证完整 ledger，再讨论真实调用 |
| direct relay baseline | 卡中只写了三条 route，没有可执行 relay receipt 或结果 | 封存 no-message、generated-planner、full-spec-relay 的同 seed/同成本账 |
| identity randomization | 没有 candidate version、分配 seed、置换表或 assignment receipt | 预注册候选身份、随机化算法和 target assignment，再开始 route |

另有一个开放项：同初始条件的两个 Planner 是否会自然产生可重复的历史/消息差异。
若它们没有差异，结果必须记为 `INCONCLUSIVE`，不能挑 seed、改 prompt 或预置专家身份
制造差异。

## 对三份验收标准的影响

这轮只关闭了“候选材料是否可审查”的一个前置问题，没有达到任何科学标准：

- 故事线与创新点：仍没有证据证明他人评价改善了后续选人或未来任务质量；
- 方法论：方案 B 的观察与责任/收益分离保持有效，但真实 source→target 更新闭环尚未运行；
- Benchmark + baseline：PIPE1 仍是 `CANDIDATE / NOT_ACTIVE`，尚未成为 benchmark，且
  `no_message`、`generated_planner`、`full_spec_relay` 尚未做公平 live 比较。

因此本轮不能打开科学投稿 gate，也不能据此选择 backbone、训练方法或启动 A800。

## 下一步

只做能关闭上述阻塞的工作：补齐 exact target scorer、时区/provider/budget contract，
实现 source-target ledger 的零调用资格审查，并由独立审查确认。追加的四次 judgment-only
预算不覆盖 PIPE1，不能借用；在新的 PIPE1 预算发行和用户明确授权前不发起模型调用。
