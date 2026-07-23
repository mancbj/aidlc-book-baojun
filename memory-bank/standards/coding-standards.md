# Coding Standards

## Overview

本项目采用轻量、可自动执行的编码与内容维护标准。规则优先服务于书稿可读性、Git 变更可审阅性，以及进度数据和可视化页面的可靠生成。

## Code Formatting

**Tool**：编辑器基础格式化与仓库校验脚本

**Key Settings**：

- HTML、CSS、JavaScript：2 空格缩进
- Python：4 空格缩进，遵循 PEP 8 的通用约定
- YAML：2 空格缩进，不使用制表符
- Markdown：标题逐级递进，列表和代码块保持 CommonMark 兼容
- 行尾：LF；文件末尾保留一个换行

**Enforcement**：保存时由编辑器处理基础格式；Pull Request 中由 GitHub Actions 执行结构与格式校验。

## Linting

**Tool**：Python 标准库校验脚本、`compileall` 及结构化数据解析
**Base Config**：仓库内规则
**Strictness**：严格处理影响自动化和可视化结果的错误，普通文案提示保持平衡

**Key Rules**：

- Python 语法错误：error，阻止合并
- YAML、JSON 或进度数据必需字段缺失：error，阻止合并
- 无效状态、时间戳或任务引用：error，阻止合并
- 失效内部链接：error；外部链接暂时不可用：warn
- 注释中的 TODO 必须关联任务编号：error
- 不保留注释掉的废弃代码：error

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| 内容目录与网页资源 | kebab-case | `chapter-progress` |
| Markdown 文件 | kebab-case | `writing-workflow.md` |
| Python 文件与函数 | snake_case | `generate_progress.py` |
| JavaScript 变量与函数 | camelCase | `renderProgress` |
| Python、JavaScript 常量 | UPPER_SNAKE | `VALID_STATUSES` |
| CSS 类 | kebab-case | `progress-card` |
| Git 分支 | 类型/任务号-简述 | `write/issue-12-agent-loop` |

**File Naming**：

- 页面和资源：kebab-case
- 自动化脚本：snake_case
- 测试：`test_<target>.py`

## File Organization

**Pattern**：按写作工作流和产物类型组织

**Structure**：

```text
book/                 # 书稿与章节
planning/             # 路线图、选题与发布计划
progress/             # 结构化状态、历史快照与可视化数据
scripts/              # 校验、聚合与生成脚本
tests/                # 自动化脚本测试
.github/workflows/     # 校验、快照与发布流程
memory-bank/           # AI-DLC 意图、故事、决策和执行记录
```

**Conventions**：

- 测试统一放在 `tests/`
- 小型脚本的类型定义就近维护
- 不使用仅为转发导入而存在的索引文件
- 生成文件与人工编辑源文件必须分离，并在文件头注明生成来源

## Testing Strategy

**Framework**：Python `unittest`
**Coverage Target**：不设形式化百分比；进度解析、状态聚合、快照生成和页面数据生成等关键路径必须有正常、边界与失败用例

**Test Types**：

| Type | Tool | When to Use |
|------|------|-------------|
| 单元测试 | `unittest` | 状态计算、字段校验、路径和日期处理 |
| 集成测试 | `unittest` + 临时目录 | 从任务数据生成快照和页面数据 |
| 冒烟测试 | GitHub Actions | 验证全仓校验、生成和发布命令可运行 |

**Conventions**：

- 测试命名：`test_<condition>_<expected_result>`
- 测试结构：Arrange–Act–Assert
- Mock 策略：只在文件系统、时间和外部 GitHub 边界使用 Mock
- 修复缺陷时必须添加能复现问题的回归测试

## Error Handling

**Pattern**：在自动化边界快速失败；预期的校验问题集中报告，非预期异常保留上下文后终止

**Custom Errors**：必要时定义面向任务数据和生成流程的异常，并包含文件、字段、错误值及修复建议

**User-facing Errors**：使用中文说明问题和下一步；GitHub Actions 同时返回非零退出码以阻止错误结果合并或发布

## Logging

**Tool**：Python `logging` 或等价标准输出
**Format**：适合 GitHub Actions 阅读的单行文本，关键快照另存为结构化数据

**Levels**：

| Level | Usage |
|-------|-------|
| INFO | 阶段开始、完成、统计摘要和产物路径 |
| WARN | 不阻止执行但需要关注的问题 |
| ERROR | 导致校验、生成或发布失败的问题 |

**Rules**：

- 始终记录：工作流名称、处理文件数、状态变化、产物路径和失败原因
- 绝不记录：GitHub Token、密钥、Cookie、个人敏感信息或完整环境变量
- 每次关键状态变化应生成可版本控制的快照，而非仅停留在临时日志中
