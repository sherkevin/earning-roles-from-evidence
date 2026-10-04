# PIPE3 canonical peer-history append integration

日期：2026-10-03  
状态：`PARTIAL`（target-credit→history append 接缝通过零调用资格；真实 history、selector consumption 和科学效果仍未开始）

## 任务与 Goal 对照

本任务落实 `GOAL.md` 的 ER-G1/ER-G2：在既有“situated judgment → attributable role evidence → future assignment → later outcome”链上，真正把持久 history 写入接到后续结果边界。它不改变 Goal、active storyline、method、benchmark 或 baseline，也不把离线 fixture 当成角色学习结果。

## 实现

新增 `scripts/peerrolebench_peer_history_adapter.py`。它只接受已经存在的 canonical ledger、`RoleEvidenceOffer`、`LaterAssignment`、target `PeerSelection` 和成功提交的 `LaterCredit`，然后：

1. 从 native source judgment 推导冻结的 `accept=1 / accept_with_rework=.5 / reject_redo=0` 标签；
2. 从 target outcome 推导 PASS/FAIL 与 later outcome label；
3. 生成 role/state scope hash 和 `AssignmentSealV1`；
4. 使用实际 `LaterCredit.credit_digest` 构造 `HistoryBindingReceiptV1`；
5. 通过 receipt 后才执行 `PeerHistoryV1.seal_assignment → append`，返回 public projection/state digest。

`pipe3_two_stage_composition.py` 版本化为 `pipe3-two-stage-composition-v1.7`，增加显式 `history_mode=off|append`。producer-owned qualification source episode 改为严格 gate 所要求的 direct `accept/use` 且无改动；recipient-owned/mixed 仍保持 UNKNOWN/no-update。默认模式仍为 `off`，历史回执不被重写。adapter 还要求传入 `DelayedCreditLedger` 中与 assignment/outcome 完全相同的已提交 credit，不能只凭一个布尔值写 history；seal+append 失败会恢复 history snapshot，避免孤儿 seal。

## 运行前冻结与原始证据

新增 qualification（v1 为未提交工作树上的保留试跑；正式可复现回执使用提交后的 v2）：

```bash
python3 scripts/peerrolebench_peer_history_integration_qualification.py \
  --output experiments/logs/n03_peer_history_integration_qualification_20261003_v2
```

配置先于执行写入 `config.json`，记录提交后的 commit、组件 SHA-256、Python/平台、seed、fixture scorer、0 LLM/API、0 GPU 和组件范围。`off` 与 `append` 在同一 deterministic scorer、seed、candidate registry 和 composition 上分别运行；原始每阶段 trace 位于两个模式子目录的 `raw.jsonl`，汇总在 `summary.json`。v1 目录保留，不与正式 v2 结果合并。

结果为 `QUALIFIED_OFFLINE`：

- producer-owned：两个模式的 native ledger digest 均为 `3bbedceb3dd2e9fb3566435b0ec78df02261b87a90fb0b72a7bc2514ed75aac9`，selection trace 相同；`append` 新增 1 条 `PASS` history entry，receipt 的 delayed-credit digest 与实际 credit 相同；
- recipient-owned、mixed：两模式 ledger 相同，source attribution 均 `NOT_RUN_UNKNOWN`，history 没有被创建；
- policy update count 在两个模式逐 control 相同；
- focused tests：26 passed（composition 11、adapter 5、binding/history 10）；py_compile 与 `git diff --check` 通过。

## 验收状态

已满足：

- 同一 canonical target-credit 边界可以在延迟信用成功后写入 history；
- source/target/candidate version/read-cut/arrival/delayed-credit lineage 仍由 `HistoryBindingReceiptV1` 约束；
- history 开关不改变选择 ledger，recipient-owned/mixed 不被错误写成 producer history；
- 失败/UNKNOWN 保持显式，不产生正标签。

仅部分满足：

- 这是 zero-call CPU fixture 的接缝资格，不是真实 recipient judgment 或 benchmark episode；
- selector 目前只得到 projection，尚未在下一次选择中消费并改变 propensity/choice；
- `HistoryCostV1` 在此 qualification 中显式为未测量的零值，不能用于成本结论。
- delayed credit/policy 与 history 的跨进程恢复仍未合并成一个持久事务；真实 runner 必须把两者的 snapshot/replay 一起封存。

尚未满足：

- history/no-history/shuffled/reset 四格独立 stream；
- 两个 structural root、七 arm same-information baseline parity、later-use precision/quality/cost；
- real API live chain、online updater/backbone、A800 challenger 和 AAMAS 科学结果。

## 问题与下一步

本轮暴露并修复了一个真实实现不一致：`two-stage-role-evidence-v2` 已要求 direct `accept/use`，而旧 composition 仍把 producer-owned source 写成 `accept_with_rework/repair`，导致合法 source gate 不可达。现在只对新 qualification path 使用严格 direct-use source fixture；该修复没有放宽 gate，也没有改写旧日志。

下一步是用同一 canonical composition 写出四格 matched replay：`history`、`no-history`、`shuffled-history`、`reset-history`。先验证 projection 是否真的在执行前被 selector 消费、乱序/重置是否按预注册语义失败，再决定是否有资格开一条真实 API 小链。A800 继续关闭。

`goal_change_requested=false`。
