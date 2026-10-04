# Canonical history provenance qualification

日期：2026-10-04
状态：`QUALIFIED_OFFLINE`（工程门通过；不产生科学效果结论）

## 目的与范围

本任务把 peer-history 的 source→target provenance 单独作为放行门，复用现有 native `PeerRoleLedger`、`RoleEvidenceOffer`、`LaterAssignment`、target selection/delivery/judgment/action/outcome、`DelayedCreditLedger`、`HistoryBindingReceiptV1` 和 adapter。它验证 history 不是脱离责任链的 hand-authored 统计；不调用 LLM/API、不提交 GPU、不改变 active benchmark/baseline/Goal。

配置在执行前写入 component hashes、commit、worktree、Python/平台和 10 个 cell；每个 cell 保存异常、entry/seal/append/update 数、成本和 raw JSONL。负例只能是 UNKNOWN，不能变成 label。

## 正式结果

正式回执：`experiments/logs/n03_peer_history_provenance_qualification_20261004_v2/`（clean commit `257791f`，配置记录空 worktree）；v1 未提交工作树回执保留。

- `QUALIFIED_OFFLINE`, `passed=true`；0 API、0 GPU，`scientific_claim_allowed=false`。
- `valid-chain`：canonical source/target chain 重建 receipt，replay 后 state/projection digest 相等；1 entry、1 seal、1 append。
- `duplicate-credit`：第一次 `APPENDED`，第二次相同 assignment/outcome 返回 `NOOP`；entry/seal 仍各 1，证明 exactly-once。
- 以下 8 个篡改/不完整 cell 全部 `UNKNOWN`，entry/seal/append/update 均为 0：
  - `wrong-source-evidence`：credit evidence 不在 offer；
  - `uncommitted-credit`：delayed credit 未提交；
  - `candidate-version-mismatch`：`peer-b@v1` 错绑给 `peer-a` assignment；
  - `registry-mismatch`：candidate registry digest 不一致；
  - `read-cut-before-source`：read cut 早于 source available；
  - `arrival-before-decision`：target outcome 在 decision 前到达；
  - `selection-mismatch`：target selection 指向 source task；
  - `credit-target-mismatch`：credit 指向 source outcome 而非 target episode。
- focused history/selector/adapter/binding tests：`22 passed`；`py_compile` 通过。

## 代码修正

`append_history_after_credit` 现在对同一 assignment+later outcome 的重复调用返回显式 `NOOP`，不增加 seal/entry；若同一 assignment 绑定不同 later lineage 仍拒绝。该修正是方法合同的幂等性要求，不是对实验结果的放宽。

## 结论与边界

这一步关闭了 canonical ledger provenance、candidate/version/registry/read-cut/arrival/selection/credit lineage 和 exactly-once 的零调用工程门。它仍不是真实 recipient/API 结果：没有独立 live histories、later-use quality/cost、same-information baseline parity、第二 structural root、实时 update p50/p95、drift/forgetting 或 AAMAS 科学结论。下一步可固定公共 feature/menu/arrival/cost，先做 baseline parity qualification；真实 API/A800 仍需后续独立放行。

`goal_change_requested=false`。
