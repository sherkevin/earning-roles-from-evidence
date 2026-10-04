# History 跨进程恢复边界 qualification

日期：2026-10-04
状态：`QUALIFIED_OFFLINE`（工程门通过；不产生科学效果结论）

## 目的与预注册指标

本任务验证 `PeerHistoryV2` 在进程边界上的持久性，避免把重启后丢状态误判成 selector 或在线更新器的结果。父进程使用已通过的 PIPE3 source→target fixture 写出 history snapshot；子进程只做 `replay → public projection → test selector`，不读取 ledger、artifact、gold、private scorer 或未来 outcome。

每个 cell 记录 snapshot SHA-256/bytes、parent/child state/projection/input digest、child PID/exit code、wall time、UNKNOWN reason、完整 cost schema 和 component hashes。负例非零退出并写结构化 UNKNOWN receipt；不回退为空历史。

## 实现与运行

- 设计卡：`docs/coordination/task_reports/20261004_history_process_boundary_card.md`。
- 子进程 worker：`scripts/peerrolebench_history_process_worker.py`。
- runner：`scripts/peerrolebench_history_process_boundary_qualification.py`。
- `PeerHistoryV2.replay` 现在显式拒绝未知 `version`；此前只检查 schema 的宽松路径被补上测试。
- 配置先写入 `config.json`；每个 cell 另写 bundle、stdout/stderr、child receipt、summary 和 raw JSONL。运行目录：`experiments/logs/n03_peer_history_process_boundary_qualification_20261004_v1/`。

## 结果

formal v1：`QUALIFIED_OFFLINE`, `passed=true`；0 LLM/API、0 GPU、`scientific_claim_allowed=false`。

| cell | 结果 | 关键证据 |
|---|---|---|
| `restored-history` | PASS | child return code 0；state/projection/selection 全部与 parent 相等；entry count 保持 1；probabilities `[0.5825702065, 0.4174297935]` |
| `restored-empty` | PASS | child return code 0；与 parent empty selection 完全相等；probabilities `[0.5,0.5]` |
| `tampered-digest` | UNKNOWN | return code 2；`ValueError: peer history snapshot digest mismatch`；无 selection/update |
| `truncated-snapshot` | UNKNOWN | return code 2；digest mismatch；无空历史回退 |
| `wrong-version` | UNKNOWN | return code 2；`ValueError: unsupported peer history version`；无 selection/update |

所有 cell `update_count=0`。focused history/selector/adapter/binding tests：`20 passed`；`py_compile` 通过。每个 cell 的成本均为 API/GPU/token/tool/update 为 0，另记录 snapshot bytes 和 child wall time。

## 结论与剩余边界

跨进程 snapshot/replay、空状态恢复和版本/完整性 fail-closed 已通过一个可复现的 CPU 工程门。它没有证明跨 episode 的真实独立 history、E2 later-use、peer suitability、policy update、质量/成本收益、实时训练速度或遗忘控制。

仍需补齐：至少两条合法 history 的顺序置换与 candidate→projection 错配负例；projection provenance/receipt 绑定；独立 live histories；same-information baseline parity；第二 structural root；完整 API/cost/UNKNOWN 分母。A800 继续关闭，Goal 不变。

`goal_change_requested=false`。
