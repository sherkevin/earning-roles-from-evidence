# Canonical manifest preflight qualification

日期：2026-10-04
状态：`QUALIFIED_OFFLINE / ENGINEERING_ONLY`
`goal_change_requested=false`

## 目的与 Goal 对照

本任务继续 ER-G1/ER-G2 的工程前置，把上一任务的 nested canonical manifest validator
接到 `PolicyMatrixRunner` 的 preflight 入口。目标是证明 malformed manifest 在任何
policy object 构造、selection 或 update 之前被拒绝；目标不是证明七臂 baseline 公平，
也不是证明 situated judgment 的效果。

## 实现

`PolicyMatrixRunner` 新增可选的 `canonical_manifest` 与
`require_canonical_manifest` 参数。入口的第一道 gate 调用
`validate_canonical_manifest()`；提供 legacy `RootRunnerManifest` 时还会检查 nested
root digest 一致。缺失或非法 canonical manifest 不会进入 policy factory。

qualification 脚本复用 synthetic `recipient_only` fixture 作为唯一正向 runner stream；
14 个 mutation cells 只调用 validator，未进入 runner。历史 v21/raw v4/terminal v5
receipt 未被重写。

## 冻结与证据

- clean tracked source commit：`5ef7016`（完整 SHA 见 receipt `commit.txt`）。
- 执行命令：

  ```text
  python3 scripts/peerrolebench_canonical_manifest_qualification.py \
    --out-dir experiments/logs/n03_canonical_manifest_validation_20261004_v4
  ```

- receipt：`experiments/logs/n03_canonical_manifest_validation_20261004_v4/`，含
  `config.json`、`raw.jsonl`、`summary.json`、`commit.txt` 和执行前工作树快照。
- 16 个 case：valid manifest、1 个 synthetic runner preflight、14 个 mutation/rejection。
- valid manifest 通过；synthetic runner 七臂各选择 2 次，产生 3 个 fixture policy
  updates；所有 14 个负向 case 为 `UNKNOWN`、`false_accept=false`、
  `runner_started=false`、`policy_updates=0`。
- receipt 状态 `QUALIFIED_OFFLINE`，`real_api_calls=0`、`gpu_jobs=0`、
  `scientific_claim_allowed=false`、`benchmark_qualified=false`。
- 测试：42 项 focused/canonical adapter regression 通过；`py_compile`、`git diff --check`
  通过。

## 解释与剩余距离

这证明 manifest validator 已经位于 policy construction 之前，并能拒绝缺 channel、
arm/spec、public-φ、root metadata、cost/UNKNOWN、cell expectation、closest placeholder
等 mutation。它仍不是 scientific executable manifest：synthetic manifest 的 stream
digest 尚未与真实 `offers/schedule/registry` 做逐项 runtime binding，三种 source
projection 也没有在同一真实 stream 中同时产生；synthetic 3 updates 只是 fixture
reachability，不是学习效果。

因此三份 active 文档仍为 `NOT_READY`，G0/G1/G2 仍 `PARTIAL`，G3–G5 仍 `OPEN`。下一项
只做 manifest-to-runtime binding：用同一 registry/menu/read-cut/arrival/propensity/φ
重新计算 offer-stream digest，并在 runner 启动前拒绝 mismatch；通过后再审查
`closest_published`、第二 root 和真实 API。A800 与正式效果流继续关闭，Goal 不降级。
