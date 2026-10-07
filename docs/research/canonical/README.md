# 研究主文档：唯一生效版本登记

本目录是 earning-roles 的研究规范入口。六个类别各自只能有一个 `ACTIVE` 版本；当前研究标准登记为 registry v1.10（方法合同 v1.3、方法评价 v1.4；benchmark/baseline 计划 v1.1，故事线评价 v1.3、benchmark/baseline 评价 v1.2）。这里的 `ACTIVE` 只表示当前唯一生效版本，不表示科学结论已经验证。版本正文放在 `docs/research/versions/`，历史版本和候选报告可以保留，但不能另行宣称为当前定义。机器可读登记见 [`active_versions.json`](active_versions.json)。

| 类别 | 当前生效版本 | 作用 |
|---|---|---|
| 故事线与创新点 | [`storyline_v1.1_20260928.md`](../versions/storyline/storyline_v1.1_20260928.md) | 问题切口、整体机制、因果链、创新边界、反驳条件 |
| 方法论 | [`method_v1.3_20261007.md`](../versions/method/method_v1.3_20261007.md) | 结构化责任 owner、typed noisy observation、独立归因、合法后续 reward 与 delayed update、数学对象与训练候选 |
| Benchmark + baseline | [`benchmark_baseline_v1.1_20260930.md`](../versions/benchmark-baseline/benchmark_baseline_v1.1_20260930.md) | ArtifactRole 主轨、PeerSelect 副轨、任务资格、root split、对照、指标和实验顺序 |
| 故事线评价标准 | [`storyline_v1.3_20260928_eval.md`](../versions/evaluation/storyline/storyline_v1.3_20260928_eval.md) | 审查故事、创新、全文论证链和段落职责是否 sharp、自洽、可证伪 |
| 方法论评价标准 | [`method_v1.4_20261007_eval.md`](../versions/evaluation/method/method_v1.4_20261007_eval.md) | 审查 observation/归因/reward 分离、评价支持度与强对照、实时性与稳定性 |
| Benchmark + baseline 评价标准 | [`benchmark_baseline_v1.2_20260929_eval.md`](../versions/evaluation/benchmark-baseline/benchmark_baseline_v1.2_20260929_eval.md) | 审查选型、baseline、完整实验矩阵和结果解释能否识别主张并公平比较 |

## 变更规则

故事、方法、benchmark/baseline 或相应评价标准的研究含义发生变化时，先由用户和助手确认，再新建版本并更新登记；旧版本标为 `SUPERSEDED` 或 `ARCHIVED`，不删除。仅修复链接、拼写或机器索引可原地修复并在 task report 记录。候选设计写入 dated research report，不占用 `ACTIVE` 名额。

`docs/coordination/GOAL.md` 是不可静默降级的项目目标章程；它不替代这六份文档。`docs/user/decisions/` 只保存单个已对齐的小决议，不复制六份正文。实验日志、任务报告、论文稿和历史审查是证据/进展面，不是第七套研究规范。

旧主线、旧评审总表和旧方法候选的完整副本在 [`docs/archive/document_reorganization_20260928/`](../../archive/document_reorganization_20260928/)，原路径保留兼容指针。
