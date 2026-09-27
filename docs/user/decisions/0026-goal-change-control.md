# 0026：Goal 标准不可因实验失败自动降级

日期：2026-09-27。
状态：Accepted。

## 决定

项目以 [`docs/coordination/GOAL.md`](../../coordination/GOAL.md) 为目标标准，以
[`docs/coordination/TASK_REPORTS.md`](../../coordination/TASK_REPORTS.md) 为逐任务审计
入口。每个任务必须逐条比较目标、证据、差距和原因。实验失败、数据无效、接口失败、
预算耗尽或当前方法不显著，只能保留证据并创建修复任务，不能自动降低 benchmark、
方法创新、实时性、稳定性、强 baseline、真实 API 或论文证据标准。

## 允许修改 Goal 的唯一条件

只有用户明确同意修改/降级，并在新的 ADR 中记录旧目标、新目标、证据、理由、影响和
未完成旧目标的处理方式，Goal 才能改变。未获同意前，状态只能是 OPEN、PARTIAL、
UNKNOWN 或 BLOCKED_BY_EVIDENCE；不得把目标修改伪装成实验结论。

## 后果

当前 Goal v1.0 保持 ACTIVE。2026-09-27 对照报告确认故事已收敛、工程资格在推进，
但 benchmark、最终方法、实时训练效果、A800 结果和 AAMAS 科学结论仍未完成；这些
差距必须通过后续任务解决，不能通过改写目标消除。
