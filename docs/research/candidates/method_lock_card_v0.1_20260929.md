# Candidate method-lock card v0.1 — responsibility-safe delayed role evidence

- **状态**：`CANDIDATE_NOT_ACTIVE`
- **日期**：2026-09-29
- **目的**：把故事线转成一个可逐事件重放、可与同信息 contextual trust 对照的最小候选；不宣称创新或效果。
- **生效规则**：不替换 `method_v1.0`；只有用户与助手确认、零调用不变量通过、closest-method parity 通过后才可提议新 active 版本。

## 1. 主 estimand 和最小原始输入

主 estimand 暂定为 **独立 producer-contract/later-use 目标上的 out-of-sample Brier risk 增量**；team quality–complete-cost 是第二层闭环 estimand，不在选择器更新中偷偷混入。给定一个不可变事件 `e`，只引入下列原始输入：

| 符号 | 原始来源 | PIPE3 case |
|---|---|---|
| `x` | `e.task_context` | `{"stage":"draft","queue":"priority","required":"FIFO"}` |
| `C` | `e.candidates` | `["peer-b@v1","peer-c@v1"]` |
| `a,p` | `e.chosen` | `a="peer-b@v1`, `p=0.5` |
| `D` | `e.delivery` | `{"sha256":"...","source_version":"src-7"}` |
| `J` | `e.recipient_judgment` | `{"decision":"accept","target_role":"producer","target_paths":["queue.py"]}` |
| `A` | `e.recipient_action` | `{"action":"use","changed_paths":[]}` |
| `Q` | `e.producer_contract` | `{"status":"PASS","coverage_complete":true}` |
| `Y` | `e.later_outcome` | `{"status":"PASS","independent":true}` |
| `k` | `e.arrival_index` | `J` at 5, `Q` at 7, `Y` at 9 |

`e` also contains the immutable `decision_id`, `delivery_id`, `candidate_id@version`, hashes and `evidence_version`. These fields are lineage keys, not model features. Missing/invalid/permission-failed fields produce `UNKNOWN`; they never become a negative label.

## 2. Eligibility and target separation

Responsibility is a typed provenance gate, not the target. Define `g(e)` from `Q`, `J`, `A`, ownership contract and lineage:

```text
g(e)=1 iff Q and Y are complete,
       J targets producer,
       J binds to D,
       changed recipient paths are empty,
       producer-owned defect or independent later-use evidence is present.
```

`y(e)` is then produced by the fixed label mapping from the independent target `Y/Q`; `J` is an input signal but is not allowed to inspect hidden `Y`. A visible recipient acceptance/rejection signal is stored separately: when `g(e)=0`, it is not a producer label. The RARE arm records `status=ineligible` and `label=None`; missing, malformed or permission-failed signals use `status=unknown` and are skipped. An ungated raw-label arm may consume the visible signal only as a pre-registered gate ablation. The four analysis arms are fixed before any result: `gate-only`, `judgment-only`, `gate+judgment`, and `contract-only`, all evaluated on the same independent later-use target.

**Case**: if `A.changed_paths=["processor.py"]` and `processor.py∈R` while `Q=PASS`, then `g=0`, `y=UNKNOWN`; the recipient's repair remains an observed outcome and cannot punish `peer-b`.

## 3. Feature and state

`φ(x,v)` is a fixed signed-hash vector of dimension `d=64`, generated only from `x`, candidate `v=id@version`, and public workflow fields. Hash seed and `encoder_version="hash64-v1"` are sealed in `decision_id`.

The policy state is `(θ_ref,A,b,W,H)`:

- `θ_ref∈R^64`: protected public anchor, initialized to zero;
- `A,b∈R^64`: diagonal fast sufficient statistics;
- `W`: at most `B=256` eligible `(key,φ,w,y)` events;
- `H`: at most `K=128` immutable old-root holdout rows `(φ,y)`.

For feature `φ_i` and an immutable visible weight `w_e∈[0,1]` (default `1`
after the gate; `w_e=0` is recorded as an explicit zero-weight observation),

$$
A_i=\lambda+\sum_{e\in W}w_e\phi_{e,i}^2,\qquad
b_i=\sum_{e\in W}w_e y_e\phi_{e,i},\qquad
\theta_{raw,i}=b_i/A_i,\quad \lambda=1.
$$

When `W` is empty, the protected anchor is exposed directly. Otherwise the
output is the bounded anchor projection

$$
\theta=\theta_{ref}+\operatorname{Proj}_{\|z\|_2\le 2}(\theta_{raw}-\theta_{ref}).
$$

For candidate `peer-b@v1` in the case above, the selector evaluates `φ(x,peer-b@v1)` and `φ(x,peer-c@v1)`; it does not read `Y`, private scorer state or another policy's memory.

## 4. Selection, assignment and evidence consumption

For each candidate `v∈C`,

$$
s(v)=\sigma(\phi(x,v)^\top\theta),\qquad
\pi(v)=(1-\epsilon)\operatorname{softmax}(s(v)/T)+\epsilon/|C|,
$$

with fixed `ε=0.10,T=1`. The sampled `a` and propensity `p=π(a)` are sealed before delivery.

Before the next task executes, a **different owner** receives only `(θ, public evidence digests, H summary, state_version)`. It must write `assignment_id`, `owner_id`, `evidence_ids`, `state_version`, `chosen`, and `p` before the next delivery. The mutation test changes only evidence while holding menu, RNG and p fixed; a changed `decision_digest` is required to prove evidence was consumed.

## 5. Arrival, correction and bounded update

Feedback arrivals use `k`, not episode order. For an eligible event:

1. verify lineage, ownership, version and independent target;
2. if `key` is duplicate, no-op;
3. if a correction supersedes an event in `W`, subtract the old contribution and add the new one;
4. if the correction is outside `W`, append a bounded `UNKNOWN` queue entry and do not silently rewrite the current state; `K_pending=128` bounds both pending correction keys and superseded tombstones;
5. insert into `W`, evict the oldest row when `|W|>B`, update `A,b`, and record the new state digest.

Every event is processed once. Snapshot/restore must produce the same digest and next choice. Selection is `O(|C|d)`, eligible update/correction is `O(d)`, and state is bounded by `O(d(B+K)) + O(K_pending)` with `B=256`, `K=128` and `K_pending=128`.

## 6. Same-information baseline and kill condition

The primary control is a delayed contextual trust policy that sees exactly the same `(x,C,D,J,A,Q,Y-arrival status,ownership,version,k,p)` fields, candidate menu, exploration and state cap. It differs only in the update/assignment rule. Raw acceptance, terminal-only, no-update and pooled controller remain additional controls.

The candidate is killed if the contextual trust control reproduces the complete mechanism's state, pre-execution assignment, unseen-root Brier/quality-cost utility and online cost within the pre-registered equivalence margin. It is also killed if `gate-only` leaks the independent target, if identity permutation changes choices without persistent experience, or if recipient-owned edits receive producer penalties.

## 7. Required qualification before active promotion

Zero-call tests must cover: eligible producer defect; recipient-only edit; sink-only failure; mixed edit; no attribution; duplicate; late correction; out-of-window correction; version replacement; snapshot/restore; identity permutation; evidence-consumption mutation; and bounded queue/tombstone state. Only after these pass may a development root be used. No API/GPU result is attached to this card.
