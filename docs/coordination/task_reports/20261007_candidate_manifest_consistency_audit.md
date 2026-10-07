# Candidate benchmark manifest consistency audit

日期：2026-10-07
状态：`BLOCKED_PRE_EXECUTION / DECISION_REQUIRED`
对应 Goal：ER-G3、ER-G4；不修改 active benchmark，不启动 API/A800。

## 审计目的

在进入任何真实 baseline parity 之前，检查旧的两 root candidate manifest、新的
same-information parity card、C1 bounded live card 和共享 runner 是否描述同一个实验。
如果它们不一致，直接运行其中任何一个配置都会让 development/confirmation split、
strongest control 或 arm coverage 失去可解释性。

## 机器审计结果

审计脚本为
[`peerrolebench_candidate_manifest_consistency.py`](../../../scripts/peerrolebench_candidate_manifest_consistency.py)，
配置和回执在
[`n03_candidate_manifest_consistency_20261007_v1`](../../../experiments/logs/n03_candidate_manifest_consistency_20261007_v1/)。
修复一次 Python 3.9 的动态 dataclass 导入问题后，2 个测试通过；审计按预期以退出码 2
报告 `BLOCKED_PRE_EXECUTION`，不是测试失败。

发现三项真实冲突：

1. 旧 manifest 将 `DIST1_queue_race` 设为 development、`PIPE3_stream_processing` 设为
   confirmation；新的 parity card 将 PIPE3 设为当前 development candidate，并没有确认 root。
2. 旧 manifest 使用 context-only `contextual_trust`；parity card 要求消费相同公共
   `phi/menu/read-cut/arrival/propensity` 的 `contextual_trust_linear`，两者不能合并成一个
   strongest baseline 名称。
3. C1 live card 只有 `no_update/contextual_trust_linear/RARE`，还没有
   `uniform/raw_acceptance/terminal_only/pooled_controller`，所以 C1 不能直接冒充完整
   parity matrix。

共享 runner 的候选七臂注册已经完成，但这只说明代码可接受这些 arm，不能填补 C1 的
真实 source adapter、later-use 和成本缺口。Meta-Team-L2-public 仍保持显式 `NO-GO`，没有
被审计误报为缺失，因为 parity card 已列出该行。

## 对 benchmark 选择的客观结论

目前不能同时声称“DIST1 是 development、PIPE3 是 confirmation”以及“PIPE3 是当前
primary parity candidate”。需要在激活前共同收敛为一个唯一版本。证据上，PIPE3 已有
责任 scorer、recipient action/adoption 和真实 API 开发材料；DIST1 的原生 grader 不执行
真实 consumer，且之前暴露 priority 覆盖盲点。因此若目标是先获得可识别的 situated
judgment→later assignment 闭环，较强的候选方向是：

- 暂把 PIPE3 作为 development parity candidate；
- 不把它直接写成 confirmation root；
- 另行选择并事前封存一个真正不同的 structural root（PIPE1 或修复后的 PIPE2），作为
  confirmation；
- 在 PIPE3 的完整八行合同中补齐四个 C1 缺失的 baseline adapter，再谈真实 API。

这是一项 benchmark split 决策，不在本审计中擅自修改 active manifest；旧 manifest 和新
parity card 均保留，避免覆盖历史判断。

## 与三份标准的关系

- 故事线：要求证明评价改变未来责任分派；split 不清时无法解释“未见任务”收益。
- 方法论：`contextual_trust_linear` 是同信息对照的必要条件；旧 Beta arm 不能替代它。
- Benchmark + baseline：当前 `baseline_frozen=false`，G3/G4/G5 仍开放。

可复用产出是一个执行前 consistency gate。任何后续 live card 必须先让该审计返回
`CONSISTENT_CANDIDATE`，再申请新的真实 API 预算。
