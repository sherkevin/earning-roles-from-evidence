# Canonical nested manifest validator qualification

日期：2026-10-04
状态：`QUALIFIED_OFFLINE / ENGINEERING_ONLY`
`goal_change_requested=false`

## 对应 Goal 与目的

本任务对应 ER-G1（benchmark/baseline 可执行性）和 ER-G2（方法可重放性）的工程
前置。它实现了 execution card 要求的向后兼容 nested validator：继续复用
`RootRunnerManifest` 作为唯一 root identity，不另造第二套 root 协议；在 policy runner
启动前检查七臂工程矩阵、三类 source channel、公共 stream digest、成本/UNKNOWN/assignment
规则、15 个 positive/negative cells，以及 `closest_published` 的 blocked placeholder。

## 实现与冻结信息

- `scripts/peerrolebench_canonical_manifest.py`：canonical envelope validator。
- `scripts/peerrolebench_canonical_manifest_qualification.py`：结构化零调用 qualification。
- `tests/test_peerrolebench_canonical_manifest.py`：valid manifest 与 mutation controls。
- clean tracked source commit：`96c4203c73e875a0b6a03be66bd6444aca42f9fa`。
- 当前 receipt：`experiments/logs/n03_canonical_manifest_validation_20261004_v2/`。
  `config.json` 记录 component SHA-256、Python 版本和零调用声明；
  `worktree_status_before.txt` 保留执行时未相关的工作树状态。

validator 强制检查：

1. nested `RootRunnerManifest`、task/structural signature/authority/split 和
   material/task/adapter/sandbox/worker digests；
2. 七个 arm 的注册顺序、contract fields、factory/version、implementation/spec digest、
   temperature、exploration 和 namespace；
3. `situated_judgment`、`raw_acceptance`、`terminal_outcome` 三个 channel 的 mapping/
   implementation/channel digest；
4. ordered menu、registry、public `φ`、offer、read-cut、arrival、RNG、propensity、
   state schema/init 的十个 stream digest；
5. selected-only、UNKNOWN/no-update、cost mode/schema、history、assignment-before-start、
   denominator preservation 和 negative-cell digest；
6. 每个 channel 的 positive/unknown/late/duplicate/mutation cell，episode unit、seed、
   expected runner start/update；
7. 缺失或未资格化的 `closest_published` 必须保持 `blocked_required`，因此不能把七臂
   工程矩阵误报成科学 baseline。

## Qualification 结果

执行命令：

```text
python3 scripts/peerrolebench_canonical_manifest_qualification.py \
  --out-dir experiments/logs/n03_canonical_manifest_validation_20261004_v2
```

15 个 case（1 valid + 14 mutation/rejection）通过：valid manifest 被接受；所有负向
case 均 `status=UNKNOWN`、`false_accept=false`、`runner_started=false`、
`policy_updates=0`。receipt 为 `QUALIFIED_OFFLINE`，`real_api_calls=0`、`gpu_jobs=0`、
`scientific_claim_allowed=false`、`benchmark_qualified=false`。

测试结果：

- canonical manifest focused tests：12 passed；
- baseline root + policy matrix + canonical manifest：32 passed；
- canonical parity/raw/terminal/manifest regression：27 passed；
- `py_compile` 与 `git diff --check` 通过。

## 证据边界与剩余缺口

这只证明 manifest 的 schema/digest/mutation 能在 runner 前 fail-closed。当前 validator
尚未接入 `PolicyMatrixRunner.run(require_manifest=True)`，也没有把 v21/raw v4/terminal
v5 三个历史 adapter receipt 重新写成一个共同 live stream；因此不能宣称 executable
scientific parity、baseline freeze、later-use、角色学习、实时性或成本结果。历史
adapter receipts 的较早 commit 仍保持原样，不被本任务覆盖。

下一步只做一项：将 validator 作为 runner 的 preflight，先在同一 synthetic stream
执行 manifest/registry/history mutation controls，并保存新的 clean receipt；通过后再
讨论 closest published adapter、第二 root 和有界真实 API。A800 与正式效果流继续关闭，
Goal 不降级。
