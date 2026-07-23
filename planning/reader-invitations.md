# 三位试读者邀请包

> D13-T01 产物：准备三位试读者的邀请说明。  
> 隐私规则：只记录匿名槽位，不保存姓名、邮箱、微信、电话或聊天账号。  
> 当前状态：作者线下确认已发送；匿名 Reader 槽位已记录为 `invited`，尚未记录为 `responded`。

## 1 · 状态表

| Slot | Assignment | Current state | Send evidence | Feedback target |
|---|---|---|---|---|
| Reader A | README + 样章理解 | invited | 作者线下确认已发送，2026-07-23T05:32:21Z | 核心公式、样章是否读懂 |
| Reader B | 10 分钟实验复现 | invited | 作者线下确认已发送，2026-07-23T05:32:21Z | 实验命令、输出、失败点 |
| Reader C | 驾驶舱与证据下钻 | invited | 作者线下确认已发送，2026-07-23T05:32:21Z | 进度、证据、下一动作可信度 |

真实发送后，再更新 [`feedback/decisions.json`](../feedback/decisions.json) 中对应 Reader 槽位：

- `status`: `invited`
- `invited_at`: 真实发送时间，ISO 8601 UTC
- 不写入真实身份或联系方式

## 2 · 统一试读说明

发送给三位试读者时，只需要给一个入口：

```text
请从仓库根 README 开始：

README.md
```

如果发送环境允许链接，可使用仓库 README 的 URL；如果只发送压缩包或本地目录，请让试读者打开根目录的 `README.md`。

试读者不需要阅读我们的聊天记录，也不需要知道任务事实源结构。README 会引导他们进入 Part 0、样章、实验、驾驶舱和反馈模板。

## 3 · Reader A 邀请文案：README + 样章理解

```text
我想请你用“第一次接触 AI-DLC 的读者”视角试读一版。

入口只看根 README.md，不需要任何聊天背景。

请完成三件事：

1. 从 README 进入 Part 0 和 CH-03 样章。
2. 用自己的话复述核心公式：AI-DLC = 𝓔（人的判断 + AI 能力）。
3. 告诉我：读完 README + 样章后，你是否知道下一步该读什么、跑什么或反馈什么？

请不要提交姓名、邮箱、聊天截图、Token、Cookie 或完整环境变量。
反馈只需要最小摘要：

- 读懂的一点：
- 卡住的一点：
- 是否影响 v0.1 发布：yes / no / unclear
- 建议改法：
```

验收方式：

- Reader A 能只依赖 README 找到样章。
- Reader A 能复述核心公式或指出无法复述的原因。
- Reader A 的反馈能整理进 [`planning/feedback-template.md`](feedback-template.md)。

## 4 · Reader B 邀请文案：10 分钟实验复现

```text
我想请你用“能否复现实验”的视角试读一版。

入口只看根 README.md，不需要任何聊天背景。

请完成三件事：

1. 从 README 找到实验入口。
2. 按说明运行 EXP-03-01 的合法样例。
3. 记录命令、耗时、输出位置，以及失败点（如果有）。

请不要提交姓名、邮箱、聊天截图、Token、Cookie 或完整环境变量。
反馈只需要最小摘要：

- 是否能从 README 找到实验：yes / no
- 实际运行命令：
- 是否得到 valid=true：yes / no
- 卡住的位置：
- 是否影响 v0.1 发布：yes / no / unclear
```

验收方式：

- Reader B 能只依赖 README 找到 `experiments/sample/README.md`。
- Reader B 能运行或明确指出不能运行的步骤。
- Reader B 的反馈能形成 accepted / rejected / deferred / pending 决策。

## 5 · Reader C 邀请文案：驾驶舱与证据下钻

```text
我想请你用“项目状态是否可信”的视角试读一版。

入口只看根 README.md，不需要任何聊天背景。

请完成三件事：

1. 从 README 打开鸟瞰驾驶舱。
2. 找到当前下一动作、readiness 状态和最近关键更新。
3. 随便选择一个任务下钻，判断产物和验收是否能看懂。

请不要提交姓名、邮箱、聊天截图、Token、Cookie 或完整环境变量。
反馈只需要最小摘要：

- 是否能从 README 找到驾驶舱：yes / no
- 当前下一动作是什么：
- 哪个证据下钻可信 / 不可信：
- 是否影响 v0.1 发布：yes / no / unclear
- 建议改法：
```

验收方式：

- Reader C 能只依赖 README 找到 `site/index.html`。
- Reader C 能说出当前下一动作。
- Reader C 能指出至少一个可信或不可信的证据下钻。

## 6 · 发送后记录

真实发送后，只更新匿名槽位：

```json
{
  "id": "Reader-A",
  "status": "invited",
  "invited_at": "YYYY-MM-DDTHH:MM:SSZ",
  "responded_at": null
}
```

收到回复后：

1. 把原始回复整理为最小摘要，不保存逐字稿。
2. 按 [`planning/feedback-template.md`](feedback-template.md) 形成决策卡。
3. 用 `scripts/record_feedback.py` dry-run。
4. 人工确认后加 `--apply`。
5. 运行 `python3 scripts/generate_progress.py --actor maintainer` 记录反馈事件。

## 7 · 当前不可伪造声明

本文件目前只证明作者已线下确认发送三份邀请；尚不证明三位读者已经回复。收到回复后，才能把对应 Reader 槽位从 `invited` 更新为 `responded`，并按反馈模板记录最小决策摘要。
