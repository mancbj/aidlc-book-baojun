---
stage: test
bolt: 002-github-writing-system-ui
completed: 2026-07-22T01:28:22Z
---

# Test Walkthrough: Visual Progress and Automatic Update Record

## Verdict

Bolt 002 的自动化、真实数据、静态链接和实际浏览器验收全部通过。测试过程中发现两个非生产逻辑问题：一个测试断言的权重算术错误，以及未来计划产物被渲染成死链；均已修正并通过完整回归。

## Automated Test Result

```text
................................
----------------------------------------------------------------------
Ran 32 tests in 0.623s

OK
```

### Fact Validation · 11 Tests

- 合法数据通过。
- 重复任务 ID、未知依赖和依赖环失败。
- 非法任务状态失败。
- blocked 缺少原因/解除动作失败。
- done 缺少验收或必需产物失败。
- 无时区时间戳失败。
- 章节下一缺口与固定阶段顺序有效。
- SHIP、KEEP-EXT、ALREADY 条件字段有效。

### Progress Core · 13 Tests

- 空任务集输出 0% 和初始化提示，不发生除零。
- 总完成率、Must/Should 和 Must ×3 / Should ×2 / Could ×1 加权规则正确。
- 下一动作过滤未满足依赖，并按优先级、工作状态、日期和 ID 稳定排序。
- blocked 独立输出原因与解除动作，不混入普通下一动作。
- 全部完成后进入发布/下一周期提示。
- 章节首个缺口、阶段完成率和实验 triage/status 分布正确。
- 不同生成时间不会改变确定性指标。
- 首次运行只生成一个初始化事件。
- 相同事实不生成事件。
- 任务、章节阶段、实验变化分别生成预期事件。
- 事件 ID 稳定，合并时去重。
- 显式版本事件有效。
- 无 Git commit 时形成稳定事实指纹。

### Generator Integration · 8 Tests

- 初次运行生成 current、事件、Changelog、快照、驾驶舱和下钻页。
- 重复运行保持事件、Changelog 和快照不变。
- 合法状态变化只追加一个对应事件和一个新来源快照。
- 非法事实使生成失败，最后成功 current 和比较基线字节不变。
- 冲突快照使生成失败，既有快照不被覆盖。
- dry-run 无文件系统副作用。
- 无 JavaScript HTML 包含核心摘要与稳定对象锚点。
- 不完整显式事件参数被拒绝。

总数为 32：原有 Validator 11 项、Core 13 项和 Generator 8 项。

## Real Repository Validation

```text
[INFO] validation summary: tasks=42, chapters=10, experiments=30, errors=0, warnings=0
[INFO] validation passed
```

真实 dry-run：

```text
[DRY-RUN] source=working-tree-5c9b6ebc6169 tasks=42 chapters=10 experiments=30 new_events=0 total_events=1 snapshot=20260721T083907Z-working-tree-5c9b6ebc6169.json
```

这证明当前事实源有效，相同事实没有制造第二条事件或第二份快照。

## Link and Asset Audit

最终结果：

```text
HTML links checked: 140; errors: 0
Site assets: 105594 bytes (103.1 KiB)
Events: 1
Snapshots: 1
```

初次链接审计发现 32 个尚未创建的计划产物被当成可点击链接。修复后的规则是：

- 已存在产物显示可点击仓库相对链接。
- 尚未创建产物显示路径和“待创建”标签，不制造死链。
- 任务、章节、实验对象下钻锚点始终可用。

最终 140 个可点击页面链接和跨页 fragment 均存在，站点体积远低于 2 MB 预算。

## Actual Browser Verification

使用本地 HTTP 服务在实际浏览器引擎中完成页面验收，而不只检查 HTML 文本。

### Desktop · 1280 × 720

| Check | Result |
|-------|--------|
| 页面级横向溢出 | 无，document/client width 均为 1280 |
| 总览指标布局 | 6 列 |
| Hero 布局 | 800px + 400px 双栏 |
| 下一动作 | 可见 |
| 可聚焦控件 | 45 个 |
| 语义 landmarks | 1 main、1 nav、7 sections、1 table |
| 控制台 warning/error | 0 |

### Mobile · 360 × 800

| Check | Result |
|-------|--------|
| 页面级横向溢出 | 无，document/client width 均为 360 |
| Hero | 单列 |
| 指标卡 | 单列 |
| 下一动作宽度 | 328px，完整位于 360px 视口内 |
| 时间线 | 仅组件内部可横向滚动，页面不溢出 |
| 顶部导航 | 可横向滚动 |
| 下钻卡片 | 单列、326px、页面不溢出 |
| 控制台 warning/error | 0 |

### Keyboard and Interaction

- Tab 键可进入筛选按钮。
- 焦点轮廓为 `3px solid`，肉眼可辨。
- 点击 Should 后 `aria-pressed=true`，当前唯一 Must 动作被正确隐藏。
- 恢复“全部”后动作重新显示。
- Day 1 时间线链接导航到 `details.html#day-01`。
- 下钻目标存在；`D01-T01` 稳定任务锚点存在。
- 10 个章节锚点和 30 个实验锚点均存在。
- 32 个未来产物显示“待创建”，不再是死链。

## No-JavaScript and Accessibility Contract

- 所有核心数字、状态、事件、时间线、章节矩阵、实验分布、阻塞和下一动作均直接存在于 HTML。
- JavaScript 只增强下一动作过滤；禁用后核心信息不消失。
- 页面包含 skip link、语义 header/nav/main/section/table/footer。
- 状态同时使用符号、文字和颜色。
- 键盘焦点可见；主要导航、过滤和下钻链接均可聚焦。
- `prefers-reduced-motion` 禁用平滑滚动依赖。

## Failure-Safety Evidence

临时仓库集成测试验证：

1. 非法事实在任何生成文件写入前失败。
2. current 和成功基线保持原 SHA-256。
3. 冲突的同源快照不被覆盖。
4. 重复运行事件和 Changelog 字节保持一致。
5. 状态变化追加时，新事件文件以旧文件全部字节为前缀。
6. 比较基线最后写入，失败后可以安全重试。

## Issues Found and Resolved

### Test arithmetic expectation

初次完整运行 31/32 通过。失败断言错误地期望加权进度 62.5%；样例完成权重为 5、总权重为 9，正确值为 55.6%。修正测试后全套通过，实现无需修改。

### Planned artifact dead links

初次 HTML 审计发现 32 个规划中但尚未创建的产物路径。渲染器已改为存在性判断，避免把未来工作伪装成可用链接。

### Automatic favicon request

本地服务观察到浏览器自动请求缺失 favicon。两个生成页面现使用空 data favicon，避免无意义 404 请求，不增加外部依赖。

## Final Commands

```text
python3 -m unittest discover -s tests
python3 scripts/validate_project.py
python3 scripts/generate_progress.py --dry-run --actor test-stage
git diff --check
```

全部成功。Stage 3 没有修改任何写作任务、章节或实验状态，也没有配置 GitHub remote 或产生外部副作用。
