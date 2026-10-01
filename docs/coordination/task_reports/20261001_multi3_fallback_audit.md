# Task report — MULTI3 fallback root audit (2026-10-01)

## Goal alignment

- **对应标准**：ER-G3 的第二 structural root、真实 artifact 依赖、scorer 可归因性和 fixture authority。
- **状态**：`CONDITIONAL-LOW`。MULTI3 可复用 generator、sandbox 和 task scaffolding，但当前 native material 不能直接进入 PeerRoleBench-TB。
- **goal_change_requested**：`false`。
- **实验边界**：只做 pinned source/fixture 静态审查与 generator 读取；0 LLM、0 GPU、0 native score、0 peer label。

## 版本与来源

- TeamBench commit：`d185aef1916fd86a9ba554d581fd256319a973af`，工作树 clean。
- `generators/gen_multi3_polyglot.py`：
  `8ecfde93d5e4a1631e3e86dea5864645463ef5a4efb106e4d2a66b478b06919c`。
- `tasks/MULTI3_polyglot/task.yaml`：
  `da91e05b8759be5099c7e769fabe846d97b7c826f466217a8cbd37637a8c19e6`。
- `tasks/MULTI3_polyglot/grade.sh`：
  `9ba4f1a2460e27020c354e48ebab42cfe8b353736f2c27f018de5e36694eaa34`。
- `tasks/MULTI3_polyglot/spec.md`：
  `3953c11de671fa9f835312451ff797d1c59a5a1d27a174832bbbacc90cdbadb6`。

## 可复用部分

seed 0–9 都能生成可解析的 JSON schema、processor/handler 模块和 envelope 结构；任务
天然表达 backend serializer → frontend handler 的潜在上下游关系，且不同 seed 提供
config、product、profile、event 等结构变化。现有 sandbox、源文件 hash、权限与任务
contract 可复用。`task.yaml` 当前只宣称 public seeds 0–2，generator 实际接受 0–9，
因此 seed split 仍需单独冻结。

## 阻塞点

1. **没有真实 handoff/adoption**：生成的测试把 `correct_wire` 和 `correct_envelope`
   硬编码给 frontend 测试；没有用 `processor.serialize_batch` 的 envelope 调用
   `handler.process_envelope`/`deserialize_record`。native round-trip 因而不能证明
   recipient 使用了本次 producer 产物。
2. **schema 不是运行时合同**：`shared/schema.json` 主要是说明文件，processor/handler
   不读取或验证它，不能直接作为跨 agent artifact contract。
3. **generator sample bug**：`_make_sample_records` 的 `records.append(rec)` 与 `return`
   缩进在 `for` 外，文档声称三条记录但实际只返回一条。虽然 sample 当前没有进入
   native 测试，仍必须在 root freeze 前修复或明确排除。
4. **信息边界不干净**：生成的 spec 带有 “Planner Only” 和 active bug inventory，
   workspace 还含 `tests/test_contract.py`；需要像 PIPE2 一样重建 neutral material，
   隐藏 oracle/bug inventory 不能进入 agent payload。
5. **合同覆盖不完整**：spec 要求字符串 UTF-8/strip，但 processor 对非 nullable 字符串
   原样透传，handler 只对一个 nullable 字段 strip；现有测试没有 whitespace/UTF-8
   覆盖。schema test 只检查字段存在，不拒绝错误 alias，真正的 alias 检查落在
   `grade.sh`，不能直接当作公开 recipient contract。

## 判定

MULTI3 不能用现有 native grader 直接替代 PIPE2，也不能因 PIPE2 fixture 阻塞就自动
升级为 active benchmark。它是有潜力的 fallback：应先写一个独立 adapter，让 producer
实际生成 wire/envelope，recipient 只接收该 sealed artifact 并调用真实 handler，再用
artifact schema、row/record sequence 和 downstream output 分别计量 producer、recipient
self、adoption；同时修复/冻结 sample bug、seed split 和 neutral prompt。

## 下一步

1. 把上述 adapter 作为零调用工程任务，不修改 TeamBench 历史源码或 native receipt。
2. 在 adapter 通过后，再与 PIPE2 一起比较 fixture validity、责任可分离性、baseline
   parity 和完整成本；在此之前不启动真实 API/A800。
3. PIPE2 的 generator authority 仍需共同决定；本报告不选择替代 root，也不降级 Goal。
