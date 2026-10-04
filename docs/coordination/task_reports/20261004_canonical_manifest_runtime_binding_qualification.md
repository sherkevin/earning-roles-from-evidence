# Canonical manifest runtime-digest binding qualification

日期：2026-10-04
状态：`QUALIFIED_OFFLINE / ENGINEERING_ONLY`
`goal_change_requested=false`

## 目的

本任务关闭 canonical manifest 与 runner runtime identity 之间的下一道工程缺口：在
policy construction 前，把 nested manifest 的 `root_commit`、registry/schedule/RNG
digest、arm order 和十项 public stream digest 与一次具体 synthetic offer stream 做
一致性检查。它对应 ER-G1/ER-G2 的可执行性和可重放性，不是 baseline 科学冻结。

## 实现

`validate_runtime_binding()` 复用 `validate_canonical_manifest()`，只比较调用者已经
物化的 runtime values，不生成第二个 root identity。`PolicyMatrixRunner.run()` 新增可选
`canonical_runtime_stream`：canonical schema 通过后、policy factory 前调用 runtime
binding；任何 root/registry/schedule/RNG/stream mutation 都在 selection/update 前拒绝。

当前实现仍保持兼容：没有传 canonical manifest 的历史 offline runner 不变；传入
`require_canonical_manifest=True` 才强制该 gate。

## 冻结与 receipt

- clean tracked source commit：`9faf81f`（完整 SHA 在 receipt `commit.txt`）。
- receipt：`experiments/logs/n03_canonical_manifest_validation_20261004_v6/`，含
  `config.json`、`raw.jsonl`、`summary.json`、commit 和执行前工作树快照。
- 执行仍为 synthetic `recipient_only` fixture，真实 API/LLM=0，GPU=0。

## 结果

17 个 case 通过：

- valid manifest：通过；
- synthetic runner preflight：通过，七臂各选择 2 次，fixture policy updates=3；
- runtime stream digest mutation：`UNKNOWN`、`false_accept=false`、
  `runner_started=false`、`policy_updates=0`；
- 其余 14 个 manifest mutation：同样全部 fail-closed、零选择/零更新。

回执状态为 `QUALIFIED_OFFLINE`，`scientific_claim_allowed=false`，
`benchmark_qualified=false`。focused canonical/adapter regression 共 46 项通过，
`py_compile` 与 `git diff --check` 通过。

## 证据边界

这证明 runtime binding 的拒绝顺序和 digest 机制可执行，但 `canonical_runtime_stream`
仍由 synthetic qualification caller 显式提供；它尚未从真实 PIPE3 offers、三个 source
adapter、candidate registry、read-cut、arrival 和 policy propensity 自动生成并逐项
绑定。因而不能把此回执写成 scientific same-information parity、baseline freeze、
later-use utility、实时训练或效果结果。`closest_published` 仍是 blocked required
第八臂，第二 structural root、independent live history 和 measured cost 仍开放。

## 下一步

只实现一个真实的 stream builder：从当前 runner 的 offers/schedule/registry/feature
capture 生成十项 `stream_values`，并在同一 synthetic manifest 上重放正负 mutation；
builder 通过前不启动 Idealab API、不提交 A800。通过后再重新审查 benchmark/baseline
是否足以进入一条有界 live history。
