# 多条 peer history 反例与 scope 隔离 qualification

日期：2026-10-04
状态：`QUALIFIED_OFFLINE`（工程门通过；不产生科学效果结论）

## 目的与运行边界

本任务针对审查指出的四个协议缺口：单条 arrival 负例不等于合法 permutation、candidate 与 projection 错配、projection 聚合篡改、跨 role/state scope 泄漏。构造两条合法 history entry（不同 assignment/arrival，且属于不同 scope），使用同一 test-only selector 做五个零调用 cell。0 LLM/API、0 GPU，不执行 target task，不改变 Goal、active method、benchmark 或 baseline。

运行前先写配置，运行中保存每格 snapshot/exception/digest/raw JSONL，运行后保存逐格 summary 与总 summary；失败的 v1 不删除。

## 结果

正式回执：`experiments/logs/n03_peer_history_adversarial_qualification_20261004_v3/`（clean commit `e7664a6`，配置记录 component hashes 与空 worktree）。v1 首次运行失败、v2 修复回执均保留在同名目录。

| cell | 结果 | 证据 |
|---|---|---|
| `valid-two-entry` | PASS | 2 条 entry、2 个 scope 按 arrival 顺序 replay；projection/input 可重放，target scope 的 propensity `0.5825702065` |
| `permuted-two-entry` | UNKNOWN | 交换两条合法 entry 后重算 snapshot digest，`ValueError: history entries must be append-only in arrival order`；无 selection/update |
| `candidate-mismatch` | UNKNOWN | 请求 `peer-b@v1` 读取 `peer-a` history，`ValueError: history projection candidate does not match history agent`；无 selection/update |
| `projection-rate-mutation` | UNKNOWN | 修改 snapshot scope rate 后重算内部 digest，`ValueError: peer history aggregate mismatch`；无 selection/update |
| `scope-isolation` | PASS | 改变不匹配 scope 的 rate 后，目标 scope 的 scores/probabilities/chosen/propensity 完全相同；仅 projection/input digest 改变并被记录 |

总结果 `QUALIFIED_OFFLINE`, `passed=true`, `scientific_claim_allowed=false`；五格 `update_count=0`。focused history/selector/adapter/binding tests：`21 passed`；`py_compile` 通过。

v1 暴露两个实现错误并保留原始目录：scope isolation 误比较包含 digest 的完整 selection，且 snapshot `scopes` 实际为 dict。v2 修正为比较 decision fields，并按 dict values 修改 scope 后通过；v3 在 clean commit 上复跑并作为正式回执。该修复没有放宽 replay 或 selector 的拒绝条件。

## 结论与边界

现在可以确认 history store 对合法多条 arrival 顺序、candidate identity、aggregate 完整性和目标 scope 读取有可重放的 fail-closed 边界。仍不能推出 peer suitability、专业化、自进化、later-use 质量/成本、实时训练、遗忘或 AAMAS 效果。

下一步仍需把 projection provenance/receipt 认证绑定到真实 independent live history；随后再按 benchmark gate 解决第二 structural root、same-information baseline parity、later-use precision 和完整成本。A800 继续关闭。

`goal_change_requested=false`。
