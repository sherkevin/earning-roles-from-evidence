# N03-next-r5.65：canonical runtime stream builder qualification

日期：2026-10-05  
状态：`partial`（工程门通过；科学准入仍关闭）  
代码提交：`72fb6d23b3ddfcb3353c07f48dc51210d6ba28c4`
`goal_change_requested=false`

## 目的

r5.64 已经能在 runner 启动前比较 root、registry、schedule、RNG 和十项
`stream_values` 的 digest，但 stream 仍由 qualification caller 手工提供。这会留下一个
重要的可执行性空洞：封存的公开输入可能与 runner 实际消费的 offer 不一致。本任务只补
这一条绑定，不改变七臂定义、评分、方法或 Goal。

## 实现

新增 `build_runtime_stream_values(offers, schedule, registry)`，从当前
`MatrixOffer`、`ArrivalAssignment` 和 `CandidateRegistryEntry` 生成 canonical manifest
要求的十项公开对象：候选菜单、registry、public `phi`、offer stream、read-cut/decision、
arrival schedule、RNG schedule、propensity、state schema 和 state initialization。

投影只保留 policy 在选择时可见的字段。它不读取 scorer-private 字段、未来 outcome、
后验 label 或 hidden judgment；所有对象都是确定性的 JSON-shaped 值，随后由同一
`canonical_digest` 封存。测试同时检查 registry payload、public rows、十项 key 的闭集和
私有字段不进入 projection。

## 验证

在 clean authored commit 上运行：

```text
python3 scripts/peerrolebench_canonical_manifest_qualification.py \
  --out-dir experiments/logs/n03_canonical_manifest_validation_20261004_v8
```

回执 `QUALIFIED_OFFLINE`，17/17 case 通过：

- valid manifest 与使用实际 fixture offer/schedule/registry 生成的 synthetic preflight 通过；
- 七臂各选择 2 次，fixture policy updates=3；
- runtime `public_phi` 篡改在 policy construction 前拒绝；
- 其余 14 个 manifest mutation 全部 `UNKNOWN`、`false_accept=false`、
  `runner_started=false`、`policy_updates=0`。

32 项 canonical-manifest/policy-matrix 回归通过，`py_compile` 和 `git diff --check` 通过。
原始配置、JSONL、summary、组件 hash、commit 和 worktree receipt 保存在
[`v8 receipt`](../../../experiments/logs/n03_canonical_manifest_validation_20261004_v8/summary.json)。

## 证据边界与标准对照

本任务只证明 manifest-to-runtime 的公开输入投影和 fail-closed digest binding 可以执行。
它没有调用 Idealab API，也没有提交 GPU（`real_api_calls=0`, `gpu_jobs=0`），不构成
benchmark qualification、baseline parity、peer-role learning、自进化、实时训练、
later-use utility 或效果结果。stream builder 仍使用当前 hand-authored PIPE3 fixture
root；`closest_published` 第八臂、第二 structural root、independent live histories、
真实跨 episode provenance、完整成本和统计分析仍开放。因此三份唯一生效文档的状态不变：
故事线、方法论和 benchmark+baseline 均 `NOT_READY`，Goal 不降级。

## 下一道门

停止继续堆叠 manifest plumbing。下一步应把这条 builder 绑定接入三类 source adapter
的同一 canonical live stream，并先完成 `closest_published` 适配器、第二 structural root
和 same-information live parity 的设计审查；在这些门通过前不启动正式 API/A800。
