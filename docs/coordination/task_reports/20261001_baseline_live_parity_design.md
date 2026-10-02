# ArtifactRole baseline live parity 设计门 — 2026-10-01

状态：`PARTIAL / DESIGN_ONLY`。本报告只冻结下一道 runner 工程门的边界，不激活 benchmark
cell、不选择第二 root authority，也不授权新的 API/GPU/A800 科学实验。

本轮已把 runtime/material binding 的纯合同接缝实现为
`LiveRuntimeBinding`/`validate_live_root_receipt`，并加入定向测试；同时将 PIPE3 composition
升为 v1.3，支持显式 `policy_factory` 与 `policy_name` 注入，默认仍为 terminal-only。用
`no_update` 做了一个负向 qualification：它正确保持 `policy_updates=0`，同时把 later credit
作为已提交但不更新 policy 的合法控制；它不会被 terminal-only 的“必须发生 update”条件误记为
失败或成功。它仍未接入七 arm live runner；没有任何科学 cell 被激活，历史 v1.2 回执不变。

## 为什么不能直接把 v16 当 live parity

当前 `peerrolebench_policy_matrix_runner_v1.py` 的 v16 receipt 只使用 hand-authored offers，
所有成本字段都是 `offline_fixture=0`，没有真实 producer/recipient/adoption scorer、
canonical ledger、later outcome 或独立 policy history。因此它证明七个 policy arm 能消费
相同的菜单、schedule、registry、UNKNOWN 和 selected-only 合同，但不能证明它们在真实任务上
公平运行。

同时，“相同菜单”不等于“相同结果”：不同 policy 可能选中不同 candidate，真实 artifact、
recipient action 和 terminal outcome 会随之改变。把所有 arm 强行绑定到一份结果会制造错误的
同信息假设。

## 下一道 runner 的两层结构

### 1. Matched replay（合同层）

使用一份封存的 canonical public event trace，对七个可执行 arm 分别重放：

- 相同 candidate menu、candidate `id@version`、source/model/config digest；
- 相同 arrival schedule、read cut、propensity 记录和 public-prefix；
- 相同 responsibility/UNKNOWN 分类、selected-only 规则和 feedback lineage；
- 各 arm 独立 policy namespace，但输入 trace 的 digest 必须一致；
- 记录 update count、state digest、manifest root、snapshot/restore 和 no-future/no-private 检查。

这一层只回答“同一合法信息是否被不同 policy 以各自声明的规则消费”，不回答效果优劣。

### 2. Independent live arm history（执行层）

在同一个 root/seed/预算下为每个 arm 建立独立 namespace，运行真实 pinned producer、recipient、
adoption scorer 和 action：

- 每个 arm 使用相同初始菜单、RNG schedule、模型/API/工具预算和 cost schema；
- policy 的实际 chosen candidate 决定 delivery source digest，不能事后替换成另一 candidate；
- 真实结果重新产生该 arm 自己的 Qp、judgment、action、terminal outcome 和 UNKNOWN 分母；
- source publication 不更新持久 policy；只有 assignment 在 task start 前封存、且 later outcome
  完成后，才允许一次 selected-only delayed update；
- uniform/no-update 也消费同一 public event stream，但不因反馈更新；raw acceptance、
  terminal-only、contextual trust、pooled 和 RARE 只能读取各自预注册的合法字段；
- 每个 arm 必须保存 native/auxiliary manifest roots、可见输入 digest、逐字段成本和失败回执。

这一层只关闭“真实 runner 能否公平执行”的工程门。单 root/单 seed 不足以估计 superiority、
信息增量或跨 root 泛化，必须写 `scientific_claim_allowed=false`、`independent_root=false`
和 `effect_not_estimable=true`。

## 必须先实现的接口约束

机器可读的候选卡已登记为
[`n03_baseline_live_parity_candidate_v0.1.json`](../../../configs/aamas2027/n03_baseline_live_parity_candidate_v0.1.json)。
它明确 `DESIGN_ONLY`、0 API/0 GPU 和 `scientific_claim_allowed=false`，在第二 root authority
确认前不得被 runner 当成 active manifest。

1. 将当前 PIPE3 composition 的 `TerminalOnlyPolicy` 改为显式 policy factory 注入；不改变
   active method，只允许 runner 选择已登记的 comparator。
2. 为每个 arm 写入 policy、state、encoder、feature、registry、schedule 和 prompt/model
   config digest；RARE 需要固定同信息 feature vectors/encoder digest。
3. 将 producer source digest 与 selected candidate 绑定；candidate treatment mismatch、
   recipient-only/mixed ownership 和 scorer/resource failure 均为 `UNKNOWN/no-update`。
4. 增加 target 后的第三个 pre-execution decision 或等价 continuation receipt，才能检查
   `update → next choice`；在此之前只报告 update committed once。
5. measured `COST_FIELDS` 必须由真实阶段计时/计数填充；不能复用离线零值。
6. closest published/Meta-Team-L2-public 尚未有可执行 adapter，必须显式 `BLOCKED/NO-GO`，
   不得为了凑八个 arm 写手工 trust score。
7. lower-bound distinction 也要预注册：`uniform`、`no_update` 和其他 policy 必须共享同一
   冻结的 base-score/feature 输入；若 base scores 来自额外模型，必须把它计入每个 arm 的
   信息与成本，不能让 RARE 的 feature-only 输入和 trust policy 的 score 输入形成隐性优势。
   当前 one-hot fixture features 只用于接口测试，不能当作模型证据。
8. live manifest 还要绑定实际 neutral material/root digest、task-contract hash、sandbox
   runtime lock/settings/worker-limits、scorer config 和每个 selected candidate 的 source
   snapshot digest；这些不能只由 registry digest 间接推断。
9. live cost gate 必须使用 `require_measured=true`。真实的 0 API/GPU 也要有阶段 receipt
   作为 measured zero，不能沿用 `offline_fixture` 零值。

## 通过条件与停止条件

通过条件是 matched replay 和 independent live arm history 都完成，且所有 arm 的错误、
UNKNOWN、成本、manifest/replay 和 pre-execution assignment 顺序可审计。任一候选身份、
责任归因、可见性、成本或 future-read 失败，立即保留 receipt 并停止，不改 label、不扩大
timeout、不启动 A800。

这份设计不替代第二 root authority。第二 root 未经确认前，只能在当前 PIPE3 上做 runner
工程资格，不能把它写成 benchmark freeze 或论文科学结果。

## v1.3 review correction — 2026-10-02

独立 parity review 对 v1.3 seam 做了 P0 复核。当前 composition 的 later event 仍固定为
`terminal_outcome`，而 `raw_acceptance`、`contextual_trust`、`pooled_controller` 和 `RARE`
声明的 accepted source 不同；如果只检查 delayed credit，就会出现非本 arm 通道的假通过。
因此 v1.3 现在要求声明了非空 accepted source 的 arm 必须有实际 policy update，否则为
`UNKNOWN`。`no_update` 是唯一允许“credit committed、policy update 为零”的工程 negative
control；这不代表它已经是科学 baseline。

复核还确认，当前 qualification 使用 hand-authored base-score overlay，role evidence 仅
检查最终 selected candidate 有 published evidence；没有 evidence mutation 导致的
decision-digest mutation。因此当前 composition 只证明 lineage、assignment-before-task-start
和 delayed-credit seam，不能证明 selector 消费 evidence，也不能宣称 update-to-choice
因果效果。七 arm live parity 必须先完成每 arm 的合法 public feedback adapter 与
evidence-consumption mutation test。
