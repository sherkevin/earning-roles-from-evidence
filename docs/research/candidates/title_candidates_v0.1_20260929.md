# 论文标题候选 v0.1

- **状态**：`SELECTED_WORKING_TITLE`
- **日期**：2026-09-29
- **当前工作标题**：`Learning Roles from Situated Peer Judgments in Multi-Agent Collaboration`
- **用途**：在不改故事线和 Goal 的前提下，寻找能表达动态、自进化和跨任务适用性的正式标题。
- **作者确认**：2026-09-29 选择首选标题，已同步当前 pre-results/proposal 稿件；历史 `main.tex` 保持不变。

## 1. 标题必须传达的四个信息

1. 角色不是预先分配的，而是通过交互和证据逐步获得；
2. 角色会随新反馈和未来任务动态变化；
3. 关键证据来自真正使用交付物的 peer/recipient，而不是抽象总分；
4. 标题要允许 peer selection、tool selection、责任分派和其他协作系统复用，而不把论文锁死在某一个任务或代码 benchmark。

“Self-evolving”只能作为方法/结果已被实验支持时的正式表述；在当前 pre-results 稿中，它是目标定位，不是已验证结论。

## 2. 候选标题

| 候选 | 形式 | 优点 | 风险 |
|---|---|---|---|
| **Earning Roles: Self-Evolving Responsibility from Situated Peer Judgments** | A:B | “Earning”表达角色由证据获得；self-evolving 与 responsibility 同时出现；不绑定具体任务 | 需要摘要第一段解释 earning 的含义 |
| **Who Should Do What Next? Self-Evolving Roles from Situated Peer Judgments** | 问号 | 直接问动态责任分派；读者立刻知道未来 assignment 是结果 | “self-evolving”仍需实验证据支撑 |
| **Know Who You Are: Self-Evolving Roles from Situated Peer Judgments** | A:B | 记忆点强，具有更大想象空间 | 容易被理解为 agent 自我反思/身份建模，未直接点出责任分派 |
| **Know Who to Trust: Earning Dynamic Roles from Situated Peer Judgments** | A:B | 保留用户提出的语感，同时更接近选择和分派 | “trust”可能把创新误读成普通 reputation |
| **Can Agent Teams Learn Who Should Do What? Dynamic Roles from Situated Peer Judgments** | 问号 | 最清楚地呈现科学问题，适合尚未承诺结果的稿件 | 想象空间略小，标题较长 |
| **From Situated Judgment to Dynamic Responsibility: Self-Evolving Roles in Agent Teams** | A:B | 因果箭头清楚，适合方法论文 | 稍偏说明性，记忆点不如前四个 |
| **Who Gets the Next Task? Earning Dynamic Roles from Situated Peer Judgments** | 问号 | 把 future assignment 变成可感知的具体问题；sharp | “task”可能比一般 responsibility 稍窄 |
| **When Peers Shape the Team: Self-Evolving Roles from Situated Use** | A:B | 强调协作关系和更广泛适用性 | “situated use”不如 “peer judgment”可检索、可识别 |

## 3. 初步推荐

首选：

> **Earning Roles: Self-Evolving Responsibility from Situated Peer Judgments**

它同时满足用户提出的三点：有动态和自进化，不把领域锁死在某个 benchmark，并且保留核心创新的证据来源。`Earning Roles` 还与项目名一致，但没有把项目名直接当作技术名。

如果希望标题更像明确的 AAMAS 科学问题，第二选择是：

> **Who Should Do What Next? Self-Evolving Roles from Situated Peer Judgments**

如果希望最大化记忆点，可以使用：

> **Know Who You Are: Self-Evolving Roles from Situated Peer Judgments**

但这一版必须在摘要中第一时间说明“know who you are”指的是由其他 agent 对实际交付的使用证据形成动态责任画像，而不是 agent 的自我认知。

## 4. 当前不建议的写法

- `Learning Roles from ...`：准确但过于平直，没有传达动态演化；
- `Self-Evolving Multi-Agent Systems`：范围过宽，无法区分 skill、memory、workflow 和 role evolution；
- `Dynamic Reputation for ...`：会把 situated judgment 降格成一般 reputation；
- `Adaptive Peer Selection ...`：会把论文主线提前缩成 selector 机制，丢掉 recipient use、责任归因和 future assignment；
- `Who Are You?` 单独作为标题：没有指出角色如何获得、谁提供证据以及证据如何改变责任。

标题只有在正式方法和结果确认 self-evolving/dynamic claim 后，才应替换主稿标题；候选版本不改变 active storyline、method 或 benchmark 文档。
