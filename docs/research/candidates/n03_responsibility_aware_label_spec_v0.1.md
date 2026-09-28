# N03 candidate: responsibility-aware label specification v0.1

状态：`CANDIDATE_NOT_ACTIVE`。这是对 v3 真实链路暴露问题的可执行设计，尚未替换
`docs/research/canonical/` 中的生效方法文档，也不改变 Goal。

## 目的

让 situated recipient judgment 只有在缺陷能够归因到 producer 责任边界时，才进入
producer role evidence。recipient 自己的 integration、sink adoption 或无法定位的混合
修改必须保留为观察结果，不能被压成 producer 的 0/1 标签。

## 原始输入

每个 episode 只使用已存在的 operator-held 证据：

- `O`: ownership contract，给出互不相交的 `P`（producer-owned paths）、`R`
  （recipient-owned paths）和 `S`（read-only support/sink paths）；
- `D`: selected delivery 的 artifact digest 与 source snapshot；
- `Qp`: producer contract scorer 的 status、coverage、decision 和 check lineage；
- `J`: recipient 的结构化 judgment，必须含 `target_role`、`target_paths`、
  `defect_type`、`observed_artifact_sha256` 和 evidence references；
- `A`: validated consumer action，含 changed paths、input/output digest 和 action type；
- `Y`: terminal outcome 与 adoption scorer 的完整性；
- `L`: later-use/independent contract evidence（若任务定义了该检查）。

自由文本 rationale 只能作为审计材料，不能单独生成标签。

## 资格函数

令 `C_P = changed_paths ∩ P`、`C_R = changed_paths ∩ R`。producer feedback 的
资格不是质量分数本身，而是一个门控：

```text
eligible_P = complete(Qp) ∧ complete(Y)
              ∧ target_role(J) = producer
              ∧ bind(J, D)
              ∧ [C_P ≠ ∅ ∨ valid(L)]
              ∧ C_R = ∅
```

若 `eligible_P` 为真，label 才能由 Qp/L/Y 的预先定义映射产生。否则 label 必须为
`UNKNOWN` 或 `PENDING_ATTRIBUTION`，policy 不更新。

## 必须区分的五种 case

1. **Producer defect**：producer-owned contract check 或 later-use 明确失败，路径和
   digest 可绑定，recipient 没有独立 integration 变更；可产生 producer label。
2. **Recipient-owned integration**：`C_P=∅` 且 `C_R≠∅`。这是 v3 的 case；保留
   judgment/action/outcome，但屏蔽 producer label。
3. **Sink adoption defect**：producer 与 recipient contract 通过，而 sink/use 失败；
   归为 adoption 结果，不回写 producer。
4. **Mixed edit**：`C_P≠∅` 且 `C_R≠∅`。除非有预注册的 counterfactual 分解，否则
   标为 UNKNOWN，避免把共同返工成本归给单一角色。
5. **No attributable change**：没有路径或 later-use 证据；不能由“recipient 说需要
   repair”推出 producer defect。

## 下一轮验证门

在任何 policy learning 或 A800 运行前，必须用同一 task root 构造 producer-defect、
recipient-only、sink-only、mixed 和 no-attribution 五类材料，验证 scorer/runner：

- 只给 case 1 eligible producer label；
- case 2–5 全部不更新 producer；
- 所有 case 保留完整 artifact lineage 和 raw judgment；
- 同一材料、候选菜单、随机数与到达顺序下，baseline 和 policy 只差 evidence 是否进入；
- 资格判断通过后，才进入 independent root、重复 episode 和效果实验。

这份规范把 v3 的真实发现转成可测的 gate，仍然不声明方法创新或 benchmark 资格。
