# 2026-09-29 PIPE3 real smoke v5

- 状态：`UNKNOWN`（模型返回 envelope；runner 使用错误的 required-path 集合）
- 真实 API：3 次；GPU：0；policy update：0；`scientific_claim_allowed=false`
- 卡片：[n03_pipe3_real_smoke_v5.json](/Users/jingwu/work/earning-roles/configs/aamas2027/n03_pipe3_real_smoke_v5.json)
- 证据：[n03_pipe3_real_smoke_20260929_v5](/Users/jingwu/work/earning-roles/experiments/logs/n03_pipe3_real_smoke_20260929_v5)

consumer 已返回唯一的 `source_files` envelope，但其中包含 selected delivery 后的四条
公共路径（包括 `producer.py`）。runner 当时错误地从 recipient 初始 material 读取三条
路径，于是把合法四文件快照误判为“路径不匹配”。没有进行猜测性接收，也没有 action、
outcome 或更新。该错误属于 runner，不属于模型；v5 输出保留，不重跑。

修复是让 parser 绑定 `prepare_pipe3_action` 产生的实际 `action_payload["source_files"]`
集合，并创建 v6 新卡。Goal 和科学准入标准未降级。
