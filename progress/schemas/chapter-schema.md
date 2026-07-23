# Chapter Schema

## Required Fields

- `id`：CH-01 至 CH-10
- `number`：1–10
- `title`
- `question`：唯一核心问题
- `reader_outcome`
- `stages`
- `updated`：带时区 ISO 8601

## Six Stages

按固定顺序：

1. question
2. framework
3. example
4. experiment
5. figure
6. review

每个阶段状态为 `pending`、`in-progress` 或 `done`。

首个非 done 阶段就是下一缺口。所有阶段 done 时，下一缺口为 null。

## Evidence Rule

影响读者实践的观点必须至少关联实验、复现指南、图表或读者练习。

