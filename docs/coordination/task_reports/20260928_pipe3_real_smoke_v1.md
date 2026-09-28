# 2026-09-28 PIPE3 real smoke v1

- 状态：`UNKNOWN`（真实 API 请求成功；producer scorer 不具备完整覆盖，按规则停止）
- 对应 Goal：ER-G1、ER-G3、ER-G4；不是科学效果实验
- `goal_change_requested=false`
- 真实 API：1 次；GPU：0；角色 policy update：0；`scientific_claim_allowed=false`

## 冻结卡与运行

卡片：[n03_pipe3_real_smoke_v1.json](/Users/jingwu/work/earning-roles/configs/aamas2027/n03_pipe3_real_smoke_v1.json)
固定了 TeamBench commit、PIPE3 seed 0、`内部/qwen3.8-max`、thinking disabled、一次
episode、最多 3 次请求、无重试和 scorer UNKNOWN 即停止。运行前写入了 config、材料
manifest 和 ledger。

完整原始证据：[n03_pipe3_real_smoke_20260928_v1](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_real_smoke_20260928_v1)

API 请求实际结果：HTTP 200、`end_turn`、无 thinking delta、1002 input tokens、208
output tokens、4.3295 秒。模型返回了结构正确的 producer.py；随后独立 Qp worker
transport 完成，但 coverage 不完整。

## 失败原因

Qp v1 的 P2/P3 使用 `probe` 作为 `UserEvent.action`。PIPE3 公开 `models.py` 的
`VALID_ACTIONS` 是 `page_view/click/scroll/purchase`，因此 worker 返回：

```text
P1_import = PASS
P2_iso_serialization = UNKNOWN (ValueError: Invalid action: probe)
P3_batch_output = UNKNOWN (ValueError: Invalid action: probe)
```

按照冻结卡，Qp coverage 不完整时没有生成 recipient judgment、consumer action、terminal
outcome 或 role evidence，也没有 policy update。该结果不能解释为 producer FAIL，也不能
解释为模型能力结果；它是 scorer/fixture contract 缺陷。v1 运行不重试、不回写。

## Goal 对照

| 标准 | 状态 |
|---|---|
| 使用真实 LLM/API 并保存原始响应 | 满足本次接入门 | raw SSE、parsed response、cost、request metadata 已保存。 |
| 真实 recipient judgment→action→outcome 链 | 未满足 | 在 Qp UNKNOWN 前按规则停止。 |
| producer/recipient 责任归因 | 未满足 | 无合法 Qp label，不能生成 evidence。 |
| benchmark/baseline/方法效果 | 未满足 | 该卡是 integration-only smoke，不能支持任何科学结论。 |

## 修复决定

不能修改 v1 的历史输出。下一步创建 versioned Qp scorer v2，让测试事件从公开模型的
合法 action 集合中确定性选择，并先做零 API mutation qualification；只有 v2 scorer 的
覆盖、digest 和 UNKNOWN 语义通过后，才考虑新的 v2 real smoke。Goal、benchmark、baseline
和方法创新标准不降级。
