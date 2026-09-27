# 论文主张—证据矩阵（2026-09-27）

目标标准来自 [`docs/coordination/GOAL.md`](../../coordination/GOAL.md) v1.0；本矩阵只能
报告证据状态，不能自动修改 Goal。

| 论文主张 | 需要的证据 | 当前状态 | 允许的表述 |
|---|---|---|---|
| recipient 的判断是有信息的 | 独立 producer contract、实际 use/rework、最终质量，和 raw/terminal 对照 | 未完成；N02 暴露 scorer 漏洞 | “这是待检验的机制假设” |
| 判断进入了未来职责 | 选择前封存概率；未直接评价的 owner 使用公共证据；后续真实执行 | N02 只证明 assignment 接线，概率未变且 peer 同构 | “协议支持该因果路径，尚无收益证据” |
| RARE 优于同信息 trust/bandit | 相同事件、propensity、预算、独立 streams 的配对比较 | 未开始 | 不得写 superiority |
| RARE 实时更新 | 每条反馈 update p50/p95、乱序语义、版本绑定和服务延迟 | 未开始 | 只能写设计约束 |
| RARE 少遗忘 | old holdout、漂移后恢复、峰值/平均遗忘 | 未开始 | 不得写保留能力 |
| PeerRoleBench-TB 是 benchmark | 两个以上结构 root、真实 payload/scorer/ledger 隔离、评分和任务划分资格通过 | PIPE3 v2 只有静态契约夹具、placeholder ledger fixture 和 listed canary；任务文本泄露 Bug 1/2/3；真实 scorer/root split 仍未完成 | “TeamBench-derived candidate with a static preflight fixture; not yet a scientific benchmark” |
| ledger 能安全进入学习更新 | parent-side hash/replay、唯一性、因果顺序、完整性、异常与 UNKNOWN 语义 | N02 v3 真实 15 事件 ledger 回放通过；8 个变异案例按预期拒绝/UNKNOWN；真实 runner 的 scorer/operator IPC 和 retry 语义仍未完成 | “protocol replay gate is qualified on a preserved trace; no learning efficacy claim” |
| scorer 异常不会伪造标签 | 中断、retry、timeout、permission、invalid response、coverage 缺失的预注册 disposition | 零 LLM boundary qualification 全部符合 UNKNOWN/INVALID 规则；独立 hidden scorer IPC 尚未接入 | “failure disposition is qualified as an engineering guard; no scorer/learning result” |
| scorer truth 与 candidate 隔离 | private expected、公开请求 schema、独立 worker、candidate read denial、response digest | v2 scorer IPC preflight 通过；v1 digest 混淆失败已保留；仍是 fixture truth | “IPC boundary is qualified on a fixture; no real scorer or benchmark result” |
| producer 交付质量可作为独立标签 | producer-owned artifact、独立 P1–P7 scorer、buggy/correct/near-miss controls、UNKNOWN mutation | v2 zero-LLM matrix 在 corrected control 上得到 PASS/1.0、buggy/near-miss 得到 FAIL、malformed/mutations 得到 UNKNOWN；但仍是 TeamBench-shaped、非对抗 Python worker，未完成独立 root/live attribution 资格 | “an unqualified diagnostic implementation exists; no role-learning label/result” |
| producer score 可安全进入因果链 | delivery-bound digest、judgment 前 producer-score event、replay constructor、UNKNOWN gate | `ProducerScore`、replay 与 runner 可选边界通过 112 项回归；尚未有真实 scorer episode 或 controller update | “producer-score event path is implemented; no live role update” |
| recipient outcome 不污染 producer attribution | immutable delivery digest、recipient-owned paths、独立 `Q_p`/`Q_r` | ADR0033 更正了首次 consumer scorer 的 tuple/list 实现错误；producer/recipient schema 仍独立，但没有由该回放支持的评分盲点证据 | “producer and recipient outcomes are measured separately in the contract” |
| peer 具备可学习个体差异 | common init、合法个人经验、matched unseen tasks、identity-renaming control | 当前 peers exchangeable | “当前实验尚未建立该条件” |
| 真实 API 链路可行 | raw SSE/API、完整 trace、失败与 UNKNOWN 记录 | v3 两条限定链通过；neutral DIST1 v1 三次请求因契约不一致为 UNKNOWN；neutral-v2 三次请求完整返回，但 producer priority 导致 scorer coverage UNKNOWN，未产生 outcome/update | 可写真实 API/传输和失败记录；不得写方法效果 |

## 结果表的空白规则

在上述“未完成”项目获得独立、可审计结果前，LaTeX 稿件不得填入数值、胜负、
显著性或“提升”字样。N02 的 4/4 consumer checks 和 0.5 概率是诊断事实，不能
放在方法效果表中。
