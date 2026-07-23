# Feedback Decision Schema

- ID：唯一 `FB-NNN`。
- decision：pending / accepted / rejected / deferred。
- accepted：必须关联 `DNN-TNN` 或 `CNN-TNN`，并提供至少一条验收。
- rejected：必须提供理由。
- deferred：必须提供理由、目标周期和重新评估条件。
- 时间：带时区 ISO 8601。
- 禁止字段：姓名、邮箱、联系方式、Cookie、Token、完整原始对话。

Reader 只使用匿名 `Reader-A/B/C` 槽位和 not-invited / invited / responded 状态。
