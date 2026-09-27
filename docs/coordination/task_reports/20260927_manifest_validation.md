# Task report：candidate benchmark manifest validation / 2026-09-27

状态：`PARTIAL`；`goal_change_requested=false`。

## Goal 对照

- **ER-G3**：候选 manifest 明确两个结构签名、development/confirmation split、角色文件和同信息 baseline；两个 root 的真实资格仍未通过。
- **ER-G4**：机器校验阻止 baseline、split、私有 scorer 可见性和 API/GPU gate 漂移；没有运行 LLM/API/GPU。
- **ER-G1/ER-G2**：不改变故事线、RARE 合同或 backbone/update 的未决状态。

## 实际动作与证据

新增候选配置 [`n03_benchmark_baseline_candidate_v1.json`](../../configs/aamas2027/n03_benchmark_baseline_candidate_v1.json)、
校验器 [`peerrolebench_validate_manifest.py`](../../scripts/peerrolebench_validate_manifest.py) 和两项回归测试。
校验器只读取 JSON，不加载 TeamBench、不运行 candidate/scorer、不调用真实 API；运行前后配置与输出由测试源码固定。

验证结果：manifest 包含 DIST1 development、PIPE3 confirmation 两个不同 structural signature，
七个 baseline、三个 update comparator、同信息约束以及 `scientific_claim_allowed=false`、
`real_api_runs_allowed=false`、`gpu_jobs_allowed=false`。baseline 缺失或 split 漂移会被拒绝。

静态 provenance 的原始运行见
[`n03_manifest_provenance_20260927_v2`](../../experiments/logs/n03_manifest_provenance_20260927_v2/)。
它发现 DIST1 的原始 generated spec 在 agent payload 中直接出现
`tests/test_concurrent.py` 和 `tests/test_message_loss.py`，这是实际的任务信息泄漏证据，
不是 scorer 或模型失败。随后新增版本化 `dist1-neutral-v1` 材料适配器，保留行为契约、
移除 bug 编号/Planner/隐藏测试名；其修复后的 provenance 见
[`n03_manifest_provenance_20260927_v3`](../../experiments/logs/n03_manifest_provenance_20260927_v3/)，
DIST1 与 PIPE3 的静态 visibility 均通过。v3 只关闭 task-text/material gate，不能推出
runtime dispatch、scorer/ledger IPC 或 benchmark 资格已经通过。

## 结论与下一步

这只是候选 manifest 的工程门，不代表两个 root 已经合格，也不允许启动新的 API 链或 A800。
下一步必须把 manifest 中的实际 source/material/scorer/ledger hash 和权限证据补齐；只有两个 root
的运行资格通过后，才复制一张小批量真实 API card，并在看到 confirmation 结果前保持 split 不变。
Goal v1.0 不变。
