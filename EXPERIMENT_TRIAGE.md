# Experiment Triage

> 事实源：[progress/experiments.json](progress/experiments.json)  
> 可执行校验：`python3 scripts/validate_project.py`

本文件定义实验进入仓库、保留外部复现或复用现有实现的治理规则。实验清单、分类值和完成状态只在 JSON 事实源中维护；本文件不复制 30 项明细或手工维护完成百分比。

## 1. 分类回答的问题

`triage` 回答“这个实验的实现与维护责任放在哪里”，不是实验进度：

| 分类 | 实现位置 | 本仓库责任 | 适用判断 |
|---|---|---|---|
| `SHIP` | 本仓库 `experiments/` | 实现、样例、测试和文档全部随书发布 | 教学核心，能以轻量、无密钥、可重复方式运行 |
| `KEEP-EXT` | 外部官方来源或作者本地复现环境 | 固定来源、配置、步骤、样例结果和限制 | 依赖外部系统，或目标是复现官方流程而非重写一份实现 |
| `ALREADY` | 本仓库已有稳定实现 | 维护一份实现，实验只建立复用与跨章引用 | 现有脚本已经满足实验语义和验收，不应重复建设 |

生命周期状态另行使用 `planned`、`ready`、`in-progress`、`verified`、`blocked`。例如，`ALREADY + ready` 表示实现已存在、可以开始采集实验数据，但不等于实验已经验证完成。

## 2. 决策顺序

每项实验按以下顺序判断，命中后停止：

1. **现有实现是否语义等价？** 路径真实存在，命令可执行，并且覆盖该实验的输入、输出和验收；满足则为 `ALREADY`。
2. **能否轻量随书交付？** 可以使用 Python、Shell、静态 Web 或 JSON 在仓库内无密钥运行，并能提供自动测试；满足则为 `SHIP`。
3. **是否必须依赖外部能力？** 目标是复现官方工作流，或依赖托管服务、商业工具、重型环境及不可分发资料；满足则为 `KEEP-EXT`。
4. 三者都无法形成可验证证据时，不得标记 `verified`，应保持 `planned` 或改为 `blocked` 并写清解除条件。

“代码看起来相似”不能判为 `ALREADY`；“未来打算写进仓库”也不能判为 `SHIP` 已完成。分类只决定治理去向，不替代实验验收。

## 3. 三类机器可校验字段

### 3.1 SHIP

必须包含：

- `repository_path`：实验根目录。
- `readme_path`：目标、运行方法、指标与限制。
- `sample_input`、`sample_output`：可提交、无敏感数据的最小样例。
- `test_path`：自动测试入口。
- `command`：从仓库根目录运行的确定命令。

进入 `verified` 前，上述路径必须真实存在，命令和测试必须通过，样例输出必须记录约定指标。当前校验器首先检查字段完整性；后续实验实现任务再检查实际路径与执行结果。

### 3.2 KEEP-EXT

必须包含：

- `external_source`：公开官方页面、外部仓库或明确的作者本地资料说明。
- `pinned_version`：版本、提交或内容哈希，避免“最新版”漂移。
- `configuration`：复现环境和仓库边界。
- `reproduction_steps`：非空、按顺序可执行的步骤。
- `sample_result`：读者应得到的基准结果。

涉及本地 `specs.md-portal/` 时，JSON 只发布官方 URL、抓取内容哈希和复现说明；本地 portal 本身继续由 `.gitignore` 排除。真实密钥、商业素材和不可再分发文件不得进入仓库。

### 3.3 ALREADY

必须包含：

- `reused_implementation`：已存在实现路径；多个入口用分号分隔并共同承担实验能力。
- `cross_chapter_references`：至少一个其他章节 ID，说明这份实现为什么值得复用。
- `command`：直接调用已有实现，禁止再指向计划中的 `experiments/<id>/` 占位目录。
- `acceptance`：描述现有实现必须继续保持的可观察行为。

如果现有实现失去语义等价性，应将实验重新分为 `SHIP` 或 `KEEP-EXT`，不能让 `ALREADY` 成为逃避实现的标签。

## 4. 可校验样例

| 分类 | 实验 | 判断依据 | 校验证据 |
|---|---|---|---|
| `SHIP` | `EXP-01-01` 同一 Intent 多次生成方差基线 | 纯文本与 JSON 即可运行，是全书核心概率性证据 | `repository_path`、样例、测试和 quickstart 命令均已声明；当前为 `planned` |
| `KEEP-EXT` | `EXP-01-03` AI-DLC 三阶段官方流程复现 | 目标是复现 specs.md 官方方法，不在书仓库复制框架 | 官方 URL、作者本地抓取 SHA-256、三步复现法和样例结果均已声明 |
| `ALREADY` | `EXP-07-01` 仓库确定性门禁组合器 | `scripts/ci_check.py` 已聚合六类确定性检查 | 运行 `python3 scripts/ci_check.py`；复用于 CH-04、CH-06、CH-08 |
| `ALREADY` | `EXP-08-01` 发布候选来源清单校验器 | readiness 与 release 脚本已实现来源一致性和 Manifest | 复用 `check_release_readiness.py` 与 `prepare_release.py`；引用 CH-06、CH-07 |

## 5. 初步分类鸟瞰

| 维度 | 结果 |
|---|---|
| 总实验 | 30 |
| `SHIP` | 18 |
| `KEEP-EXT` | 10 |
| `ALREADY` | 2 |
| S / M / L | 10 / 10 / 10 |
| `planned` / `ready` | 28 / 2 |

章节分布保持每章 3 项：CH-01 至 CH-06、CH-09、CH-10 各为 `2 SHIP + 1 KEEP-EXT`；CH-07 与 CH-08 各为 `1 SHIP + 1 KEEP-EXT + 1 ALREADY`。

## 6. 修改与自动记录协议

1. 在 `progress/experiments.json` 修改分类、条件字段和更新时间。
2. 运行 `python3 scripts/validate_project.py`；缺少对应分类字段时必须失败。
3. 运行 `python3 scripts/generate_progress.py --actor <actor>`。
4. 生成器自动记录 `triage` 和实验状态变化，刷新快照、变更日志与可视化队列。
5. 在正文或章节 README 中只引用稳定实验 ID，避免复制会漂移的分类统计。

`tests/test_validate_project.py` 覆盖三类条件字段的负向测试；任何规则变更必须同时更新事实源、校验器、测试和本文档。
