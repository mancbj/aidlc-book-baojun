# EXP-04-01 · Memory Bank 冷启动恢复 A/B 实验

> **状态：READY → VERIFIED 候选**  
> 目标：用一个无模型、无网络、可重复的最小实验，验证 Memory Bank 与 Standards 能否帮助新会话恢复正确上下文和下一动作。

## 实验目的

同一个项目问题：“请继续推进下一任务。”  
比较两组候选首轮行动：

- **with_memory_bank**：读取版本化事实源、周期、章节、标准和排除边界后行动。
- **without_memory_bank**：只依赖聊天印象和模糊项目背景行动。

实验不判断自然语言质量，只检查首轮行动是否恢复了四类关键上下文：

1. 当前周期与下一动作；
2. 必须更新的证据路径；
3. 不得纳入 GitHub 仓库的本地目录；
4. 必须保留的专用术语。

## 环境

- Python 3.9+
- 只使用标准库
- 不联网
- 不需要模型 API、Token 或其他密钥

## 运行命令

从仓库根目录运行：

```bash
python3 experiments/exp-04-01/quickstart.py --sample
```

等价显式命令：

```bash
python3 experiments/exp-04-01/quickstart.py \
  --input experiments/exp-04-01/samples/input.json \
  --output experiments/exp-04-01/output/sample.json
```

## 输出指标

生成路径：`experiments/exp-04-01/output/sample.json`

核心指标：

- `context_recovery_accuracy_percent`
- `first_action_error`
- `clarification_question_count`
- `accuracy_gain_percent`
- `clarification_reduction`

## 验收

- 合法样例以 exit `0` 结束。
- 输出包含两组候选的可复核判定。
- `with_memory_bank` 的上下文恢复准确率高于 `without_memory_bank`。
- `with_memory_bank` 的首个动作没有错误。
- 重复运行产生字节一致输出。

事实状态以 `progress/experiments.json` 为准。
