# Tests

运行：

```text
python3 -m unittest discover -s tests
```

测试使用临时目录和最小 JSON 夹具，不修改真实 `progress/` 数据。

- `test_validate_project.py`：事实完整性和条件门禁
- `test_progress_core.py`：指标、排序、阻塞、章节/实验聚合和事件差异
- `test_generate_progress.py`：完整生成、重复运行、失败安全、快照冲突和页面契约
- `test_build_book.py`：一条命令生成离线 HTML 书稿候选、哈希清单与安全覆盖门禁
