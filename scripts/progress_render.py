#!/usr/bin/env python3
"""Render human-readable progress artifacts from one aggregate projection."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from progress_core import CHAPTER_STAGE_NAMES, STATUS_LABELS


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _pct(value: Any) -> str:
    return f"{float(value):.1f}%"


def render_current_markdown(projection: Dict[str, Any], recent_events: Sequence[Dict[str, Any]]) -> str:
    tasks = projection["tasks"]
    goal = projection["goal"]
    must = tasks["priority"]["must"]
    should = tasks["priority"]["should"]
    lines = [
        "# 当前写作进度",
        "",
        "> 本文件由 `python3 scripts/generate_progress.py` 自动生成，请勿手工维护统计数字。",
        "",
        f"- 目标：{goal['name']}",
        f"- 当前：Day {goal['current_day']} / {goal['total_days']}，剩余 {goal['days_remaining']} 个计划日",
        f"- 总进度：{tasks['done']}/{tasks['total']}（{_pct(tasks['percent'])}）",
        f"- 加权进度：{_pct(tasks['weighted_percent'])}",
        f"- Must：{must['done']}/{must['total']}（{_pct(must['percent'])}）",
        f"- Should：{should['done']}/{should['total']}（{_pct(should['percent'])}）",
        f"- 阻塞：{len(projection['blockers'])}",
        f"- 反馈：{projection.get('feedback', {}).get('total', 0)} 条；accepted {projection.get('feedback', {}).get('decision_counts', {}).get('accepted', 0)} 条",
        f"- 下一周期：{projection.get('cycles', {}).get('active_cycle') or '尚未激活'}",
        f"- 事实最近更新：{projection['latest_fact_update'] or '尚无'}",
        f"- 来源：`{projection['source_id']}`",
        "",
        "## 下一动作",
        "",
    ]
    if projection["next_actions"]:
        for index, task in enumerate(projection["next_actions"], start=1):
            scope = task.get("scope_label") or f"Day {task['day']}"
            lines.append(
                f"{index}. **{task['id']} · {task['title']}** — {task['priority'].upper()} / {task['status_label']} / {scope}"
            )
    else:
        lines.append(projection["release_message"] or "当前没有依赖已满足的普通任务，请先处理阻塞项。")

    lines.extend(["", "## 阻塞", ""])
    if projection["blockers"]:
        for blocker in projection["blockers"]:
            lines.append(f"- **{blocker['id']} · {blocker['title']}**：{blocker['reason']}")
            lines.append(f"  - 解除动作：{blocker['unblock_action']}")
    else:
        lines.append("- 当前没有阻塞任务。")

    lines.extend(["", "## 最近关键更新", ""])
    if recent_events:
        for event in list(recent_events)[-10:][::-1]:
            lines.append(f"- `{event['occurred_at']}` · {event['summary']} (`{event['id']}`)")
    else:
        lines.append("- 尚无关键更新事件。")

    lines.extend(
        [
            "",
            "## 下钻入口",
            "",
            "- [鸟瞰驾驶舱](../../site/index.html)",
            "- [时间线与生产线](../../site/progress.html)",
            "- [任务事实](../tasks.json)",
            "- [章节事实](../chapters.json)",
            "- [实验事实](../experiments.json)",
            "- [反馈事实](../../feedback/decisions.json)",
            "- [周期事实](../cycles.json)",
            "- [完整变更日志](../CHANGELOG.md)",
            "",
        ]
    )
    return "\n".join(lines)


def append_changelog(
    existing: str,
    events: Sequence[Dict[str, Any]],
    snapshot_name: str,
    source_id: str,
) -> str:
    if not existing.strip():
        existing = (
            "# Progress Changelog\n\n"
            "> 由进度生成器根据关键状态变化自动追加。完整机器事件见 "
            "[`events/events.jsonl`](events/events.jsonl)。\n"
        )
    if not events:
        return existing
    occurred_at = events[0]["occurred_at"]
    lines = [
        existing.rstrip(),
        "",
        f"## {occurred_at} · `{source_id}`",
        "",
        f"快照：[`{snapshot_name}`](snapshots/{snapshot_name})",
        "",
    ]
    for event in events:
        lines.append(f"- **{event['type']}** · {event['summary']} (`{event['id']}`)")
    lines.append("")
    return "\n".join(lines)


def _status_badge(status: str) -> str:
    label = STATUS_LABELS.get(status, status)
    symbol = {
        "done": "✓",
        "in-progress": "◐",
        "review": "◆",
        "blocked": "!",
        "ready": "→",
        "backlog": "·",
        "pending": "·",
        "planned": "·",
        "verified": "✓",
    }.get(status, "·")
    return f'<span class="status status--{_e(status)}"><span aria-hidden="true">{symbol}</span> {_e(label)}</span>'


def _metric_card(label: str, value: str, detail: str, modifier: str = "") -> str:
    class_name = "metric" + (f" metric--{modifier}" if modifier else "")
    return (
        f'<article class="{class_name}"><p class="metric__label">{_e(label)}</p>'
        f'<p class="metric__value">{_e(value)}</p><p class="metric__detail">{_e(detail)}</p></article>'
    )


def _repo_link(path: str) -> str:
    normalized = path[2:] if path.startswith("./") else path
    return "../" + normalized


def _stable_anchor(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value]
    return "-".join("".join(chars).split("-")).strip("-") or "item"


def _render_timeline(projection: Dict[str, Any], element_id: str = "progress-timeline") -> str:
    timeline = "".join(
        (
            f'<a class="day-card{" day-card--current" if day["is_current"] else ""}" '
            f'href="{_e(day["href"])}" aria-label="Day {day["day"]}：{day["done"]}/{day["total"]} 完成">'
            f'<span class="day-card__day">D{day["day"]:02d}</span>'
            f'<span class="day-card__bar"><span style="width:{day["percent"]}%"></span></span>'
            f'<strong>{day["done"]}/{day["total"]}</strong>'
            f'<small>{"当前" if day["is_current"] else ("受阻 " + str(day["blocked"]) if day["blocked"] else "计划")}</small></a>'
        )
        for day in projection["tasks"]["timeline"]
    )
    return f'<div id="{_e(element_id)}" class="timeline">{timeline}</div>'


def _render_chapter_table(projection: Dict[str, Any]) -> str:
    chapter_rows = []
    for chapter in projection["chapters"]["rows"]:
        cells = "".join(
            f'<td data-label="{_e(stage["label"])}">{_status_badge(stage["status"])}</td>'
            for stage in chapter["stages"]
        )
        chapter_rows.append(
            f'<tr><th scope="row"><a href="{_e(chapter["href"])}">{_e(chapter["id"])} · {_e(chapter["title"])}</a>'
            f'<small>下一缺口：{_e(chapter["next_gap_label"])}</small></th>{cells}'
            f'<td data-label="进度"><strong>{_pct(chapter["percent"])}</strong></td></tr>'
        )
    chapter_headers = "".join(
        f"<th scope=\"col\">{_e(projection['chapters']['stage_totals'][name]['label'])}</th>"
        for name in CHAPTER_STAGE_NAMES
    )
    return (
        '<div class="table-wrap" role="region" aria-label="章节生产线，可横向滚动" tabindex="0">'
        f'<table><thead><tr><th scope="col">章节</th>{chapter_headers}<th scope="col">进度</th></tr></thead>'
        f"<tbody>{''.join(chapter_rows)}</tbody></table></div>"
    )


def _render_experiment_summary(projection: Dict[str, Any]) -> str:
    triage_cards = "".join(
        _metric_card(name, str(count), "个候选实验", "compact")
        for name, count in projection["experiments"]["triage_counts"].items()
    )
    experiment_status = "".join(
        f'<li>{_status_badge(status)}<strong>{count}</strong></li>'
        for status, count in projection["experiments"]["status_counts"].items()
    )
    return (
        f'<div class="metric-grid metric-grid--three">{triage_cards}</div>'
        f'<ul class="status-list status-list--inline" aria-label="实验状态">{experiment_status}</ul>'
    )


def _render_blockers(projection: Dict[str, Any]) -> str:
    if projection["blockers"]:
        return "".join(
            f'<article class="blocker"><h3><a href="{_e(item["href"])}">{_e(item["id"])} · {_e(item["title"])}</a></h3>'
            f'<p><strong>原因：</strong>{_e(item["reason"])}</p><p><strong>解除动作：</strong>{_e(item["unblock_action"])}</p></article>'
            for item in projection["blockers"]
        )
    return '<p class="empty-state"><span aria-hidden="true">✓</span> 当前没有阻塞任务。</p>'


def _render_recent_events(recent_events: Sequence[Dict[str, Any]]) -> str:
    if recent_events:
        return "".join(
            f'<li><time datetime="{_e(event["occurred_at"])}">{_e(event["occurred_at"])}</time>'
            f'<p>{_e(event["summary"])}</p><code>{_e(event["id"])}</code></li>'
            for event in list(recent_events)[-10:][::-1]
        )
    return "<li><p>尚无关键更新事件。</p></li>"


def _render_next_actions(projection: Dict[str, Any]) -> str:
    if projection["next_actions"]:
        return "".join(
            f'<article class="action-card" data-priority="{_e(item["priority"])}">'
            f'<div><span class="eyebrow">{_e(item["priority"].upper())} · DAY {item["day"]}</span>'
            f'<h3><a href="{_e(item["href"])}">{_e(item["id"])} · {_e(item["title"])}</a></h3>'
            f'<p>{_status_badge(item["status"])} · 负责人 {_e(item["owner"])} · 计划 {_e(item["planned_date"])}</p></div>'
            f'<a class="button" href="{_e(item["href"])}">打开任务事实 <span aria-hidden="true">→</span></a></article>'
            for item in projection["next_actions"]
        )
    return f'<p class="empty-state">{_e(projection["release_message"] or "请先处理阻塞项。")}</p>'


def _render_core_link(
    eyebrow: str,
    title: str,
    body: str,
    href: str,
    link_label: str,
) -> str:
    return (
        '<article class="pipeline-card pipeline-card--linked">'
        f'<p class="eyebrow">{_e(eyebrow)}</p><h3>{_e(title)}</h3><p>{_e(body)}</p>'
        f'<a class="card-link" href="{_e(href)}">{_e(link_label)} <span aria-hidden="true">→</span></a>'
        '</article>'
    )


def _render_task_drilldown(facts: Dict[str, Dict[str, Any]], projection: Dict[str, Any]) -> str:
    tasks = list(facts["tasks"].get("tasks", []))
    current_day = projection["goal"]["current_day"]
    day_tasks = [task for task in tasks if task.get("day") == current_day]
    if not day_tasks:
        day_tasks = [task for task in tasks if task.get("status") != "done"][:3]
    if not day_tasks:
        return '<p class="empty-state">全部任务已完成，等待发布或下一周期激活。</p>'

    cards = []
    for task in day_tasks:
        artifacts = task.get("artifacts", [])
        required_count = sum(1 for item in artifacts if item.get("required"))
        acceptance = task.get("acceptance", [])
        passed_count = sum(1 for item in acceptance if item.get("passed"))
        dependencies = ", ".join(task.get("dependencies", [])) or "无"
        cards.append(
            '<article class="action-card action-card--compact">'
            f'<div><span class="eyebrow">{_e(task["priority"].upper())} · DAY {task["day"]}</span>'
            f'<h3><a href="details.html#task-{_e(task["id"])}">{_e(task["id"])} · {_e(task["title"])}</a></h3>'
            f'<p>{_status_badge(task["status"])} · 依赖 {_e(dependencies)} · 产物 {len(artifacts)} / 必需 {required_count} · 验收 {passed_count}/{len(acceptance)}</p></div>'
            f'<a class="button" href="details.html#task-{_e(task["id"])}">任务下钻 <span aria-hidden="true">→</span></a>'
            '</article>'
        )
    return "".join(cards)


def _render_artifact_drilldown(facts: Dict[str, Dict[str, Any]], root: Path) -> str:
    artifact_index: Dict[str, Dict[str, Any]] = {}
    for task in facts["tasks"].get("tasks", []):
        for artifact in task.get("artifacts", []):
            path = artifact.get("path", "").strip()
            if not path:
                continue
            entry = artifact_index.setdefault(
                path,
                {
                    "path": path,
                    "required": False,
                    "tasks": [],
                    "exists": (root / path).exists(),
                },
            )
            entry["required"] = bool(entry["required"] or artifact.get("required"))
            entry["tasks"].append(task["id"])

    if not artifact_index:
        return '<p class="empty-state">尚未声明任务产物。</p>'

    rows = []
    for item in sorted(
        artifact_index.values(),
        key=lambda value: (not value["required"], value["path"]),
    ):
        task_links = " ".join(
            f'<a href="details.html#task-{_e(task_id)}"><code>{_e(task_id)}</code></a>'
            for task_id in item["tasks"]
        )
        if item["exists"]:
            artifact_cell = f'<a href="{_e(_repo_link(item["path"]))}"><code>{_e(item["path"])}</code></a>'
            state = "已生成"
        else:
            artifact_cell = f'<code>{_e(item["path"])}</code>'
            state = "待创建"
        rows.append(
            f'<tr id="artifact-{_stable_anchor(item["path"])}"><th scope="row">{artifact_cell}'
            f'<small>{"必需" if item["required"] else "可选"} · {state}</small></th>'
            f'<td data-label="关联任务">{task_links}</td>'
            f'<td data-label="状态">{_status_badge("done" if item["exists"] else "pending")}</td></tr>'
        )
    return (
        '<div class="table-wrap" role="region" aria-label="产物下钻，可横向滚动" tabindex="0">'
        '<table class="artifact-table"><thead><tr><th scope="col">产物</th><th scope="col">关联任务</th><th scope="col">状态</th></tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _render_github_drilldown(root: Path) -> str:
    entries = [
        ("Issue 表单", ".github/ISSUE_TEMPLATE/writing.yml", "把写作任务结构化为 GitHub Issue。"),
        ("PR 模板", ".github/pull_request_template.md", "让审校、产物和验收在 PR 中可检查。"),
        ("验证 Workflow", ".github/workflows/validate.yml", "在 Pull Request 上运行同一套本地校验。"),
        ("Pages Workflow", ".github/workflows/pages.yml", "把站点产物发布为 GitHub Pages 候选。"),
        ("Projects 说明", "docs/GITHUB-PROJECTS.md", "将事实源投影到 GitHub Projects，而不反客为主。"),
        ("协作说明", "docs/GITHUB-COLLABORATION.md", "协作者如何进入写作、实验、反馈和发布流程。"),
    ]
    cards = []
    for title, path, body in entries:
        if (root / path).exists():
            action = f'<a class="card-link" href="{_e(_repo_link(path))}">打开 GitHub 链接 <span aria-hidden="true">→</span></a>'
        else:
            action = '<span class="planned-label">待创建</span>'
        cards.append(
            '<article class="pipeline-card pipeline-card--linked">'
            f'<p class="eyebrow">GITHUB</p><h3>{_e(title)}</h3><p>{_e(body)}</p>{action}</article>'
        )
    return f'<div class="github-link-grid">{"".join(cards)}</div>'


def render_dashboard(projection: Dict[str, Any], recent_events: Sequence[Dict[str, Any]]) -> str:
    tasks = projection["tasks"]
    goal = projection["goal"]
    must = tasks["priority"]["must"]
    current_day = next(
        (item for item in tasks["timeline"] if item.get("is_current")),
        tasks["timeline"][-1] if tasks["timeline"] else {"done": 0, "total": 0, "percent": 0.0},
    )
    stage_totals = projection["chapters"]["stage_totals"]
    stage_done = sum(item["done"] for item in stage_totals.values())
    stage_total = sum(item["total"] for item in stage_totals.values())
    next_action = projection["next_actions"][0] if projection["next_actions"] else None
    next_value = next_action["id"] if next_action else "无"
    next_detail = next_action["title"] if next_action else (projection["release_message"] or "当前没有依赖已满足的普通任务")
    cards = "".join(
        [
            _metric_card("总体进度", _pct(tasks["percent"]), f"{tasks['done']} / {tasks['total']} 项完成", "blue"),
            _metric_card("Day 进度", f"{current_day['done']}/{current_day['total']}", f"Day {current_day['day']} · {_pct(current_day['percent'])}"),
            _metric_card("倒计时", f"{goal['days_remaining']} 天", f"当前 Day {goal['current_day']} / {goal['total_days']}"),
            _metric_card("章节阶段", f"{stage_done}/{stage_total}", f"十章六阶段 · {_pct((stage_done * 100 / stage_total) if stage_total else 0)}"),
            _metric_card("下一动作", next_value, next_detail),
            _metric_card("阻塞", str(len(projection["blockers"])), "需要先解除的任务", "red" if projection["blockers"] else "green"),
        ]
    )

    status_items = "".join(
        f'<li><span>{_status_badge(status)}</span><strong>{count}</strong></li>'
        for status, count in tasks["status_counts"].items()
    )
    timeline = "".join(
        (
            f'<a class="day-card{" day-card--current" if day["is_current"] else ""}" '
            f'href="{_e(day["href"])}" aria-label="Day {day["day"]}：{day["done"]}/{day["total"]} 完成">'
            f'<span class="day-card__day">D{day["day"]:02d}</span>'
            f'<span class="day-card__bar"><span style="width:{day["percent"]}%"></span></span>'
            f'<strong>{day["done"]}/{day["total"]}</strong>'
            f'<small>{"当前" if day["is_current"] else ("受阻 " + str(day["blocked"]) if day["blocked"] else "计划")}</small></a>'
        )
        for day in tasks["timeline"]
    )

    chapter_rows = []
    for chapter in projection["chapters"]["rows"]:
        cells = "".join(
            f'<td data-label="{_e(stage["label"])}">{_status_badge(stage["status"])}</td>'
            for stage in chapter["stages"]
        )
        chapter_rows.append(
            f'<tr><th scope="row"><a href="{_e(chapter["href"])}">{_e(chapter["id"])} · {_e(chapter["title"])}</a>'
            f'<small>下一缺口：{_e(chapter["next_gap_label"])}</small></th>{cells}'
            f'<td data-label="进度"><strong>{_pct(chapter["percent"])}</strong></td></tr>'
        )
    chapter_headers = "".join(
        f"<th scope=\"col\">{_e(projection['chapters']['stage_totals'][name]['label'])}</th>"
        for name in CHAPTER_STAGE_NAMES
    )

    triage_cards = "".join(
        _metric_card(name, str(count), "个候选实验", "compact")
        for name, count in projection["experiments"]["triage_counts"].items()
    )
    experiment_status = "".join(
        f'<li>{_status_badge(status)}<strong>{count}</strong></li>'
        for status, count in projection["experiments"]["status_counts"].items()
    )

    feedback = projection.get("feedback", {})
    decision_counts = feedback.get("decision_counts", {})
    reader_counts = feedback.get("reader_counts", {})
    feedback_cards = "".join(
        _metric_card(label, str(decision_counts.get(key, 0)), "条反馈决策", "compact")
        for key, label in (
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("deferred", "Deferred"),
        )
    )
    reader_summary = " · ".join(
        f"{name} {reader_counts.get(name, 0)}"
        for name in ("not-invited", "invited", "responded")
    )
    cycle_rows = projection.get("cycles", {}).get("rows", [])
    if cycle_rows:
        cycle_html = "".join(
            f'<article class="action-card"><div><span class="eyebrow">{_e(item["status"].upper())}</span>'
            f'<h3><a href="{_e(item["href"])}">{_e(item["id"])}</a></h3>'
            f'<p>{_e(item["monthly_target"])} · {item["task_done"]}/{item["task_total"]} tasks · '
            f'{item["carried_task_total"]} carried · {item["carried_gap_total"]} gaps</p></div></article>'
            for item in cycle_rows
        )
    else:
        cycle_html = '<p class="empty-state">尚无下一周期草案。</p>'

    if projection["blockers"]:
        blocker_html = "".join(
            f'<article class="blocker"><h3><a href="{_e(item["href"])}">{_e(item["id"])} · {_e(item["title"])}</a></h3>'
            f'<p><strong>原因：</strong>{_e(item["reason"])}</p><p><strong>解除动作：</strong>{_e(item["unblock_action"])}</p></article>'
            for item in projection["blockers"]
        )
    else:
        blocker_html = '<p class="empty-state"><span aria-hidden="true">✓</span> 当前没有阻塞任务。</p>'

    if recent_events:
        event_html = "".join(
            f'<li><time datetime="{_e(event["occurred_at"])}">{_e(event["occurred_at"])}</time>'
            f'<p>{_e(event["summary"])}</p><code>{_e(event["id"])}</code></li>'
            for event in list(recent_events)[-10:][::-1]
        )
    else:
        event_html = "<li><p>尚无关键更新事件。</p></li>"

    if projection["next_actions"]:
        action_html = "".join(
            f'<article class="action-card" data-priority="{_e(item["priority"])}">'
            f'<div><span class="eyebrow">{_e(item["priority"].upper())} · DAY {item["day"]}</span>'
            f'<h3><a href="{_e(item["href"])}">{_e(item["id"])} · {_e(item["title"])}</a></h3>'
            f'<p>{_status_badge(item["status"])} · 负责人 {_e(item["owner"])} · 计划 {_e(item["planned_date"])}</p></div>'
            f'<a class="button" href="{_e(item["href"])}">打开任务事实 <span aria-hidden="true">→</span></a></article>'
            for item in projection["next_actions"]
        )
    else:
        action_html = f'<p class="empty-state">{_e(projection["release_message"] or "请先处理阻塞项。")}</p>'

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI-DLC Book 两周 v0.1 自动进度鸟瞰驾驶舱">
  <title>AI-DLC Book · 进度驾驶舱</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/dashboard.css">
</head>
<body>
  <a class="skip-link" href="#main">跳到主要内容</a>
  <header class="topbar">
    <a class="brand" href="../README.md"><span>AI-DLC</span> BOOK OPS</a>
    <nav aria-label="主要导航">
      <a aria-current="page" href="index.html">驾驶舱</a>
      <a href="progress.html">生产线</a>
      <a href="../book/part-00-overview.md">Part 0 导读</a>
      <a href="../progress/generated/current.md">文字摘要</a>
      <a href="details.html">对象下钻</a>
      <a href="../progress/CHANGELOG.md">更新记录</a>
    </nav>
  </header>
  <main id="main">
    <section class="hero" aria-labelledby="page-title">
      <div>
        <p class="eyebrow">{_e((projection.get('cycles') or {}).get('active_cycle') or goal['name'])} · SOURCE {_e(projection['source_id'])}</p>
        <h1 id="page-title">写作进度<br><span>鸟瞰驾驶舱</span></h1>
        <p class="hero__intro">一个页面看清当前阶段、阻塞、章节生产线、实验队列，以及现在最值得完成的 Must 任务。</p>
      </div>
      <aside class="hero__meta" aria-label="生成信息">
        <p><span>下一动作</span><a class="hero__action" href="{_e(next_action['href']) if next_action else 'details.html#tasks'}"><strong>{_e((next_action['id'] + ' · ' + next_action['title']) if next_action else (projection['release_message'] or '暂无下一动作'))}</strong></a></p>
        <p><span>事实最近更新</span><strong>{_e(projection['latest_fact_update'] or '尚无')}</strong></p>
        <p><span>页面生成时间</span><strong>{_e(projection['generated_at'])}</strong></p>
      </aside>
    </section>

    <section class="section section--flush" aria-labelledby="overview-title">
      <div class="section__heading"><div><p class="eyebrow">01 · OVERVIEW</p><h2 id="overview-title">两周目标总览</h2></div><p>{_e(goal['name'])}</p></div>
      <div class="metric-grid">{cards}</div>
      <div class="overview-split">
        <div><h3>任务状态</h3><ul class="status-list">{status_items}</ul></div>
        <div><h3>当前第一动作</h3>{action_html.split('</article>')[0] + '</article>' if projection['next_actions'] else action_html}</div>
      </div>
    </section>

    <section class="section" aria-labelledby="timeline-title">
      <div class="section__heading"><div><p class="eyebrow">02 · TIMELINE</p><h2 id="timeline-title">任务时间线</h2></div><a href="../planning/14-day-v0.1.md">查看 v0.1 计划 →</a></div>
      <div class="timeline">{timeline}</div>
    </section>

    <section class="section" aria-labelledby="chapters-title">
      <div class="section__heading"><div><p class="eyebrow">03 · CHAPTER FACTORY</p><h2 id="chapters-title">十章六阶段生产线</h2></div><a href="../progress/chapters.json">下钻章节事实 →</a></div>
      <div class="table-wrap" role="region" aria-label="章节生产线，可横向滚动" tabindex="0">
        <table><thead><tr><th scope="col">章节</th>{chapter_headers}<th scope="col">进度</th></tr></thead><tbody>{''.join(chapter_rows)}</tbody></table>
      </div>
    </section>

    <section class="section" aria-labelledby="experiments-title">
      <div class="section__heading"><div><p class="eyebrow">04 · EXPERIMENTS</p><h2 id="experiments-title">实验治理队列</h2></div><a href="details.html#experiments">下钻 30 个实验 →</a></div>
      <div class="metric-grid metric-grid--three">{triage_cards}</div>
      <ul class="status-list status-list--inline" aria-label="实验状态">{experiment_status}</ul>
    </section>

    <section class="section" aria-labelledby="feedback-title">
      <div class="section__heading"><div><p class="eyebrow">05 · FEEDBACK / CYCLE</p><h2 id="feedback-title">反馈闭环与下一周期</h2></div><a href="details.html#feedback">查看决策下钻 →</a></div>
      <div class="metric-grid">{feedback_cards}</div>
      <p class="empty-state">Reader slots：{_e(reader_summary)} · 未关联 accepted：{feedback.get('unresolved_accepted', 0)}</p>
      <div id="cycle-overview">{cycle_html}</div>
    </section>

    <section class="section section--dark" aria-labelledby="blockers-title">
      <div class="section__heading"><div><p class="eyebrow">06 · BLOCKERS</p><h2 id="blockers-title">阻塞中心</h2></div><a href="details.html#tasks">查看任务下钻 →</a></div>
      <div class="blocker-grid">{blocker_html}</div>
    </section>

    <section class="section two-column" aria-label="关键更新和下一动作">
      <div>
        <div class="section__heading"><div><p class="eyebrow">07 · EVENTS</p><h2>最近关键更新</h2></div><a href="../progress/CHANGELOG.md">完整记录 →</a></div>
        <ol class="event-list">{event_html}</ol>
      </div>
      <div>
        <div class="section__heading"><div><p class="eyebrow">08 · NEXT</p><h2>可立即执行</h2></div></div>
        <div class="filter-bar" aria-label="下一动作过滤器"><button class="filter is-active" type="button" data-filter="all" aria-pressed="true">全部</button><button class="filter" type="button" data-filter="must" aria-pressed="false">Must</button><button class="filter" type="button" data-filter="should" aria-pressed="false">Should</button></div>
        <div id="next-actions">{action_html}</div>
      </div>
    </section>
  </main>
  <footer><p>数字来自版本化事实源，页面由 <code>scripts/generate_progress.py</code> 自动生成。</p><a href="../docs/PROGRESS-AUTOMATION.md">自动记录规则</a></footer>
  <script src="assets/dashboard.js" defer></script>
</body>
</html>
"""


def render_progress_page(
    facts: Dict[str, Dict[str, Any]],
    projection: Dict[str, Any],
    root: Path,
    recent_events: Sequence[Dict[str, Any]],
) -> str:
    tasks = projection["tasks"]
    goal = projection["goal"]
    current_day = next(
        (item for item in tasks["timeline"] if item.get("is_current")),
        tasks["timeline"][-1] if tasks["timeline"] else {"day": 0, "done": 0, "total": 0, "percent": 0.0},
    )
    stage_totals = projection["chapters"]["stage_totals"]
    stage_done = sum(item["done"] for item in stage_totals.values())
    stage_total = sum(item["total"] for item in stage_totals.values())
    experiment_total = sum(projection["experiments"]["status_counts"].values())
    experiment_done = projection["experiments"]["status_counts"].get(
        "verified",
        projection["experiments"]["status_counts"].get("done", 0),
    )
    next_action = projection["next_actions"][0] if projection["next_actions"] else None
    pipeline_metrics = "".join(
        [
            _metric_card("时间线", f"D{current_day['day']:02d}", f"{current_day['done']}/{current_day['total']} · {_pct(current_day['percent'])}", "blue"),
            _metric_card("章节生产线", f"{stage_done}/{stage_total}", "十章六阶段完成量"),
            _metric_card("实验生产线", f"{experiment_done}/{experiment_total}", "verified / total"),
            _metric_card("阻塞", str(len(projection["blockers"])), "影响后续流动的任务", "red" if projection["blockers"] else "green"),
        ]
    )
    compass_cards = "".join(
        [
            _render_core_link("INPUT", "任务事实源", "任务 JSON 是行动、写作卡片与验收的权威输入。", "#task-drilldown", "打开任务下钻"),
            _render_core_link("OUTPUT", "产物索引", "每个任务声明的必需产物都能回到任务和文件。", "#artifact-drilldown", "打开产物下钻"),
            _render_core_link("GITHUB", "协作入口", "Issue、PR、Workflow 和 Projects 是后续多人协作入口。", "#github-drilldown", "打开 GitHub 链接"),
            _render_core_link("TRACE", "事件账本", "关键更新自动写入事件、快照和变更日志。", "#event-production", "查看最近事件"),
        ]
    )
    timeline_html = _render_timeline(projection)
    chapter_table = _render_chapter_table(projection)
    experiment_html = _render_experiment_summary(projection)
    blocker_html = _render_blockers(projection)
    event_html = _render_recent_events(recent_events)
    task_drilldown_html = _render_task_drilldown(facts, projection)
    artifact_drilldown_html = _render_artifact_drilldown(facts, root)
    github_drilldown_html = _render_github_drilldown(root)

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI-DLC Book 时间线、章节、实验、阻塞和最近事件生产线视图">
  <title>AI-DLC Book · 时间线与生产线</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/dashboard.css">
</head>
<body>
  <a class="skip-link" href="#main">跳到主要内容</a>
  <header class="topbar">
    <a class="brand" href="../README.md"><span>AI-DLC</span> BOOK OPS</a>
    <nav aria-label="主要导航">
      <a href="index.html">驾驶舱</a>
      <a aria-current="page" href="progress.html">生产线</a>
      <a href="../book/part-00-overview.md">Part 0 导读</a>
      <a href="../progress/generated/current.md">文字摘要</a>
      <a href="details.html">对象下钻</a>
      <a href="../progress/CHANGELOG.md">更新记录</a>
    </nav>
  </header>
  <main id="main">
    <section class="hero" aria-labelledby="progress-title">
      <div>
        <p class="eyebrow">PRODUCTION LINE · SOURCE {_e(projection['source_id'])}</p>
        <h1 id="progress-title">时间线与<br><span>生产线</span></h1>
        <p class="hero__intro">把“今天做什么、章节推进到哪、实验如何服务样章、阻塞在哪里、最近发生了什么”放在同一张鸟瞰图里。</p>
      </div>
      <aside class="hero__meta" aria-label="生成信息">
        <p><span>下一动作</span><a class="hero__action" href="{_e(next_action['href']) if next_action else 'details.html#tasks'}"><strong>{_e((next_action['id'] + ' · ' + next_action['title']) if next_action else (projection['release_message'] or '暂无下一动作'))}</strong></a></p>
        <p><span>当前目标</span><strong>{_e(goal['name'])}</strong></p>
        <p><span>页面生成时间</span><strong>{_e(projection['generated_at'])}</strong></p>
      </aside>
    </section>

    <section class="section section--flush" aria-labelledby="pipeline-overview-title">
      <div class="section__heading"><div><p class="eyebrow">01 · PIPELINE OVERVIEW</p><h2 id="pipeline-overview-title">生产线鸟瞰</h2></div><p>指标在首页，流动关系在这里。</p></div>
      <div class="metric-grid metric-grid--four">{pipeline_metrics}</div>
      <div class="pipeline-grid" aria-label="生产线读法">{compass_cards}</div>
    </section>

    <section class="section" id="timeline-production" aria-labelledby="timeline-production-title">
      <div class="section__heading"><div><p class="eyebrow">02 · TIMELINE</p><h2 id="timeline-production-title">任务时间线</h2></div><a href="../planning/14-day-v0.1.md">查看 v0.1 计划 →</a></div>
      {timeline_html}
    </section>

    <section class="section" id="chapter-production" aria-labelledby="chapter-production-title">
      <div class="section__heading"><div><p class="eyebrow">03 · CHAPTER FACTORY</p><h2 id="chapter-production-title">章节生产线</h2></div><a href="../progress/chapters.json">打开章节事实 →</a></div>
      {chapter_table}
    </section>

    <section class="section two-column" aria-label="实验与阻塞生产线">
      <div id="experiment-production">
        <div class="section__heading"><div><p class="eyebrow">04 · EXPERIMENTS</p><h2>实验生产线</h2></div><a href="details.html#experiments">实验下钻 →</a></div>
        {experiment_html}
      </div>
      <div id="blocker-production">
        <div class="section__heading"><div><p class="eyebrow">05 · BLOCKERS</p><h2>阻塞中心</h2></div><a href="details.html#tasks">任务下钻 →</a></div>
        <div class="blocker-grid blocker-grid--single">{blocker_html}</div>
      </div>
    </section>

    <section class="section" id="task-drilldown" aria-labelledby="task-drilldown-title">
      <div class="section__heading"><div><p class="eyebrow">06 · TASK DRILLDOWN</p><h2 id="task-drilldown-title">任务下钻</h2></div><a href="details.html#tasks">打开完整任务详情 →</a></div>
      <div class="drilldown-stack">{task_drilldown_html}</div>
    </section>

    <section class="section" id="artifact-drilldown" aria-labelledby="artifact-drilldown-title">
      <div class="section__heading"><div><p class="eyebrow">07 · ARTIFACT DRILLDOWN</p><h2 id="artifact-drilldown-title">产物下钻</h2></div><a href="../progress/tasks.json">查看任务事实源 →</a></div>
      {artifact_drilldown_html}
    </section>

    <section class="section" id="github-drilldown" aria-labelledby="github-drilldown-title">
      <div class="section__heading"><div><p class="eyebrow">08 · GITHUB LINKS</p><h2 id="github-drilldown-title">GitHub 链接</h2></div><a href="../docs/GITHUB-COLLABORATION.md">协作说明 →</a></div>
      {github_drilldown_html}
    </section>

    <section class="section" id="event-production" aria-labelledby="event-production-title">
      <div class="section__heading"><div><p class="eyebrow">09 · EVENTS</p><h2 id="event-production-title">最近事件</h2></div><a href="../progress/CHANGELOG.md">完整记录 →</a></div>
      <ol class="event-list">{event_html}</ol>
    </section>
  </main>
  <footer><p>本页由 <code>scripts/generate_progress.py</code> 自动渲染；所有状态来自版本化事实源。</p><a href="index.html">返回驾驶舱</a></footer>
</body>
</html>
"""


def render_details(
    facts: Dict[str, Dict[str, Any]], projection: Dict[str, Any], root: Path
) -> str:
    tasks = facts["tasks"].get("tasks", [])
    chapters = facts["chapters"].get("chapters", [])
    experiments = facts["experiments"].get("experiments", [])
    feedback_decisions = facts.get("feedback", {}).get("decisions", [])
    cycles = facts.get("cycles", {}).get("cycles", [])

    day_sections = []
    task_days = sorted({int(item.get("day")) for item in tasks if isinstance(item.get("day"), int)})
    for day in task_days:
        task_cards = []
        for task in (item for item in tasks if item.get("day") == day):
            artifact_items = []
            for item in task.get("artifacts", []):
                path = item["path"]
                required = " · 必需" if item.get("required") else ""
                if (root / path).exists():
                    artifact_items.append(
                        f'<li><a href="{_e(_repo_link(path))}"><code>{_e(path)}</code></a>{required}</li>'
                    )
                else:
                    artifact_items.append(
                        f'<li><code>{_e(path)}</code>{required} · <span class="planned-label">待创建</span></li>'
                    )
            artifacts = "".join(artifact_items) or "<li>未声明产物</li>"
            dependencies = ", ".join(task.get("dependencies", [])) or "无"
            task_cards.append(
                f'<article class="detail-card" id="task-{_e(task["id"])}"><div class="detail-card__head">'
                f'<span class="eyebrow">{_e(task["priority"].upper())} · {_e(task["id"])}</span>{_status_badge(task["status"])}</div>'
                f'<h3>{_e(task["title"])}</h3><p>负责人：{_e(task["owner"])} · 计划：{_e(task["planned_date"])} · 依赖：{_e(dependencies)}</p>'
                f'<h4>产物</h4><ul>{artifacts}</ul><a class="text-link" href="../progress/tasks.json">打开完整任务事实 →</a></article>'
            )
        day_sections.append(
            f'<section class="detail-day" id="day-{day:02d}" aria-labelledby="day-{day:02d}-title">'
            f'<h2 id="day-{day:02d}-title">Day {day:02d}</h2><div class="detail-grid">{"".join(task_cards)}</div></section>'
        )

    writing_card_labels = {
        "outline": "01 · 论证骨架",
        "draft": "02 · 可读稿",
        "review": "03 · 审校证据",
    }
    chapter_writing_sections = []
    for chapter in sorted(chapters, key=lambda item: item.get("number", 999)):
        chapter_tasks = sorted(
            (item for item in tasks if item.get("chapter") == chapter.get("id")),
            key=lambda item: item.get("id", ""),
        )
        if not chapter_tasks:
            continue
        cards = []
        for task in chapter_tasks:
            artifacts = "".join(
                f'<li><code>{_e(item["path"])}</code>{" · 必需" if item.get("required") else ""}</li>'
                for item in task.get("artifacts", [])
            ) or "<li>未声明产物</li>"
            dependencies = ", ".join(task.get("dependencies", [])) or "无"
            card_label = writing_card_labels.get(task.get("card", ""), task.get("card", "写作卡片"))
            cards.append(
                f'<article class="detail-card detail-card--compact" id="chapter-writing-{_e(task["id"])}">'
                f'<div class="detail-card__head"><span class="eyebrow">{_e(card_label)} · {_e(task["id"])}</span>{_status_badge(task["status"])}</div>'
                f'<h3>{_e(task["title"])}</h3><p>Day {int(task["day"]):02d} · 计划：{_e(task["planned_date"])} · 依赖：{_e(dependencies)}</p>'
                f'<p>{_e("; ".join(item.get("text", "") for item in task.get("acceptance", [])))}</p>'
                f'<h4>产物</h4><ul>{artifacts}</ul><a class="text-link" href="#task-{_e(task["id"])}">跳到任务卡 →</a></article>'
            )
        done = sum(1 for item in chapter_tasks if item.get("status") == "done")
        chapter_writing_sections.append(
            f'<section class="detail-day" id="chapter-writing-{_e(chapter["id"])}" aria-labelledby="chapter-writing-{_e(chapter["id"])}-title">'
            f'<h3 id="chapter-writing-{_e(chapter["id"])}-title">{_e(chapter["id"])} · {_e(chapter["title"])} <small>{done}/{len(chapter_tasks)}</small></h3>'
            f'<div class="detail-grid">{"".join(cards)}</div></section>'
        )

    chapter_cards = []
    for chapter in chapters:
        stages = "".join(
            f'<li>{_status_badge(stage["status"])} <span>{_e(stage["name"])}</span></li>'
            for stage in chapter.get("stages", [])
        )
        chapter_cards.append(
            f'<article class="detail-card" id="chapter-{_e(chapter["id"])}"><span class="eyebrow">{_e(chapter["id"])}</span>'
            f'<h3>{_e(chapter["title"])}</h3><p>{_e(chapter["question"])}</p><ul class="stage-list">{stages}</ul>'
            f'<a class="text-link" href="../progress/chapters.json">打开完整章节事实 →</a></article>'
        )

    triage_sections = []
    for triage in ("SHIP", "KEEP-EXT", "ALREADY"):
        cards = []
        for experiment in (item for item in experiments if item.get("triage") == triage):
            cards.append(
                f'<article class="detail-card" id="experiment-{_e(experiment["id"])}"><div class="detail-card__head">'
                f'<span class="eyebrow">{_e(triage)} · {_e(experiment["id"])}</span>{_status_badge(experiment["status"])}</div>'
                f'<h3>{_e(experiment["name"])}</h3><p>章节 {_e(experiment["chapter"])} · 工作量 {_e(experiment["effort"])}</p>'
                f'<p><strong>运行：</strong><code>{_e(experiment["command"])}</code></p>'
                f'<a class="text-link" href="../progress/experiments.json">打开完整实验事实 →</a></article>'
            )
        triage_sections.append(
            f'<section id="experiments-{_e(triage)}"><h3>{_e(triage)} · {len(cards)}</h3><div class="detail-grid">{"".join(cards)}</div></section>'
        )

    feedback_cards = []
    for item in feedback_decisions:
        feedback_cards.append(
            f'<article class="detail-card" id="feedback-{_e(item["id"])}"><div class="detail-card__head">'
            f'<span class="eyebrow">{_e(item["id"])} · {_e(item["decision"].upper())}</span></div>'
            f'<h3>{_e(item["object"])}</h3><p>{_e(item["summary"])}</p>'
            f'<p><strong>关联任务：</strong>{_e(item.get("linked_task") or "未关联")}</p></article>'
        )
    if not feedback_cards:
        feedback_cards.append('<p class="empty-state">尚无反馈决策；匿名 Reader 槽位不代表真实反馈。</p>')

    cycle_sections = []
    for cycle in cycles:
        task_cards = "".join(
            f'<article class="detail-card" id="cycle-task-{_e(task["id"])}"><div class="detail-card__head">'
            f'<span class="eyebrow">{_e(task["priority"].upper())} · {_e(task["id"])}</span>{_status_badge(task["status"])}</div>'
            f'<h3>{_e(task["title"])}</h3><p>{_e("；".join(task.get("acceptance", [])))}</p></article>'
            for task in cycle.get("tasks", [])
        )
        carried_tasks = "".join(
            f'<li><code>{_e(item["id"])}</code> · {_e(item["title"])} · {_e(item["status"])}</li>'
            for item in cycle.get("carried_tasks", [])
        ) or "<li>暂无带入的 v0.1 未完成项。</li>"
        carried_gaps = "".join(
            f'<li><code>{_e(item["code"])}</code> · {_e(item["object"])} · {_e(item["priority"])}</li>'
            for item in cycle.get("carried_gaps", [])
        ) or "<li>暂无带入的公开缺口。</li>"
        cycle_sections.append(
            f'<section id="cycle-{_e(cycle["id"])}"><h3>{_e(cycle["id"])} · {_e(cycle["status"])}</h3>'
            f'<p>{_e(cycle.get("monthly_target", ""))}</p><div class="detail-grid">{task_cards}</div>'
            f'<h4>带入的未完成项</h4><ul>{carried_tasks}</ul><h4>带入的公开缺口</h4><ul>{carried_gaps}</ul></section>'
        )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="AI-DLC Book 任务、章节与实验对象下钻">
  <title>AI-DLC Book · 对象下钻</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="assets/dashboard.css">
</head>
<body>
  <a class="skip-link" href="#main">跳到主要内容</a>
  <header class="topbar"><a class="brand" href="../README.md"><span>AI-DLC</span> BOOK OPS</a><nav aria-label="主要导航"><a href="index.html">驾驶舱</a><a href="progress.html">生产线</a><a aria-current="page" href="details.html">对象下钻</a><a href="../progress/generated/current.md">文字摘要</a></nav></header>
  <main id="main" class="details-main">
    <section class="details-hero"><p class="eyebrow">DRILLDOWN · {_e(projection['source_id'])}</p><h1>从鸟瞰进入<br>具体对象</h1><p>每个 Task ID、章节阶段和实验都保留稳定锚点，并链接到对应产物或权威事实源。</p></section>
    <nav class="anchor-nav" aria-label="对象下钻目录"><a href="#tasks">任务时间线</a><a href="#chapter-writing-cards">十章写作卡片</a><a href="#chapters">十章生产线</a><a href="#experiments">30 个实验</a><a href="#feedback">反馈</a><a href="#cycles">下一周期</a></nav>
    <section class="details-group" id="tasks"><p class="eyebrow">TASKS</p><h2>任务时间线</h2>{''.join(day_sections)}</section>
    <section class="details-group" id="chapter-writing-cards"><p class="eyebrow">WRITING CARDS</p><h2>十章写作任务卡片</h2>{''.join(chapter_writing_sections) or '<p class="empty-state">尚未定义章节写作卡片。</p>'}</section>
    <section class="details-group" id="chapters"><p class="eyebrow">CHAPTERS</p><h2>十章生产线</h2><div class="detail-grid">{''.join(chapter_cards)}</div></section>
    <section class="details-group" id="experiments"><p class="eyebrow">EXPERIMENTS</p><h2>实验治理队列</h2>{''.join(triage_sections)}</section>
    <section class="details-group" id="feedback"><p class="eyebrow">FEEDBACK</p><h2>反馈决策</h2><div class="detail-grid">{''.join(feedback_cards)}</div></section>
    <section class="details-group" id="cycles"><p class="eyebrow">CYCLES</p><h2>持续更新周期</h2>{''.join(cycle_sections)}</section>
  </main>
  <footer><p>下钻内容与驾驶舱由同一次生成运行产生。</p><a href="index.html">返回鸟瞰驾驶舱</a></footer>
</body>
</html>
"""
