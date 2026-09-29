# Meta-Team-L2-public profile boundary qualification — 2026-09-30

## 结论

完成了 `MetaTeam-L2-public` 的零调用 schema/信息边界 qualification，状态为
`QUALIFIED_OFFLINE`；这只证明一个可审计的 adapter 输入/输出合同，**不等于 Meta-Team
已实现、没有调用 LLM、没有 benchmark effect，也没有 baseline freeze**。

固定的定性 profile 字段来自已下载的一手 L2 prompt：`reliability`、`strengths`、
`weaknesses`、`communication_style`、`notes`。本项目的 profile record 只允许这些有界
字段，并绑定 selected candidate、producer/recipient/version、selection/delivery/source
event、source arrival index、profile availability watermark、parser/model config digest
和 correction lineage。原生 Meta-Team 使用完整 interaction trajectory 与 post-task result；
这些字段在 public adapter 输入中被拒绝，不能把它们悄悄带入主比较。

## 实现

- schema：`scripts/peerrolebench_metateam_profile_sidecar.py`
- qualification：`scripts/peerrolebench_metateam_profile_qualification.py`
- tests：`tests/test_peerrolebench_metateam_profile_sidecar.py`
- 当前 adapter 状态：`NOT_IMPLEMENTED / QUALIFICATION_REQUIRED`
- 三层设计仍保留：`original_info` 只做宽信息诊断，`public` 才可能进入同信息主比较，
  `ablation_profile_only` 用于去掉 L3/team-structure 影响；本次只验证三层共用的 profile
  record 合同，没有执行任何一层的生成模型。

硬检查包括：

1. profile 必须来自 `eligible/public` 的 selected interaction，candidate key 必须与
   selected candidate 相同；UNKNOWN、unselected 或 recipient 自有不可归因事件不能生成
   profile。
2. profile 的 source arrival 不得晚于 availability watermark；下一次 assignment 的
   consumption 必须使用更晚的 decision index，且 read cut 不得早于 watermark 或晚于
   decision。
3. revision 大于一时必须显式 `supersedes_profile_id`；profile/attestation digest
   覆盖全部公开字段，mutation 会被拒绝。
4. 公开输入拒绝 terminal/final/hidden score、raw trajectory、operator ledger、private
   scorer、其他 policy state 和 future result；profile 不携带这些字段的替代副本。
5. profile schema、parser version、model config digest、文本/条目上限和固定 enum 均必须
   在执行前封存。

## 证据与失败记录

- v1：初版 8 格 fixture 通过，但尚未包含 selected-candidate binding、严格 attestation
  digest 和完整运行元数据，不能作为当前版本回执。
- v2：构造 `ProfileConsumptionAttestation` 时漏传 candidate key，真实运行失败；保留
  `config.json`，后续修复未覆盖该记录。
- v3：修复后的初步 8 格通过；仍未加入完整配置/测试回执。
- v4：最终 schema 版本的 8 格 qualification 通过，`real_api_calls=0`、`gpu_jobs=0`、
  `scientific_claim_allowed=false`；配置、逐检查 summary 和定向测试输出保留在
  [`experiments/logs/n03_metateam_public_profile_qualification_20260930_v4/`](../../../experiments/logs/n03_metateam_public_profile_qualification_20260930_v4/)。
- v4 的第一次全套测试命令把 glob 作为字面参数，得到 `no tests ran`；原始失败保存在
  `full_peerrolebench_test_output.json`，没有计为通过。
- v6 在最终 attestation digest 修复后重跑：定向 8 passed，完整 47 个
  `test_peerrolebench_*.py` 文件共 **273 passed**；回执在
  [`experiments/logs/n03_metateam_public_profile_qualification_20260930_v6/`](../../../experiments/logs/n03_metateam_public_profile_qualification_20260930_v6/)。

## 仍未关闭的科学闸门

本任务没有验证 profile 摘要质量、LLM 调用成本、profile 是否预测 later-use、assignment
是否在真实 PIPE3 runner 中消费、隔离进程的 policy-read trace、独立 live histories、完整
producer/recipient/judge/scorer/repair/replay cost 或 Meta-Team 原论文结果。`source_input_digest`
在本任务只作为公共输入绑定占位，尚未由真实 runner 生成并 replay；因此不能把这次 fixture
qualification 写成“Meta-Team baseline 已实现”。

下一小任务是把该 schema 接到 PIPE3 public sidecar 的零调用 builder/replay seam，先验证真实
`source_input_digest`、selected-only lineage 和 assignment offer 的同一 record hash；若无法
在不读取 hidden terminal/trajectory 的情况下生成 profile，`MetaTeam-L2-public` 保持 `NO-GO`，
不启动正式 API 或 A800。
