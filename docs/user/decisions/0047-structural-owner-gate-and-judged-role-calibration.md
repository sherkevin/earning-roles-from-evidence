# ADR 0047 — 用结构化责任 owner 决定 evidence 资格，保留 judged role 做校准

日期：2026-10-06  
状态：Accepted  
范围：ArtifactRole 的 source responsibility gate 与后续 live comparison

## Context

C1 v3 的真实 API 追踪显示，同一个结构化 source artifact 在不同 policy arm 中得到的
`target_role` 文本可能不同。若把模型生成的自由文本角色直接作为资格硬条件，一个 arm
会被随机排除；但若完全相信模型角色，又会把 recipient-owned 或 mixed work 错归给
producer。需要把可审计的责任 owner 与带噪声的模型描述分开。

## Decision

采用方案 A：`structural_owner_role` 由冻结 task contract、candidate registry、changed
paths、独立 producer check 和预注册 defect/quality 事件在父进程中推导；模型返回的
`target_role` 与 `target_paths` 只作为原始 judged observation 和校准字段。判断不一致
必须记录 `judged_role_agrees=false`，但不能单独创造或取消 producer evidence。

只有结构化 owner 为 producer、交付/使用/contract check/artifact binding 完整，且没有
recipient、sink 或 mixed ownership 时，source event 才可进入 producer evidence。recipient-
only、mixed、unknown、资源失败、缺字段和非法 replay 仍然是 UNKNOWN/PENDING，不能更新
producer 或 selector。

## Rationale

该切分让责任依据来自可重放的工程事实，而不是某个 arm 的措辞；同时保留 judged role
用于测量 judge reliability、文字歧义和安全边界。A1--A8 zero-call mutation/replay
qualification 必须通过，尤其是 producer owner/judged recipient 的不一致、recipient-only
反例、mixed ownership、重复事件和 contract mutation。

## Consequences

- active method 升级为 `method_v1.2_20261006`，gate versions 为
  `pipe3-responsibility-label-v2-structural-owner` 与
  `two-stage-role-evidence-v3-structural-owner`。
- 旧 receipt 不回写、不重评分；下一张 live card 必须显式携带 structural-owner registration
  并报告 judged-role disagreement。
- 该决议只修复归因资格和校准接口，不证明 producer quality、future assignment、实时训练
  或 self-evolution；independent roots、baseline parity、later-use 和 quality-cost
  confirmation 仍是开放科学门。
