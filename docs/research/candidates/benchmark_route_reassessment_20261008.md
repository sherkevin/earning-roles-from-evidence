# Benchmark 路线重审：PIPE1、PIPE2、PIPE3

日期：2026-10-08。状态：`CANDIDATE / NOT A DECISION`。

本文件不是把某个候选静默升级为 active benchmark；它把最新证据转成下一步的
取舍标准，避免继续在错误的执行环境上购买 API。

## 先看论文真正需要什么

主张不是“一个 agent 能否把规则写成消息”，而是：具体交付被真实接收、评价和使用
后，这个证据能否在**下一次执行开始前**改善责任分派，并在未见任务上改善质量和
完整成本。一个候选 benchmark 必须同时提供：

1. producer 有独立且可运行的交付义务；
2. recipient 的使用/修改/返工是可观测的，而且不被误记为 producer 缺陷；
3. 未来任务在选人后真实执行，有独立 outcome 和成本；
4. 强同信息对照能排除“直接看到任务说明”或“集中式历史”带来的替代解释；
5. 运行时隔离、可见性和 lineage 足够强，不能靠 prompt 约束代替。

## 目前证据的矩阵

| 候选 | 已有真实/离线资产 | 最新阻塞 | 目前能支持的结论 |
|---|---|---|---|
| PIPE3 | producer/recipient/adoption scorer、ActorExperience、fresh producer stage；2 次真实生成均 P1/P2/P3 PASS | 两个 task×actor 组合没有有限 Qp 差异；旧 J 只看 producer.py，Y 非独立；无 later assignment | 可测试接线与有限产出事实，不能支撑自然 peer 差异或 role learning |
| PIPE1 | 原生 Planner→Executor 消息、四域材料、full-spec relay 语义、route receipt | Executor 可读 reports/expected，shell 无白名单；run_all 漏写 spec/brief；Verifier/最终 grade 可掩盖 Planner 增量 | 适合研究信息转交，但尚不能公平执行；需要独立 sandbox 和 pre-Verifier scorer |
| PIPE2 derived | 10 seed overlay 的形状与 producer×recipient/adoption sandbox 资格；责任 gate 唯一正例可达 | overlay 权威性、独立 root、J/later assignment/independent Y、live baseline 均未闭合；10 seed 只有5个材料等价类 | 最接近可补齐 ArtifactRole 主轨的工程候选，但仍不是 active benchmark |

## 当前路线判断

**不再继续 PIPE3 时间戳小任务的判断调用。** 两次真实生成已经说明固定 native-bad /
patched-good 不能当自然 peer 能力轴；继续购买同一类判断不会增加识别力。

**PIPE1 不能直接作为第二 root 实验。** 它的任务依赖很清楚：Planner 持有完整
mapping，Executor 只有 brief 和样例，因此 `full_spec_relay` 是必须的强简单控制。
但原生 harness 的隔离与材料接线不合格。修复成本不是小补丁，必须另立版本化 runner，
先通过零调用 mutation matrix，再谈 API。

**PIPE2 是当前最值得优先做零调用路线资格化的候选。** 它已经有 producer/recipient/
adoption 的可执行分离和责任 gate，缺口集中在 later assignment、独立 future outcome、
same-information baseline 和 derived-root authority。它仍可能被审稿人认为是同一
TeamBench generator 的 overlay 变体，必须保留五个 schema family 的分组，不能把十个
seed 当十个独立样本。

后续的 Scheme-B 接线审查进一步收紧了这项判断：PIPE2 的真实 recipient 收到的是
`artifact/extracted_rows.json` 数据工件，不是 producer source。现有 observation bridge
要求 source-file handoff，因此不能直接接到 PIPE2；runtime receipt 也没有 J/A/Y 或
recipient pre/post diff。这个事实将 PIPE2 暂停在 `BLOCKED_BY_HANDOFF_SEMANTICS`，不把
synthetic observation fixture 当作资格证据。详见
[compatibility audit](../coordination/task_reports/20261008_pipe2_observation_bridge_compatibility.md)。

这不是把 PIPE2 选成最终 benchmark 的决定。下一步只做一个低成本问题：在 PIPE2 derived
材料上，能否把 source evidence、future assignment 和 independent outcome 的 lineage
接成一个不泄漏的零调用 fixture，并让 strong same-information control 读取同一菜单、
同一 public feature、同一到达顺序与成本字段。如果接不成，PIPE2 也不能救主线。

## 对 baseline 的直接约束

PIPE1 的 `no_message` 只能是依赖诊断；`full_spec_relay` 必须与 generated Planner
共享 message channel、最大长度、Executor sandbox、Verifier、retry 和完整成本。
PIPE2/PIPE3 的 contextual selector 也必须读取与候选相同的 public representation，
不能用更弱的 context-only comparator 充当 strongest control。

任何候选在完成上述资格化之前，`baseline_frozen=false`、`scientific_claim_allowed=false`
和 `gpu_runs_allowed=false` 继续保持不变。原生最终分数或离线 fixture 不能填入论文效果表。

## 可复用资产

- PIPE1：pinned generator/material、消息通道语义、route receipt hash chain；
- PIPE2：derived CSV adapter、10-seed shape/runtime qualification、严格 responsibility gate；
- PIPE3：fresh producer stage、bounded ActorExperience、公开 contract scorer、现有选人/capture；
- 共同：UNKNOWN/selected-only/成本日志和主版 PDF 的版本化维护规则。

下一张工程卡应先围绕 PIPE2 的 typed handoff descriptor（artifact path/schema/hash、
producer provenance、recipient pre/post action scope、显式 J/A/Y）做零调用 schema 与
mutation qualification，再接 source→assignment→future outcome lineage 和
same-information parity；它不是方法变更，也不授权 API。任何把 PIPE2 登记为 active
benchmark、把 PIPE1 修复为安全 runner 或改变生效方法的决定仍需共同确认。
