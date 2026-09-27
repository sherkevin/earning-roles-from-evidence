# 审查报告：DIST1 neutral-v2 契约与接线

日期：2026-09-27  
审查范围：未提交的 `dist1-neutral-v2` adapter、候选 manifest、manifest provenance、
closed-loop runner、runtime preflight 及既有 producer scorer。  
审查性质：静态与内存构造审查；没有发起 LLM、GPU 或新的真实 episode；没有修改历史日志。

## 结论

v2 的主要修复方向是自洽的：公开材料明确规定了 `get() -> None | (message, receipt)`、
非阻塞空队列、`ack`/`nack` 名称与容量语义，hidden producer scorer 当前检查的接口也与此
一致。adapter 能从 pinned DIST1 生成材料，隐藏路径未进入 payload，public source 可解析；
provenance 和 runner 都能按 `material_adapter: dist1-neutral-v2` 选择该实现。

但目前还不能把它视为可运行或可科学解释的 benchmark 修复。至少有一个需要在下一次
真实请求前修正的配置安全问题，以及若干必须完成的零 LLM qualification。

## 已通过的静态检查

- v2 payload 的 `schema_version` 为 `peerrolebench-dist1-materials-v2`，接口契约版本为
  `dist1-queue-interface-v1`，producer/recipient 的所有权与交付路径保持明确。
- 对 seed 0 的内存构造和 provenance 调用均成功；`scientific_task_text_qualified=true`，
  `hidden_path_leaks=[]`，public source 均能被 AST 解析。
- v2 runner 接线位于 `load_runner_materials`，manifest provenance 与 runtime preflight
  都把 root 上的 `material_adapter` 传入；v1 历史 adapter 路径仍被保留。
- producer scorer 的 P3/P4/P7 所需的 `ack`、`nack`、非阻塞空队列与 `(message, receipt)`
  形式，已经与 v2 公开契约相符；v1 真实 episode 暴露的四个歧义在材料层确实被消除。

## 必须修正或证明的问题

### 1. 未知 adapter 会静默降级（必须修正）

`peerrolebench_manifest_provenance.load_materials` 对未知或拼写错误的 adapter 默认回落
到 v1；`real_closed_loop.load_runner_materials` 对未知值则回落到原生
`export_task_materials`。这会让配置 typo 在不报错的情况下改变任务材料，甚至重新暴露
原生任务文本。对于一个声称可复现的实验，这是高风险的静默条件变化。

应把 `None`（仅用于明确的历史默认）与已知值显式区分：未知非空 adapter 立即抛出
`ValueError`，并加入 provenance、runner 的回归测试。v2 实验卡自身当前拼写正确，但不能
以此替代防护。

### 2. v2 adapter 缺少直接回归测试

现有 adapter 测试仍主要覆盖 v1，manifest provenance 测试也固定读取 v1 manifest。
在任何真实 API 请求前，至少应有测试覆盖：v2 schema/contract 字段、隐藏路径与 oracle
检查、producer/recipient writable/required paths、与 v1 不意外相同，以及未知 adapter
拒绝。仅手工调用内存函数不足以成为冻结证据。

### 3. 必须运行 v2 的零 LLM runtime preflight 与 scorer preflight

当前 runtime preflight 原先固定 v1，虽已增加 `--manifest`，但 v2 输出尚未形成独立日志。
需要用 v2 manifest 运行 payload dispatch、delivery digest、operator ledger denial 和
lineage 检查；随后用与真实 runner 相同的 v2 producer source 运行 P1--P7。若 scorer 在
20 秒 RPC 窗口内仍 timeout，应先把它记录为 coverage/timeout 缺陷并版本化 scorer，不能
把 UNKNOWN 当作模型标签，也不能直接跑 PIPE3 或 A800。

### 4. 公开契约与 hidden scorer 的接近程度需要记录

v2 为修复 v1 的协议歧义，公开材料直接给出了 scorer 依赖的接口细节。这在任务定义上
可以是合法的 public API contract，但它降低了“从 situated delivery 判断真实接口”的
难度，可能使任务变成契约遵循而不是开放式协作。下一份 qualification 记录应明确：
这些语义来自真实公共接口/任务目标，而不是从 hidden test 名称反推；不能把 v2 与 v1 的
episode 结果混合比较。

### 5. identity 与版本追踪仍需更清楚

候选 manifest 已升级为 v2，但 root id/structural signature 仍写作 `..._v1`。这不一定
错误，因为结构根未变，但材料契约已经变化。建议在冻结前把 adapter/interface 版本写入
root provenance 的不可变身份字段，或在报告中明确“结构根相同、公开契约版本不同”；否则
后续聚合很容易误把 v1 UNKNOWN 与 v2 结果视为同一条件。

## 科学判定

这次 v2 修改只修复了可执行性和评分契约，尚未证明 producer label 有效、recipient
judgment 能形成可迁移 role evidence、controller 能学习，或 RARE 优于 baseline。v1 的
真实 UNKNOWN 必须保留；v2 只有在上述零 LLM gates 全部通过后，才值得消耗最多一条新的
真实 episode。任何 v2 UNKNOWN 都应关闭该 integration route，而不是增加重试、放宽超时或
启动 GPU。

`goal_change_requested=false`；本报告不修改 Goal，也不把工程修复写成科学结果。
