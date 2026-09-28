# 2026-09-28 故事线评价标准 v1.3 对齐

- 状态：`COMPLETE`（文档治理任务）
- 对应 Goal：ER-G1、ER-G4
- `goal_change_requested=false`
- 真实 API/GPU：0。

## 发现

active storyline 已经是 v1.1，但原 active evaluation v1.2 的评价对象仍指向历史 storyline v1.0。这会让“唯一生效文档”与验收对象不一致，评分不能审查当前主线。

## 修复

新建并登记 [storyline evaluation v1.3](../../research/versions/evaluation/storyline/storyline_v1.3_20260928_eval.md)，明确评价 v1.1 的有机闭环叙事，同时保留 matched composition、正交消融、全因子主效应/交互和跨 root 证据门。v1.2 标记为 `SUPERSEDED`，canonical registry 更新为 v1.4；没有修改 Goal 或放宽任何验收标准。

`check_research_registry.py` 和 AAMAS 文档同步检查通过。这个修复只解决评价对象一致性，不提高科学证据分。
