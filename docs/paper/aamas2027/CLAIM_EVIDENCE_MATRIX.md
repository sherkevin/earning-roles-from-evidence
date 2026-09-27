# 论文主张—证据矩阵（2026-09-27）

| 论文主张 | 需要的证据 | 当前状态 | 允许的表述 |
|---|---|---|---|
| recipient 的判断是有信息的 | 独立 producer contract、实际 use/rework、最终质量，和 raw/terminal 对照 | 未完成；N02 暴露 scorer 漏洞 | “这是待检验的机制假设” |
| 判断进入了未来职责 | 选择前封存概率；未直接评价的 owner 使用公共证据；后续真实执行 | N02 只证明 assignment 接线，概率未变且 peer 同构 | “协议支持该因果路径，尚无收益证据” |
| RARE 优于同信息 trust/bandit | 相同事件、propensity、预算、独立 streams 的配对比较 | 未开始 | 不得写 superiority |
| RARE 实时更新 | 每条反馈 update p50/p95、乱序语义、版本绑定和服务延迟 | 未开始 | 只能写设计约束 |
| RARE 少遗忘 | old holdout、漂移后恢复、峰值/平均遗忘 | 未开始 | 不得写保留能力 |
| PeerRoleBench-TB 是 benchmark | 两个以上结构 root、真实 payload/scorer/ledger 隔离、评分和任务划分资格通过 | PIPE3 v2 只有静态契约夹具、placeholder ledger fixture 和 listed canary；任务文本泄露 Bug 1/2/3；真实 scorer/root split 仍未完成 | “TeamBench-derived candidate with a static preflight fixture; not yet a scientific benchmark” |
| peer 具备可学习个体差异 | common init、合法个人经验、matched unseen tasks、identity-renaming control | 当前 peers exchangeable | “当前实验尚未建立该条件” |
| 真实 API 链路可行 | raw SSE/API、完整 trace、失败与 UNKNOWN 记录 | v3 两条限定链通过 | 可写协议/传输可行性 |

## 结果表的空白规则

在上述“未完成”项目获得独立、可审计结果前，LaTeX 稿件不得填入数值、胜负、
显著性或“提升”字样。N02 的 4/4 consumer checks 和 0.5 概率是诊断事实，不能
放在方法效果表中。
