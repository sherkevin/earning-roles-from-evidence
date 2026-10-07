# 第二 structural root 决策备忘录任务汇报

日期：2026-10-07
状态：`PARTIAL / DECISION_REQUIRED`

## 目的

在不启动新 API/GPU 实验的前提下，比较 PIPE1、PIPE2-derived 和 DIST1 作为 PIPE3
确认 root 的真实可行性，避免继续在互相矛盾的 development/confirmation manifest 上
执行 baseline。

## 完成内容

依据现有零调用 qualification、preflight 和真实 N02 暴露的问题，形成了
[第二 root 决策备忘录](../../research/candidates/second_root_decision_memo_v0.1_20261007.md)。
比较维度固定为：上游权威性、结构独立性、producer/recipient/adoption 责任覆盖、later
assignment 可接入性、完整成本和剩余工程量。

## 结论

- DIST1 不再适合作为 confirmation root：native grader 没有执行真实 consumer，且
  priority coverage blind spot 已被真实 N02 结果暴露；保留为历史工程诊断。
- PIPE2-derived 当前最接近可执行的第二 root，但 CSV overlay 的 authority 仍需共同确认，
  不能自动进入 active manifest。
- PIPE1 的原生性更强，但 22 项 preflight 仅 11 项通过，剩余 route/scorer/visibility/
  provider/budget/identity 门尚未关闭，直接运行会产生不可识别结果。

因此当前仍保持 `baseline_frozen=false`、`scientific_claim_allowed=false`、无新 API/GPU
预算。该备忘录只把选择变成可审查的重大决策，不替用户确认 root split。

## Goal 对照

ER-G3 获得了更清晰的 root 选择依据，但“至少两个独立 root + 冻结 split”仍未完成；
ER-G4 没有新增科学样本。下一步是在 root 选择后建立唯一 parity card，再补齐七臂、独立
history、later outcome 和完整成本，之后才能申请有界真实 API。
