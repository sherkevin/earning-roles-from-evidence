# PIPE1 native-material binding — 2026-10-07

状态：`QUALIFIED_OFFLINE_MATERIAL_BINDING`。本轮继续只做零调用资格工程：把 route
receipt 的 source/target digest 绑定到封存的 PIPE1 原生 seed 0/3 投影，并让 source 与
target 必须属于同一 structural root。没有调用模型、生成器、候选代码或 GPU，没有修改
v4 或更早历史日志。

## 修复的问题

此前 route schema 只检查 digest 的形状和内部 hash chain。一个结构上合法、但与真实
Planner/Executor 材料无关的回执仍可能得到协议 `PASS`。这不能成为昂贵 route 的前置
条件，因为它没有证明回执描述的就是当前 benchmark 材料。

## 实现

- `pipe1-material-binding-v1` 的 canonical payload 只使用已有封存投影中的
  `task_id`、`seed`、`spec_md_sha256`、`brief_md_sha256` 和 `workspace_sha256`；不把
  expected 输出或额外领域标签混入材料身份。
- `build_material_binding()` 从
  `n03_pipe1_native_material_audit_20261007_v1/seed_{0,3}` 重算这些哈希，并由统一的
  `canonical_digest` 生成 source/target `material_digest`。
- `--material-binding` 接受封存 audit 目录或同 schema JSON。缺失绑定为 `BLOCKED`；
  digest、task 或 seed 不匹配为 `FAIL`；只有精确匹配才允许 route receipt 检查为
  `PASS`。绑定目录中的文件也进入 preflight source hash。
- route validator 增加 `source.root_id == target.root_id` 约束，避免把同一 PIPE1
  structural root 的筛查误写成跨 root 路由。

## 零调用证据

完整记录在
[`n03_pipe1_preflight_20261007_v5`](../../../experiments/logs/n03_pipe1_preflight_20261007_v5/)。

- `25 passed`，两个脚本 `py_compile` 通过；
- 精确材料绑定：12 `PASS`、10 `BLOCKED`、1 `OPEN`，整体仍
  `BLOCKED_PRE_EXECUTION`；
- 缺失绑定：合法结构回执仍 `BLOCKED`；
- digest mismatch：`FAIL`，整体 fail-closed；
- 缺失 route：`BLOCKED`；
- 全部路径均为 0 API、0 generator、0 candidate、0 GPU，且
  `scientific_claim_allowed=false`。

合法路径仍使用合成 route receipt，只证明预检能拒绝材料错配并接受精确的封存材料
身份；它不证明真实 actor 交付、Verifier 终局质量、后续收益或任务泛化。

## Goal 对照

这关闭了“结构回执可以脱离当前原生材料”的一个工程漏洞，但没有关闭真实
source→message→artifact→Executor→Verifier lineage、exact outcome scorer、provider/
timezone pin、预算发行、relay baseline、同初始 peer 可辨识差异或 scientific efficacy。
三份验收标准和投稿 gate 仍未打开。下一步仍应实现并零调用验证完整 ledger runner，之后
再讨论新的 PIPE1 预算和真实调用。
