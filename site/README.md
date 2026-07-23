# Static Progress Dashboard

- `index.html`：由 `scripts/generate_progress.py` 自动生成的无 JavaScript 回退页面
- `details.html`：42 个任务、10 章和 30 个实验的稳定对象锚点与产物入口
- `data/progress.json`：与当前机器摘要同源的数据投影
- `assets/dashboard.css`：IBM Carbon 风格、响应式和焦点样式
- `assets/dashboard.js`：下一动作过滤增强；核心内容不依赖它

在仓库根目录运行 `python3 scripts/generate_progress.py` 更新页面。不要手工复制统计数字到 HTML。
