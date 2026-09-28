# 2026-09-28 PIPE3 candidate registry boundary

- 状态：`DONE`（身份层工程子门）
- 对应 Goal：ER-G1（选择与后续责任可归属）、ER-G2（可回放的在线更新输入）、ER-G4（证据与主张一致）
- `goal_change_requested=false`
- 真实 LLM API：0；GPU：0；scientific cell：0

## 要解决的问题

原生 `PeerSelection` 只保存 `candidate_id`，而 policy sidecar 的
`CandidateRef` 还需要 `candidate_version`。如果模型、提示词、可写权限或源代码改变
后仍复用同一个 ID，后续的反馈就无法判断它针对的是哪个实际 agent 版本。仅记录一个
字符串 ID 会让版本漂移、责任归因和历史重放混在一起。

## 实现

新增 `scripts/peerrolebench_candidate_registry.py`，提供四个受限操作：

1. `CandidateRegistryEntry` 强制记录 `candidate_id`、`candidate_version`、
   `source_digest`、`model_id` 和 `model_config_digest`；源和配置 digest 必须是
   小写 SHA-256，不能用占位短值；
2. `validate_registry()` 检查非空、ID 唯一、`id@version` 唯一以及与预注册菜单完全
   一致，并按 candidate ID 产生稳定 canonical 顺序；
3. `registry_digest()` 对 canonical registry 产生配置/证据 digest，列表输入顺序不
   影响该 digest；
4. `candidate_refs()` 只允许从已验证 registry 将 native ID 映射为
   `CandidateRef(id, version)`，未知 ID 或重复菜单直接拒绝。

测试 `tests/test_peerrolebench_candidate_registry.py` 覆盖 canonical digest、版本映射、
重复 ID、未知 ID、非法 digest 和版本变更。定向集合（registry、assignment manifest、
event-time qualification）共 `13 passed`，并通过 `py_compile` 与 `git diff --check`。

## 解释边界

这是身份与版本的必要前置门，不是 candidate 能力差异、peer role learning 或效果证据。
当前 registry 还没有把 prompt/material adapter、allowed writable paths 和 actor payload
digest 纳入 entry；这些字段必须在真实 runner card 中以不可变快照补齐。初始同构 agent
不能借 registry 预置专家差异；若 source/model 配置发生变化，应生成新版本并在 card
中明确记录。

## 对 Goal 的判断与下一步

- **满足一个工程子门**：native ID 到 versioned sidecar identity 的映射现在有可执行
  的拒绝规则和稳定 digest。
- **仍未满足**：PIPE3 真实 runner、global arrival schedule、native/auxiliary 双回放、
  responsibility-aware feedback、强 same-information baseline、真实 API 和 A800
  scientific cells 都没有启动。

下一步实现版本化 `peerrolebench_pipe3_real_runner_v1.py` 的最小 runner boundary：
冻结完整 registry/material/card，使用同一 offer、candidate 顺序、RNG 和 arrival schedule
运行 policy 与 comparator；在 native selection 封存后再建立消费 attestation，并分别回放
native sidecar manifest 与 assignment auxiliary manifest。任何 Qp/判断/action/outcome
出现 UNKNOWN 时只保留审计链，不更新 policy。
