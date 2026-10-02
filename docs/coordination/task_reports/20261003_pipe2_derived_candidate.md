# PIPE2 派生候选根：CSV 序列化 overlay 资格审计

日期：2026-10-03（本地工作日；运行 receipt 使用 UTC 时间戳）
状态：`PARTIAL`；派生根的工程资格已通过，尚未成为 active benchmark。

## 任务与 Goal 对照

本任务只推进 `GOAL.md` 中“至少两个结构根、可执行且可审查的材料/责任边界、真实
反馈前的测量资格”这些前置条件。它没有测试 situated judgment、future assignment、
role learning、online update 或跨任务质量/成本，因此没有完成 Goal 的科学主链，也没有
请求降低 Goal。

用户已确认可以把 CSV-writer 修复做成版本化 **candidate derived root**。这项确认不等
于把它登记为 active benchmark；active benchmark/baseline 文档和 registry 保持不变。

## 冻结的输入与实现

- TeamBench checkout：`d185aef1916fd86a9ba554d581fd256319a973af`；generator
  `generators/gen_pipe2_data_pipeline.py` 的 SHA-256 为
  `558f9ea25e57dc0544cff13bf6c8aa4b3acc97c73316d2c788d2df0b02618c5b`。
- 候选 overlay：`pipe2-csv-writer-v1`，代码为
  `scripts/peerrolebench_pipe2_derived_material_adapter.py`。它只将同一组逻辑行用
  `csv.writer`（QUOTE_MINIMAL、LF、双引号）序列化；不改 pipeline 代码、schema、bug
  定义、角色 ownership、prompt 或 hidden expected 语义。
- 候选 recipe：
  `configs/aamas2027/pipe2_derived_root_candidate_v1.json`，root digest
  `f984db3deb81cf66001864ab9fb013ceef91019c97d860159693c820fccf770e`，overlay 源码
  digest `c42c2fed440329e26558361d5aaee0e8002c3858dfa772cda2fab280367658d5`。
  recipe 是 hash-only；expected bytes 只在 parent 侧重建和校验，不进入 agent payload。
- seeds 固定为 `0..9`。此前 shape audit 中 malformed 的 `1,4,6,9` 被修复；其余
  seeds 的 derived bytes 与 pinned bytes 相同。recipe 中的 public/hidden 仅继承 shape
  审计记录，并明确标为 `NOT_A_SCIENTIFIC_SPLIT`。

## 实际验证与原始证据

### 1. 派生材料形状审计

命令：

```bash
python3 scripts/peerrolebench_pipe2_derived_shape_audit.py \
  --output experiments/logs/n03_pipe2_derived_root_shape_audit_20261003_v2 \
  --seeds 0 1 2 3 4 5 6 7 8 9
```

结果为 `AUDITED`：10/10 seed 的 source 和 expected CSV 均为合法声明列，无 invalid 或
unknown。receipt 保留 `config.json`、`raw.jsonl` 和 `summary.json`，并记录 0 LLM、0
GPU、未执行 candidate code、`scientific_claim_allowed=false`。

### 2. 派生材料上的实际 sandbox qualification

命令（v2 receipt 额外绑定 candidate recipe root digest；先前 v1 receipt 保留为历史
运行，不删除也不覆盖）：

```bash
python3 scripts/peerrolebench_pipe2_derived_runtime_qualification.py \
  --output experiments/logs/n03_pipe2_derived_root_runtime_qualification_20261003_v2 \
  --seeds 0 1 2 3 4 5 6 7 8 9
```

该 runner 是显式版本化 wrapper，复用已经资格化的 sandbox、producer×recipient 矩阵、
canary、drop-row 和 ignore-artifact controls；只替换 material loader，不改 pinned
runner 的默认行为。结果：

- `QUALIFIED_OFFLINE`，10/10 fixture `VALID`；
- producer discrimination、handoff matrix、canary sensitivity、negative controls
  全部通过；`runtime_adoption_scorer_qualified=true`；
- candidate code 在 sandbox 中真实执行；API/LLM 调用 `0`、GPU `0`、native grader `0`；
- `benchmark_qualified=false`、`scientific_claim_allowed=false`；
- 运行 receipt 的 `working_tree_dirty=true` 被如实保留，不能当成发布构建证明。

## 标准状态

| Goal/验收项 | 状态 | 证据或缺口 |
|---|---|---|
| 第二结构根材料可重现、可审计 | `PARTIAL → engineering pass` | recipe、全 10 seed shape audit、derived runtime receipt |
| producer/recipient ownership 与 delivery adoption 可执行 | `PARTIAL → engineering pass` | 10 seed runtime matrix；仍是 parent-side qualification |
| public payload 与 hidden expected 隔离 | `PARTIAL → engineering pass` | adapter tests 和 runtime config；尚无正式 benchmark release bundle |
| 权威 benchmark / active split | `OPEN` | TeamBench 原始 generator 的修复来源和 split 尚未通过 benchmark 冻结门 |
| recipient situated judgment | `OPEN` | 当前 runtime 只有 self/adoption diagnostics，没有正式 judgment 事件 |
| later assignment 与独立 terminal outcome | `OPEN` | PIPE2 尚未接入选择、future read-cut、later task 和 independent histories |
| same-information baseline parity | `OPEN` | 尚未有完整 live baseline matrix |
| online learner / A800 效果 | `OPEN` | 没有科学 API 或 GPU 运行；当前不应启动 |

## 发现与边界

派生 overlay 修复的是数据载体的 CSV 语法问题，而不是任务本身的缺陷。它消除了
`DictReader` 额外 `null` 列造成的 fixture coverage UNKNOWN，因此值得作为第二 root 候选
继续推进；但它没有自动提供权威性、独立任务根、真实 recipient judgment 或 later
assignment。不能把 `QUALIFIED_OFFLINE` 改写成 benchmark 通过，也不能把全 seed 通过解释
成 role-learning 或方法效果。

## 下一步

1. 在不改 active benchmark 文档的前提下，用该 candidate root 接入 responsibility-aware
   judgment、later-assignment/read-cut 和 independent outcome 的零调用 replay。
2. 为同一 root 建立 same-information baseline contract/parity receipt，并明确哪些字段
   可以进入 baseline；保持 public/hidden 科学 split 未冻结的事实。
3. 只有责任归因、later outcome、独立历史和 baseline parity 全部通过，才申请新的
   benchmark 版本和有限真实 API 运行；A800 仍等待真实信号和明确 update bottleneck。

`goal_change_requested=false`。
