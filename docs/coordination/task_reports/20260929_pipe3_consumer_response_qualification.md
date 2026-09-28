# 2026-09-29 PIPE3 consumer response contract qualification

- 状态：五格 envelope contract 通过；`consumer_contract_qualified=false`
- 真实 API：0；GPU：0；native grader：0；科学 claim：禁止
- 证据：[n03_pipe3_consumer_response_qualification_20260929_v1](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_consumer_response_qualification_20260929_v1)

针对 v4 的裸字典失败，新增严格 parser，要求 response 顶层只有 `source_files`，路径集合
必须与 operator-prepared action payload 完全一致，所有值必须是文本。五个零调用 case
通过：exact envelope 为 PASS；bare dict、extra metadata、missing path、non-text source
均为 UNKNOWN。该 qualification 只验证 parser 契约，不代表 actor 能力或 benchmark 质量。

随后 v5 真实 smoke 发现 runner 传入了错误的三路径集合，v6 修复为使用 selected
delivery-aware action payload 的四路径集合。历史 v5 保留。
