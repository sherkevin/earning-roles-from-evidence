# Baseline root manifest scope audit — 2026-10-01

状态：`PARTIAL / BLOCKED_BY_EVIDENCE`
Goal 变更：无。benchmark/baseline 仍未冻结，未启动真实 API 或 A800。

## 结论

上一份 v13 离线 policy-matrix receipt 真实执行了七个 arm 和七个 hand-authored
case，但它只能证明“在当时 runner 代码的有限 manifest 接口下，离线 parity 逻辑可回放”。
独立审查发现它不能支持“root manifest 已经完整约束 canonical runner”的表述。v13 的
config、raw output 和 summary 不修改，作为历史证据保留；本报告收紧其解释边界。

## 审查发现

1. `manifest` 在 runner API 中可省略，只有显式 `require_manifest=True` 的新入口才拒绝
   bypass；历史兼容入口不能当作科学 root runner。
2. manifest 原先没有把 `arm_names`、当前 commit、component digest、RNG/visibility、
   root seed 和执行预算逐项绑定到实际运行对象。
3. public prefix 只比较集合会允许重排；累计 offer 会重复计数已经出现过的
   `UNKNOWN`/ignored row，污染 denominator。
4. `validate_root_receipt` 接收独立的 `feedback_rows`，因此 denominator 可以与实际
   observed prefix 不一致。
5. fixture runner 在所有 case 执行后才回写 manifest，失败时没有一个先于执行的完整
   sealed config。`max_episode_attempts` 在该离线 stream 中实际表示 offer-stream 上限，
   不是 live episode counter；这不能被带入正式 live runner。

## 已实施的修复

- manifest 拒绝非规范 commit/digest、负或非整数 seed、NaN/非法预算；
- prefix 强制保持冻结 arrival order；denominator 行必须以唯一 `feedback_id` 与 observed
  prefix 完全同序绑定；runner 对重复 row 做全局 seen 分类；
- `require_manifest=True`、当前 HEAD/component hash、arm order、registry/schedule digest、
  RNG/visibility、显式 root seed 和 wall/stream budget 在运行时校验；
- fixture runner 在首个 case 启动前一次性写入全部 manifest；历史 v13 不回写；
- 针对上述边界补充定向测试，当前 baseline root/runner 定向集合为 `17 passed`。

## 证据边界与下一步

这些修复仍只覆盖离线 matrix implementation identity，不等价于 TeamBench generator、
neutral-material、scorer、canonical ledger 和真实 cost 的 root manifest。新的 v14 必须在
修复提交之后重新生成，并报告 `source/generator/scorer` 的实际文件身份、root seed、预算、
七 case receipt 和失败保留。PIPE3 另行使用其真实 pinned material/scorer/ledger digest，
不能复用这个离线 runner 的字段语义。

在 v14 receipt 与 PIPE3 两阶段接缝均通过前，不启动 LLM/API、A800 或 benchmark freeze。
本审计没有降级任何 Goal 标准；它只撤回 v13 超出证据的解释。
