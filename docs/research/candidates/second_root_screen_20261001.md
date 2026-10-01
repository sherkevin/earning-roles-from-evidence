# 第二 structural root 候选筛选（candidate，2026-10-01）

## 筛选标准

第二 root 必须与 `PIPE3_stream_processing` 在交付结构上独立，并同时能分出：

- producer 的中间 artifact 与 contract correctness；
- recipient 自己必须执行的后续处理；
- recipient 是否真正使用该 artifact 的 adoption 结果；
- private gold/expected output、native grader 和 operator ledger 的隔离；
- failure/UNKNOWN、成本和 later assignment 的可 replay 记录。

## 候选比较

| 候选 | 结构 | 主要缺陷 | 筛选结论 |
|---|---|---|---|
| `PIPE2_data_pipeline` | Extractor → Transformer → Loader 的三段 ETL；中间 rows 会改变后续输入，seed 只替换 schema/data | upstream brief/spec 直接描述三类 bug；native `grade.sh` 混用静态源码检查、candidate workspace 的 pytest 和 expected output，不能直接作为独立 producer/adoption scorer | **CONDITIONAL-HIGH**：材料/ownership/delivery 资格已通过；下一道是 runtime/adoption scorer，仍未冻结 |
| `MULTI3_polyglot` | Backend serializer → Frontend handler，另有 shared schema | schema ownership 未决；native tests 使用 hardcoded `correct_wire`，不能证明 frontend 使用本次 producer wire；生成器有 sample-record 缺陷 | **CONDITIONAL-LOW**：保留 fallback，不先投入 |
| `DIST4_clock_skew` | Lamport clock 与 ordering 两个模块 | 更像单体修复；没有自然 recipient 使用 producer artifact 的闭环 | **NO-GO** for primary causal extension |

## PIPE2 的可复用切法

保持 TeamBench generator/seed/OS sandbox 不变，新增独立 adapter：

1. producer 只写 `extract.py` 或生成封存的 extracted-row artifact；其 contract scorer
   检查 key-column null 规则和 artifact digest。
2. recipient 只读 producer rows 与 public schema，写 `transform.py`/`load.py`；其 self
   scorer 检查 255 字符规则、列顺序和自身修改范围。
3. sink/adoption scorer 在 parent 侧把 recipient 的真实 output 与 producer artifact
   digest 绑定，区分“producer 正确但 recipient 未采用”“recipient 自己错误”和“双方
   都不完整”。
4. expected output、hidden tests 和 operator ledger 留在 scorer 进程；不能进入 agent
   prompt、public role evidence 或 policy overlay。
5. source episode 完成后才允许发布 native role evidence；later assignment 和 target
   selection 必须沿用当前 `SelectionPlan` 的 preview→assignment→commit 合同。

这会形成与 PIPE3 不同的交付形态：PIPE3 是 queue/priority/streaming execution，PIPE2
是 tabular ETL transformation。两者仍共享责任协议、ledger、selected-only policy API 和
统计分析，但不能把 seed 当独立 root，也不能把 native TeamBench score 直接当 situated
judgment label。

## 当前判定

- `PIPE2_data_pipeline` 只是第二 root 候选，不是已冻结 benchmark；
- 在新增 adapter 通过 source/artifact/adoption/replay qualification 之前，active manifest
  仍保持 `CANDIDATE_NOT_FROZEN`，不启动正式 API/A800；
- 若 PIPE2 的 independent scorer 仍无法隔离 expected output 或真实 recipient use，立即
  保留失败证据并回退到 MULTI3/外部 CooperBench substrate，不修改 Goal。
