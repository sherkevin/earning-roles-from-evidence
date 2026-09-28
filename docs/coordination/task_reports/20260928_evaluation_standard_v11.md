# 2026-09-28 验收标准 v1.1 升级

- **状态**：`COMPLETE`（评价标准升级）；不代表论文已达到任何录用结论
- **对应 Goal**：ER-G1/ER-G2/ER-G3/ER-G4 的严格预检
- **goal_change_requested**：`false`
- **真实 API/GPU**：未运行；本任务是标准设计与文献来源审查

## 为什么升级

独立审查认为 v1.0 能防止明显的故事漂移，但还不足以称为高质量论文的严格预检：estimand、主假设、统计不确定性、基座/污染审计、closest published baseline、负迁移、clean replay、Proceedings/Findings 档次和 supplementary 边界不够明确。

## v1.1 新增硬门

- 故事线：最小反例、唯一创新、五个近邻 novelty table、H1/H2/H3 estimand、assignment 实际采用率、claim-evidence 分级和 Proceedings-ready/Findings-ready 双档。
- 方法：目标函数/estimand、调参 split、复杂度/容量/吞吐/backlog/RAM、drift 窗口、judge reliability/propensity、late correction/replay digest 和 clean-environment replay。
- Benchmark/baseline：权威基座 commit/license/scorer pin、污染审计、faithful closest adapter、parity table、95% uncertainty、精度/功效理由、多重比较、异质性、Pareto quality-cost 和多 root/多 stream 目标。

v1.0 没有删除，已标记 `SUPERSEDED`；唯一 active 入口已切到三个 v1.1 文件。具体来源边界见 [`docs/research/20260928_evaluation_criteria_provenance.md`](../../research/20260928_evaluation_criteria_provenance.md)。

## 与 Goal 对照

- 已完成：评价标准更严格、可执行、可审计，并区分官方要求与项目化标准。
- 部分满足：标准要求的实验和方法证据尚未取得；当前不满足 Proceedings-ready。
- 未满足：benchmark 未冻结、RARE/updater 未锁定、独立 confirmation 与 A800 结果不存在。

升级没有改变 Goal，也没有把“两 root”偷偷升格成官方阈值；v1.1 把两 root定义为当前硬底线，并把三 root/多 stream写成 Proceedings-ready 强目标，若要改变 Goal 仍需单独确认。
