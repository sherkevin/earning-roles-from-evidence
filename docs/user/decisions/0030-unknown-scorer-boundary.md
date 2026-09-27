# 0030：异常 scorer 不产生标签或 role evidence

日期：2026-09-27。
状态：Accepted as a qualification contract; 不改变 Goal v1.0。

## 背景

真实 runner 的阶段请求不自动重试。producer、delivery 或 recipient judgment 在中途
失败时，账本只保留已经发生的前缀；scorer 还可能超时、权限失败、缺少回执或返回
非法 JSON。若这些情况被当成 `FAIL`，更新器会学习基础设施故障而不是交付质量。

## 决定

在 parent boundary 中统一采用以下 disposition：

- 完整 ledger replay 且 scorer 回执为 `PASS`/`FAIL`、版本和覆盖完整时，才允许 terminal
  label 与 evidence/update；
- selection、delivery 或 judgment 后的中断是 `UNKNOWN`，列出缺失阶段，不产生负标签；
- retry event 不是第二个样本，当前协议直接以 `INVALID/unsupported_retry` 拒绝；
- timeout、permission、transport error、invalid JSON 和 incomplete coverage 都是
  `UNKNOWN`，`update_allowed=false`。

上述语义已经在真实 N02 v3 ledger 的零 LLM mutation qualification 中通过；该检查没有
实现 hidden scorer，也没有证明实际 IPC 隔离。

## 后果

后续真实 runner 必须把 scorer 的 response digest、退出码、超时和权限错误写入 raw
records，并在合法回执后通过 replay gate。网络重试若未来开放，必须定义新 attempt ID
和收费/因果语义，不得重写原 ledger。下一 gate 是独立 scorer worker 的 stdin/RPC 与
operator/expected 隔离；在该 gate 通过前不冻结 benchmark 或启动 A800。
