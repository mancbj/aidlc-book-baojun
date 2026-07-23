#!/usr/bin/env python3
"""Validate the versioned writing-system fact sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set


TASK_STATUSES = {
    "backlog",
    "ready",
    "in-progress",
    "review",
    "done",
    "blocked",
}
TASK_TYPES = {"writing", "experiment", "engineering", "review", "release"}
TASK_PHASES = {"foundation", "progress", "github", "release"}
PRIORITIES = {"must", "should", "could"}
CHAPTER_STAGE_NAMES = [
    "question",
    "framework",
    "example",
    "experiment",
    "figure",
    "review",
]
CHAPTER_STAGE_STATUSES = {"pending", "in-progress", "done"}
EXPERIMENT_TRIAGE = {"SHIP", "KEEP-EXT", "ALREADY"}
EXPERIMENT_EFFORTS = {"S", "M", "L"}
EXPERIMENT_STATUSES = {"planned", "ready", "in-progress", "verified", "blocked"}
TASK_ID_RE = re.compile(r"^D(?P<day>\d{2})-T\d{2}$")
CHAPTER_ID_RE = re.compile(r"^CH-(?P<number>\d{2})$")


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    source: str
    object_id: str
    field: str
    value: Any
    message: str
    fix: str

    def render(self) -> str:
        value = repr(self.value)
        return (
            f"[{self.level}] {self.source} :: {self.object_id} :: "
            f"{self.field}={value} — {self.message} 修复：{self.fix}"
        )


@dataclass
class ValidationReport:
    issues: List[ValidationIssue]
    task_count: int = 0
    chapter_count: int = 0
    experiment_count: int = 0

    @property
    def errors(self) -> List[ValidationIssue]:
        return [issue for issue in self.issues if issue.level == "ERROR"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [issue for issue in self.issues if issue.level == "WARN"]

    @property
    def ok(self) -> bool:
        return not self.errors


class ProjectValidator:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.issues: List[ValidationIssue] = []

    def error(
        self,
        source: str,
        object_id: str,
        field: str,
        value: Any,
        message: str,
        fix: str,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                "ERROR", source, object_id, field, value, message, fix
            )
        )

    def warn(
        self,
        source: str,
        object_id: str,
        field: str,
        value: Any,
        message: str,
        fix: str,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                "WARN", source, object_id, field, value, message, fix
            )
        )

    def load_json(self, relative_path: str) -> Optional[Dict[str, Any]]:
        path = self.root / relative_path
        if not path.is_file():
            self.error(
                relative_path,
                "document",
                "path",
                relative_path,
                "事实源文件不存在。",
                "创建文件并提交到仓库。",
            )
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.error(
                relative_path,
                "document",
                "json",
                str(exc),
                "无法读取有效 JSON。",
                "修正 JSON 语法和 UTF-8 编码。",
            )
            return None
        if not isinstance(value, dict):
            self.error(
                relative_path,
                "document",
                "root",
                type(value).__name__,
                "顶层必须是 JSON object。",
                "使用包含 schema_version、updated 和记录数组的 object。",
            )
            return None
        return value

    def validate(self) -> ValidationReport:
        tasks_doc = self.load_json("progress/tasks.json")
        chapters_doc = self.load_json("progress/chapters.json")
        experiments_doc = self.load_json("progress/experiments.json")

        task_count = self.validate_tasks(tasks_doc, "progress/tasks.json")
        chapter_ids, chapter_count = self.validate_chapters(
            chapters_doc, "progress/chapters.json"
        )
        experiment_count = self.validate_experiments(
            experiments_doc, chapter_ids, "progress/experiments.json"
        )

        return ValidationReport(
            issues=self.issues,
            task_count=task_count,
            chapter_count=chapter_count,
            experiment_count=experiment_count,
        )

    def validate_document_timestamp(
        self, document: Optional[Dict[str, Any]], source: str
    ) -> None:
        if document is None:
            return
        self.validate_timestamp(
            document.get("updated"), source, "document", "updated"
        )

    def validate_tasks(
        self, document: Optional[Dict[str, Any]], source: str
    ) -> int:
        if document is None:
            return 0
        self.validate_document_timestamp(document, source)
        tasks = document.get("tasks")
        if not isinstance(tasks, list):
            self.error(
                source,
                "document",
                "tasks",
                tasks,
                "tasks 必须是数组。",
                "使用 JSON array 保存任务对象。",
            )
            return 0

        required = {
            "id",
            "title",
            "type",
            "phase",
            "status",
            "priority",
            "owner",
            "day",
            "planned_date",
            "dependencies",
            "artifacts",
            "acceptance",
            "updated",
        }
        by_id: Dict[str, Dict[str, Any]] = {}
        id_sources: Dict[str, int] = {}

        for index, task in enumerate(tasks):
            object_id = self.object_id(task, f"task[{index}]")
            if not isinstance(task, dict):
                self.error(
                    source,
                    object_id,
                    "record",
                    task,
                    "任务必须是 object。",
                    "把该记录改为包含任务字段的 object。",
                )
                continue
            self.require_fields(task, required, source, object_id)

            task_id = task.get("id")
            if isinstance(task_id, str):
                if task_id in by_id:
                    self.error(
                        source,
                        task_id,
                        "id",
                        task_id,
                        f"任务 ID 与 task[{id_sources[task_id]}] 重复。",
                        "为任务分配唯一稳定 ID。",
                    )
                else:
                    by_id[task_id] = task
                    id_sources[task_id] = index
                match = TASK_ID_RE.fullmatch(task_id)
                if not match:
                    self.error(
                        source,
                        task_id,
                        "id",
                        task_id,
                        "任务 ID 不符合 DNN-TNN。",
                        "例如使用 D03-T02。",
                    )
                elif isinstance(task.get("day"), int):
                    encoded_day = int(match.group("day"))
                    if encoded_day != task["day"]:
                        self.error(
                            source,
                            task_id,
                            "day",
                            task["day"],
                            "ID 中的 Day 与 day 字段不一致。",
                            f"把 day 改为 {encoded_day} 或修正 ID。",
                        )

            self.require_nonempty_string(
                task.get("title"), source, object_id, "title"
            )
            self.require_nonempty_string(
                task.get("owner"), source, object_id, "owner"
            )
            self.require_allowed(
                task.get("type"), TASK_TYPES, source, object_id, "type"
            )
            self.require_allowed(
                task.get("phase"), TASK_PHASES, source, object_id, "phase"
            )
            self.require_allowed(
                task.get("status"), TASK_STATUSES, source, object_id, "status"
            )
            self.require_allowed(
                task.get("priority"), PRIORITIES, source, object_id, "priority"
            )

            day = task.get("day")
            if not isinstance(day, int) or isinstance(day, bool) or not 1 <= day <= 14:
                self.error(
                    source,
                    object_id,
                    "day",
                    day,
                    "day 必须是 1–14 的整数。",
                    "使用当前 14 天路线中的相对 Day。",
                )
            self.validate_date(
                task.get("planned_date"), source, object_id, "planned_date"
            )
            self.validate_timestamp(
                task.get("updated"), source, object_id, "updated"
            )
            self.validate_dependencies_shape(task, source, object_id)
            self.validate_artifacts(task, source, object_id)
            self.validate_acceptance(task, source, object_id)
            self.validate_task_conditionals(task, source, object_id)

        known_ids = set(by_id)
        for task_id, task in by_id.items():
            for dependency in task.get("dependencies", []):
                if dependency not in known_ids:
                    self.error(
                        source,
                        task_id,
                        "dependencies",
                        dependency,
                        "任务引用未知依赖。",
                        "修正 ID 或先创建依赖任务。",
                    )

        for cycle in find_dependency_cycles(by_id):
            self.error(
                source,
                cycle[0],
                "dependencies",
                " -> ".join(cycle),
                "检测到循环依赖。",
                "删除或重排至少一条依赖边。",
            )

        for task_id, task in by_id.items():
            if task.get("status") == "done":
                self.validate_done_task(task_id, task, by_id, source)

        return len(tasks)

    def validate_task_conditionals(
        self, task: Dict[str, Any], source: str, object_id: str
    ) -> None:
        if task.get("status") == "blocked":
            self.require_nonempty_string(
                task.get("blocker_reason"),
                source,
                object_id,
                "blocker_reason",
            )
            self.require_nonempty_string(
                task.get("unblock_action"),
                source,
                object_id,
                "unblock_action",
            )

    def validate_done_task(
        self,
        task_id: str,
        task: Dict[str, Any],
        by_id: Dict[str, Dict[str, Any]],
        source: str,
    ) -> None:
        acceptance = task.get("acceptance", [])
        if not acceptance or any(
            not isinstance(item, dict) or item.get("passed") is not True
            for item in acceptance
        ):
            self.error(
                source,
                task_id,
                "acceptance",
                acceptance,
                "done 任务必须通过全部验收。",
                "完成验收并把每项 passed 设为 true。",
            )

        for artifact in task.get("artifacts", []):
            if not isinstance(artifact, dict) or artifact.get("required") is not True:
                continue
            relative = artifact.get("path")
            if isinstance(relative, str) and self.safe_relative_path(relative):
                if not (self.root / relative).exists():
                    self.error(
                        source,
                        task_id,
                        "artifacts",
                        relative,
                        "done 任务的必需产物不存在。",
                        "创建产物或把任务退回非 done 状态。",
                    )

        for dependency in task.get("dependencies", []):
            dependency_task = by_id.get(dependency)
            if dependency_task and dependency_task.get("status") != "done":
                self.error(
                    source,
                    task_id,
                    "dependencies",
                    dependency,
                    "done 任务仍依赖未完成任务。",
                    "先完成依赖或修正依赖关系。",
                )

    def validate_dependencies_shape(
        self, task: Dict[str, Any], source: str, object_id: str
    ) -> None:
        dependencies = task.get("dependencies")
        if not isinstance(dependencies, list) or any(
            not isinstance(item, str) or not item for item in dependencies
        ):
            self.error(
                source,
                object_id,
                "dependencies",
                dependencies,
                "dependencies 必须是字符串数组。",
                "无依赖时使用 []。",
            )

    def validate_artifacts(
        self, task: Dict[str, Any], source: str, object_id: str
    ) -> None:
        artifacts = task.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            self.error(
                source,
                object_id,
                "artifacts",
                artifacts,
                "任务至少需要一个产物。",
                "添加包含 path 和 required 的产物。",
            )
            return
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                self.error(
                    source,
                    object_id,
                    "artifacts",
                    artifact,
                    "产物必须是 object。",
                    "使用 path 和 required 字段。",
                )
                continue
            path = artifact.get("path")
            if not isinstance(path, str) or not path:
                self.error(
                    source,
                    object_id,
                    "artifacts.path",
                    path,
                    "产物路径必须非空。",
                    "使用仓库根目录相对路径。",
                )
            elif not self.safe_relative_path(path):
                self.error(
                    source,
                    object_id,
                    "artifacts.path",
                    path,
                    "产物路径必须位于仓库内。",
                    "删除绝对路径或 .. 路径段。",
                )
            if not isinstance(artifact.get("required"), bool):
                self.error(
                    source,
                    object_id,
                    "artifacts.required",
                    artifact.get("required"),
                    "required 必须是 boolean。",
                    "使用 true 或 false。",
                )

    def validate_acceptance(
        self, task: Dict[str, Any], source: str, object_id: str
    ) -> None:
        acceptance = task.get("acceptance")
        if not isinstance(acceptance, list) or not acceptance:
            self.error(
                source,
                object_id,
                "acceptance",
                acceptance,
                "任务至少需要一个二元验收项。",
                "添加 text 和 passed 字段。",
            )
            return
        for item in acceptance:
            if not isinstance(item, dict):
                self.error(
                    source,
                    object_id,
                    "acceptance",
                    item,
                    "验收项必须是 object。",
                    "使用 text 和 passed 字段。",
                )
                continue
            self.require_nonempty_string(
                item.get("text"), source, object_id, "acceptance.text"
            )
            if not isinstance(item.get("passed"), bool):
                self.error(
                    source,
                    object_id,
                    "acceptance.passed",
                    item.get("passed"),
                    "passed 必须是 boolean。",
                    "未验收使用 false，通过后使用 true。",
                )

    def validate_chapters(
        self, document: Optional[Dict[str, Any]], source: str
    ) -> tuple[Set[str], int]:
        if document is None:
            return set(), 0
        self.validate_document_timestamp(document, source)
        chapters = document.get("chapters")
        if not isinstance(chapters, list):
            self.error(
                source,
                "document",
                "chapters",
                chapters,
                "chapters 必须是数组。",
                "使用 JSON array 保存章节对象。",
            )
            return set(), 0

        ids: Set[str] = set()
        required = {
            "id",
            "number",
            "title",
            "question",
            "reader_outcome",
            "stages",
            "updated",
        }
        for index, chapter in enumerate(chapters):
            object_id = self.object_id(chapter, f"chapter[{index}]")
            if not isinstance(chapter, dict):
                self.error(
                    source,
                    object_id,
                    "record",
                    chapter,
                    "章节必须是 object。",
                    "改为章节对象。",
                )
                continue
            self.require_fields(chapter, required, source, object_id)
            chapter_id = chapter.get("id")
            if isinstance(chapter_id, str):
                if chapter_id in ids:
                    self.error(
                        source,
                        chapter_id,
                        "id",
                        chapter_id,
                        "章节 ID 重复。",
                        "使用唯一 CH-NN。",
                    )
                ids.add(chapter_id)
                match = CHAPTER_ID_RE.fullmatch(chapter_id)
                if not match:
                    self.error(
                        source,
                        chapter_id,
                        "id",
                        chapter_id,
                        "章节 ID 不符合 CH-NN。",
                        "例如使用 CH-03。",
                    )
                elif isinstance(chapter.get("number"), int):
                    encoded_number = int(match.group("number"))
                    if encoded_number != chapter["number"]:
                        self.error(
                            source,
                            chapter_id,
                            "number",
                            chapter["number"],
                            "ID 编号和 number 不一致。",
                            f"把 number 改为 {encoded_number}。",
                        )
            self.require_nonempty_string(
                chapter.get("title"), source, object_id, "title"
            )
            self.require_nonempty_string(
                chapter.get("question"), source, object_id, "question"
            )
            self.require_nonempty_string(
                chapter.get("reader_outcome"),
                source,
                object_id,
                "reader_outcome",
            )
            self.validate_timestamp(
                chapter.get("updated"), source, object_id, "updated"
            )
            self.validate_chapter_stages(
                chapter.get("stages"), source, object_id
            )

        return ids, len(chapters)

    def validate_chapter_stages(
        self, stages: Any, source: str, object_id: str
    ) -> None:
        if not isinstance(stages, list):
            self.error(
                source,
                object_id,
                "stages",
                stages,
                "stages 必须是数组。",
                "按六阶段顺序创建对象数组。",
            )
            return
        names = [
            stage.get("name") if isinstance(stage, dict) else None
            for stage in stages
        ]
        if names != CHAPTER_STAGE_NAMES:
            self.error(
                source,
                object_id,
                "stages",
                names,
                "章节阶段必须严格使用固定六阶段顺序。",
                f"使用 {CHAPTER_STAGE_NAMES}。",
            )
        for stage in stages:
            if not isinstance(stage, dict):
                continue
            self.require_allowed(
                stage.get("status"),
                CHAPTER_STAGE_STATUSES,
                source,
                object_id,
                f"stages.{stage.get('name')}.status",
            )

    def validate_experiments(
        self,
        document: Optional[Dict[str, Any]],
        chapter_ids: Set[str],
        source: str,
    ) -> int:
        if document is None:
            return 0
        self.validate_document_timestamp(document, source)
        experiments = document.get("experiments")
        if not isinstance(experiments, list):
            self.error(
                source,
                "document",
                "experiments",
                experiments,
                "experiments 必须是数组。",
                "使用 JSON array 保存实验对象。",
            )
            return 0

        ids: Set[str] = set()
        required = {
            "id",
            "name",
            "chapter",
            "triage",
            "effort",
            "inputs",
            "outputs",
            "metrics",
            "command",
            "acceptance",
            "status",
            "updated",
        }
        conditional = {
            "SHIP": {
                "repository_path",
                "readme_path",
                "sample_input",
                "sample_output",
                "test_path",
            },
            "KEEP-EXT": {
                "external_source",
                "pinned_version",
                "configuration",
                "reproduction_steps",
                "sample_result",
            },
            "ALREADY": {
                "reused_implementation",
                "cross_chapter_references",
            },
        }

        for index, experiment in enumerate(experiments):
            object_id = self.object_id(experiment, f"experiment[{index}]")
            if not isinstance(experiment, dict):
                self.error(
                    source,
                    object_id,
                    "record",
                    experiment,
                    "实验必须是 object。",
                    "改为实验对象。",
                )
                continue
            self.require_fields(experiment, required, source, object_id)
            experiment_id = experiment.get("id")
            if isinstance(experiment_id, str):
                if experiment_id in ids:
                    self.error(
                        source,
                        experiment_id,
                        "id",
                        experiment_id,
                        "实验 ID 重复。",
                        "使用唯一实验 ID。",
                    )
                ids.add(experiment_id)
            self.require_nonempty_string(
                experiment.get("name"), source, object_id, "name"
            )
            self.require_allowed(
                experiment.get("triage"),
                EXPERIMENT_TRIAGE,
                source,
                object_id,
                "triage",
            )
            self.require_allowed(
                experiment.get("effort"),
                EXPERIMENT_EFFORTS,
                source,
                object_id,
                "effort",
            )
            self.require_allowed(
                experiment.get("status"),
                EXPERIMENT_STATUSES,
                source,
                object_id,
                "status",
            )
            self.validate_timestamp(
                experiment.get("updated"), source, object_id, "updated"
            )
            chapter = experiment.get("chapter")
            if chapter not in chapter_ids:
                self.error(
                    source,
                    object_id,
                    "chapter",
                    chapter,
                    "实验引用未知章节。",
                    "使用 chapters.json 中的章节 ID。",
                )
            for field in ("inputs", "outputs", "metrics", "acceptance"):
                self.require_nonempty_list(
                    experiment.get(field), source, object_id, field
                )
            self.require_nonempty_string(
                experiment.get("command"), source, object_id, "command"
            )

            triage = experiment.get("triage")
            if triage in conditional:
                self.require_fields(
                    experiment, conditional[triage], source, object_id
                )
                for field in conditional[triage]:
                    value = experiment.get(field)
                    if field in {
                        "reproduction_steps",
                        "cross_chapter_references",
                    }:
                        self.require_nonempty_list(
                            value, source, object_id, field
                        )
                    else:
                        self.require_nonempty_string(
                            value, source, object_id, field
                        )

        return len(experiments)

    def require_fields(
        self,
        record: Dict[str, Any],
        required: Iterable[str],
        source: str,
        object_id: str,
    ) -> None:
        for field in sorted(required):
            if field not in record:
                self.error(
                    source,
                    object_id,
                    field,
                    None,
                    "缺少必需字段。",
                    f"添加 {field}。",
                )

    def require_allowed(
        self,
        value: Any,
        allowed: Set[str],
        source: str,
        object_id: str,
        field: str,
    ) -> None:
        if value not in allowed:
            self.error(
                source,
                object_id,
                field,
                value,
                "值不在允许集合中。",
                f"使用 {sorted(allowed)} 之一。",
            )

    def require_nonempty_string(
        self, value: Any, source: str, object_id: str, field: str
    ) -> None:
        if not isinstance(value, str) or not value.strip():
            self.error(
                source,
                object_id,
                field,
                value,
                "必须是非空字符串。",
                f"填写 {field}。",
            )

    def require_nonempty_list(
        self, value: Any, source: str, object_id: str, field: str
    ) -> None:
        if not isinstance(value, list) or not value:
            self.error(
                source,
                object_id,
                field,
                value,
                "必须是非空数组。",
                f"为 {field} 添加至少一个值。",
            )

    def validate_timestamp(
        self, value: Any, source: str, object_id: str, field: str
    ) -> None:
        if not isinstance(value, str):
            self.error(
                source,
                object_id,
                field,
                value,
                "时间戳必须是字符串。",
                "使用 2026-07-21T12:00:00Z 格式。",
            )
            return
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            parsed = None
        if parsed is None or parsed.tzinfo is None:
            self.error(
                source,
                object_id,
                field,
                value,
                "时间戳不是带时区 ISO 8601。",
                "使用 2026-07-21T12:00:00Z 或带 offset 的格式。",
            )

    def validate_date(
        self, value: Any, source: str, object_id: str, field: str
    ) -> None:
        if not isinstance(value, str):
            self.error(
                source,
                object_id,
                field,
                value,
                "日期必须是 YYYY-MM-DD 字符串。",
                "填写计划日期。",
            )
            return
        try:
            date.fromisoformat(value)
        except ValueError:
            self.error(
                source,
                object_id,
                field,
                value,
                "日期不是有效 YYYY-MM-DD。",
                "修正日历日期。",
            )

    @staticmethod
    def safe_relative_path(value: str) -> bool:
        path = Path(value)
        return not path.is_absolute() and ".." not in path.parts

    @staticmethod
    def object_id(record: Any, fallback: str) -> str:
        if isinstance(record, dict) and isinstance(record.get("id"), str):
            return record["id"]
        return fallback


def chapter_next_gap(chapter: Dict[str, Any]) -> Optional[str]:
    """Return the first unfinished stage, or None when the chapter is done."""
    for stage in chapter.get("stages", []):
        if isinstance(stage, dict) and stage.get("status") != "done":
            return stage.get("name")
    return None


def find_dependency_cycles(
    by_id: Dict[str, Dict[str, Any]]
) -> List[List[str]]:
    """Return stable, de-duplicated dependency cycles."""
    visiting: Set[str] = set()
    visited: Set[str] = set()
    stack: List[str] = []
    cycles: List[List[str]] = []
    signatures: Set[tuple[str, ...]] = set()

    def visit(task_id: str) -> None:
        if task_id in visited:
            return
        if task_id in visiting:
            start = stack.index(task_id)
            cycle = stack[start:] + [task_id]
            core = cycle[:-1]
            rotations = [
                tuple(core[index:] + core[:index])
                for index in range(len(core))
            ]
            signature = min(rotations)
            if signature not in signatures:
                signatures.add(signature)
                cycles.append(cycle)
            return

        visiting.add(task_id)
        stack.append(task_id)
        task = by_id.get(task_id, {})
        dependencies = task.get("dependencies", [])
        if isinstance(dependencies, list):
            for dependency in dependencies:
                if dependency in by_id:
                    visit(dependency)
        stack.pop()
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(by_id):
        visit(task_id)
    return cycles


def run_validation(root: Path) -> ValidationReport:
    return ProjectValidator(root).validate()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="校验 AI-DLC 写作系统的任务、章节和实验事实源。"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="仓库根目录，默认从脚本位置推导。",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_validation(args.root)

    for issue in report.issues:
        print(issue.render())

    print(
        "[INFO] validation summary: "
        f"tasks={report.task_count}, "
        f"chapters={report.chapter_count}, "
        f"experiments={report.experiment_count}, "
        f"errors={len(report.errors)}, "
        f"warnings={len(report.warnings)}"
    )
    if report.ok:
        print("[INFO] validation passed")
        return 0
    print("[ERROR] validation failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())

