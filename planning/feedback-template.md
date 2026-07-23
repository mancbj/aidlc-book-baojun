# 试读反馈模板

> 用途：把试读者观察整理为最小、匿名、可决策的反馈。  
> 事实源：[`feedback/decisions.json`](../feedback/decisions.json)  
> 写入工具：[`scripts/record_feedback.py`](../scripts/record_feedback.py)

## 1 · 给试读者填写

请只写影响判断的最小摘要，不提交姓名、邮箱、电话、Token、Cookie、完整环境变量或未经许可的私密原文。

```text
Reader slot：Reader-A / Reader-B / Reader-C / anonymous
对象：README / Part 0 / CH-03 样章 / EXP-03-01 / 驾驶舱 / Release Notes / 其他
观察：我看到或遇到的最小事实
影响：这会如何影响理解、复现、信任或发布判断
期望：我希望看到的可观察结果
证据入口：仓库相对路径、Issue 链接或截图说明；不要粘贴敏感原文
是否阻断 v0.1：yes / no / unclear
```

## 2 · 维护者决策卡

每条反馈必须进入以下四种状态之一：

| Decision | 何时使用 | 必填字段 |
|---|---|---|
| `pending` | 已收到，但还没判断 | source、object、summary、created_at |
| `accepted` | 决定采纳，并形成修订任务 | linked_task、acceptance、decided_at |
| `rejected` | 决定不采纳 | reason、decided_at |
| `deferred` | 暂不进入 v0.1，带入后续周期评估 | reason、target_cycle、revisit_when、decided_at |

决策卡：

```text
Feedback ID：FB-NNN（写入工具自动分配）
Source：Reader-A / Reader-B / Reader-C / GitHub Issue / review
Object：被反馈对象，例如 book/chapters/sample.md
Summary：不含个人信息的最小证据摘要
Decision：pending / accepted / rejected / deferred
Reason：accepted 可为空；rejected/deferred 必填
Linked task：accepted 必填，例如 D13-T02 或 C02-T01
Acceptance：accepted 必填，至少一条二元验收
Target cycle：deferred 必填，例如 v0.2-draft
Revisit when：deferred 必填，写明重新评估条件
```

## 3 · 记录命令样例

默认 dry-run，不写入事实源：

```bash
python3 scripts/record_feedback.py \
  --source Reader-A \
  --object book/chapters/sample.md \
  --summary "读者无法区分结构校验和语义正确性" \
  --decision pending
```

### accepted

```bash
python3 scripts/record_feedback.py \
  --source Reader-A \
  --object book/chapters/sample.md \
  --summary "建议在实验指标表后再次说明 valid=true 只代表结构有效" \
  --decision accepted \
  --linked-task D13-T02 \
  --acceptance "样章实验段增加结构/语义边界提醒，并通过样章审校"
```

accepted 必须关联 `DNN-TNN` 或 `CNN-TNN`，并至少有一条验收。

### rejected

```bash
python3 scripts/record_feedback.py \
  --source Reader-B \
  --object experiments/sample/quickstart.py \
  --summary "建议把实验改成联网调用模型自动生成 Stories" \
  --decision rejected \
  --reason "偏离 v0.1 的无网络、无密钥、确定性结构实验边界"
```

rejected 必须记录理由，说明取舍和证据。

### deferred

```bash
python3 scripts/record_feedback.py \
  --source Reader-C \
  --object book/images/ch03-intent-to-bolt.svg \
  --summary "希望 CH-03 有专属 SVG，而不是 Mermaid 局部图" \
  --decision deferred \
  --reason "不阻断 v0.1；当前已有核心图和 Mermaid 结构图" \
  --target-cycle v0.2-draft \
  --revisit-when "v0.1 发布后规划 CH-03 专属图示增强"
```

deferred 必须有目标周期和重新评估条件。

## 4 · 人工确认后写入

确认 dry-run 输出无误后，再加 `--apply`：

```bash
python3 scripts/record_feedback.py ... --apply
python3 scripts/validate_feedback.py
python3 scripts/generate_progress.py --actor maintainer
```

写入后，反馈决策会进入：

- [`feedback/decisions.json`](../feedback/decisions.json)
- [`progress/events/events.jsonl`](../progress/events/events.jsonl)
- [`progress/generated/current.md`](../progress/generated/current.md)
- [鸟瞰驾驶舱](../site/index.html)

## 5 · 发布处理规则

- v0.1 blocker：优先进入 `accepted`，关联 D13-T02 或 D14-T01。
- 非阻断但有价值：进入 `deferred`，目标周期通常为 `v0.2-draft`。
- 与事实源、边界或隐私规则冲突：进入 `rejected`，保留理由。
- 尚未判断：保留 `pending`，但不能冒充已经处理。

所有真实反馈都可以匿名。仓库只保存影响决策的必要摘要，不保存读者身份和原始逐字稿。
