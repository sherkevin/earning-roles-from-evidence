# History 跨进程恢复边界卡（零调用）

日期：2026-10-04
状态：`DESIGN_ONLY`

## 目的

`PeerHistoryV2` 当前已经能在同一进程 append、replay 和投影，但 active method 仍未证明进程边界上的持久性。真实 API 之前先验证：E1 产生的合法 history 在进程重启后不会丢失；重启后的 selector 只读恢复后的 public projection；篡改、截断或版本不匹配的快照不会产生选择或 update。

这一步只关闭状态恢复工程门，不验证 peer suitability、实时训练收益、质量/成本收益或 AAMAS 科学结果。它不改变 Goal、active method、benchmark、baseline 或最终 updater。

## 固定输入

- 使用已经通过的 PIPE3 canonical source→target fixture、candidate registry、`history`/`no-history` matched snapshot、相同 read cut、base score 和 RNG seed；不引入新任务根或新标签。
- 父进程在 E1 credit 已提交且 history entry 已封存后写入 `snapshot.json`；子进程只执行 `PeerHistoryV2.replay → selector_projection → test selector`，不读取 ledger、gold、artifact、private scorer 或未来 outcome。
- 每个 cell 使用独立目录和 state namespace；进程间只通过显式 snapshot 文件与 JSONL receipt 交换。

## Cells 与通过条件

| cell | 传给新进程的输入 | 必须满足 |
|---|---|---|
| `restored-history` | 合法 E1 snapshot | parent/child `state_digest`、projection digest、selection input/choice/propensity 完全相等；entry count 保持 1 |
| `restored-empty` | 合法空 snapshot | 与 `no-history` 的 projection、selection 和 propensity 完全相等 |
| `tampered-digest` | 修改 state digest | 子进程非零退出，输出只有结构化 UNKNOWN receipt，不产生 selection/update |
| `truncated-snapshot` | 删除 entries/scopes 或缺字段 | 同上；不能回退成空历史 |
| `wrong-version` | 修改 schema/version | 同上；不能按旧版本宽松读取 |

每个 cell 预注册 `snapshot_sha256`、snapshot bytes、parent/child state/projection/input digest、child pid/exit code、wall time、update count、完整 cost schema、UNKNOWN reason 与组件 SHA-256。`restored-*` 的 equality 是字节/字段级断言；负例必须保留 raw stderr/stdout。

## 预算与停止规则

预算为 0 LLM/API、0 GPU、只允许本机 Python 子进程和文件读写。任一恢复 equality、版本拒绝、UNKNOWN 或 digest 记录缺失即整批 `FAILED_OFFLINE`，保留失败目录并停止，不扩大 timeout、不接真实 API。

## 通过后的下一步

只有该门通过，才把 `PeerHistoryV2` 接入独立 episode stream 的持久 namespace，并让同一 selector 在 E2 读取恢复状态；仍需在真实 API 前完成 independent histories、same-information baseline parity、第二 structural root 和完整 cost ledger。

`goal_change_requested=false`。
