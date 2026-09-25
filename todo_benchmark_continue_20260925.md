### 2026-09-25 · ArtifactRole-TB two-task vertical slice
- [doing] 2026-09-25 将 TeamBench 的两个任务接入 producer → recipient judgment → consumer action → terminal grade → delayed evidence → later assignment 的最小 runner；先跑 deterministic fixture，再跑真实 `内部` API。备注：只验证协议与因果顺序，不把两任务当作方法效果。
  - [done] 审计 TeamBench generator、grader、隐藏信息边界和可归因 artifact 快照；发现 native grader 不是安全 benchmark 协议，已写入 `docs/research/peer_role_protocol_causality_audit_20260925.md`。
  - [done] 实现 append-only JSONL runner 与四个最小条件：random、static、terminal-only、recipient-judgment；加入 fresh evaluator workspace、source allowlist、test/expected hash 审计。
  - [done] 运行 zero-LLM vertical-slice fixture：16 episodes，strict ledger、artifact lineage、test/expected hash 全通过；结果仍标记 `scientific_claim_allowed=false`。
  - [done] 运行真实 `内部` API：修正 TLS transport 后用 curl direct 完成真实 qwen3.8-max judgment；256 input / 700 output tokens，原始响应和本地 postprocess 修正均记录。
  - [doing] gate 结论：暂不投 A800。先补 full sandbox/任务数量/held-out split，再决定是否扩大实验；当前 runner 明确报告三项阻塞原因。
