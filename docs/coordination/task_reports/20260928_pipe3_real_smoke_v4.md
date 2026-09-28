# 2026-09-28 PIPE3 real smoke v4

- 状态：`UNKNOWN`（structured judgment 通过；consumer response contract 失败）
- 真实 API：3 次；GPU：0；policy update：0；`scientific_claim_allowed=false`
- 卡片：[n03_pipe3_real_smoke_v4.json](/Users/jingwu/work/earning-roles/configs/aamas2027/n03_pipe3_real_smoke_v4.json)
- 证据：[n03_pipe3_real_smoke_20260928_v4](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_real_smoke_20260928_v4)

## 运行结果

producer API、judgment API、consumer API 都返回 HTTP 200；Qp 在 consumer 前已 PASS。
新的责任 judgment contract 也成功通过，模型返回：

- `target_role=recipient`
- `target_paths=["processor.py"]`
- `defect_type=recipient_integration`
- artifact digest 与 delivery 一致
- evidence refs 指向 artifact/Qp/sink 观察

这正好识别出 v3 暴露的 recipient-owned integration 问题。随后 consumer 返回了
`processor.py/models.py/sink.py/producer.py` 的裸文件字典，没有按 runner contract 包在
`{"source_files": {...}}` 中。runner 严格拒绝该响应，记录 UNKNOWN；因此没有 action、
recipient/adoption scorer、terminal outcome、responsibility sidecar 或 policy update。

## 解释边界

这不是模型质量结论，也不是 producer 失败：它是 consumer response schema 不满足冻结
卡的契约。v4 不能重试或从裸字典猜测字段，否则会破坏可审计的 actor/scorer 边界。原始
SSE、parsed response、cost、ledger 和失败 traceback 全部保留。

## Goal 对照

| Goal 标准 | 状态 |
|---|---|
| 结构化归因字段可被真实模型生成并绑定 artifact | 本次满足 |
| malformed actor output 被识别为 UNKNOWN | 本次满足 |
| 完整 judgment→action→outcome→evidence | 未满足，consumer schema 在 action 前停止 |
| attribution-safe role learning / benchmark effect | 未满足 |

下一步只修复并离线 qualification consumer envelope contract，再决定是否开新的真实卡。
不改变 v4 历史输出，也不降低 Goal 或科学准入标准。
