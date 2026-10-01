# Task report — root manifest qualification (2026-10-01)

## 状态

`PARTIAL`。root identity/split/budget 已可封存，正式 live runner 尚未接入；
`goal_change_requested=false`。

## 完成内容

在 [`peerrolebench_baseline_root_contract.py`](../../../scripts/peerrolebench_baseline_root_contract.py)
中加入 `RootRunnerManifest`。manifest 固定 root id、上游 commit、source/generator/scorer
hash、schedule 与 candidate registry digest、seed split、七个 baseline arm 的顺序、RNG
算法、visibility rule 和 episode/API/wall-clock budget，并由 canonical JSON 计算
`manifest_digest`。不满足 64 位 hash、重复/未排序 seed、arm 顺序变化或非法预算时直接
拒绝。

这一步解决了“修复 generator 后仍沿用原 root 身份”的风险：PIPE2 的 A 选项、valid
subset 的 B 选项、MULTI3 的 C 选项或暂缓 D，都必须产生各自新的 manifest；旧 root 的
证据不会被静默重写。

## 验证与证据

证据在 [`n03_baseline_manifest_20261001_v1`](../../../experiments/logs/n03_baseline_manifest_20261001_v1/)。
运行前已写入 config，使用 0 API、0 GPU、`scientific_claim_allowed=false`：

- manifest/root-contract 与 policy-matrix 定向测试：14 passed；
- `tests/test_peerrolebench_*.py`：359 passed。

这是 schema/identity qualification，不是 benchmark freeze、baseline effect 或
root independence 证据。

## 仍未满足的门

manifest 尚未由 live runner 强制消费；目前 schedule prefix 仍由离线 hand-authored
fixture 提供。还缺 canonical ledger → read-cut projection、LaterAssignment→task_start
→later outcome、真实 per-arm costs、independent live histories、closest published adapter
和 confirmation split。因此 scientific readiness 继续为 `false`，第二 root authority
A–D 仍待作者选择，不启动真实 API/A800。

## 下一步

把 manifest 接到 root runner 的启动检查，并让 runner 只从 manifest 绑定的 canonical
ledger 重建 feedback prefix；随后重新运行 baseline parity qualification。此过程不改变
Goal，也不把 manifest 通过写成实验效果。
