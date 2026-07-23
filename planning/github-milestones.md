# GitHub Milestones

## v0.0.1 · Day 7 可读闭环

用途：验证“一个样章 + 一个实验 + 一张图 + 一次构建”能够端到端运行。

包含：

- 一个可读样章草稿
- 一个可在 10 分钟内复现的实验
- 一张解释核心框架的图
- HTML 构建与最小审校记录
- 当前进度、关键事件和快照

关闭门禁：相关 Must 任务全部 done、验收通过、产物存在、校验/测试通过、已记录已知缺口。

不包含：十章完整正文、全部 30 个实验、正式 v0.1 Release。

## v0.1 · Day 14 可发布版本

用途：交付可公开试读、可复现实验、可追踪进度并能接收反馈的首个版本。

包含：

- 审校后的样章
- 十章结构与唯一核心问题
- 至少一个可复现实验和一张核心图
- 可重复运行的 HTML 构建；PDF 按工具可用性明确生成或跳过
- Pages 驾驶舱、Release manifest、Release Notes 候选
- 反馈入口和下一周期草案

关闭门禁：v0.1 Must 任务全部完成、没有未解释 blocker、全套 CI 通过、发布产物含来源 SHA/生成时间/哈希、人工发布审阅通过。

不包含：所有章节定稿、多语言站点、自定义域名、长期分析系统。

## Remote Setup Checklist

当前文件是仓库内权威说明，不会自动创建远程 milestone。连接目标 GitHub 仓库后：

1. 按上述标题创建两个 milestone。
2. 把 due date 与实际 14 天起点对齐。
3. 复制范围和关闭门禁到 description。
4. 将 Issue 按 Task ID 归入对应 milestone。
5. milestone 关闭前运行 `python3 scripts/ci_check.py`。
