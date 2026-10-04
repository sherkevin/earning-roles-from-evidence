# 多条 peer history 反例与 scope 隔离卡（零调用）

日期：2026-10-04
状态：`DESIGN_ONLY`

## 目的

上一轮审查确认，单条 entry 的 arrival-before-seal 失败只能证明非法快照被拒绝，不能证明合法多条历史的顺序、候选身份、projection 完整性和 role/state scope 隔离。因此在进入 independent live histories 前，用两个合法 entry 和同一 selector 做四类可反驳检查。

## 固定对象与预算

- 一个 canonical PIPE3 source→target history fixture，扩展为两条合法、不同 assignment/arrival 的 entry；另一个 entry 使用不同 role/state scope。
- 同一 candidate registry、read cut、base score、RNG 和 test-only selector；不调用 LLM/API，不提交 GPU，不执行 target task。
- 父进程写配置和原始 JSONL；所有负例保留 snapshot、exception、digest 和 no-update 结果。

## Cells 与指标

| cell | 变体 | 预期 |
|---|---|---|
| `valid-two-entry` | 两条 entry 按 arrival 顺序 replay | PASS；entry count=2，projection/input digest 可重放 |
| `permuted-two-entry` | 交换两条合法 entry 顺序并重算 snapshot digest | UNKNOWN；replay 拒绝顺序，不回退为空历史 |
| `candidate-mismatch` | 用 `peer-a` snapshot 请求 `peer-b@v1` projection | UNKNOWN；candidate identity 不匹配，无 selector/update |
| `projection-rate-mutation` | 改变 public scope rate 后保持原 attested snapshot digest | UNKNOWN；快照/聚合完整性失败，无 selector/update |
| `scope-isolation` | 只改变不匹配 role/state scope 的 rate | PASS；目标 scope 的 scores/probabilities/choice/propensity 完全不变 |

每个 cell 记录 `status`、entry/scope count、state/projection/input digest、selected peer、propensity、exception、update count、snapshot bytes、wall time、完整 cost schema 和组件 hash。所有未知/资源错误只保留 UNKNOWN，不改成负例标签。

## 通过条件与下一步

五格全部满足预期才算 `QUALIFIED_OFFLINE`。通过只说明 history store 的顺序、身份、完整性和 scope 读取边界；它不证明 peer suitability、later-use、质量/成本收益、实时更新或 AAMAS 科学效果。失败则修复协议并保留回执；通过后才有资格把同一 projection 接入 independent live history，随后才讨论第二 root、baseline parity 和真实 API。

`goal_change_requested=false`。
