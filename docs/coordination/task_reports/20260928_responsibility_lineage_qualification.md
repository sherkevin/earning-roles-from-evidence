# 2026-09-28 严格 responsibility lineage qualification

## 任务

修复第二 root 复审发现的 sidecar 缺口：反馈不能只指向一个合法 judgment/outcome record，
还必须逐跳绑定 canonical selection→delivery→judgment/action/outcome。只做零 API、零 GPU
工程资格，不把结果写成 benchmark 或学习效果。

## 实现

- `FeedbackSidecar` 支持兼容旧 v2 和严格 v3；v3 增加 `artifact_sha256`、
  `delivery_record_hash`、`action_id`、`action_record_hash`。
- `replay_policy_sidecars(..., require_responsibility_lineage=True)` 在 policy update 前
  校验 producer/version、recipient、delivery selection/task、artifact digest、canonical
  judgment/action/outcome 和对应 record hash。
- 新增 [资格脚本](../../../scripts/peerrolebench_responsibility_lineage_qualification.py)
  与单测 [test_peerrolebench_responsibility_lineage.py](../../../tests/test_peerrolebench_responsibility_lineage.py)。

## 真实执行记录

配置、逐 case 原始记录和汇总均在：

- 首次 v1：record index 未覆盖 `producer_delivery`，canonical case 错误拒绝；失败保留。
- v2：修正 index 后暴露 fixture 把 terminal sidecar action 写成 `use`，而 canonical
  recipient 实际 action 是 `repair`；失败保留。
- v3：修正 fixture 后通过，但运行时在代码提交前；保留。
- 最终 v4：[config](../../../experiments/logs/n03_responsibility_lineage_qualification_20260928_v4/config.json)、
  [raw](../../../experiments/logs/n03_responsibility_lineage_qualification_20260928_v4/raw.jsonl)、
  [summary](../../../experiments/logs/n03_responsibility_lineage_qualification_20260928_v4/summary.json)，
  commit `f857aec`，5 cases 全部符合预期：canonical `PASS/update=1`；wrong delivery、
  artifact、action、producer 均 `INVALID/update=0`。

## Goal 对照

| Goal 要求 | 状态 | 说明 |
|---|---|---|
| 责任归因和 situated judgment 可审计 | PARTIAL | 离线 strict lineage 已通过；PIPE3 live runner 尚未产生这些 sidecar |
| benchmark/scorer 资格 | OPEN | 没有真实候选执行或独立 hidden scorer |
| baseline 公平性 | OPEN | 同 snapshot/信息/成本口径未接入 runner |
| 真实学习效果、训练与 A800 | OPEN | 零 API、零 GPU，无科学效果主张 |
| Goal 变更 | UNCHANGED | 未修改或降级 Goal |

首轮失败不是被覆盖掉的“修复前结果”：它证明旧 fixture/validator 会把 action 责任错连，
因此保留为实现诊断；最终通过只表示新 v3 gate 在这个 in-memory contract fixture 上能
拒绝四类 cross-link mutation。

`goal_change_requested=false`。
