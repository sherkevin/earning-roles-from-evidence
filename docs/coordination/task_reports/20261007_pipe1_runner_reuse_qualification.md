# PIPE1 runner-reuse component qualification — 2026-10-07

状态：`QUALIFIED_OFFLINE_COMPONENTS`。本轮运行现有
`peerrolebench_pipe3_live_contract_qualification.py`，验证复用候选模块本身的零调用
合同。它不是 PIPE1 benchmark 结果，也不证明真实 actor、任务泛化、角色学习或收益。

## 启动失败与修正

- v1：stdout 重定向目标目录未先创建，shell 在 Python 启动前失败；原始错误保存在
  [`n03_pipe1_runner_reuse_qualification_20261007_v1/launch_failure.json`](../../../experiments/logs/n03_pipe1_runner_reuse_qualification_20261007_v1/launch_failure.json)。
- v2：误先创建了脚本要求由自身创建的目标目录，Python 在写配置前以
  `FileExistsError` 退出；原始错误保存在 v2 `launch_failure.json`。
- v3：只创建父目录，由 wrapper 打开 stdout，再由 qualification 脚本创建目标目录；
  成功完成，未修改 v1/v2。

## v3 结果

完整 evidence 在
[`n03_pipe1_runner_reuse_qualification_20261007_v3`](../../../experiments/logs/n03_pipe1_runner_reuse_qualification_20261007_v3/)。

- 5/5 cases 通过，`pipe3-live-contract-v1`；
- 17-event ledger replay 和 source→target schedule 通过；反向顺序被拒绝；
- candidate registry/menu/propensity 通过；
- ownership 表正确区分 `ELIGIBLE`、recipient-only `PENDING_ATTRIBUTION`、mixed/outside
  `UNKNOWN`；
- `unknown_no_update` 保持 state 不变、无 label、无 assignment、无 target selection；
- 0 real API、0 generator、0 candidate execution、0 GPU、0 policy update，
  `scientific_claim_allowed=false`。

## 结论边界

这证明已有模块可以作为 PIPE1 adapter 的底层 contract，且启动方式已经被记录并可复现。
它没有证明 PIPE1 的 source→artifact→Executor→Verifier live lineage，也没有证明
selected-only 真实读取、后续任务收益、baseline parity 或训练效果。下一步仍是把这些
组件接到 PIPE1 的离线 event fixture，先让 adapter 输出已绑定的 route receipt，再考虑
新的真实预算。
