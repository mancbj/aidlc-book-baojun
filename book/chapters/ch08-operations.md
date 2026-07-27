# 第 8 章 · Operations：从交付候选到可持续运行

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-08 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D22-T03 · 完成章节审校与证据对齐 |
| Draft Completeness | 正式十章生产线可读稿；D22-T03 五类审校已完成 |
| Primary Question | 如何通过 Build、Deploy、Runtime Verify、Monitor 与恢复机制，让通过测试的候选物成为可运行、可观测、可回滚的系统？ |
| Reader Outcome | 能够定义构建凭证、环境门禁、部署策略、冒烟验证、监控指标和回滚 Runbook |
| Related Experiments | `EXP-08-01`、`EXP-08-02`、`EXP-08-03` |

## 01 · Question：为什么“测试通过”还不是运行成功

第 7 章回答了验证问题：如何组合确定性检查、独立测试、模型评审和人工判断，证明 AI 参与的交付候选不是模型自评的幻觉。第 8 章继续往前一步：**候选物已经通过验证之后，如何让它成为可运行、可观测、可回滚的系统？**

这就是 Operations 的范围。

在 AI-DLC 中，Operations 不是“最后把东西上线一下”，也不是把测试通过的文件复制到某个地方。它是一组运行责任：构建必须可追溯，部署必须有环境门禁，验证必须接近真实运行条件，监控必须能发现偏差，恢复机制必须在出事前准备好。

如果没有 Operations，团队会在两个地方犯错。

第一，把交付候选误认为运行系统。一个候选物可能通过 CI、链接检查和人工审校，但它还没有被打包、部署、冒烟验证和监控。第二，把发布成功误认为持续成功。页面能打开、服务能启动、版本能创建，只说明某一刻的动作完成；真正的运行状态还要看监控、告警、回滚和后续恢复。

AI 参与后，这个问题会更明显。AI 可以很快帮你准备 Release Notes、生成部署配置、修复失败脚本，也可以同样快地把错误发布范围扩大。如果 Operations 没有边界，AI 的速度会让“上线”显得像一件轻飘飘的小事；但真正的运行系统从来不是一句“已发布”，而是一套可以追溯、观察和恢复的责任链。

因此，本章的核心问题是：**如何通过 Build、Deploy、Runtime Verify、Monitor 与恢复机制，让通过测试的候选物成为可运行、可观测、可回滚的系统？**

读完本章，读者应能完成三个动作：

1. 为一个发布候选定义来源清单、构建凭证和文件哈希。
2. 为部署定义环境门禁、部署策略、冒烟验证和监控指标。
3. 为失败场景准备回滚 Runbook，并把恢复过程写入可复核记录。

### Gate

- [x] 核心问题只有一个：如何把通过验证的候选物推进到可持续运行。
- [x] 读者结果可以观察：能定义构建凭证、环境门禁、部署策略、冒烟验证、监控指标和回滚 Runbook。
- [x] 本章不重新讨论验证强度选择；那是 CH-07 的重点。
- [x] 本章不把当前 Operations 工具写成成熟生产能力；目录中的参考实现仍需标注 alpha / planned 边界。

## 02 · Framework：Operations 的五段运行链

本章用五段运行链描述 Operations：

```text
Build
  从已验证来源生成可追溯、可复现、带哈希的候选资产

Deploy
  将候选资产发布到明确环境，并记录环境、权限、版本和部署策略

Runtime Verify
  在目标环境执行冒烟验证、入口检查、发布清单核对和回归门禁

Monitor
  观察关键指标、错误信号、用户入口、告警和漂移

Recover
  在失败时按 Runbook 回滚、降级、恢复数据或暂停发布
```

这五段与 CH-07 的验证链不同。CH-07 问的是“候选物是否可以被批准”；CH-08 问的是“批准后的候选物能否进入运行，并在运行中被观察和恢复”。换句话说，验证解决正确性证据，Operations 解决运行责任。

也可以把二者关系写成一句话：

```text
CH-07 Verify: Should this candidate be approved?
CH-08 Operations: Can this approved candidate run, be observed, and be recovered?
```

这一区分很重要。很多团队在 AI 辅助开发里会把 CI 绿勾当成“已经上线成功”，或者把 GitHub Release 创建成功当成“用户已经可用”。前者混淆了验证与运行，后者混淆了部署动作与运行状态。Operations 的任务，就是让这两种混淆都被拆开。

### 2.1 Build：构建必须回答“从哪里来”

Build 的第一职责是来源可追溯。一个可发布资产至少要知道：源提交是什么，事实源身份是什么，构建时间是什么，输入文件有哪些，输出文件哈希是什么，是否混入了未审阅状态。

构建不是“把文件放进 zip”。它要回答三个问题。

- Source：这些资产来自哪个提交、哪组事实源、哪次 readiness？
- Process：它们由哪个脚本、哪个环境、哪个 workflow 构造？
- Output：生成了哪些文件，每个文件的哈希和大小是什么？

在本书项目里，`scripts/prepare_release.py` 和 `scripts/prepare_pages.py` 都体现了这一点。Pages 发布树会记录 source facts、commit、generated_at、workflow_run 和文件哈希；Release 候选会生成 `release-manifest.json`，记录 HTML zip、PDF 状态、release notes 和 readiness 来源。

这些信息并不浪漫，但很重要。它们让团队在发现问题后不用猜：“这个页面到底是从哪个提交来的？”“这个 Release 用的是哪份 readiness？”“PDF 是不是只是占位文件改名？”构建凭证把这些问题提前回答掉。

本层结论：**Build 不是打包动作，而是来源证明。**

### 2.2 Deploy：部署必须回答“到哪里去”

Deploy 的关键不是按下发布按钮，而是明确目标环境和策略。发布到 GitHub Pages、发布为 GitHub Release、部署到 staging、部署到 production，风险都不同。目标环境、权限、并发策略、是否允许覆盖、是否创建 draft、是否需要人工批准，都应该被记录。

本项目的 `.github/workflows/pages.yml` 与 `.github/workflows/release.yml` 提供了两个不同部署语义：Pages 是持续发布入口，Release 是版本候选与草稿发布入口。前者关心页面可访问，后者关心版本资产不可混淆。

Deploy 最容易出问题的地方，是把环境当成背景板。实际上，环境会改变风险。一个页面部署到本地 `.artifacts/`，影响范围很小；部署到 GitHub Pages，就开始影响读者入口；创建 draft Release 还在人工审阅边界内；发布正式 Release，则进入公开版本历史。

因此，部署策略至少要说明：

- Environment：目标是 local、preview、staging、production，还是 draft release？
- Permission：谁可以触发，谁可以批准，使用哪些 token 或 GitHub permissions？
- Concurrency：并发发布如何处理？是否允许取消旧任务？
- Overwrite：是否允许覆盖已有版本或未标记目录？
- Roll-forward / Rollback：失败后是修复前进，还是回滚到上一个稳定版本？

本层结论：**Deploy 不是复制文件，而是把候选物放进有边界的环境。**

### 2.3 Runtime Verify：运行环境仍要再验证

CH-07 的验证发生在交付候选进入 Operations 之前；Operations 中的 Runtime Verify 发生在部署之后。两者不能混为一谈。候选物在本地通过测试，不代表目标环境没有配置差异、路径差异、权限差异、缓存差异或资产缺失。

Runtime Verify 应该接近真实入口。对于 Pages，至少要确认入口页、驾驶舱、下钻链接和发布来源清单；对于 Release，至少要确认版本号、资产哈希、release notes、readiness 来源和 draft 状态。

运行验证要尽量小而锋利。它不是重新跑全部测试，而是检查“部署到这个环境后，最关键的入口是否真的工作”。例如：

```text
Pages
  index.html 可访问
  site/index.html 可访问
  publish-manifest.json 存在
  source commit 与预期一致

Release
  release-manifest.json 存在
  release notes 非空
  HTML zip hash 与 manifest 一致
  PDF 若存在，必须是真 PDF，而不是占位文件
```

本层结论：**运行验证负责证明候选物在目标环境可用。**

### 2.4 Monitor：发布后要能看见偏差

发布成功只是一个瞬间。系统进入运行后，真正的问题可能延迟出现：页面路径失效、资产未加载、用户无法找到入口、版本说明误导、指标异常、错误率升高、反馈入口无人处理。

Monitor 的目标不是收集所有数据，而是选择能代表运行状态的关键指标。对本书项目来说，监控可以先从轻量信号开始：Pages workflow 是否成功、Release artifact 是否存在、进度驾驶舱是否更新、反馈入口是否可用、试读反馈是否出现新阻断。

对一个更典型的软件系统来说，监控可能包括错误率、延迟、吞吐、资源消耗、业务转化、异常日志、告警触发和用户反馈。指标不在多，而在能不能回答“系统是否仍然按照发布目标运行”。

一个实用的 Monitor 设计可以分三层：

- Technical signals：构建、部署、HTTP、错误、延迟、资源。
- Product signals：入口访问、关键路径完成率、用户反馈。
- Governance signals：阻断项、人工批准、回滚记录、known gap。

本层结论：**Monitor 让发布从一次动作变成持续观察。**

### 2.5 Recover：恢复机制必须在失败前写好

Recover 不是事故发生后临时想办法。Runbook 应该在发布前准备好：如何回滚版本，如何撤下错误页面，如何重新生成候选，如何恢复上一次快照，如何通知读者，如何标记 known gap，如何暂停继续扩散。

AI 参与 Operations 时尤其需要明确恢复机制。AI 可以快速修复，但也可能快速扩大错误。Recover 的价值是给修复动作加上边界和顺序，让团队在压力下仍能做确定动作。

最低限度的 Runbook 应该包含：

| 项目 | 要回答的问题 |
|---|---|
| Trigger | 什么信号说明需要恢复动作？ |
| Owner | 谁负责决策和执行？ |
| Scope | 要回滚页面、Release、配置、数据，还是全部？ |
| Steps | 具体命令、入口或手动操作是什么？ |
| Verification | 恢复后如何证明状态正常？ |
| Communication | 需要通知谁，如何记录？ |

本层结论：**Recover 把失败从恐慌事件变成可执行流程。**

## 03 · Three-Part Argument：为什么 Operations 是交付闭环

### 第一段：通过验证的候选物还没有运行身份

测试通过、审校通过和 CI 通过，说明候选物达到进入下一阶段的条件，但它还没有获得运行身份。运行身份来自构建清单、目标环境、部署记录、发布入口和可追溯资产。

如果没有运行身份，团队很难回答一个朴素问题：线上现在跑的到底是什么？这在 AI 协作中尤其危险，因为 AI 可能在多个会话中生成多个候选物、多个页面、多个 Release 草案。没有 manifest 和 source identity，所有候选物都像长得很像的影子。

本段结论：**Operations 的第一项价值，是给交付候选物建立可追溯的运行身份。**

### 第二段：运行风险不同于构建前风险

构建前风险主要来自内容、代码、配置和证据链；运行风险来自环境、权限、网络、缓存、用户路径、版本覆盖、监控盲区和恢复缺失。把两类风险混在一起，团队会用错误工具解决问题。

例如，CI 无法证明 GitHub Pages 环境一定启用；单元测试无法证明 Release 没有被重复覆盖；本地链接检查无法证明读者入口路径清楚；模型评审无法证明监控会在错误发生后提醒你。运行风险需要运行工具治理。

本段结论：**Operations 的第二项价值，是把运行风险从开发验证中分离出来单独治理。**

### 第三段：恢复能力决定发布是否可持续

不可回滚的发布会让团队变得保守；没有监控的发布会让错误沉默扩散；没有 Runbook 的恢复会依赖临场发挥。真正可持续的发布不是永远不失败，而是在失败时能够被发现、定位、回滚和复盘。

这也是 Operations 的成熟度标志。初级团队问：“能不能上线？”成熟团队问：“上线后如果错了，我们多久发现，怎么撤回，谁负责，证据在哪里？”AI-DLC 要训练的是后一个问题。

本段结论：**Operations 的第三项价值，是让交付闭环具备失败后的恢复能力。**

## 04 · Example：以本书 Pages 与 Release 链路为例

本书项目已经存在两条最小 Operations 链路：GitHub Pages 发布链路和 GitHub Release 候选链路。它们不是完整生产系统，但足以作为 CH-08 的案例：同一个书稿项目，如何从验证通过进入可审计的运行入口。

### 4.1 Pages：持续入口的运行链

Pages 链路由 `.github/workflows/pages.yml` 描述。它包含四个关键 job：`validate`、`build`、`record` 和 `deploy`。

```text
validate
  python3 scripts/ci_check.py --budget-seconds 60

build
  generate_progress.py
  prepare_pages.py
  upload-pages-artifact

record
  generate_progress.py
  commit or upload recoverable progress-record

deploy
  deploy-pages
```

这条链路的 Operations 意义在于：它不是直接把 `site/` 发布出去，而是先验证，再生成发布树，再上传 Pages artifact，最后部署。`prepare_pages.py` 会构造一个带 `.aidlc-generated` 标记的输出目录，并生成 `publish-manifest.json`。发布入口页会显示 source commit、source facts、generated_at 和 workflow_run。

也就是说，读者看到的不是一个孤立页面，而是一个带来源身份的运行入口。

### 4.2 Release：版本候选的运行链

Release 链路由 `.github/workflows/release.yml` 描述。它的核心 job 依赖顺序是 `validate` → `readiness` → `build` → `publish`（YAML 声明顺序可能不同，以 `needs` 为准）。

```text
validate
  version syntax
  ci_check.py

readiness
  needs: validate
  check_release_readiness.py
  render_release_notes.py
  upload v0.1-readiness

build
  needs: [validate, readiness]
  download exact readiness evidence
  prepare_release.py
  upload release-candidate

publish
  needs: [validate, readiness, build]
  refuse overwrite
  gh release create ... --draft
```

这条链路特别值得注意的一点是：Release build 依赖 readiness。`prepare_release.py` 会拒绝使用不是 ready 的 readiness，也会拒绝 readiness source 与当前事实来源不一致的候选。这就避免了一个常见发布事故：拿 A 提交的 readiness 去包装 B 提交的资产。

它还对 PDF 做了诚实处理：如果没有通过 `--pdf` 提供经过验证的 PDF，则 manifest 明确记录 `pdf.status = skipped`，而不是伪造 PDF。这一点很 AI-DLC：不知道就是不知道，没验证就是没验证，不能把占位物包装成资产。

### 4.3 Recover：已有链路里的恢复设计

本项目当前的恢复设计还很轻量，但已经有几个重要钩子。

第一，`prepare_pages.py` 和 `prepare_release.py` 都拒绝覆盖没有生成标记的目录，避免误删人工目录。第二，Release workflow 创建 draft Release，而不是直接发布不可撤回版本。第三，readiness gate 会在 build 之前阻止不满足 v0.1 DoD 的候选。第四，进度系统保留事件、快照和 source identity，允许团队回看某次状态变化。

这还不是完整的生产 Runbook，但已经体现了 Operations 的基本态度：发布前拒绝混合来源，发布中保留凭证，发布后允许追溯，失败时尽量可恢复。

## 05 · Pattern：一份最小 Operations 清单

读者可以把本章案例抽象成一份最小清单。

| 阶段 | 最小凭证 | 常见失败 |
|---|---|---|
| Build | source commit、facts identity、manifest、artifact hash | 混入未审阅变更、资产不可复现 |
| Deploy | environment、permissions、version、strategy、artifact id | 发布到错误环境、覆盖已有版本 |
| Runtime Verify | entrypoint、smoke checks、manifest match、critical path | 本地过了，目标环境入口坏了 |
| Monitor | workflow result、errors、usage/feedback、blocker signals | 发布后无人看见错误 |
| Recover | trigger、owner、steps、rollback target、post-check | 出事后靠临场发挥 |

这张表可以直接用于小项目。大项目可以扩展每一格，但不应删除任何一格。

## 06 · Experiment：三个验证方向

本章实验入口包括三项：

- `EXP-08-01 · 发布候选来源清单校验器`：复用 readiness / manifest 校验模型，验证发布候选来源、必需资产与文件哈希是否一致。运行：`python3 experiments/exp-08-01/quickstart.py --sample`。
- `EXP-08-02 · 回滚桌面演练模拟器`：根据部署拓扑、故障场景、监控信号与 Runbook，生成发现、决策、回滚和恢复时间线。运行：`python3 experiments/exp-08-02/quickstart.py --sample`。
- `EXP-08-03 · Operations 四阶段复现`：对照冻结 pin 指南，复现 Build、Deploy、Runtime Verify、Monitor 四阶段凭证与回滚就绪度。运行：`python3 experiments/exp-08-03/quickstart.py --sample`。

其中 `EXP-08-01` 已为 `ALREADY / verified`：样例在 `experiments/exp-08-01/output/sample.json`。它证明冻结的 readiness/manifest 输入上，来源一致性、必需资产覆盖与哈希格式可被确定性校验，并给出 `source_completeness_percent` 与 `hash_mismatch_count`。它不证明真实生产环境已经完整可观测，也不把 ALREADY 改写成 SHIP。

`EXP-08-02` 已 verified：样例报告在 `experiments/exp-08-02/output/sample.json`。它证明部署拓扑、故障、监控信号与 Runbook 可连成 detect→decide→rollback→recover 时间线，并给出发现到回滚耗时、数据损失窗口与 Runbook 缺口数。桌面演练不等于生产恢复能力。

`EXP-08-03` 已为 `KEEP-EXT / verified`：样例在 `experiments/exp-08-03/output/sample.json`，给出 `stage_completion_percent` 与 `rollback_readiness_percent`。其中 Runtime Verify 属于 CH-08 运行时核验，不等于 CH-07 交付候选验证；冻结 pin 不等于成熟生产能力。

三项实验分别服务于三个问题。

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-08-01` | 发布候选来源、readiness 与 artifact hash 是否一致 | 不证明真实生产环境已经完整可观测；ALREADY 不得改写成 SHIP |
| `EXP-08-02` | 发现、决策、回滚和恢复的时间线是否清楚 | 不证明所有故障都能桌面演练覆盖 |
| `EXP-08-03` | Operations 四阶段凭证是否能按冻结指南复现 | 不把 alpha 参考实现写成成熟生产能力；KEEP-EXT 不得改写成 SHIP |

## 07 · Figure：Operations 运行闭环

本章图示为“Operations 运行闭环”：

![图 8-1 · Operations 运行闭环](images/ch08-operations-loop.svg){.core-figure width=100%}

源文件：`book/images/ch08-operations-loop.svg`。运行链摘要：

```text
Verified Candidate
  ↓
Build → Deploy → Runtime Verify → Monitor
  ↑                                ↓
  └──────── Recover / Rebuild ◀────┘
```

左侧为 Verified Candidate，中间为 Build / Deploy / Runtime Verify / Monitor，底部低权重回路为 Recover / Rebuild，右侧为 Sustainable Runtime。Runtime Verify 属于运行时核验，不等于 CH-07 的交付候选验证。

这张图要帮助读者看见三件事：

1. Operations 从已验证候选物开始，而不是从随手发布开始。
2. Build、Deploy、Runtime Verify、Monitor 都要产生可追溯凭证。
3. Recover / Rebuild 不是失败后的补丁，而是运行闭环的一部分。

图中不要把 Monitor 画成终点。Monitor 的价值是触发 Recover、Rebuild 或下一轮改进。

## 08 · Boundary：本章不解决什么

第一，本章不重新定义验证强度。CH-07 已经回答如何组合确定性检查、独立测试、模型评审和人工判断。CH-08 只处理批准之后的运行链。

第二，本章不讨论组织规模化治理。不同团队、业务线和风险等级如何选择不同 Flow，是 CH-09 的重点。

第三，本章不把当前 `memory-bank/operations/` 写成已经存在的成熟目录。当前仓库还没有正式 operations 目录；本章只把它作为方法落点和后续实现方向。

第四，本章不承诺 `EXP-08-02` 已证明生产恢复能力；`EXP-08-03` 虽已 verified，也只证明冻结四阶段凭证可复现，不证明生产可观测或恢复能力成熟。

第五，本章不把发布自动化当成生产成熟度。自动化只是动作可靠；成熟度还包括环境门禁、监控、恢复、审计和责任。

第六，`EXP-08-01` 的 verified 只证明候选来源与 manifest 一致性校验可复现；它不等于 Runtime Verify 已通过，也不证明监控与恢复能力已经成熟。

### Operations 阶段与官方方法（摘要）

AWS AI-DLC **Operations** 强调：AI 分析 metrics/logs/traces、对接 runbook 提议扩缩容/调优/隔离，并在**人批准后**执行；Deployment Units 含镜像/Serverless/IaC 等，并生成功能、安全与负载测试（摘要见 [白皮书](https://prod.d13rzhkk8cj2z0.amplifyapp.com)）。本书第 8 章用 Build→Deploy→Runtime Verify→Monitor→Recover 表达同类闭环，并**明确 specs.md Operations Agent / `memory-bank/operations/` 仍为 alpha 参考**——不得因官方白皮书描述而写成「工具已生产成熟」。本书仓库的 Pages/Release 自动化是教学级 Operations 样例，不是 AWS 部署单元的替代实现。

## Reader Exercise

选择一个你准备发布的候选物，用 30 分钟写一份最小 Operations Runbook。

1. 写出候选物：它从哪个提交、事实源、构建脚本和 readiness 来？
2. 写出 Build 凭证：manifest、文件哈希、构建时间和输出资产是什么？
3. 写出 Deploy 策略：目标环境、触发方式、权限、是否 draft、是否允许覆盖。
4. 写出 Runtime Verify：发布后必须检查哪三个真实入口？
5. 写出 Monitor：发布后 24 小时内看哪些信号？谁负责看？
6. 写出 Recover：如果入口坏了、资产错了、版本说明错了，如何回滚或重建？
7. 最后写一句判定：Release、Rollback、Rebuild、Pause，或 Escalate。

如果你能回答“这个候选物出了问题时，我们如何知道、如何撤回、如何重建”，你就已经从发布动作进入了 Operations 思维。

## References

- `scripts/check_release_readiness.py`：v0.1 readiness 与发布阻断报告。
- `scripts/prepare_release.py`：可追溯 Release 候选资产构造。
- `scripts/prepare_pages.py`：GitHub Pages 发布树构造与 publish manifest。
- `.github/workflows/pages.yml`：Pages 构建、上传、部署和进度记录链路。
- `.github/workflows/release.yml`：Release readiness、候选构造与草稿发布链路。
- `planning/releases/v0.1-policy.json`：v0.1 Definition of Done 的机器可读门禁。
- `experiments/exp-08-01/output/sample.json`：发布候选来源清单校验样例。
- `progress/experiments.json`：`EXP-08-01`、`EXP-08-02`、`EXP-08-03` 实验治理状态。
- `book/toc.md`：CH-08 核心问题、读者结果和实验方向。
- [AWS AI-DLC 方法定义（Amplify）](https://prod.d13rzhkk8cj2z0.amplifyapp.com)：Operations 阶段摘要（非 mature 工具宣称）。
