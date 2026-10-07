# Candidate baseline runner arm registration qualification

日期：2026-10-07
状态：`PARTIAL / QUALIFIED_OFFLINE`
对应 Goal：ER-G3、ER-G4；不冻结 benchmark/baseline，不启动真实 API/A800。

## 发现

parity 候选卡要求的 `contextual_trust_linear` 已在
`scripts/peerrolebench_baseline_policies.py` 中实现，但旧的
`PolicyMatrixRunner` 默认注册表只允许 legacy `contextual_trust`。如果直接用候选卡的
七臂集合调用 runner，会在 policy construction 前被当成 unsupported arm；这会让“同一
runner、同一菜单、同一 replay”无法成为后续 live parity 的起点。

## 修复

在不改动默认 legacy 七臂和历史回执的前提下，新增独立的
`CANDIDATE_EXECUTABLE_ARM_NAMES`：

```text
uniform / no_update / raw_acceptance / terminal_only /
contextual_trust_linear / pooled_controller / RARE
```

共享 runner 现在同时接受 legacy arm 和这组候选 arm。`Meta-Team-L2-public` 没有被伪装成
可执行 policy；它继续作为 parity 矩阵中的显式 `BLOCKED_NO_GO` 行，等待 profile parser、
公开信息边界、assignment consumer、独立 history 和成本合同资格化。

## 零调用资格

配置和源码哈希先写入
`experiments/logs/n03_candidate_runner_arm_registry_20261007_v1/config.json`，然后执行：

- `tests/test_peerrolebench_policy_matrix_runner.py`：18 passed；
- 两 offer 的候选七臂 replay：`PASS`，每臂选择数为 2，所有 snapshot replay equal；
- `py_compile` 和 scoped `git diff --check`：通过；
- 0 API、0 generator、0 candidate、0 GPU、0 policy update。

完整输出、metrics、回执和摘要见同名日志目录。

## 证据边界

这一步只证明候选 arm 可以进入统一离线 runner，并且不会破坏历史 legacy receipt。它没有
证明真实 recipient judgment、producer attribution、later assignment、独立 later outcome、
真实成本、few-shot 泛化或 RARE 优势；`scientific_claim_allowed=false` 保持不变。

下一道科学闸门仍是：封存第二 structural root 和全套 runtime/material/scorer digest，
让七个可执行 arm 在同一条真实 live 流上共享机会和信息；closest published adapter 若
仍不可执行，必须保留 `NO-GO`，不能删掉该行后声称 baseline 完整。
