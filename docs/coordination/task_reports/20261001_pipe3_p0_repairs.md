# PIPE3 P0 contract repairs and real-scorer gate — 2026-10-01

状态：`PARTIAL`。Goal、active storyline、method 和 benchmark 版本均未降级或修改。

## 本轮关闭的工程语义

在 `pipe3-two-stage-composition-v1.2` 中，四个 P0 约束被写入同一条可回放路径：

- candidate registry 将 `candidate_id@version` 绑定到实际 producer source digest、model id、
  model-config digest 和 registry digest；`Delivery`、scorer input manifest、role offer 与
  isolated read 保留该绑定。delivery 与 selected candidate 不一致时停止为 `UNKNOWN`。
- 当前责任归因路径把 `producer.py` 设为 recipient read-only。只有预注册的 producer defect、
  objective producer `FAIL`，且完整 source outcome 存在时才允许 producer evidence；recipient
  integration、mixed edit 和 later PASS 不能反向制造 producer label。历史没有显式 defect 字段的
  receipts 仍走兼容分支，便于回放，不改变当前 runner 的严格路径。
- delayed credit 使用 `terminal_outcome` channel；source publication 仍不更新 persistent
  policy。`terminal_only` policy 用于该 qualification，避免把 terminal quality 伪装成
  `recipient_judgment`。
- RoleEvidenceOffer publication/read、后续 assignment offer/consumption attestation 共用同一
  auxiliary append-only chain；offer 的 previous root、read trace 和 manifest root 被保存并校验。

## 离线验证

- `tests/test_peerrolebench_*.py`：`368 passed`。
- 新的 injected qualification：producer defect/只读 producer 路径可完成一次 delayed update；
  candidate treatment mismatch、recipient-owned 与 mixed controls 均停止在 UNKNOWN/no-update。
- 所有历史 Delivery ledger replay 通过；optional treatment digest 不会把旧记录重写成显式 null。

这些结果只证明 contract/replay 语义，不证明模型效果、专业化或 benchmark 比较。

## 真实 CPU sandbox 结果

配置与原始日志保留在：

- 首次本地启动失败：`experiments/logs/n03_pipe3_two_stage_composition_20261001_v3/`。原因是
  runner 要求输出目录不存在，但启动前预创建了目录；没有进入 scorer。
- 修正目录后真实运行：
  `experiments/logs/n03_pipe3_two_stage_composition_20261001_v3_run/`。

后者确实调用了真实 pinned sandbox scorer，但三个 before-action scorer 都返回
`UNKNOWN / PermissionError: [Errno 1] Operation not permitted (originated from sysctl() malloc 1/3)`，
因此没有 action、evidence、target 或 policy update。运行使用 0 LLM API、0 GPU；不能把它写成
方法失败，也不能写成资格通过。这个环境问题需要单独修复/复测，当前不重复提交同一 sandbox 路径。

## 复测结果（v1.2，2026-10-01）

在单 scorer transport probe 成功后，按原有配置重新执行了一轮完整的 v1.2 CPU
qualification；输出目录为
[`n03_pipe3_two_stage_composition_20261001_v4`](../../../experiments/logs/n03_pipe3_two_stage_composition_20261001_v4/)。
这次 18 次 pinned sandbox scorer 调用全部完成，三种 control 的结果为：

- `producer_owned`：producer objective `FAIL`（P2 serialization），source attribution
  `ELIGIBLE`，RoleEvidenceOffer 发布、isolated read、assignment-before-selection、target
  terminal outcome、17-event native replay 和一次 delayed update 均完成。
- `recipient_owned`：source 责任门得到 `UNKNOWN`，没有发布 producer evidence、target 或
  policy update；这是预期的保护性拒绝。
- `mixed`：producer/recipient ownership 不可归因，责任门为 `PENDING_ATTRIBUTION`，同样停止
  为 `UNKNOWN`，没有 policy update。

runner 回执为 `QUALIFIED_OFFLINE`、`contract_passed=true`；记录了 native manifest root
`fdc26049145a28a4308ab3c1687261231fea2d445e1957768619e71d2dcc76c0` 和 auxiliary manifest
root `04b78676c67353522106dcf3c7a343caeda593919001d62c2c9641d044a7f070`。本轮 0 LLM API、
0 GPU，`scientific_claim_allowed=false`。因此它关闭的是责任/证据/执行前分派/延迟回写的
有限同 root 工程资格，不是 benchmark、baseline、真实 situated judgment 或 role-learning
效果证据；`same_root_qualification=true` 且 `independent_benchmark=false`。

## 下一步门

不再重复这一条已经通过的本地 transport 路径。下一道门是把同一 contract 接入独立
confirmation root、独立 policy/history namespace、真实 situated judgment 和同信息 baseline
runner，并补齐完整成本与 later-use outcome。只有这些门通过，才可把结果纳入 benchmark
matrix、讨论实时更新效果或提交 A800 challenger。v4 仍不解冻 benchmark/baseline，也不
支持任何科学效果主张。
