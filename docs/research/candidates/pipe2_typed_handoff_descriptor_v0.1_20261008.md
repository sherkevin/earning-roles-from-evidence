# PIPE2 typed handoff descriptor（候选 v0.1）

日期：2026-10-08。状态：`CANDIDATE / NOT ACTIVE / ZERO-CALL DESIGN`。

本卡不是对 PIPE2 的 benchmark 选定，也不是对 Scheme B 的方法修改。它解决一个
具体接口问题：PIPE2 的 producer 交付的是 `artifact/extracted_rows.json` 数据工件，
recipient 不会收到 `pipeline/extract.py`；因此源码交接版 observation bridge 不能直接
复用。设计目标是让真实 runner 将 producer provenance、交付工件、recipient 行为和
未来 outcome 分开记录，缺字段时保持 `UNKNOWN`。

## 1. 四个不可合并的对象

| 对象 | 绑定内容 | 能否成为 producer credit |
|---|---|---|
| producer provenance | candidate `id@version`、source digest、model/config digest、producer-owned contract | 只能证明来源，不能单独给分 |
| delivered artifact | path=`artifact/extracted_rows.json`、schema=`pipe2-extracted-rows-v1`、`artifact_sha256`（沿用 `validate_extracted_rows` 的 length-prefixed digest） | 只能证明交付身份 |
| recipient observation/action | J=`accept/accept_with_rework/reject_redo` 在 action 前封存；A=`use/repair/independent_redo`；recipient pre/post manifest 与 ownership scope | noisy observation；不能自动奖励 producer |
| future outcome | later assignment/selection 后新执行产生的独立 Y、成本和 arrival | 只有合法责任规则与完整 lineage 后才可能构成 delayed credit |

`output_sha256`、adoption key sequence、recipient self score 是独立诊断维度，不能重命名
为 J、A 或 Y。

## 2. 候选 descriptor

```json
{
  "schema": "pipe2-typed-handoff-v1",
  "task_id": "PIPE2_data_pipeline",
  "source_task_index": 0,
  "candidate_key": "producer-a@v1",
  "candidate_source_digest": "<producer source manifest digest>",
  "delivery_path": "artifact/extracted_rows.json",
  "delivery_schema": "pipe2-extracted-rows-v1",
  "delivery_artifact_sha256": "<validate_extracted_rows artifact digest>",
  "producer_contract_digest": "<frozen ownership/registry contract>",
  "recipient_before_manifest_digest": "<pre-action recipient files>",
  "recipient_after_manifest_digest": "<post-action recipient files>",
  "recipient_changed_paths_digest": "<operator-sealed diff descriptor>",
  "judgment_id": "<J event>",
  "action_id": "<A event>",
  "outcome_id": "<source completion event>",
  "target_task_index": 1,
  "source_read_cut": 0,
  "observation_available_index": 0
}
```

`candidate_source_digest` 由 registry 绑定 producer provenance；`delivery_artifact_sha256`
由 `validate_extracted_rows` 生成并与 `Delivery.artifact_sha256` 一致。二者必须不同字段，
不能用 root digest 或 synthetic hash 代替。recipient manifest 只能包含其真实可见的
transform/load/support 文件；不得补回 producer source。changed-path descriptor 由
执行器在 action 前后封存，不能从最终 `output_sha256` 反推。

## 3. 必须满足的顺序和投影

```text
selection → task_start → delivery(descriptor)
          → producer score + J sealed → A → source completion
          → typed noisy observation publication
          → neutral completion anchor → preview → assignment → later selection
          → target delivery/action/Y → delayed credit（当前仍关闭）
```

观察 publication 不改持久 selector state；neutral anchor 与 attributable evidence 使用
不同 namespace。assignment 可以引用 native neutral anchor 以满足协议格式，但 public
selector 只能读 observation 的公开字段和同信息菜单/feature/read-cut/arrival/cost；不得
读 hidden expected、private Qp 或 future Y。

三种合法源配对必须保留：

| J | A | 预期 observation |
|---|---|---|
| accept | use | `PUBLISHED`, `producer_credit_allowed=false` |
| accept_with_rework | repair | `PUBLISHED`, `recipient_scope` 单独记录 |
| reject_redo | independent_redo | `PUBLISHED`, `recipient_scope` 单独记录 |

它们都不是 producer label。recipient-only 或 mixed 修改不能直接进入 producer credit；
缺 J/A/Y、资源失败、descriptor digest 错配、late read-cut 和重复事件一律 `UNKNOWN`。

## 4. 同信息 parity 合同

observation、count-only、J-masked 和 terminal-only（若其 outcome 已独立可见）必须共享
同一 candidate menu、candidate registry digest、public feature schema/digest、read cut、
arrival order、propensity stream、state cap 和成本范围。只替换 history payload；不能让
count-only 读到更少的任务或更早的反馈，也不能让 observation 读到更多 private fields。

## 5. 零调用 mutation matrix

在任何真实 API 前，至少执行并记录：artifact path/schema/hash mutation、producer-source
digest mutation、recipient pre/post manifest mutation、J-after-A、assignment-before-
observation、late read-cut、menu/propensity/feature mismatch、duplicate anchor、hidden
expected injection、`output_sha256` masquerading as Y。每个负例都必须是 runner 未启动、
policy update=0、结果 `UNKNOWN/INVALID`，且原始输入留存。

## 6. 当前结论

现有 source-file bridge 的 typed observation 与 neutral-anchor 实现可复用其 namespace、
read-cut、assignment-before-selection、replay 和 fail-closed 语义；不能复用其
`recipient_before[p] == delivered[p]` 源码不变量。实现 descriptor adapter 之前，PIPE2
runtime receipts 不得回放成 observation，更不得进入 selector 或训练。该候选仍需独立
审查与零调用资格化；Goal、active method、benchmark 和 A800 gate 均不变。
