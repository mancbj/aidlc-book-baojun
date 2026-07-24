# 第 8 章 · Operations：从交付候选到可持续运行

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-08 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D22-T01 · 锁定章节论证骨架 |
| Draft Completeness | 正式十章生产线论证骨架；等待 D22-T02 扩展为完整可读稿 |
| Primary Question | 如何通过 Build、Deploy、Verify、Monitor 与恢复机制，让通过测试的候选物成为可运行、可观测、可回滚的系统？ |
| Reader Outcome | 能够定义构建凭证、环境门禁、部署策略、冒烟验证、监控指标和回滚 Runbook |
| Related Experiments | `EXP-08-01`、`EXP-08-02`、`EXP-08-03` |

## 01 · Question：为什么“测试通过”还不是运行成功

第 7 章回答了验证问题：如何组合确定性检查、独立测试、模型评审和人工判断，证明 AI 参与的交付候选不是模型自评的幻觉。第 8 章继续往前一步：**候选物已经通过验证之后，如何让它成为可运行、可观测、可回滚的系统？**

这就是 Operations 的范围。

在 AI-DLC 中，Operations 不是“最后把东西上线一下”，也不是把测试通过的文件复制到某个地方。它是一组运行责任：构建必须可追溯，部署必须有环境门禁，验证必须接近真实运行条件，监控必须能发现偏差，恢复机制必须在出事前准备好。

如果没有 Operations，团队会在两个地方犯错。

第一，把交付候选误认为运行系统。一个候选物可能通过 CI、链接检查和人工审校，但它还没有被打包、部署、冒烟验证和监控。第二，把发布成功误认为持续成功。页面能打开、服务能启动、版本能创建，只说明某一刻的动作完成；真正的运行状态还要看监控、告警、回滚和后续恢复。

因此，本章的核心问题是：**如何通过 Build、Deploy、Verify、Monitor 与恢复机制，让通过测试的候选物成为可运行、可观测、可回滚的系统？**

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

Verify
  在目标环境执行冒烟验证、入口检查、发布清单核对和回归门禁

Monitor
  观察关键指标、错误信号、用户入口、告警和漂移

Recover
  在失败时按 Runbook 回滚、降级、恢复数据或暂停发布
```

这五段与 CH-07 的验证链不同。CH-07 问的是“候选物是否可以被批准”；CH-08 问的是“批准后的候选物能否进入运行，并在运行中被观察和恢复”。换句话说，验证解决正确性证据，Operations 解决运行责任。

### 2.1 Build：构建必须回答“从哪里来”

Build 的第一职责是来源可追溯。一个可发布资产至少要知道：源提交是什么，事实源身份是什么，构建时间是什么，输入文件有哪些，输出文件哈希是什么，是否混入了未审阅状态。

在本书项目里，`scripts/prepare_release.py` 和 `scripts/prepare_pages.py` 都体现了这一点。Pages 发布树会记录 source facts、commit、generated_at、workflow_run 和文件哈希；Release 候选会生成 `release-manifest.json`，记录 HTML zip、PDF 状态、release notes 和 readiness 来源。

本层结论：**Build 不是打包动作，而是来源证明。**

### 2.2 Deploy：部署必须回答“到哪里去”

Deploy 的关键不是按下发布按钮，而是明确目标环境和策略。发布到 GitHub Pages、发布为 GitHub Release、部署到 staging、部署到 production，风险都不同。目标环境、权限、并发策略、是否允许覆盖、是否创建 draft、是否需要人工批准，都应该被记录。

本项目的 `.github/workflows/pages.yml` 与 `.github/workflows/release.yml` 提供了两个不同部署语义：Pages 是持续发布入口，Release 是版本候选与草稿发布入口。前者关心页面可访问，后者关心版本资产不可混淆。

本层结论：**Deploy 不是复制文件，而是把候选物放进有边界的环境。**

### 2.3 Verify：运行环境仍要再验证

CH-07 的验证发生在交付候选进入 Operations 之前；Operations 中的 Verify 发生在部署之后。两者不能混为一谈。候选物在本地通过测试，不代表目标环境没有配置差异、路径差异、权限差异、缓存差异或资产缺失。

Operations Verify 应该接近真实入口。对于 Pages，至少要确认入口页、驾驶舱、下钻链接和发布来源清单；对于 Release，至少要确认版本号、资产哈希、release notes、readiness 来源和 draft 状态。

本层结论：**运行验证负责证明候选物在目标环境可用。**

### 2.4 Monitor：发布后要能看见偏差

发布成功只是一个瞬间。系统进入运行后，真正的问题可能延迟出现：页面路径失效、资产未加载、用户无法找到入口、版本说明误导、指标异常、错误率升高、反馈入口无人处理。

Monitor 的目标不是收集所有数据，而是选择能代表运行状态的关键指标。对本书项目来说，监控可以先从轻量信号开始：Pages workflow 是否成功、Release artifact 是否存在、进度驾驶舱是否更新、反馈入口是否可用、试读反馈是否出现新阻断。

本层结论：**Monitor 让发布从一次动作变成持续观察。**

### 2.5 Recover：恢复机制必须在失败前写好

Recover 不是事故发生后临时想办法。Runbook 应该在发布前准备好：如何回滚版本，如何撤下错误页面，如何重新生成候选，如何恢复上一次快照，如何通知读者，如何标记 known gap，如何暂停继续扩散。

AI 参与 Operations 时尤其需要明确恢复机制。AI 可以快速修复，但也可能快速扩大错误。Recover 的价值是给修复动作加上边界和顺序，让团队在压力下仍能做确定动作。

本层结论：**Recover 把失败从恐慌事件变成可执行流程。**

## 03 · Three-Part Argument：为什么 Operations 是交付闭环

### 第一段：通过验证的候选物还没有运行身份

测试通过、审校通过和 CI 通过，说明候选物达到进入下一阶段的条件，但它还没有获得运行身份。运行身份来自构建清单、目标环境、部署记录、发布入口和可追溯资产。

本段结论：**Operations 的第一项价值，是给交付候选物建立可追溯的运行身份。**

### 第二段：运行风险不同于构建前风险

构建前风险主要来自内容、代码、配置和证据链；运行风险来自环境、权限、网络、缓存、用户路径、版本覆盖、监控盲区和恢复缺失。把两类风险混在一起，团队会用错误工具解决问题。

本段结论：**Operations 的第二项价值，是把运行风险从开发验证中分离出来单独治理。**

### 第三段：恢复能力决定发布是否可持续

不可回滚的发布会让团队变得保守；没有监控的发布会让错误沉默扩散；没有 Runbook 的恢复会依赖临场发挥。真正可持续的发布不是永远不失败，而是在失败时能够被发现、定位、回滚和复盘。

本段结论：**Operations 的第三项价值，是让交付闭环具备失败后的恢复能力。**

## 04 · Example Skeleton：以本书 Pages 与 Release 链路为例

D22-T02 可读稿将复用本书项目已有发布链路作为案例，重点展示从验证候选到运行入口的最小 Operations 证据。

最小案例结构如下：

```text
Build Evidence
  scripts/prepare_pages.py
  scripts/prepare_release.py
  releases/v0.1-rc/readiness.json
  publish-manifest.json / release-manifest.json

Deploy Evidence
  .github/workflows/pages.yml
  .github/workflows/release.yml
  GitHub Pages artifact
  GitHub draft Release

Runtime Verify
  Pages entrypoint
  site/index.html
  release notes
  artifact hashes

Monitor
  workflow result
  progress-record artifact
  feedback facts
  release blocker report

Recover
  refusal to overwrite unmarked directories
  draft release before publish
  readiness gate before release build
  previous snapshots and source identity
```

这个例子要回答一个关键问题：如果一个版本发布出现问题，团队能不能知道它从哪个源提交来、包含哪些资产、是否通过 readiness、部署到哪里、如何撤回或重建？如果能，Operations 就不只是“发布按钮”，而是运行闭环。

## 05 · Experiment & Figure Entry

本章实验入口包括三项：

- `EXP-08-01 · 发布候选来源清单校验器`：复用 `scripts/check_release_readiness.py` 与 `scripts/prepare_release.py`，验证发布候选来源、构建日志、文件哈希与 readiness 是否一致。
- `EXP-08-02 · 回滚桌面演练模拟器`：根据部署拓扑、故障场景、监控信号与 Runbook，生成发现、决策、回滚和恢复时间线。
- `EXP-08-03 · Operations 四阶段复现`：参考 Operations Agent 流程与可部署示例，复现 Build、Deploy、Verify、Monitor 四阶段凭证。

其中 `EXP-08-01` 当前为 `ALREADY / ready`，因为本项目已经存在 release readiness 与 release preparation 脚本。`EXP-08-02` 与 `EXP-08-03` 仍为 `planned`，因此本章骨架只把它们作为验证方向，不把回滚指标或阶段完成率写成已验证结论。

本章图示方向为“Operations 运行闭环”：

```text
Verified Candidate
  ↓
Build → Deploy → Runtime Verify → Monitor
  ↑                                ↓
  └──────── Recover / Rebuild ◀────┘
```

若后续生成独立 SVG，可命名为 `book/images/ch08-operations-loop.svg`，采用宽屏运行链布局：左侧为 Verified Candidate，中间为 Build/Deploy/Verify/Monitor，底部低权重回路为 Recover / Rebuild，右侧为 Sustainable Runtime。

## 06 · D22-T02 Writing Plan

D22-T02 将把本骨架扩展为完整可读稿。重点动作：

1. 扩写 Build、Deploy、Verify、Monitor、Recover 五段运行链。
2. 用 Pages workflow、Release workflow、`prepare_pages.py`、`prepare_release.py` 和 readiness 脚本展示最小 Operations 案例。
3. 写清 CH-07 Verify 与 CH-08 Runtime Verify 的区别。
4. 将 `EXP-08-01` 写成 already-ready 的项目证据入口；将 `EXP-08-02`、`EXP-08-03` 保持为 planned。
5. 增加读者练习：为一个发布候选写出构建凭证、环境门禁、冒烟验证、监控指标和回滚 Runbook。

## References

- `scripts/check_release_readiness.py`：v0.1 readiness 与发布阻断报告。
- `scripts/prepare_release.py`：可追溯 Release 候选资产构造。
- `scripts/prepare_pages.py`：GitHub Pages 发布树构造与 publish manifest。
- `.github/workflows/pages.yml`：Pages 构建、上传、部署和进度记录链路。
- `.github/workflows/release.yml`：Release readiness、候选构造与草稿发布链路。
- `planning/releases/v0.1-policy.json`：v0.1 Definition of Done 的机器可读门禁。
- `progress/experiments.json`：`EXP-08-01`、`EXP-08-02`、`EXP-08-03` 实验治理状态。
- `book/toc.md`：CH-08 核心问题、读者结果和实验方向。
