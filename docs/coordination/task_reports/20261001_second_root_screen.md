# Task report — second structural root screen (2026-10-01)

## Goal alignment

- **对应标准**：ER-G3/ER-G4；第二 independent root、producer/recipient/adoption 可识别性和 benchmark 可复现性。
- **状态**：`PARTIAL`。从已 pinned TeamBench 任务中筛选出比 MULTI3 更合适的 `PIPE2_data_pipeline` 候选；没有把它升级为冻结 benchmark。
- **goal_change_requested**：`false`。

## 证据与发现

本轮只读取 pinned TeamBench generator/spec/brief/task metadata/grader，没有调用 LLM API、
Nebula 或 GPU。`PIPE2` 的三段 ETL（extract/transform/load）天然提供中间 rows 和下游
处理，比 `MULTI3` 的 shared schema/`correct_wire` 依赖更容易做责任切分。它仍有两个硬缺陷：
upstream brief/spec 显式列出 bug，native grader 把静态源码检查、候选 workspace 测试和
expected output 混在一起，不能直接充当独立 scorer。

## 对验收标准的结论

- 已满足：找到一个结构上区别于 PIPE3、且具有真实 producer→recipient 数据流的第二候选；
  记录了与 MULTI3 的差异和可复用切法。
- 部分满足：PIPE2 作为 derived TeamBench root 的 authority substrate 可复用，但任务材料
  去 oracle、parent-side artifact/adoption scorer、权限和 replay 尚未通过。
- 未满足：第二 root freeze、独立 live histories、baseline parity、later-use effect、
  完整成本和 confirmation split。

## 下一步

先实现一个零调用 PIPE2 material/ownership/adoption adapter qualification，沿用现有
`RoleEvidenceOffer` 与 `SelectionPlan`，只验证 producer output 真实进入 recipient input、
expected output 不泄漏、责任 scorer 能区分 producer/recipient/mixed/UNKNOWN。该资格通过
后再决定是否纳入 candidate cell manifest；期间不启动正式 API/A800。
