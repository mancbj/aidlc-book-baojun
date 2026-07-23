# Progress Facts

本目录同时保存权威运行事实与由其产生的审计投影。

## 权威事实

- `tasks.json`：14 天任务
- `chapters.json`：十章六阶段状态
- `experiments.json`：实验治理记录
- `schemas/`：字段和门禁说明

只有这三个顶层 JSON 是日常写作状态的权威源。

## 自动生成的投影与历史

- `generated/current.json`：当前机器指标
- `generated/current.md`：当前人类可读摘要
- `generated/last-successful-facts.json`：事件比较基线
- `events/events.jsonl`：追加式关键事件账本
- `snapshots/`：按来源身份保存的不可变整体快照
- `CHANGELOG.md`：与关键事件同步的人类可读记录

修改后必须运行：

```text
python3 scripts/validate_project.py
```

更新事实后运行：

```text
python3 scripts/generate_progress.py
```

生成文件不得反向覆盖三个权威事实源。详细契约见 [进度自动化说明](../docs/PROGRESS-AUTOMATION.md)。
