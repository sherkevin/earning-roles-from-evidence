# earning-roles 项目结构

本文件只说明信息应该放在哪里。研究含义的唯一生效来源是 [`docs/research/canonical/README.md`](docs/research/canonical/README.md)；项目目标是 [`docs/coordination/GOAL.md`](docs/coordination/GOAL.md)。

```text
.
├── docs/
│   ├── research/
│   │   ├── canonical/       六类 active 文档的唯一登记
│   │   ├── versions/        storyline/method/benchmark-baseline 及三份评价标准版本
│   │   └── *.md             dated 研究报告、候选设计和证据记录
│   ├── coordination/        Goal、任务状态、task report、阶段门
│   ├── user/decisions/      一文件一决议；只存已对齐的小选择和不变量
│   ├── paper/aamas2027/     venue 要求、兼容索引、证据矩阵和论文说明
│   ├── scientist/           科学分析与交接历史
│   ├── engineer/            工程日志、结果、runbook 和交接
│   ├── reviewer/            审查交付
│   ├── chats/               短交接 memo
│   └── archive/             完整历史快照，不作为当前规范
├── article/                 可编译论文源、模板和构建产物
├── configs/                 实验卡、manifest、模型与环境配置
├── scripts/                 runner、scorer、校验和分析代码
├── experiments/logs/        JSON/JSONL 原始运行证据、失败、UNKNOWN 和 summary
├── artifacts/               统计、图、forensic 和审稿产物
├── references/              固定论文、开源源码和调研来源
└── workspace/               实现代码与可复用组件
```

## 六份 active 文档

每类最多一个 `ACTIVE` 版本，由 [`docs/research/canonical/active_versions.json`](docs/research/canonical/active_versions.json) 指向。旧版本不得删除；新版本必须保留旧文件并写明 supersedes。候选报告、任务报告和实验日志不能抢占 active 名额。

## 决议与任务

决议不是研究论文的替代物。只有一个小的已对齐工程/方法选择、争议取舍或不可变约束才进入 `docs/user/decisions/`，并按 0001、0002 顺序建立索引。普通进展进入 task report；实验细节进入配置和 JSONL 日志。详见 [`ADR0039`](docs/user/decisions/0039-canonical-research-documents-and-decision-boundary.md)。

## 变更与复现

科学文档含义、评价标准或 Goal 发生改变前，先完成用户与助手的双重确认并写版本/决议；拼写、链接和机器索引可修复但须在 task report 记录。实验必须先落 config，再实时写 raw events，最后写 summary；真实 API、模型、数据、硬件、代码和失败边界都要可追溯。未通过资格门时保留 `UNKNOWN`，不能用文档整理代替实验。
