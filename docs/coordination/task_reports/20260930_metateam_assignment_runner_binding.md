# Meta-Team profile offer → next selection binding qualification — 2026-09-30

## 结论

完成了 assignment offer/consumption attestation 到下一次 selection 的 zero-call runner
boundary。`bind_assignment_to_selection` 现在检查：

- attestation 与 offer 的 `offer_id`/`offer_digest` 一致；
- assignment decision index 与后续 selection 的 `task_index` 一致；
- 后续 selection 的 candidate menu 与 offer 完全一致；
- selection 的开始时间不早于 profile read-cut。

因此 profile watermark 和 candidate menu 可以在执行前绑定到下一次选择对象。这个结果仍
不是隔离 policy-read trace：诚实 runner 可以生成 attestation，恶意 policy 仍可能伪造它。
没有调用 API/LLM/GPU，也没有执行下一次真实 agent episode。

## 证据

- 新增 boundary：`bind_assignment_to_selection(...)`
- 定向 profile/offer 测试：**15 passed**
- 完整 `test_peerrolebench_*.py`：**280 passed**
- 最终 qualification：14 个语义检查均为 `PASS`
- 回执：[`experiments/logs/n03_metateam_public_profile_qualification_20260930_v12/`](../../../experiments/logs/n03_metateam_public_profile_qualification_20260930_v12/)
- v11 的 candidate-menu fixture mismatch 失败保留在
  `experiments/logs/n03_metateam_public_profile_qualification_20260930_v11/failure.json`；
  该失败说明 boundary 确实拒绝了不一致 menu，而不是把错误 fixture 当作通过。

## 仍未关闭的门

下一步必须在 versioned PIPE3 runner 中把这一绑定放进真正的 selection→task-start 边界，
并在隔离 policy 进程中记录可重放的 input digest；同时要运行真实 profile generator，
把摘要模型调用、token、延迟和错误作为完整成本。当前只验证了一个 material fixture 和一条
合法 profile，不能支持 later-use、quality/cost、独立 history 或 closest-baseline 效果结论。
Meta-Team-L2-public 继续保持 `NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`，baseline 继续
`NOT_FROZEN`，不启动正式 API/A800。
