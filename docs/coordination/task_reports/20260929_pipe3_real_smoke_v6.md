# 2026-09-29 PIPE3 real smoke v6

- 状态：`COMPLETE_PENDING_ATTRIBUTION`
- 真实 API：3 次；GPU：0；policy update：0；`scientific_claim_allowed=false`
- 卡片：[n03_pipe3_real_smoke_v6.json](/Users/jingwu/work/earning-roles/configs/aamas2027/n03_pipe3_real_smoke_v6.json)
- 证据：[n03_pipe3_real_smoke_20260929_v6](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_real_smoke_20260929_v6)

## 真实结果

`内部/qwen3.8-max` 在 thinking disabled、temperature 0、无重试条件下完成 producer、
judgment、consumer 三次 HTTP 200/end-turn 请求。用量为 3,401 input tokens、1,506
output tokens，另有 1,024 cache-read tokens；墙钟时间约 28.17 秒。Qp、Qr 和 adoption
三个独立 scorer 均为 PASS、quality 1.0、coverage/decision complete。

consumer 严格 envelope 也通过；它实际修改了 `processor.py`，validated action 的
`changed_paths=["processor.py"]`，delivery digest 与 action input digest 绑定。

## 责任 gate 的实际判定

模型首次在真实 judgment 中返回了结构化归因字段：

```json
{
  "target_role": "recipient",
  "target_paths": ["processor.py"],
  "defect_type": "recipient_integration"
}
```

它明确说明 producer.py 看起来正确，而 recipient 自己的 processor.py 存在 latin-1
编码和 envelope 问题。operator-side gate 因而输出：

```json
{
  "producer_feedback_status": "PENDING_ATTRIBUTION",
  "producer_feedback_eligible": false,
  "policy_update_allowed": false
}
```

terminal outcome 已记录为 adoption PASS，但没有写 `role_evidence_update`。ledger 保留
selection、task start、delivery、Qp、judgment、action、outcome 七个事件；回放状态是
`UNKNOWN`，原因是严格协议仍把 role evidence 作为完整 replay 的必需阶段。该 UNKNOWN
是有意表达“终局完成、学习更新待归因”，不是运行崩溃。

## 结论边界

v6 首次在真实 LLM 链中同时验证了结构化责任判断、delivery-aware consumer envelope、
recipient-owned repair 和 producer update 屏蔽。它没有证明 peer selection、角色形成、
性能提升或成本下降；仍没有 later assignment、独立 root、同信息 baseline 或统计重复。

下一步应解决协议层的 `role_evidence_update` 与 attribution sidecar 分离，使
`COMPLETE_PENDING_ATTRIBUTION` 能被严格 replay 表达为合法终局状态，然后再构造真实
producer-defect 对照。Goal、benchmark、baseline 和创新标准均未降级。
