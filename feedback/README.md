# Feedback Decisions

`decisions.json` 是反馈回流的版本化事实源，只保存匿名编号、结构化决策、理由和可追踪任务引用，不保存姓名、邮箱、电话、Cookie、Token、逐字稿或其他敏感原文。

## Decision Flow

1. 用 [`planning/feedback-template.md`](../planning/feedback-template.md) 整理建议。
2. 先运行 dry-run，检查将要写入的结构化事实。
3. 只有人工确认后才使用 `--apply`。
4. 重新生成进度，让决策、事件、快照与驾驶舱同步留痕。

```text
python3 scripts/record_feedback.py --help
python3 scripts/validate_feedback.py
python3 scripts/generate_progress.py --actor maintainer
```

accepted 决策必须绑定现有章节或任务和验收标准；rejected 必须记录理由；deferred 必须记录目标周期与回看条件。尚未收到真实试读回复时，读者状态保持 `not-invited` 或相应真实状态。
