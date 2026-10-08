# Guide v3：哪些条件下应该赢、平或输

日期：2026-10-08。状态：`CURRENT_CONDITIONAL_RESEARCH_GUIDE`。
独立逻辑审查：`GO`。真实效果预测：`NOT_IDENTIFIED`。

这份 Guide 将三份正文矩阵对应到方法机制、匹配对照、优势条件、失效条件、完整成本
和反证。它是内部研究指南，不是已拟合结果，不修改 Goal、ACTIVE 规范或确认标准。
“合理”意味着输赢有原因和可检验条件，不意味着人为给方法安排胜负。

- 唯一当前 [Guide PDF](../../../../../artifacts/aamas2027/guide_experiment_matrix.pdf)。
- 固定 [v3 PDF](../../../../../artifacts/aamas2027/guide_experiment_matrix_v3_20261008/guide_experiment_matrix.pdf)。
- [LaTeX 源](../../../../../article/aamas2027/guides/v3_20261008/guide_experiment_matrix.tex)。
- [独立审查全过程](independent_review.md)、[机器记录](review_rounds.json)。
- [代数边界输入](boundary_spec.json)、[计算](../../../../../artifacts/aamas2027/guide_experiment_matrix_v3_20261008/boundary_calculations.json)。
- [v2 联合分布与误差参照](../v2_20261008/README.md)，固定版本仍保留。
- [公开原生成绩参照](../../../../../../reasonable_results/earning-roles/20261008_v1/README.md)。

## 四页内容

1. 五个审核维度的状态、真实证据口径、八行正文对照与必要补充强控制。
2. ArtifactRole 的判断信息、未来分工、冷启动、任务错配和强基线反证；Qp/Y 分离、
   read cut、同样本预测评价及 selected-only 边界。
3. PeerSelect 的实时/漂移/稳定性边界；四格交互、责任 gate 覆盖代价与事实错误。
4. 七个可复算赢/平/输边界、v2 成本模型的结构性乐观、UNKNOWN 的排序界限、共同
   分布/误差的留出检验要求。

正向例：有合法、可归因且包含额外信息的 judgment，足够可比较历史，及时反馈，且
收益超过完整成本。逆向例：0-shot、恒定/错误判断、语义相似却要求变化、peer 替换、
稀疏合法标签、长延迟、高成本/高到达率。相对同信息的任务条件 ridge 或 matched
composition 没有预设优势；若其解释全部收益，方法专属增量尚未成立。

所有数值例都没有命名方法、估计 SD/CI 或经验排名。科学家可以用它设计反转测试，
不能把其中的手设输入当作高置信度预期均值。更不能把公开 native 成绩移植为我们的
binary/later-use/payoff 成绩。

## 复现与版本

生成入口：`python3 scripts/build_experiment_target_guide_v3.py`，读取明确 JSON 输入。
当前修复稿构建日志在 `experiments/logs/experiment_target_guide_20261008_v3_r2/`；
首稿日志在同层 `experiment_target_guide_20261008_v3/`。配置先于计算落盘，记录源摘要、
命令、git commit 和未观测状态。重跑须另开版本，不能覆盖冻结记录。

首稿源、参数、计算、PDF、编译日志和 manifest 保存于版本包 `pre_review/`。每页有
GUIDE/NOT OBSERVED 水印。独立导出后只同步 Guide 主版；论文 `main.pdf` 与正文表不写入。

下一步是正文/确认卡集成待办和资格化后的真实联合数据验证；没有新增 API/GPU/benchmark
实验，没有用本 Guide 授权额外预算。三份科学验收标准仍未通过。
