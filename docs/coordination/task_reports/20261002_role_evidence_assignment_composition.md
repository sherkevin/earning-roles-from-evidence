# Public judgment assignment 接入 canonical composition — 2026-10-02

状态：`QUALIFIED_OFFLINE`（工程接缝）；不是 benchmark、baseline 或科学效果结果。
本任务没有调用 LLM/API、没有 GPU/Nebula 作业，也没有修改 Goal。

## 做了什么

把 `role-evidence-judgment-beta-v1` 作为 `assignment_mode="public_judgment"` 接入
PIPE3 two-stage canonical composition。默认 `hand_authored` 路径保持不变；新路径在
同一个 source-bound `RoleEvidenceOffer` 上先计算公共 judgment score，再执行既有的
isolated read → `LaterAssignment` → exact selection commit。runner 版本从 v1.3 升到
`pipe3-two-stage-composition-v1.4`，并把 scorer 源码 hash 与 score `input_digest`
写入回执，避免新旧语义共用一个版本号。

## 回执

- v2 是版本递增前的历史回执，保留在
  [`n03_role_evidence_assignment_composition_20261002_v2`](../../../experiments/logs/n03_role_evidence_assignment_composition_20261002_v2/)，不能替代后续版本；
- v3 是版本化后的主回执：
  [`n03_role_evidence_assignment_composition_20261002_v3`](../../../experiments/logs/n03_role_evidence_assignment_composition_20261002_v3/)；
- `producer_owned`：`QUALIFIED_OFFLINE`，完成 source evidence、isolated public read、
  assignment-before-selection、target execution 和 delayed terminal update；
- `recipient_owned` / `mixed`：`UNKNOWN`，责任门拒绝伪造 producer evidence、assignment
  或 update；
- 三个 control 的 `assignment_mode` 均为 `public_judgment`，runner/policy/source hash
  在 config 中封存；`real_api_calls=0`、`gpu_jobs=0`、`scientific_claim_allowed=false`。

## 失败与修复

第一次接入测试把 `read_cut` 同时放入通用 preview 参数和 public-judgment wrapper，
导致 producer-owned case 在 assignment preview 阶段抛出
`TypeError: ... got multiple values for keyword argument 'read_cut'`；该次运行没有被当作
通过，随后将 read-cut 责任收回 wrapper 并重新执行。修复后的定向回归为 `19 passed`，
版本递增后的 v3 回执才是当前可引用的 qualification。这个失败说明 wrapper 的参数边界
需要独立测试，不能由最终 summary 的状态反推接口正确。

## 这条证据支持什么

它证明公共 judgment comparator 可以进入现有 canonical runner，并保留 assignment-before-
selection 与责任边界。它没有证明 judgment 的预测性、B/C evidence mutation 在真实流中的
因果效果、角色专长、跨 root 迁移、在线训练收益或 quality-cost 改善。

## 下一道门

仍需在同一 runner 中为各 baseline arm 接入各自声明的 feedback channel，完成 B/C 双向
mutation 与 selected-only/UNKNOWN/cost parity；第二 structural root authority 仍等待作者
确认。两道门未通过前不启动正式 live cell 或 A800。
