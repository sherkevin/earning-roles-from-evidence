# Task report：candidate manifest v2 validator fix / 2026-09-27

状态：`COMPLETE`（仅对应 manifest 机器校验条目）；`goal_change_requested=false`。

## 发现

`n03_benchmark_baseline_candidate_v2.json` 已通过 v2 provenance 和双 root payload
preflight，但通用 `peerrolebench_validate_manifest.py` 仍把 manifest version 写死为
`peerrolebench-benchmark-baseline-candidate-v1`。因此同一份 v2 manifest 在 provenance
中通过、在命令行 validator 中失败，形成了可复现性上的配置门不一致。

## 修复与验证

- validator 现在显式接受 v1 和 v2 两个候选版本；未知版本仍然失败。
- 新增 v2 回归测试；v1 原有严格测试保持不变。
- 零 LLM/零 GPU 回执：
  [`n03_manifest_validator_v2_20260927`](../../experiments/logs/n03_manifest_validator_v2_20260927/)。
  结果为 `valid=true`、2 个 root、7 个 baseline，`benchmark_frozen=false`。
- 13 项 manifest/provenance/runner 回归通过；没有启动真实 API。

## Goal 对照

这一步完成了 G3 的“候选 manifest 机器结构校验”子项；它没有完成两个 root 的科学
资格、scorer/ledger 隔离、baseline freeze 或方法效果。候选 manifest 的状态仍是
`CANDIDATE_NOT_FROZEN`，Goal 没有修改。

## 后续

继续处理 producer scorer 的 failure disposition 和 PIPE3 的真实 root 资格；在这两个
问题没有收紧前不启动 A800，也不把 manifest 标成 frozen。
