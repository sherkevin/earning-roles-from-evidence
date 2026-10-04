# Canonical seven-arm manifest：执行卡与 schema 合同

日期：2026-10-04
状态：`DESIGN_ONLY / NOT_ACTIVATED`
任务类型：零调用前置设计
`goal_change_requested=false`

## 目的

把 situated judgment、raw acceptance 和 independent terminal outcome 放进同一
canonical PIPE3 stream 之前，先冻结 manifest 必须绑定的身份、信息、成本、失败和
分析字段。当前七臂只能作为工程 parity stream；active benchmark 标准还要求一个
`closest_published` 科学对照臂，因此本卡不把七臂标记为 `baseline_frozen`，也不改变
benchmark-baseline v1.1。

## 已有合同，直接复用

manifest 以现有 `RootRunnerManifest` 为身份和预算 envelope，不另造平行 root 协议，
并复用：

- `validate_contract()` / `BASELINE_ARM_SPECS`：七个工程臂的 source、update、history、
  correction、visibility 和 comparison group；
- `LiveRuntimeBinding`：material、task contract、sandbox、scorer、worker limits、
  policy namespace 和 candidate source snapshots；
- candidate registry、arrival schedule、RNG schedule、public-prefix、cost ledger、
  assignment-before-start 和 UNKNOWN/no-update validators。

现有 `RootRunnerManifest` 只绑定了部分 root/schedule/registry/budget 字段。三个最新
qualifier 的 config 也没有把它传入 `PolicyMatrixRunner.run`，所以当前不能称为
executable manifest；本卡先记录缺口，再实现向后兼容的 nested envelope。

## Manifest v1 最小字段

### A. root 与运行身份

必须绑定 `manifest_version`、`root_id`、`task_id`、`root_commit`、
`structural_signature`、authority/root source digest、generator/scorer/runner/component
digests、seed split、development/confirmation status、configuration path、sealed-at
时间、parent/root manifest digest 和自身 `manifest_digest`。历史 v21/raw v4/terminal v5
仍保留原始 commit，不能回写成当前 manifest 的覆盖证据。

### B. 七臂语义与第八臂前置

`baseline_contract_digest` 必须覆盖每个 arm 的稳定 `arm_id`、factory/class/version、
implementation digest、accepted source、update/correction/history/visibility 规则、
temperature、exploration、tie-break 和 state namespace。七臂为：

`uniform`、`no_update`、`raw_acceptance`、`terminal_only`、`contextual_trust`、
`pooled_controller`、`RARE`。

另设 `closest_published` 状态字段和 cell placeholder。它在 faithful public adapter、
成本/assignment 合同和独立回执产生前必须是 `blocked_required`，不能被七臂通过掩盖。

### C. 三种 source channel

`channel_adapters` 必须同时列出：

1. `situated_judgment`：native recipient judgment sidecar、mapping/schema/implementation
   digest、正向 cell 和 UNKNOWN/late/duplicate/mutation 负向 cell；
2. `raw_acceptance`：`RawAcceptanceSidecar`、mapping/version/digest 和同样的正负 cell；
3. `terminal_outcome`：`TerminalOutcomeSidecar`、`terminal-success-v1` mapping/digest
   和同样的正负 cell。

每格预注册 expected disposition（eligible/update、ignored、UNKNOWN/no-update、
preflight rejection），并要求 runner 启动前完成 registry/history mutation 检查。

三类 channel 的信息关系也必须写入 cell：raw acceptance 与 situated judgment 可以
来自同一 native `j0`，但必须绑定各自不同的公开 projection；terminal outcome 必须
发生在 selection/read-cut 之后，且不得把 scorer-private 或未来 outcome 字段泄漏进
`φ`；pooled 与 own history 必须分别记录可见范围和 namespace，不能仅改 policy 名称。
每个 cell 还要绑定 independent unit、episode 数和 seed split，避免把一次 eligible/update
误读成效应或实时性证据。

### D. 公共输入与时序

必须封存 ordered candidate menu/version digest、candidate registry digest、public `φ`
的 schema/version/digest、offer-stream digest、read-cut/decision-index/selected-at
schedule digest、arrival schedule digest、RNG seed schedule、sampling rule、temperature/
exploration、propensity digest、state cap/history schema digest 和 per-arm state-init
digest。七臂只能读取同一合法 public prefix；未来 outcome、private scorer、operator
字段和其他 arm 的 state 不得进入 `φ`。

### E. 运行材料与成本

每臂绑定同一 material/task/sandbox/scorer/worker/model/API/tool budget；namespace 只能
按 arm 隔离。manifest 需要 `cost_schema_digest`、`cost_mode`（`offline_unmeasured` 或
`live_measured`）、state byte cap 和 stage budget。离线资格允许零值但必须明确
`measured=false`；科学 live mode 必须通过 `validate_live_root_receipt`，逐臂记录
producer、recipient、judge、scorer、selection、update、retry、communication、repair、
replay、state、API、tokens、GPU 和 wall-clock 全部成本。

### F. 因果、失败与分析指针

manifest 必须绑定 assignment-before-start 语义版本、source→target ledger/history
digest、later-outcome/read-cut digest、UNKNOWN rule/version、negative-cell contract
digest、denominator-preservation 标志、failure taxonomy 和 raw/summary receipt schema。
完整 estimand、independent unit、aggregation、CI/randomization/blocking、sample-size、
multiple-comparison 与预注册停止规则放在 `analysis_plan_digest` 指向的冻结文档中，
不把长统计文本复制进 runner。

## 激活条件

工程七臂可以进入零调用 executable qualification，只有同时满足下列条件才能把它写成
科学 baseline manifest：

1. `RootRunnerManifest` nested envelope 和上述字段均由 runner 在执行前校验；
2. 三种 source adapter 共用同一菜单、`φ`、read-cut、arrival、成本和 namespace；
3. positive/negative cells、UNKNOWN/no-update、duplicate、late、mutation 和 history
   registry preflight 都有可重放 receipt；
4. `closest_published` 已有 faithful public adapter，或明确记录 `NO-GO` 并从主结论中
   排除，不能声称 baseline 已冻结；
5. benchmark authority、第二 structural root、independent live history、later-use
   outcome、完整成本和 analysis plan 均已绑定，才允许真实 API 流。

因此 confirmation/科学矩阵的激活 validator 必须拒绝缺失的第八个
`closest_published` role；七臂回执只能叫 `engineering_matrix`，不能叫完整 baseline。

## 这张卡的边界

本卡没有改 active 方法、benchmark 或 Goal；没有 API/LLM/GPU 调用，也没有产生科学
结果。下一小任务是实现一个向后兼容的 nested manifest validator，并用当前 v21/raw
v4/terminal v5 做一次零调用 rejected-cell qualification。实现完成前不启动真实 API 或
A800。

证据与输入审查：

- `scripts/peerrolebench_baseline_root_contract.py`
- `scripts/peerrolebench_baseline_contract.py`
- `scripts/peerrolebench_policy_matrix_runner_v1.py`
- `experiments/logs/n03_canonical_pipe3_parity_20261004_v21/`
- `experiments/logs/n03_canonical_raw_adapter_20261004_v4/`
- `experiments/logs/n03_canonical_terminal_adapter_20261004_v5/`
- [post-adapter three-document audit](20261004_three_doc_post_adapter_audit.md)
