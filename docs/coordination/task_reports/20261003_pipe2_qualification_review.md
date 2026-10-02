# PIPE2 严格 qualification 路径审查

日期：2026-10-02

状态：`DESIGN-READY / AUTHORITY-BLOCKED`

范围：只读检查当前 PIPE2 adapter、runtime worker、shape audit、derived-fixture probe
和已有 receipts。没有调用 LLM、外部 API、Nebula 或 GPU，没有修改 active
benchmark/method 文档，也没有把离线 qualification 当作科学结果。

## 结论

PIPE2 已经有一条可以执行的 **零调用 runtime/adoption qualification runner**：

```text
scripts/peerrolebench_pipe2_runtime_qualification.py
  ├─ peerrolebench_pipe2_material_adapter_v2.py
  ├─ peerrolebench_pipe2_runtime_worker.py
  └─ peerrolebench_sandbox.py
```

它能在 parent 侧保存 private expected output，运行真实的 producer `extract.py` 和
recipient `transform.py`/`load.py`，并分出 producer contract、recipient self、sealed
artifact adoption、transport UNKNOWN 和负向控制。`v8` 在 seed `0/2` 的 producer×recipient
2×2 矩阵上通过；但这只是工程边界，`benchmark_qualified=false`、
`scientific_claim_allowed=false`。

当前不能直接进行“严格第二 root qualification”。阻塞点是 **fixture authority 尚未
决定并封存**：pinned TeamBench generator 的 seed `1/4/6/9` 将逗号写入未转义的 CSV，
`DictReader` 产生额外 `None` 列。`v9` 对 `0–9` 正确地返回 `FAILED_OFFLINE`，没有给这些
病例发 label。CSV-writer overlay 的 `derived_fixture_probe_v2` 证明可以保持逻辑行并
修复序列化，但 derived root 只停留在 decision evidence，尚未成为 active fixture。

## 已有 runner 和实际输入

### 1. 生成器与材料

`peerrolebench_pipe2_material_adapter_v2.py` 固定：

- TeamBench commit `d185aef1916fd86a9ba554d581fd256319a973af`；
- task `PIPE2_data_pipeline`；
- producer ownership：`pipeline/extract.py`；
- recipient ownership：`pipeline/transform.py`、`pipeline/load.py`；
- producer delivery：`artifact/extracted_rows.json`，schema `pipe2-extracted-rows-v1`；
- private：`data/expected_output.csv`、native tests、requirements 和 operator-only
  fields；
- public source/spec 与 hidden output 的路径检查、oracle pattern 检查和 digest。

当前 adapter 只能加载 pinned generator 的 workspace。它没有读取
`derived_fixture_probe` 产生的修复后 CSV，也没有接受一个已封存 fixture manifest；因此
不能把 derived overlay 误当作现有 runner 的输入。

### 2. 零调用运行

严格的工程重跑命令是：

```bash
python3 scripts/peerrolebench_pipe2_runtime_qualification.py \
  --output experiments/logs/<new-run-id> \
  --seeds <frozen-seed-list>
```

输出目录必须不存在。runner 会写入 `config.json`、append-only `raw.jsonl`、每个
producer/recipient/control 的 sandbox evidence 和 `summary.json`；代码会记录 TeamBench
commit、worker digest、material adapter 版本、seed、Python/platform、运行参数以及
`llm_calls=0`、`gpu_jobs=0`、`native_grader_invoked=false`。候选代码在已资格化 sandbox
内执行，parent 才能读取 expected output 并计算标签。

在 authority 尚未决定前，唯一可复现的输入是已有 valid seeds；它们不构成新的
benchmark split。不得为了得到全绿结果而从 `0–9` 删除 invalid seed。

### 3. 独立的 shape gate

`peerrolebench_pipe2_fixture_shape_audit.py` 不执行候选代码，检查 pinned generator 的
source/expected CSV header、row shape、source commit、generator digest 和 dirty state：

```bash
python3 scripts/peerrolebench_pipe2_fixture_shape_audit.py \
  --output experiments/logs/<new-shape-run> --seeds 0 1 2 3 4 5 6 7 8 9
```

已有 `v3` receipt：valid `0,2,3,5,7,8`；invalid `1,4,6,9`；public `0–2` 中有一个
invalid。该 gate 的 `INVALID_FIXTURE` 不应转换为 0/1 peer label。

## 现有 receipts 的边界

| receipt | 结果 | 可以支持的结论 | 不能支持的结论 |
|---|---|---|---|
| material qualification v2 | `QUALIFIED_OFFLINE`，seed 0/1/2 | ownership、hidden isolation、typed delivery shape | candidate correctness、judgment、later assignment |
| runtime qualification v8 | `QUALIFIED_OFFLINE`，seed 0/2；2×2 handoff、canary、drop-row/ignore-artifact 通过 | producer/recipient/adoption 的可执行 parent-side 工程判别 | benchmark authority、situated judgment、role evidence、效果 |
| runtime qualification v9 | `FAILED_OFFLINE`，seed 0–9 | full-root shape failure 被保留并可追溯 | 不能把 valid subset 升格为 full root |
| fixture shape audit v3 | `AUDITED`，6 valid / 4 invalid | generator 数据合同问题的定位 | 修复后 derived root 已获授权 |
| derived fixture probe v2 | `PROBE_COMPLETE`，0–9 derived shape-valid | serialization repair 是一个可审查选项 | active benchmark、native authority、scientific label |

`runtime_adoption_qualification` 的“qualified”只表示其内部的 producer discrimination
与 recipient discrimination 通过。runner 明确将 `benchmark_qualified` 和
`scientific_claim_allowed` 置为 false。

## 下一次严格 qualification 需要的输入

下一次不是继续重复 v8/v9，而是先获得一份版本化、可回放的 authority manifest。它至少
要包含：

1. **authority 选择**：pinned malformed generator 的修复版本、外置 derived root，或
   公开 valid subset。选择必须由 active 决议/benchmark 版本确认；不能在 runner 内隐式
   修复 CSV。
2. **完整 fixture bundle**：每个 seed 的 source/expected bytes、schema/key columns、
   generator/overlay version、root digest、public/hidden split 与 malformed-case policy。
   修复不得覆盖旧 bytes；旧 v3/v9 receipts 保持不可变。
3. **adapter 输入接口**：`load_pipe2` 应能从该 manifest 加载 fixture，并记录
   `fixture_authority_digest`；仅修改 runtime runner 的 seed 参数不足以实现 derived root。
4. **重跑的工程门**：shape audit 全部通过后，逐 seed 执行 producer×recipient 矩阵、
   canary 和 negative controls；任何 transport/resource error 保持 `UNKNOWN`。
5. **完整 ArtifactRole 闭环**：recipient 对绑定的 delivery 产生结构化
   accept/repair/reject judgment，记录 artifact digest；责任 scorer 分开 `Q_p`、recipient
   self、adoption、judgment、UNKNOWN；随后才允许 source-bound evidence。
6. **later assignment 与 outcome**：将 evidence 在 assignment read-cut 前消费，绑定
   `candidate_id@version`、menu、propensity、assignment、task start；下一次独立 task
   必须有 terminal quality/adoption/rework/complete cost。当前 PIPE2 runner 没有这些
   状态机。
7. **same-information policy parity**：同一 root/菜单/arrival/预算/UNKNOWN 分母下，
   `uniform`、`no_update`、`raw_acceptance`、`terminal_only`、`contextual_trust`、
   `pooled_controller`、RARE 共用独立 live histories；PIPE2 的零调用 runner 不能替代
   这条 baseline runner。

## 放行与停止条件

严格 qualification 在下列条件全部满足后才可申请：

- authority manifest、root digest、split 和 fixture replay 通过；
- 所有指定 seed shape-valid，或 invalid policy 已由共同确认的 active 版本明确规定，且
  invalid 不产生 label；
- public payload 不含 expected output、tests、native oracle 或 operator judgment；
- producer contract、recipient self、adoption 和 recipient judgment 可按 delivery
  digest 独立评分；
- recipient 确实读取 sealed artifact；worker/sandbox/runtime failure 留为 UNKNOWN；
- judgment→evidence→read-cut→assignment→task-start→later outcome 顺序可回放；
- 独立 root/history、baseline information/cost parity 和 complete cost 字段已封存。

任一条件失败即停止在 zero-call qualification，保留失败 receipt，不启动 LLM、A800 或
论文效果实验。尤其不能以“valid seed 子集通过”“derived probe shape-valid”或
“parent control 通过”替代 benchmark freeze。

## 可复用资产和建议

当前最值得复用的是 v2 material adapter、已资格化 sandbox、producer×recipient 2×2
矩阵、digest-bound artifact、adoption key-sequence 检查、UNKNOWN policy 和 negative
controls。下一步工程工作应集中在 **authority manifest + fixture-loading seam +
source-bound judgment/later-assignment composition**。在这三项完成并复核前，不需要新增
LLM 调用、GPU 作业或另一套 PIPE2 handoff runner。
