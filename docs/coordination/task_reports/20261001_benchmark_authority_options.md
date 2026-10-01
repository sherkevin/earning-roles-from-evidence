# Task report — second-root fixture authority options (2026-10-01)

## 当前事实

- `PIPE2_data_pipeline` 使用 TeamBench commit
  `d185aef1916fd86a9ba554d581fd256319a973af`；generator seed 0–9 中
  `1,4,6,9` 的 source/expected CSV 因未转义逗号产生额外 `None` 字段。
- v2 runtime 在 valid seed 0/2 上通过有限 handoff/scorer qualification；完整 root
  v9 为 `FAILED_OFFLINE`，invalid seed 不发 peer label。
- `MULTI3_polyglot` 的 JSON fixtures 可解析，但 native tests 使用 hardcoded
  `correct_wire/correct_envelope`，没有真实 producer→recipient adoption；sample
  generator、schema contract、seed split 和 prompt oracle 仍未冻结。
- 当前生效 benchmark 计划仍以 `DIST1_queue_race`/`PIPE3_stream_processing` 为 active
  主轨候选；PIPE2 是 conditional next candidate，MULTI3 是 conditional-low fallback。

## 可选路径与硬门

| 选项 | 需要做什么 | 主要收益 | 主要代价/风险 | 进入 active root 的硬门 |
|---|---|---|---|---|
| A. 修复 PIPE2 generator | 在派生、明确版本的新 root 中用标准 CSV writer；重新生成全部声明 seed，固定 source/expected hashes 和 seed split；重跑 material/runtime/adoption/replay | 保留最清晰的 ETL producer→recipient 因果切口，已有 v2 adapter 可复用 | 改变 root hash，不能声称仍是原生 TeamBench fixture；需要明确 derived benchmark authority 和完整重验 | 全 seed shape valid；neutral material；2×2 handoff、lineage、ledger/replay、same-info baseline、independent history 和 later-use 通过 |
| B. 预注册自洽 seed 子集 | 只使用 valid seed `0,2,3,5,7,8`，明确它们是派生子集，不删除失败证据 | 工程成本最低，可继续验证 v2 责任协议 | public seed 0–2 已有 1/3 invalid，样本支持弱；容易被审稿人质疑选择性保留与 root 独立性 | 用户/作者确认 subset estimand；完整 subset manifest、confirmation split、baseline parity、成本和 later-use 通过 |
| C. 转向 MULTI3 | 新写 producer wire→sealed envelope→recipient handler adapter；修 sample bug、schema runtime 校验、seed split 和 neutral payload | 跨模块 artifact 语义更接近 serializer/consumer 协作 | 当前 native oracle 泄漏和 handoff 缺失较多，adapter 成本高；不应把 native pass 当真实协作证据 | 独立 adapter 的 2×2 handoff、完整 lineage、负对照、replay、baseline parity、independent history 通过 |
| D. 暂缓第二 root | 保留 PIPE2/MULTI3 审计，先在现有 active root 完成 baseline/confirmation 资格 | 不引入未经确认的 benchmark 改动 | 延后两 root 的确认实验，主线仍不能宣称跨 root 泛化 | active root 自身达到完整 API、baseline、later-use 和 confirmation 门后再重开 |

## 不允许的捷径

- 不把 valid seed 子集的 v8 结果写成 TeamBench root 的 benchmark 结果。
- 不在未记录新 root hash、source/expected hash 和 split 的情况下直接改写原 generator。
- 不把 MULTI3 的 hardcoded `correct_wire`/`correct_envelope` native tests 当成 adoption label。
- 不因 fixture 失败删除历史日志、把 `UNKNOWN` 转成负例或降低 GOAL 的 root/证据标准。

## 当前建议的顺序

先由作者确认 A–D 中的 authority 路径；在确认前继续做的工作只限于可复用的零调用
adapter、replay、baseline contract 和成本记录，不启动真实 API/A800，也不产生新的
scientific label。无论选择哪条路径，PIPE2 v2、PIPE2 v9、fixture audit 和 MULTI3
静态审查回执都作为不可变的审计证据保留。
