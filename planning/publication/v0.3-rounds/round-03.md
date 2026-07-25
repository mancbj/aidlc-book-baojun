# Round 03 · Evidence & Chapter Boundaries

**Decision:** KEEP

## 目标

消除 CH-07 Verify 与 CH-08 Runtime Verify 的命名混淆；收紧 `ready` 实验的措辞，避免读成已 verified。

## 变更

- `book/chapters/ch08-operations.md`：核心问题与 EXP-08-03 使用 `Runtime Verify`；EXP-08-01 标明 `ready ≠ verified`
- `book/toc.md`、`book/part-00-overview.md`、`book/chapters/ch01-ai-native-sdlc.md`：Operations 链统一为 Runtime Verify
- `book/chapters/ch07-verification.md`：EXP-07-01 改为可核查调用表述，去掉“每天被用于”的过强语感

## 验证

- 抽查：Operations 主链不再裸用 `Build → Deploy → Verify`
- 公式仍为 `𝓔 = Engineering with Exsecutio`
- `python3 scripts/ci_check.py`（本轮提交后跑）

## 评分

- Content: **44 / 50**
- HTML: **12 / 25**
- PDF: **14 / 25**
- **Total: 70 / 100**

## 下一轮

Round 04：术语与 planned 软表述扫尾；随后进入 HTML 设计系统。
