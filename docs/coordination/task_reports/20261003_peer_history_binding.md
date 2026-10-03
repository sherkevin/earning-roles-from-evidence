# Canonical source-to-target history binding seam

日期：2026-10-03
状态：`PARTIAL`（lineage contract 通过零调用资格；尚未接入 live runner）

## 任务与 Goal 对照

上一轮审计确认 `PeerHistoryV2` 只有 append/projection，不能证明一条 history 记录来自
“source evidence 发布 → future assignment/read-cut → target outcome”。本任务补上最小
可复用接缝，目标是让 history entry 与 canonical ledger 的 source/target 事件形成一条
不可替换的绑定，同时保留当前 active method 的信息边界。不改变 storyline、benchmark、
baseline 或 Goal，也不启动 API/GPU。

## 复用的已有组件

实现 `scripts/peerrolebench_peer_history_binding.py` 没有新建 learner 或替代协议，直接
复用：

1. `build_role_evidence_from_ledger`：从 native source ledger 推导 producer、delivery、
   recipient judgment/action/outcome 的 source evidence；
2. `RoleEvidenceOffer`：封存 source evidence 的 candidate/version、registry digest、
   available watermark 和 target task；
3. `LaterAssignment` 与 target `PeerSelection`：检查 assignment 在 selection 之前被记录，
   且 selection 选择了同一 native peer；
4. native target delivery/judgment/action/outcome：检查 target artifact 和 episode lineage；
5. `HistoryEntryV1`：只保存 selector 未来所需的最小统计，丰富 lineage 放在独立的
   `HistoryBindingReceiptV1` 中。

这个分离是必要的：native `LaterAssignment` 没有 offer record hash、read-cut 或 candidate
menu digest，不能单独承担证据消费的可审计性；同时 `peer-a@v1` 与 native `peer-a` 的
版本化身份差异必须在 receipt 中显式校验。

## 绑定不变量

有效 receipt 必须同时满足：

- source evidence 在 offer 中且被 target assignment 引用；
- source task index 严格小于 target task index；
- source available index ≤ assignment read-cut ≤ target decision index；
- offer registry digest 与 binding registry digest 相同，candidate version 在 menu 中，
  且其 base ID 与 native assignment/selection/target producer 一致；
- target delivery、judgment、action、outcome 都来自同一 target episode，并绑定 target
  selection；
- history entry 的 source artifact/judgment、target assignment/outcome 和 arrival index
  与 receipt 一致；target outcome 必须晚于 decision，history entry 只能在 outcome 后到达；
- `PASS/FAIL` history entry 必须携带已成功提交的 delayed-credit digest；`UNKNOWN` 不得
  携带 credit；native ledger 的 source evidence → assignment → target selection → target
  outcome 顺序必须严格成立；
- receipt 自身有 canonical SHA-256 digest，source evidence 只允许一条，避免重复 credit。

## 零调用验证

运行前记录配置，使用一个 hand-authored native ledger，包含 source episode、role evidence、
later assignment、target selection 和 target outcome；随后对 read-cut、candidate version 和
late arrival 做 mutation rejection：

```bash
python3 scripts/peerrolebench_peer_history_binding_qualification.py \
  --output experiments/logs/n03_peer_history_binding_qualification_20261003_v1
```

收紧 delayed-credit 与 event-order 后使用同一命令将输出目录换为
`n03_peer_history_binding_qualification_20261003_v2` 重跑；旧 v1 receipt 保留。

结果：`QUALIFIED_OFFLINE`，25 个 focused tests 通过（qualification receipt 固定其中
10 项 binding/history tests）；v2 receipt 在增加 delayed-credit 和 native event-order
约束后重跑，仍为 `QUALIFIED_OFFLINE`。v3 在提交 `1742404` 后重新运行，用当前提交
绑定配置与代码，结果仍为 `QUALIFIED_OFFLINE`。三次原始 stdout/stderr、config、summary
均保存在 `n03_peer_history_binding_qualification_20261003_v1/`、`_v2/` 与 `_v3/`，
0 LLM/API、0 GPU、0 native grader。

## 尚未完成

这项工作只证明 lineage seam 能拒绝明显错绑，尚未证明：

- live PIPE3 runner 在 target credit 成功后真的执行 `seal_assignment → append`；
- `PeerHistory` projection 被 selector 消费并改变 propensity/choice；
- history/no-history/shuffled/reset 四格的独立结果、质量、成本和 update latency；
- 第二 benchmark root、baseline parity 或 online training 效果。

因此 benchmark activation、科学结果和 A800 仍保持关闭。下一步把 receipt 接入现有
PIPE3 target-credit boundary，先做零调用 matched replay，再考虑有限真实 API。`goal_change_requested=false`。
