# Task report：固化论文主线、证据选择与创新点约束 / 2026-09-27

状态：`DONE`；`goal_change_requested=false`。

## 完成内容

根据本次明确共识，新增 ADR 0037：

[`docs/user/decisions/0037-research-quality-and-mainline-invariants.md`](../../user/decisions/0037-research-quality-and-mainline-invariants.md)

该决议固定了四条工作规则：

1. 故事线和方法论必须充分、合理、完备、自洽，问题切口必须 sharp；
2. benchmark 要能证明主张并具备权威性，baseline 要覆盖直接比较且具有时效性、新颖度或经典性；
3. “learning roles from others' situated judgments” 继续作为核心创新主线，不能因局部实现问题或一次实验失败被静默删除、替换或降级；
4. 后续遇到抉择或任务漂移先回看 ADR、Goal 和 task report，任何实质修改都要先与用户双重确认，并建立新的编号 ADR。

## 与 Goal 的对照

本任务落实了 Goal v1.0 的目标变更控制和主线保持要求，明确 `goal_change_requested=false`。
它没有宣称 benchmark、baseline、方法、实时训练或论文效果已经完成，也没有改变当前
`OPEN`/`UNKNOWN` 的阶段状态。

## 证据与边界

这是一次决议归档任务，不是实验。没有 LLM 调用、GPU 作业或科学效果数字；它只改变后续
研究决策的约束文件和索引，不回写任何历史实验日志。

## 下一步

继续按照 ADR 0037 和 Goal v1.0，完成 PIPE3 scorer/lineage 的资格审查，然后再讨论
benchmark freeze、baseline freeze 和真实 API 小流；在证据门通过前不把候选实现写成最终创新。
