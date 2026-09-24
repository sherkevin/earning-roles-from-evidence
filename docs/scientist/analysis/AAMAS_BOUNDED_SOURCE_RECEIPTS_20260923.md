# A0 后续实验的有界公开来源回执（未接入冻结 v4）

2026-09-23。A0 v4 的 `2a163ab_1` 第 6 步出现 55 次 `venmo.show_social_feed` 公开 GET。原控制器逐次把每个响应的前 12,000 字符放入下一轮提示，使来源回执达 406,234 字符、下一请求达 553,677 JSON bytes；两次同请求均超时。长度是明确的控制器缺陷，但不能单独证明超时原因。原始 [v4 报告](../../../artifacts/experiments/aamas2027/peer_judgment_a0_v4_20260923/report.md) 和执行源码保持原样。

独立辅助模块 [aamas_bounded_source_receipts.py](../../../scripts/aamas_bounded_source_receipts.py) 提供三个纯函数：

1. `bounded_observation_feedback(observation, new_calls, sources, producer_world, secrets.scrub, max_bytes=4096)`：给模型一条最多 4096 UTF-8 bytes 的 JSON 反馈。它包含经过脱敏的原生观察摘要、精确来源数量、可验证的连续来源 ID 范围（仅在无缺口时）、前后少量来源 ID/类型/API/响应哈希；不复制 55 个响应正文。被省略的内容明确标为不能作为证据。
2. `source_index_page(new_calls, sources, producer_world, secrets.scrub, offset=0, limit=8)`：按原调用顺序给出有界的来源 ID、类型和哈希页。对于第 6 步 55 个来源，可分页列全。
3. `lookup_public_source(source_id, path, sources, producer_world, secrets.scrub)`：按来源 ID 和 JSON Pointer 取真实、完整且脱敏的公开值；只在值完全装入预算时返回可复制的 `{kind, source_id, path, value}`。过大的值只返回 `requires_narrower_pointer`，不把截断字符串冒充证据。它校验世界、公开 GET 类型、记录的响应 SHA256 与值一致。

未来新版本 runner 的接法：先由现有 `api_guard` 将每个调用的**完整脱敏响应**写入 `public_api_call` 原始 JSONL、登记 `sources`，再记录原生 `environment_observation`，然后用 `bounded_observation_feedback(...)` 构造下一条模型消息；不得反过来用有界消息代替原始日志。控制器需要另加显式、只读的 `source_index_page` / `lookup_public_source` 请求入口，返回结果也要写日志并计入模型调用/令牌与交互预算。生产者提案仍按现有 `source_ref` 验证器针对原始 `sources` 检查，而不是针对文本摘要检查。消费者世界不应访问生产者 `sources`，除非协议明确允许交付及其公开引用。

零 LLM 确定性测试为 [test_aamas_bounded_source_receipts.py](../../../scripts/test_aamas_bounded_source_receipts.py)。它重放冻结的真实原始日志：56 次调用中 55 个可引用 GET、完整响应合计超过 300 KB；新反馈为 **3274 UTF-8 bytes**，在 4096-byte 上限内。7 个分页请求列全 55 个 ID，末页 `/0/transaction_id` 精确取值与原始日志及响应 SHA256 相符，日志文件哈希保持不变。测试另覆盖不连续 ID 不生成虚假范围、值超限不生成 `source_ref`、跨世界拒绝和凭据脱敏。运行：`PYTHONPATH=scripts python3 -m unittest -v scripts.test_aamas_bounded_source_receipts`。

边界：该模块只消除**回执/观察反馈**的单轮无界复制；历史消息数量、模型自行打印的大量内容、模型推理预算、provider 120 秒超时和任务本身难度仍可能使后续请求失败。它尚未接入任何真实 LLM 新实验，也没有提高完成率、任务质量或角色学习效果的证据。若后续接入，需另冻新协议、配置及 runner，做零 LLM 原生 fixture 和真实 provider 健康检查，再按预定停机规则运行；不得修改已执行的 v4 文件。
