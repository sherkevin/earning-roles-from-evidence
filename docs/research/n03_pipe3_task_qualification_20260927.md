# N03 PIPE3 静态契约夹具与 listed canary

日期：2026-09-27。源码固定为 `TeamBench@d185aef1916fd86a9ba554d581fd256319a973af`。
本记录是无 LLM 的工程前置检查，不是 benchmark 结果、真实 agent 运行资格或
peer-role 方法效果实验。

原始 v1 结果保留在
[`v1/config.json`](../../experiments/logs/n03_pipe3_task_qualification_20260927/config.json)、
[`v1/raw.jsonl`](../../experiments/logs/n03_pipe3_task_qualification_20260927/raw.jsonl)、
[`v1/summary.json`](../../experiments/logs/n03_pipe3_task_qualification_20260927/summary.json)。
收窄后的 v2 结果在
[`v2/config.json`](../../experiments/logs/n03_pipe3_task_qualification_20260927_v2/config.json)、
[`v2/raw.jsonl`](../../experiments/logs/n03_pipe3_task_qualification_20260927_v2/raw.jsonl)、
[`v2/summary.json`](../../experiments/logs/n03_pipe3_task_qualification_20260927_v2/summary.json)。

## v2 做了什么

脚本生成 seed 0/1/2，检查 TeamBench pin、文件集合、producer/recipient 写权限、支持
文件、hidden path deny-list，并构造了**静态 actor payload schema 与 digest**。同时保留
一个明确标记为 fixture 的六事件顺序检查，以及已有的列出的文件/网络/fork/资源访问
canary。运行前写入 config；本轮 `llm_calls=0`、`gpu_jobs=0`、没有 pytest/native
grader/network。

| 字段 | v2 结果 | 含义 |
|---|---:|---|
| `task_contract_passed` | true | TeamBench pin、seed 文件和写权限静态检查通过 |
| `ledger_fixture_passed` | true | 新建的顺序夹具通过，不是真实 ledger replay |
| `listed_isolation_canary_passed` | true | 列出的访问/资源检查通过 |
| `task_text_scientific_qualified` | false | 原始 spec/brief/source 出现 Bug 1/2/3、Fix、Planner 等 oracle 词 |
| `contract_fixture_preflight_passed` | true | 仅表示上述三项静态工程检查通过 |
| `real_agent_preflight_verified` | false | 没有真实 payload dispatch、隐藏 scorer 或 IPC 可见性证明 |
| `benchmark_qualified` | false | root split、真实评分和责任证据仍未完成 |
| `scientific_claim_allowed` | false | 不允许 discovery/attribution/效果主张 |

## 结论边界

这轮不能声称“hidden tests/expected 已被真实 agent 隔离”，只能说静态 payload 设计
记录了预期边界。`validate_ledger` 每次都会新建 placeholder events，因此不能声称
真实事件的 exact-once、lineage、propensity、异常路径或 watermark 已验证。listed
canary 也不等于 production sandbox，且没有解决候选与 native scorer 同进程的问题。

审查还发现任务文本把三个 bug 和修复方向直接告诉了 agent；所以 PIPE3 当前只能作为
协议/修复流候选，不能作为 discovery 或 situated responsibility attribution 的数据。
在删去这些 oracle、实现真实 export adapter/payload、隐藏 scorer 与 operator ledger
的独立进程边界、完成真实 ledger replay 和多事件异常覆盖之前，不启动 PIPE3 LLM
小流，不冻结 PeerRoleBench-TB，不启动 A800。

本结论由 [ADR 0024](../user/decisions/0024-narrow-pipe3-preflight-conclusion.md)
取代了 ADR 0023 中过宽的措辞；历史 v1 运行目录不改写。

## 后续材料适配器检查

为修复这个具体问题，新增了
[`peerrolebench_pipe3_material_adapter.py`](../../scripts/peerrolebench_pipe3_material_adapter.py)。
它不改写 TeamBench checkout，而是在本项目的边界内生成中性任务说明，移除公开源码
中的解释性注释/文档字符串，保留可执行接口、producer/recipient 写权限和支持文件，
并把 payload digest 写入 manifest。零 LLM 的三 seed preflight 记录在
[`v1`](../../experiments/logs/n03_pipe3_material_preflight_20260927/) and the corrected
[`v2`](../../experiments/logs/n03_pipe3_material_preflight_20260927_v2/) runs record this
preflight.

该适配器 v2 的 `material_preflight_passed=true` 只说明材料构造没有发现 oracle 文本、
hidden path 或 expected bug-id 元数据泄露；`runtime_dispatch_verified=false` 仍然成立。
候选进程实际能看到什么、operator ledger 和 hidden scorer 是否在独立边界内，必须由
下一版真实 runner 的 IPC/可见性 probe 证明。
