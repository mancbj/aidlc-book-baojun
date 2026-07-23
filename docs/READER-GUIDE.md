# v0.1 试读与复现说明

## 试读者只需要这些入口

1. 根 `README.md`：定位本书、样章、实验和反馈入口。
2. `site/index.html`：确认当前进度、已知阻塞和来源。
3. `book/chapters/sample.md`：样章；文件不存在时表示尚未开放试读。
4. `experiments/sample/README.md`：10 分钟实验；文件不存在时表示尚未开放复现。
5. `planning/feedback-template.md`：提交最小反馈摘要，并由维护者进入 pending / accepted / rejected / deferred 决策流。

## 建议任务

- Reader A：只阅读 README 与样章，复述核心公式和一个可执行动作。
- Reader B：按 README 复现实验，记录命令、耗时、输出与失败点。
- Reader C：从驾驶舱找到下一项 Must，并检查下钻证据是否可信。

## 反馈如何被处理

- `accepted`：采纳并关联任务与二元验收。
- `rejected`：不采纳，但必须记录理由。
- `deferred`：不阻断 v0.1，带入目标周期并写明重评条件。
- `pending`：已收到但尚未判断，不能冒充已处理。

反馈事实源是 `feedback/decisions.json`；公开仓库只保存匿名槽位和最小决策摘要。

## 隐私

反馈可以匿名。不要提交 Token、Cookie、密钥、完整环境变量、个人联系方式或未经许可的私密原文。仓库只保存影响决策的必要摘要。

当前 Reader A/B/C 均为匿名槽位，不代表已经邀请或收到反馈。
