# N03-next-r5.67：feature-aware contextual baseline qualification

日期：2026-10-05
状态：`PARTIAL`（公共输入资格通过；baseline 尚未冻结，未进行 live efficacy）
`goal_change_requested=false`

## 目的

r5.66 的静态审计发现，原有 `contextual_trust` 只读取 context×candidate 的 Beta
计数，而 RARE 读取同一 runner 提供的 64 维 `captured_features`；同时 RARE 丢弃
`base_scores`。在这个状态下，任何 live 差异都无法归因于责任感知更新。此任务只修复
这个可识别性缺口，不改变 active 故事线、方法合同、七臂 manifest 或 Goal。

## 实现

- 新增 `FeatureContextualTrustPolicy`，注册名为
  `contextual_trust_linear`。它使用与 RARE 相同的 `hash64-v1`、64 维 bounded
  feature、candidate menu、selected-only `recipient_judgment`、base-score 项和
  snapshot/restore 接口。
- 更新器是普通 diagonal ridge/RLS：
  `A_i <- A_i + phi_i^2`，`b_i <- b_i + phi_i y`，`theta_i=b_i/A_i`。
  它没有 RARE 的 protected anchor、fast-window、correction queue 或责任专用逻辑。
- RARE 现在把相同的 `base_scores` 加入 utility；这修复了原先静态输入合同不一致，
  不改变历史 receipt。
- feature-aware comparator 对 candidate 数量、维度、有限性、L2 范数、encoder/schema
  version 做 fail-closed 校验；UNKNOWN、重复 feedback 和不支持的 correction 不更新。
- 现有 Beta `contextual_trust` 保留为 context-only diagnostic，没有被静默改名或替换。

## 执行前冻结与证据

执行前写入配置：

[`experiments/logs/n03_feature_contextual_qualification_20261005_v2/config.json`](../../../experiments/logs/n03_feature_contextual_qualification_20261005_v2/config.json)

原始逐 case 记录和汇总：

- [`raw.jsonl`](../../../experiments/logs/n03_feature_contextual_qualification_20261005_v2/raw.jsonl)
- [`summary.json`](../../../experiments/logs/n03_feature_contextual_qualification_20261005_v2/summary.json)

配置明确记录 0 real API、0 GPU、`scientific_claim_allowed=false` 和
`baseline_frozen=false`。使用的是 CPU-only deterministic fixture；没有伪造模型结果。

## 结果

6/6 个离线资格 case 通过：

1. RARE 与 feature-aware comparator 的 menu、base score、encoder/schema 和 feature
   digest 相同；
2. feature mutation 会改变两者的 assignment score，旧 context-only control 则不读取
   feature；
3. 两者都实际消费 base score，修复前的 RARE 忽略问题不再存在；
4. correction 语义被明确区分：RARE 更新，普通 comparator no-op；这仍是预注册 updater
   差异，不是信息差异；
5. 两者 snapshot/restore 后的下一次概率一致；
6. 越界 feature 被拒绝，未启动选择或更新。

回归验证：baseline/policy/canonical/adapter 相关定向测试 `80 passed`；
`py_compile` 通过。上述结果都是协议/实现资格，不能支持 RARE 优于 comparator、实时
训练、角色专业化或 benchmark 冻结。

## 与 Goal 和三份标准的对照

- **已推进**：关闭了 strongest same-information baseline 的 feature/base-score 输入
  缺口，满足进入下一道 parity preflight 的必要条件。
- **仍未满足**：closest published adapter、第二 structural root authority、independent
  live histories、真实 recipient judgment/later-use、完整 measured cost、scientific
  effect 和 A800 训练均未完成。三份验收标准仍不能判定为通过。
- **原因分类**：本任务前的阻塞是实现/信息 parity 缺陷；剩余项目是证据不足和 benchmark
  资格未完成，不是实验失败，也不构成 Goal 降级理由。

## 下一步

先把 `contextual_trust_linear` 作为 candidate comparator 接入 canonical manifest 的
版本化 parity preflight，并完成 A0/B0 的 closest/second-root go/no-go；只有同信息、独立
namespace、独立 outcome 生成都通过，才允许一条有界 PIPE3 live parity。当前不启动新的
API 或 A800，不把这个离线 receipt 写成科学结果。
