# Stream-JEV 创新边界：2026-09-25

## 结论先行

目前没有已经确定的 backbone，也没有已经成立的新训练结构。
`Laya multilingual 322M + 在线 RLS + replay` 是一个合理的工程起点和强基线，
不是论文创新。真正需要证明的是：能否设计一个在 selected-only、延迟、乱序、动态
候选和旧能力保护同时存在时，仍能逐反馈快速更新的机制。

## Laya 核查结论

| 事实 | 证据 | 对选择的含义 |
|---|---|---|
| multilingual 约 322M，English/typed-decisions 约 421M | Laya README 的 checkpoint 表和 `laya/router.py` | 规模、typed 输出和本地部署是优点，不是任务适配证据 |
| 双向 encoder + typed decision head，不是自回归 LLM | `laya/common.py`、`laya/agent.py` | 适合作为小型决策 encoder；不等于适合在线更新 |
| 公开 fine-tune 是固定数据、多 epoch、AdamW/DDP/RLCD/CE | `notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb` | 它没有解决实时 selected-only 训练 |
| hooks 观测/改写请求，没有 label-fit/update API | `laya/hooks.py`、`laya/agent.py` | 我们必须自己定义并实现更新机制 |
| 当前项目没有加载 Laya 权重 | `references/aamas/streamjev_20260924/` | backbone 还未经过真实闭环验证 |

Laya 的公开项目页面：[repository](https://github.com/NandhaKishorM/laya)，
模型表和训练入口见固定源码副本
`/Users/jingwu/work/benchmark/task/task47-jev-source-evaluation/reference/laya/`。
上游 README 的准确率和延迟是作者 benchmark 结果，不能代替我们的 peer/tool 数据。

## 当前结构哪些是已有的

| 组件 | 当前角色 | 创新判断 |
|---|---|---|
| Laya/mmBERT/ModernBERT | encoder/静态基线 | 现成模型 |
| Beta、RLS、LinUCB、IPS | 在线估计或 bandit 更新 | 现成方法 |
| selected-only delayed feedback | 问题约束/学习设置 | 不是单独的新算法 |
| replay、reservoir、KL/EWC、GEM | 遗忘控制 | 现成方向 |
| GRU/gated fast state、短 unroll | 快速适应候选 | 已有 fast weights/meta-learning 家族，需要强基线 |
| LoRA、异步 learner、checkpoint、RLinf Channel | 系统实现 | 工程基础设施 |
| 冻结 encoder + RLS + replay | 当前 baseline | 组合可用，但不足以支撑新模型论文 |

## 候选新机制

### A：Meta-learned Event Update Operator

冻结语义 encoder，只保留低秩可写参数 `A_t`。离线在随机 selected-only stream
上学习更新器 `U_ψ`，线上把决策时捕获的特征、标签、延迟、propensity 和不确定度
映射为低秩写入。目标是未来 prequential utility 加旧 regime 保留，而不是拟合当前
标签。必须与 RLS、online SGD、GRU state 和普通 learned optimizer 同预算比较。

### B：Delay/Version-correct Event-sourced Updater

在决策时保存 feature/eligibility、propensity、candidate version 和 snapshot。
反馈乱序到达时，按原决策事件生成独立增量，再以可重放、可合并的 sufficient
statistics 更新。关键判据是不同到达顺序得到相同的 canonical 状态，候选版本替换
不会污染旧事件。只有日志队列而没有可验证的等价性，不能称算法创新。

### C：Protected-plasticity Update

把参数分成不可写的语义基座和离线学习的低秩可写子空间。selected label 只能写入
该子空间；每次写入前用旧任务回放的 KL/ECE/trust-region 检查，超限就拒绝或投影，
通过 locked holdout 后才异步巩固。必须和 RLS、EWC/GEM、LoRA、replay-only 比较
适应速度–遗忘曲线。

三条都只是研究假说，当前不选择。A 的算法风险最高但潜在新颖性最大；B 的系统和
可验证性质最清楚；C 最贴近“实时适应与少遗忘”的核心矛盾。

## 判别实验，而不是扩量实验

下一次只做一个真实小闭环：选一套资格明确的 peer/tool replay，先运行候选 encoder
的 static scorer，保存决策时特征和完整 propensity；然后只比较同一 scorer 的 no-update
与一个在线更新器。通过后才选择 A/B/C 中的一条，加入同预算 RLS、online SGD 和周期
refit。主指标只保留：post-update prequential reward、漂移恢复、旧任务退化、更新
p95、状态大小和版本/延迟错误率。

任何候选机制都必须满足：无全量真值、无 oracle 排名、随机延迟和候选 churn；至少
10 个配对 seed；label-shuffle/no-feedback 不应产生同等收益。否则停止算法扩展，
把论文定位为实时在线选择系统。

## 最终判定

现在能确定的是**研究约束和基线层**，不能确定的是最终 backbone 和新训练结构。
先例并没有证明问题没有价值，只说明“Laya 离线训练 + RLS + replay”不能作为答案。
只有候选新机制在真实 selected-only 闭环上显示出稳定的适应–遗忘 Pareto 优势，才
锁定 backbone、训练方式和论文主张。
