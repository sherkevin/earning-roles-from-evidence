# 0031：scorer truth 必须留在独立 worker，response 才能进入 parent ledger

日期：2026-09-27。
状态：Accepted as a bounded qualification contract; 不改变 Goal v1.0。

## 背景

前置检查只验证了 candidate worker 读不到 operator-only 文件，尚未验证 scorer 的
expected/score payload 是否真的在独立进程。若 scorer truth 被放入 agent payload，或者
parent 将 ledger file hash、delivery artifact hash 与 scorer response hash 混用，结果就
无法解释。

## 决定

新增 private scorer IPC preflight：

- scorer trusted worker 私有保存 fixture expected artifact digest，只接受 `op`、
  `artifact_sha256` 和 public context；
- parent 记录 PASS/FAIL response、response digest、worker hash 和运行边界；
- candidate-side probe 不接收 expected 值，读取 scorer trusted worker 被 sandbox 拒绝；
- delivery artifact digest、ledger file digest、response digest 分开命名和记录；
- 只有后续真实 scorer/runner 接通后，才可把该边界用于科学 label/evidence。

v1 的 digest 混淆失败保留，v2 修复后通过。当前结论仍是隔离资格，不是 benchmark 分数。

## 后果

下一次 runner 集成必须使用相同字段边界，并记录 scorer timeout、退出码、权限错误和
响应摘要；任何缺失都回到 `UNKNOWN`。实际 hidden tests、operator ledger IPC、真实
producer/recipient LLM 流程仍是后续 gate。
