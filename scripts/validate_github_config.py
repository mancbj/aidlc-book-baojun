#!/usr/bin/env python3
"""Validate the repository's GitHub collaboration and automation contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
ISSUE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
PINNED_ACTION_RE = re.compile(r"^\s*uses:\s*[^\s@]+@([0-9a-f]{40})(?:\s+#\s+v\S+)?\s*$", re.MULTILINE)
ANY_ACTION_RE = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)


def require_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path.relative_to(ROOT)}: 无法读取：{exc}")
        return ""


def require_tokens(path: Path, text: str, tokens: Iterable[str], errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{path.relative_to(ROOT)}: 缺少契约标记 {token!r}")


def validate_workflows(errors: list[str]) -> None:
    required = {
        "validate.yml": [
            "pull_request:",
            "workflow_dispatch:",
            "permissions:\n  contents: read",
            "Run the read-only PR gate",
            "scripts/ci_check.py",
        ],
        "pages.yml": [
            "branches: [main]",
            "scripts/prepare_pages.py",
            "--commit-sha \"$GITHUB_SHA\"",
            "actions/upload-pages-artifact@",
            "actions/configure-pages@",
            "enablement: true",
            "actions/deploy-pages@",
            "id-token: write",
            "progress-record.tgz",
        ],
        "release.yml": [
            "tags: [\"v*\"]",
            "Resolve and validate version",
            "scripts/check_release_readiness.py",
            "scripts/render_release_notes.py",
            "scripts/prepare_release.py",
            "scripts/stage_release_rc_assets.py",
            "Ensure bilingual RC book assets",
            "release-notes.md",
            "release-candidate",
            "gh release create",
            "--draft",
            "refusing overwrite",
        ],
        "project-sync.yml": [
            "workflow_dispatch:",
            "scripts/sync_github_project.py",
            "--force-reproject",
            "git diff --exit-code -- progress/tasks.json",
        ],
        "post-release.yml": [
            "types: [published]",
            "scripts/open_next_cycle.py",
            "release_published",
            "pull-requests: write",
            "next-cycle-record.tgz",
        ],
    }
    combined = ""
    for name, tokens in required.items():
        path = WORKFLOW_DIR / name
        text = require_text(path, errors)
        combined += text + "\n"
        require_tokens(path, text, tokens, errors)
        for action in ANY_ACTION_RE.findall(text):
            if action.startswith("./"):
                continue
            if not re.fullmatch(r"[^\s@]+@[0-9a-f]{40}", action):
                errors.append(
                    f"{path.relative_to(ROOT)}: Action 未锁定到 40 位提交 SHA：{action}"
                )
        uses_count = len([a for a in ANY_ACTION_RE.findall(text) if not a.startswith("./")])
        pinned_count = len(PINNED_ACTION_RE.findall(text))
        if uses_count != pinned_count:
            errors.append(
                f"{path.relative_to(ROOT)}: Action 锁定/版本注释不完整 "
                f"({pinned_count}/{uses_count})"
            )

    if "pull_request_target:" in combined:
        errors.append(".github/workflows: 禁止 pull_request_target；Fork PR 必须保持不可信、只读。")
    validate_text = require_text(WORKFLOW_DIR / "validate.yml", errors)
    if "contents: write" in validate_text or "secrets." in validate_text:
        errors.append(".github/workflows/validate.yml: PR 门禁不得写仓库或读取秘密。")
    if "permissions:\n  contents: read" not in validate_text:
        errors.append(".github/workflows/validate.yml: 顶层权限必须显式为 contents: read。")
    ci_path = ROOT / "scripts" / "ci_check.py"
    ci_text = require_text(ci_path, errors)
    require_tokens(
        ci_path,
        ci_text,
        ["validate_pr_metadata.py", "GITHUB_EVENT_PATH", "--pr-body-file", "--required"],
        errors,
    )
    pages_builder = ROOT / "scripts" / "prepare_pages.py"
    pages_text = require_text(pages_builder, errors)
    require_tokens(
        pages_builder,
        pages_text,
        ["Source commit", "Source facts", "publish-manifest.json", "commit_sha"],
        errors,
    )


def validate_issue_forms(errors: list[str]) -> None:
    forms = {
        "writing.yml": ("id: task_id", "id: goal", "id: artifacts", "id: acceptance"),
        "experiment.yml": (
            "id: task_id",
            "id: experiment_id",
            "id: triage",
            "id: artifacts",
            "id: acceptance",
        ),
        "bug.yml": ("id: task_id", "id: actual", "id: artifacts", "id: acceptance"),
        "feedback.yml": ("id: task_id", "id: observation", "id: artifacts", "id: acceptance"),
    }
    for name, tokens in forms.items():
        path = ISSUE_DIR / name
        text = require_text(path, errors)
        require_tokens(path, text, tokens, errors)
        if text.count("required: true") < len(tokens):
            errors.append(f"{path.relative_to(ROOT)}: 必填字段数量少于核心契约字段。")

    config = require_text(ISSUE_DIR / "config.yml", errors)
    require_tokens(ISSUE_DIR / "config.yml", config, ["blank_issues_enabled: false"], errors)
    pr_path = ROOT / ".github" / "pull_request_template.md"
    pr = require_text(pr_path, errors)
    require_tokens(
        pr_path,
        pr,
        ["Task ID", "## 产物", "## 测试与构建", "## 验收", "## 风险与回滚"],
        errors,
    )


def validate_taxonomy(errors: list[str]) -> None:
    path = ROOT / ".github" / "labels.yml"
    text = require_text(path, errors)
    names = re.findall(r"\{name:\s*\"([^\"]+)\"", text)
    colors = re.findall(r"color:\s*\"([^\"]+)\"", text)
    if len(names) != len(set(names)):
        errors.append(f"{path.relative_to(ROOT)}: label 名称必须唯一。")
    if len(colors) != len(names) or any(not re.fullmatch(r"[0-9a-fA-F]{6}", color) for color in colors):
        errors.append(f"{path.relative_to(ROOT)}: 每个 label 必须有 6 位十六进制颜色。")
    if len(colors) != len(set(colors)):
        errors.append(f"{path.relative_to(ROOT)}: label 颜色必须唯一，便于鸟瞰辨识。")
    required = {
        "type:writing",
        "type:experiment",
        "type:engineering",
        "type:review",
        "type:release",
        "priority:must",
        "priority:should",
        "priority:could",
        "status:blocked",
    }
    missing = sorted(required - set(names))
    if missing:
        errors.append(f"{path.relative_to(ROOT)}: 缺少 labels：{', '.join(missing)}")

    doc_path = ROOT / "planning" / "github-taxonomy.md"
    doc = require_text(doc_path, errors)
    require_tokens(
        doc_path,
        doc,
        [
            ".github/labels.yml",
            "planning/github-milestones.md",
            "v0.0.1",
            "v0.1",
            "type:writing",
            "type:experiment",
            "type:engineering",
            "priority:must",
            "priority:should",
            "priority:could",
            "phase:github",
            "phase:release",
            "status:blocked",
            "GitHub Issues、Pull Requests、Milestones 和 Projects 用于协作",
        ],
        errors,
    )


def validate_project_schema(errors: list[str]) -> None:
    path = ROOT / "planning" / "github-project.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: 无法读取有效 JSON：{exc}")
        return
    fields = data.get("fields", [])
    views = data.get("views", [])
    field_names = [field.get("name") for field in fields if isinstance(field, dict)]
    view_names = [view.get("name") for view in views if isinstance(view, dict)]
    expected_fields = {
        "Status",
        "Priority",
        "Type",
        "Day",
        "Chapter",
        "Experiment",
        "Milestone",
        "Artifact",
        "Task ID",
    }
    expected_views = {"Board", "Roadmap", "Chapters", "Experiments"}
    if len(fields) != 9 or set(field_names) != expected_fields:
        errors.append(f"{path.relative_to(ROOT)}: 必须恰好定义约定的 9 个字段。")
    if len(views) != 4 or set(view_names) != expected_views:
        errors.append(f"{path.relative_to(ROOT)}: 必须恰好定义约定的 4 个鸟瞰视图。")
    if data.get("authority") != "repository-to-project":
        errors.append(f"{path.relative_to(ROOT)}: authority 必须是 repository-to-project。")
    sync = data.get("sync", {})
    if sync.get("default_mode") != "dry-run" or sync.get("divergence_policy") != "report-and-stop":
        errors.append(f"{path.relative_to(ROOT)}: 默认 dry-run 与分歧停止策略不可删除。")

    doc_path = ROOT / "planning" / "github-project.md"
    doc = require_text(doc_path, errors)
    require_tokens(
        doc_path,
        doc,
        [
            "Board",
            "Roadmap",
            "Chapter / Chapters",
            "Experiment / Experiments",
            "Status",
            "Priority",
            "Type",
            "Day",
            "Task ID",
            "scripts/sync_github_project.py",
            "progress/generated/project-sync-report.json",
            "GitHub Projects V2 对 view layout 的自动化接口并不稳定",
        ],
        errors,
    )


def main() -> int:
    errors: list[str] = []
    validate_workflows(errors)
    validate_issue_forms(errors)
    validate_taxonomy(errors)
    validate_project_schema(errors)
    if errors:
        for error in errors:
            print(f"[ERROR] {error} 修复：恢复 implementation-plan.md 中的安全和字段契约。", file=sys.stderr)
        return 1
    print("[INFO] GitHub configuration passed: workflows=5, issue_forms=4, fields=9, views=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
