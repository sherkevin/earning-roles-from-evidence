# 0022：锁定论文主线、单一候选机制与证据门

日期：2026-09-27。
状态：Accepted as the internal paper contract; empirical method remains unvalidated.

## 背景

旧 `main.tex` 是 allocation/router 历史内部稿，不能代表当前选择的
“learning roles from others' situated judgments”。N02 的两条真实链证明了部分
协议可运行，但也证明了 consumer 分数漏掉 producer 错误、正常 integration 被误报
repair、feedback 没有改变选择、peer 没有持续个人状态。继续扩展调用或先做 A800
训练会把错误标签和 exchangeable peer 当成学习信号。

## 决定

论文只保留一个中心问题：recipient 的 situated judgment 是否能形成可归因的
producer role evidence，改变未来责任，并改善完整质量—成本目标。

把 `Responsibility-Aware Role Evidence (RARE)` 作为可执行候选机制：分离
recipient judgment、recipient action、producer contract check 和最终团队结果；
只有责任可归因的事件才能更新公共角色证据；延迟、版本、propensity 和 UNKNOWN
规则必须可审计。RARE 不是已证明的新算法；RLS、online SGD、周期性 refit、
raw acceptance、contextual trust/bandit、terminal-only 和 pooled controller 是
预先声明的比较条件。

TeamBench-derived PeerRoleBench-TB 是候选 benchmark，不在 PIPE3 资格、隔离、
责任切分和 root-level split 通过前冻结。N02 不再补样本；N03 只在资格通过后按
剩余预算启动。A800 训练延后到方法在小规模真实 selected-only 流上有可识别目标。

## 理由

这样可以让论文的唯一因果箭头保持可识别：

```text
真实交付 -> recipient judgment/use -> role evidence -> future assignment -> utility
```

如果 RARE 不能超过同信息 trust/bandit，或没有未来责任变化，论文必须收窄为协议/负
结果，不能用模型规模、角色熵或一次终局分数补足缺失证据。

## 后果

主线、方法合同、baseline、RQ 和当前证据边界已写入
`docs/paper/aamas2027/MAINLINE_V1.md` 与 `CLAIM_EVIDENCE_MATRIX.md`。LaTeX 主稿
应先作为 internal pre-results draft；旧 `main.tex` 保留为历史稿，避免混淆实验语义。
