# 原 Q1 的下一基准：AppWorld 人工交接与 CooperBench 天然双 feature 合作

2026-09-23，零模型调用的基准可行性补充。**只完成一个公开 CooperBench 样本的本地获取、初始化和宿主机测试；没有运行其官方 Docker 评分、两个代码 agent、同伴验收或跨任务角色学习。** 本文件不更改现有 AppWorld 配对实验的 runner/config，也不选定最终基准。

## 判断

CooperBench 比 AppWorld 更自然地提供**两名执行者面对兼容性冲突**的工作：同一 Click 基底上的两个 feature，各有独立需求与测试。本次抽取的 `pallets_click_task/task2800` feature 1 与 7 能在本机初始化；两份参考补丁独立通过各自的本地测试，直接合并会冲突，完整参考补丁分别通过两组测试。这是可执行的协作压力样本，**不是“真实接收者验收 → 被评者角色 → 后续职责”已存在的样本**。官方 `coop` 预先把 feature 分给 agent，`team` 还预设 lead；测试器给的是功能结果而非接收者的行动前判断。需另建并验证该因果链。

| 边界 | AppWorld（现有本机工作） | CooperBench（本次小样本） |
|---|---|---|
| 原生任务 | 一名 agent 在状态环境中完成 API 读写；只读生产者→写入接收者是我们另加的协议 | 同一仓库基底的两个 feature，原生 `coop` 启动两名独立代码 agent、消息与补丁；参考补丁在本例直接合并冲突 |
| 接收者与判断 | 人工拆分后可让真正行动的接收者在写前封存 `accept/repair/reject` 与拟使用内容；先前一个开发例已有交付、独立核查和匹配行动，但未证明交付的边际价值 | 自由文本消息、每人轨迹和补丁可追踪；原生记录没有结构化的实际采纳、验收、返工或跨任务角色状态。`team` 的固定 lead 不能被误称为学出的角色 |
| 客观核验 | 原生 evaluator 核查最终状态；近例的任务写入与 `complete_task` 答案字段需分报 | 每个 feature 的 `tests.patch` 与双补丁合并测试能检验功能/兼容；`both_passed` 还可能来自 lead 单独实现两项，必须连同 `merge.strategy` 和双方贡献一起报告 |
| 首要识别风险 | 接收者本来就能自行读取全部信息；人为生产者可能没有边际价值；同一生成家族只有三个 sibling | 两项 feature 可并行做完，冲突/合并不必经过一个 agent 判断另一个的交付；固定分工、单人兜底与同 PR 多 pair 复用均会冒充社会学习 |

AppWorld 的既有边界和唯一真实开发见证见[可行性报告](AAMAS_PEER_JUDGMENT_FEASIBILITY_20260923.md)；CooperBench 的 runner/评分机制见[固定上游源码审计](../../../references/aamas/cooperbench_20260923/README.md)。两者都**没有现成的角色学习实验**。

## 可复核的小样本初始化与测试

- 上游固定在 CooperBench 提交 `63b9d44d9f39a02fccf5bf0052db48a917a011fd`。选择官方 `flash_10` 中的 `pallets_click_task/task2800` feature 1、7；该列表按既有模型表现人工挑过，故本例只作工程开发 smoke，不可当未见确认样本。Feature 1 修复 shell completion 的文件上下文释放，feature 7 加入嵌套 Context 校验；两者都碰 `src/click/shell_completion.py`。[来源说明](../../../references/aamas/cooperbench_20260923/dataset_README.md)
- 仅下载该 task 的 Docker/测试脚本、两个 feature 描述/补丁/测试及完整参考补丁：11 文件、47,909 bytes，逐文件 SHA-256 在[获取回执](../../../references/aamas/cooperbench_20260923/samples/pallets_click_task2800/fetch_receipt.json)。按任务 Dockerfile 的基底提交 `d8763b93021c416549b5f8b4b5497234619410db` 下载 Click 源码 tarball 341,879 bytes（设 8 MiB 硬上限），[基底回执](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/base_fetch_receipt.json)记录哈希。没有克隆 CooperBench 大仓库或拉 Docker 镜像。
- 在 `/tmp` 初始化该 Click 基底为临时 Git 仓库；五份相关补丁均通过 `git apply --check`。[初始化回执](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/host_init_receipt.json)保存路径与返回码。宿主机执行数据集自带 `run_tests.sh`，而非官方 Docker evaluator：base + feature 1 测试为 **67/68**，feature 1 参考补丁 + 自身测试 **68/68**；base + feature 7 测试 **67/72**，feature 7 参考补丁 + 自身测试 **72/72**；完整参考补丁对两套测试分别 **68/68、72/72**。逐次命令、时长、退出码与原始 stdout 在[负对照](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/base_negative_results.json)、[独立参考补丁](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/host_test_retry_results.json)、[整合参考补丁](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/combined_oracle_results.json)及相邻 `.log`。
- 两个 feature 参考补丁从同一基底分支独立提交后，宿主机 `git merge` 在 `src/click/shell_completion.py` 发生内容冲突；[合并回执](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/gold_merge_probe_retry.json)保存命令和冲突文件。第一次合并检查误假设默认分支叫 `master`，失败原始记录保留，随后读取实际 `main` 分支并纠正；这不是实验效果。第一次测试还因 `UV_PYTHON` 环境覆盖把 `uv pip` 指向外部管理解释器而失败，保留[失败记录](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/host_test_results.json)并在[修订记录](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/host_test_amendment.json)说明原样两例的重跑。
- 本机没有 `docker`、`podman`、`colima` 或 `nerdctl`；宿主机脚本实际选用 CPython 3.14.5，而任务 Dockerfile 使用 Python 3.11。所以上述通过/失败只能证明**本机源代码与原生测试脚本的轻量可执行性**，不是官方 `test_merged` 结果，也不能代替代码 agent 的真实交互。没有 LLM API 调用；没有美元成本测量。

## 对原创新点的适配边界与代价

如果采用 CooperBench，应先让两个初始同能力身份各自形成可审计的补丁/说明，再让**实际要集成或依赖它的人**在看到独立测试结果前封存判断：接纳哪些内容、实际用了哪些补丁、修复了什么、增加多少工作。离线运行测试只能校正该判断，不能充当判断本身。角色证据必须按被评价者、任务/消费者语境和判断来源跨任务更新，实际改变下一任务的职责机会；否则得到的只是代码合并 benchmark 或普通 pair 成功率。原生 `coop` 的预分配、`team` 的 lead 和 `solo-agent1` 兜底都要分层记录，不能当角色涌现。确认划分应至少按原始 PR/task 根分组；同根不同 feature pair 不是独立任务，最好另测留仓库迁移。

当前轻量宿主机六次测试在本机每次约 2.4–4.5 秒，整个样本源文件加基底压缩包不足 0.4 MB；这只估计**样本获取与参考测试**。正式运行另需官方 Docker 镜像/daemon、消息服务、CooperBench 适配器、两名真实代码 agent、审阅/返工阶段及跨任务状态。官方 `test_merged` 的 `timeout` 参数默认为 600 秒，但不是本例实测运行时间；agent 调用数、token、Docker 镜像体积、缓存与货币成本均未测，不能由宿主机测试外推。AppWorld 的模型调用与原生评分基础设施已有，但人为交接还需证明交付相对于独立接收者确有价值；目前只有一条受污染的开发见证，无后续职责效果。

**首个可执行步骤**：在有 Docker 的隔离执行机，仍用本次固定提交和开发样本，先做零 LLM 的官方沙箱 preflight：分别运行单 feature 参考补丁及完整参考补丁的原生测试，记录 `test_merged` 的 `apply_status`、`merge.status/strategy`、两组测试与是否走单人兜底；对照本地宿主机回执并估算镜像/测试时间。若这个评分层不能复现，先停在基准工程问题。通过后再冻结真正的接收者判断事件、观察权限、下一任务职责规则及同信息强对照，才花模型调用跑开发样本。不能拿本次参考补丁/测试或已挑选的 `flash_10` 结果作确认数据。

## 本机 Docker/Colima 只读可用性复核（同日）

本机是 macOS 26.3.2、Apple Silicon `arm64`，24 GiB RAM、15 个逻辑 CPU；`kern.hv_support=1`，系统存在 `Virtualization.framework`，APFS 数据卷约有 382 GiB 可用。Homebrew 7.0.4、`uv` 和 Python 3.12 已在 PATH；`docker`、`colima`、`limactl`、`podman`、`nerdctl`、`redis-server` 均不在 PATH，常见的 Docker/Colima 应用和 Homebrew Cellar 安装目录也不存在。因此**硬件/系统具备尝试 Colima VZ 的条件，但官方 Docker scorer 现在不能在这台机器上直接启动**；框架存在和 `hv_support=1` 不是 daemon/镜像/网络已通过的证明。本次只读检查没有安装、启动或拉取任何东西。

[CooperBench 固定提交 README](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/README.md)写 Python 3.12+、Docker 或云执行后端，以及 `coop` 通信用 Redis；同提交的 [`pyproject.toml`](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/pyproject.toml)元数据为 Python ≥3.10、`docker>=7.0` 等大量运行依赖。按更保守的 README，现有 Python 3.12 满足主机版本条件。固定提交的 [Docker backend](https://github.com/cooperbench/CooperBench/blob/63b9d44d9f39a02fccf5bf0052db48a917a011fd/src/cooperbench/eval/backends/docker.py)通过 Docker SDK 连接 daemon，以任务镜像启动容器；仅做参考补丁的**评分预检不需要 Redis 或 LLM key**，以后实际跑双 agent `coop` 才需要消息服务和模型适配。任务 Dockerfile 钉住 Python 3.11 与 Click 基底；宿主机之前的 Python 3.14 通过测试仍不能替代这个容器环境。

最短的后续本地路线是：在隔离环境按 [Colima 官方安装说明](https://github.com/abiosoft/colima/blob/main/README.md)用 Homebrew 安装 `colima` 和 Docker CLI（Lima 由依赖解决），以 Docker runtime 和 `vz` VM 类型启动，再用 `docker version` 确认 daemon 可连接；将 CooperBench scorer 固定到上述提交，在开发样本上先测单 feature 参考补丁与完整参考补丁，再调用官方 `test_merged` 记录冲突/兜底路径。`coop` 阶段才启动 Redis。[Colima 官方说明](https://github.com/abiosoft/colima/blob/main/README.md)给出 `brew install colima`、`brew install docker`、`colima start`；默认 VM 为 2 CPU/2 GiB/100 GiB 虚拟磁盘。这里的命令是**待执行步骤**，本次没有运行。实际代码 agent 和其镜像可能需要更多内存；评分预检宜先用单并发，不能把默认配置视为已验证的性能保证。

下载量目前只能给边界：已取得的样本与 Click 基底压缩包合计约 0.39 MB；安装 Colima/Lima/Docker CLI、首次 VM 基础镜像、CooperBench Python 依赖和 `akhatua/cooperbench-pallets-click:task2800` 任务镜像另计。Docker Hub 标签元数据的只读请求在本机遇到 TLS EOF/SSL 连接失败，故**镜像层大小及总下载量未核实**；应先恢复 registry 可达性并读 manifest，再决定是否在这台 Mac 拉镜像。保守工程预留是数 GiB 磁盘与相应网络流量，属于估计而非实测账单；382 GiB 空间不构成眼下的硬阻碍。更可能的卡点是 registry/TLS、Colima 首启虚拟机、Apple Silicon 镜像架构匹配、Python 包依赖/固定源码版本一致性，以及 Docker sandbox 的挂载/权限。官方[数据说明](../../../references/aamas/cooperbench_20260923/dataset_README.md)称任务镜像支持 `linux/arm64`，但这个标签的实际 manifest 本机尚未核验。因此目前可称“**低模型成本的零 LLM 预检有明确执行路径**”，不能称“本机官方评分已跑通”或保证低下载/低时间成本。

## 官方 Docker scorer 工程预检：TLS 停机（同日）

随后按固定样本启动有界、零 LLM 的官方 scorer 工程预检。任何安装、VM 启动或镜像拉取之前，先落盘[配置与资源上限](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/config.json)和[逐步事件流](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/events.jsonl)。配置限定上游提交、样本、目标镜像、匿名 manifest 每端点最多两次、镜像压缩层总量最多 2 GiB、拟用 Colima 上限 2 CPU/4 GiB/30 GiB、总时长 30 分钟，并禁止触碰已有容器和调用模型。预检实际只走到第一项只读网络核验。

对 `auth.docker.io` 的匿名 OCI 令牌请求连续两次均在本机 TLS 校验时失败：`CERTIFICATE_VERIFY_FAILED`，证书与 `auth.docker.io` 主机名不匹配。[原始错误日志](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/official_logs/manifest_probe.log)和[机器可读结果](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/official_preflight_result.json)留存两次尝试及停机原因。这只证明**本机当前网络/证书路径无法安全完成该请求**，尚未诊断是代理、证书链还是别的环境问题，不能推断 Docker Hub 镜像整体不可用。没有关闭 TLS 校验或继续试探规避；未取得令牌，故无法读取 manifest，`linux/arm64` 是否在该标签、镜像层大小及可拉取性仍未知。

按预置规则在此停止：**未安装 Colima/Docker，未启动 VM，未拉镜像，未运行官方 `test_merged`，未调用 LLM。** 宿主机 68/68、72/72 和合并冲突的结果仍仅是前述轻量开发 smoke，不能升级为官方 Docker 评分，更不是角色学习实验。下一步需要在合法可用的本机证书/网络路径或另一台已可访问 registry 的 Docker 主机上，重新从匿名 manifest、架构和层大小的有界检查开始；这些通过后才可按同一固定样本做官方参考补丁评分，并分开记录 apply、merge、两组测试与 fallback strategy。

另按项目已有配置对唯一已知科研服务器做了一次只读 SSH 可达性检查；本机到该主机的 TCP 22 超时，远端命令没有执行，因此远端 Docker/镜像状态仍为 `UNKNOWN`，不能把它当作已可用的绕行路线。[检查回执](../../../artifacts/analysis/aamas2027/cooperbench_task2800_20260923/remote_readonly_feasibility.json)记录范围、超时与零远端改动。
