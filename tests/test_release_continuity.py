"""Bolt 004 tests for feedback, release readiness and the next update cycle."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import audit_roadmap_evidence as evidence_audit  # noqa: E402
import check_internal_links as links  # noqa: E402
import check_release_readiness as readiness_gate  # noqa: E402
import generate_progress as generator  # noqa: E402
import open_next_cycle as next_cycle  # noqa: E402
import prepare_pages as pages  # noqa: E402
import prepare_release as release  # noqa: E402
import progress_core as core  # noqa: E402
import record_feedback  # noqa: E402
import render_release_notes as release_notes  # noqa: E402
import validate_feedback as continuity  # noqa: E402


TIMESTAMP = "2026-07-22T04:00:00Z"
FIXTURE_DIRS = (
    ".github",
    "book",
    "docs",
    "feedback",
    "planning",
    "progress",
    "releases",
    "site",
    "tests",
    "writer-chats",
)
FIXTURE_FILES = (
    "README.md",
    "EXPERIMENT_TRIAGE.md",
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quiet_call(function, *args):
    with redirect_stdout(StringIO()):
        return function(*args)


def copy_fixture(destination: Path) -> Path:
    root = destination / "fixture"
    root.mkdir()
    for relative in FIXTURE_DIRS:
        source = REPO_ROOT / relative
        if source.exists():
            shutil.copytree(source, root / relative)
    for relative in FIXTURE_FILES:
        shutil.copy2(REPO_ROOT / relative, root / relative)
    return root


def ensure_artifact(root: Path, relative: str) -> None:
    path = root / relative
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        path.write_text("{}\n", encoding="utf-8")
    elif path.suffix == ".svg":
        path.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180">'
            '<title>AI-DLC core loop</title><rect width="320" height="180" fill="#0f62fe"/></svg>\n',
            encoding="utf-8",
        )
    elif path.suffix == ".py":
        path.write_text("# Verified fixture artifact.\n", encoding="utf-8")
    elif path.suffix == ".sh":
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    else:
        path.write_text("# Verified fixture evidence\n\n人工验收已完成。\n", encoding="utf-8")


def make_ready(root: Path) -> None:
    tasks_path = root / "progress/tasks.json"
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    for task in tasks["tasks"]:
        if task["id"] == "D14-T03":
            task["status"] = "backlog"
            task["updated"] = TIMESTAMP
            for item in task["acceptance"]:
                item["passed"] = False
        else:
            task["status"] = "done"
            task["updated"] = TIMESTAMP
            for item in task["acceptance"]:
                item["passed"] = True
            for artifact in task["artifacts"]:
                if artifact.get("required"):
                    ensure_artifact(root, artifact["path"])
    tasks["updated"] = TIMESTAMP
    write_json(tasks_path, tasks)

    sample = root / "book/chapters/sample.md"
    sample.parent.mkdir(parents=True, exist_ok=True)
    body = "本节用一个可复现的小步骤连接问题、证据、判断和下一动作。"
    sample.write_text(
        "# 可读样章\n\n" + (body * 120) + "\n\n核心图来源：`book/images/fig0-1.svg`。\n",
        encoding="utf-8",
    )
    ensure_artifact(root, "book/images/fig0-1.svg")

    categories = json.loads(
        (root / "planning/releases/v0.1-policy.json").read_text(encoding="utf-8")
    )["required_review_categories"]
    review_lines = ["# Sample Chapter Review", ""]
    for category in categories:
        review_lines.extend(
            [
                f"## {category}",
                "",
                "- 结论：pass",
                "- 证据：人工核对内容、实验和图示一致。",
                "",
            ]
        )
    (root / "planning/reviews/sample-chapter.md").write_text(
        "\n".join(review_lines), encoding="utf-8"
    )

    experiments_path = root / "progress/experiments.json"
    experiments = json.loads(experiments_path.read_text(encoding="utf-8"))
    shipped = next(item for item in experiments["experiments"] if item["triage"] == "SHIP")
    shipped["status"] = "verified"
    shipped["updated"] = TIMESTAMP
    (root / shipped["repository_path"]).mkdir(parents=True, exist_ok=True)
    for field in ("readme_path", "sample_input", "sample_output", "test_path"):
        ensure_artifact(root, shipped[field])
    experiments["updated"] = TIMESTAMP
    write_json(experiments_path, experiments)

    feedback_path = root / "feedback/decisions.json"
    feedback = json.loads(feedback_path.read_text(encoding="utf-8"))
    feedback["updated"] = TIMESTAMP
    feedback["decisions"] = [
        {
            "id": "FB-001",
            "source": "Reader-A",
            "object": "book/chapters/sample.md",
            "summary": "补充读者首次运行的观察点。",
            "decision": "accepted",
            "reason": "",
            "linked_task": "C02-T04",
            "target_cycle": "",
            "revisit_when": "",
            "acceptance": ["读者入口包含首次运行观察点"],
            "created_at": TIMESTAMP,
            "decided_at": TIMESTAMP,
        }
    ]
    write_json(feedback_path, feedback)

    generator.generate(
        SimpleNamespace(
            root=root,
            actor="fixture",
            generated_at=TIMESTAMP,
            event_type=None,
            event_object=None,
            event_summary=None,
            dry_run=False,
        )
    )


def reset_v02_cycle_preview(root: Path) -> None:
    cycles_path = root / "progress/cycles.json"
    cycles = json.loads(cycles_path.read_text(encoding="utf-8"))
    cycles["active_cycle"] = None
    for cycle in cycles["cycles"]:
        if cycle.get("id") == "v0.2-draft":
            cycle["status"] = "preview"
            cycle["origin_release"] = None
            cycle["accepted_feedback"] = []
            cycle["carried_tasks"] = []
            cycle["carried_gaps"] = []
            for task in cycle["tasks"]:
                if task["id"] == "C02-T01":
                    task["status"] = "ready"
                elif task["id"] in {"C02-T02", "C02-T03"}:
                    task["status"] = "backlog"
        elif cycle.get("status") == "active":
            # Later patch maintenance cycles must not block v0.1→v0.2 fixture replay.
            cycle["status"] = "complete"
    write_json(cycles_path, cycles)


def initialize_git(root: Path) -> str:
    commands = (
        ("git", "init", "-q"),
        ("git", "config", "user.name", "Fixture"),
        ("git", "config", "user.email", "fixture@example.invalid"),
        ("git", "add", "."),
        ("git", "commit", "-q", "-m", "ready fixture"),
    )
    for command in commands:
        subprocess.run(command, cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=root,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def release_event(path: Path) -> None:
    write_json(
        path,
        {
            "action": "published",
            "release": {
                "id": 101,
                "tag_name": "v0.1",
                "draft": False,
                "published_at": TIMESTAMP,
                "html_url": "https://example.invalid/releases/v0.1",
            },
        },
    )


class FeedbackValidationTests(unittest.TestCase):
    def base_document(self) -> dict:
        return {
            "schema_version": "1.0.0",
            "updated": TIMESTAMP,
            "readers": [
                {
                    "id": "Reader-A",
                    "status": "not-invited",
                    "invited_at": None,
                    "responded_at": None,
                }
            ],
            "decisions": [],
        }

    def test_all_decision_types_validate_with_required_evidence(self):
        document = self.base_document()
        common = {
            "source": "Reader-A",
            "object": "sample",
            "summary": "最小证据摘要",
            "created_at": TIMESTAMP,
        }
        document["decisions"] = [
            {
                **common,
                "id": "FB-001",
                "decision": "accepted",
                "linked_task": "C02-T04",
                "acceptance": ["修订已通过审校"],
                "reason": "",
                "target_cycle": "",
                "revisit_when": "",
                "decided_at": TIMESTAMP,
            },
            {
                **common,
                "id": "FB-002",
                "decision": "rejected",
                "linked_task": "",
                "acceptance": [],
                "reason": "与已验证证据冲突",
                "target_cycle": "",
                "revisit_when": "",
                "decided_at": TIMESTAMP,
            },
            {
                **common,
                "id": "FB-003",
                "decision": "deferred",
                "linked_task": "",
                "acceptance": [],
                "reason": "等待更多样本",
                "target_cycle": "v0.2-draft",
                "revisit_when": "获得三个真实样本",
                "decided_at": TIMESTAMP,
            },
            {
                **common,
                "id": "FB-004",
                "decision": "pending",
                "linked_task": "",
                "acceptance": [],
                "reason": "",
                "target_cycle": "",
                "revisit_when": "",
                "decided_at": None,
            },
        ]
        self.assertEqual([], continuity.validate_feedback_document(document, "fixture"))

    def test_missing_link_pii_and_false_reader_response_are_rejected(self):
        document = self.base_document()
        document["email"] = "reader@example.invalid"
        document["readers"][0]["status"] = "responded"
        document["decisions"] = [
            {
                "id": "FB-001",
                "source": "Reader-A",
                "object": "sample",
                "summary": "建议",
                "decision": "accepted",
                "linked_task": "",
                "acceptance": [],
                "reason": "",
                "target_cycle": "",
                "revisit_when": "",
                "created_at": TIMESTAMP,
                "decided_at": TIMESTAMP,
            }
        ]
        issues = continuity.validate_feedback_document(document, "fixture")
        combined = "\n".join(issue.render() for issue in issues)
        self.assertIn("禁止的敏感", combined)
        self.assertIn("accepted 必须关联任务", combined)
        self.assertIn("responded 必须有", combined)

    def test_recorder_dry_run_is_clean_and_apply_is_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "feedback").mkdir()
            shutil.copy2(REPO_ROOT / "feedback/decisions.json", root / "feedback/decisions.json")
            before = digest(root / "feedback/decisions.json")
            arguments = [
                "--root",
                str(root),
                "--source",
                "Reader-A",
                "--object",
                "sample",
                "--summary",
                "导航建议",
                "--decision",
                "rejected",
                "--reason",
                "偏离当前读者目标",
                "--created-at",
                TIMESTAMP,
            ]
            self.assertEqual(0, quiet_call(record_feedback.main, arguments))
            self.assertEqual(before, digest(root / "feedback/decisions.json"))
            self.assertEqual(0, quiet_call(record_feedback.main, [*arguments, "--apply"]))
            value = json.loads((root / "feedback/decisions.json").read_text(encoding="utf-8"))
            self.assertEqual("FB-001", value["decisions"][0]["id"])
            self.assertEqual([], continuity.validate_feedback_document(value, "fixture"))

    def test_writer_review_and_reader_templates_cover_the_feedback_contract(self):
        writer = (REPO_ROOT / "writer-chats/template.md").read_text(encoding="utf-8")
        review = (REPO_ROOT / "planning/reviews/chapter-review-template.md").read_text(
            encoding="utf-8"
        )
        feedback = (REPO_ROOT / "planning/feedback-template.md").read_text(encoding="utf-8")
        reader = (REPO_ROOT / "docs/READER-GUIDE.md").read_text(encoding="utf-8")
        for field in ("Task ID", "采用方案", "放弃方案", "理由", "下一动作"):
            self.assertIn(field, writer)
        for category in (
            "技术正确性与过度承诺",
            "重复内容与概念边界",
            "结构连贯性与读者路径",
            "术语一致性",
            "正文与实验/图/练习对应",
        ):
            self.assertIn(category, review)
        for token in ("accepted", "rejected", "deferred", "record_feedback.py", "target_cycle"):
            self.assertIn(token, feedback)
        self.assertIn("Reader A", reader)
        self.assertIn("反馈", reader)


class ProgressContinuityTests(unittest.TestCase):
    def test_active_cycle_accepts_ready_must_with_done_dependencies(self):
        document = {
            "schema_version": "1.0.0",
            "updated": TIMESTAMP,
            "active_cycle": "v0.2-draft",
            "cycles": [
                {
                    "id": "v0.2-draft",
                    "status": "active",
                    "origin_release": {"status": "published"},
                    "monthly_target": "v0.2 readable release",
                    "cadence": {
                        "content_per_week": 1,
                        "experiment_per_week": 1,
                        "build_or_review_per_week": 1,
                        "release_per_month": 1,
                    },
                    "accepted_feedback": [],
                    "carried_tasks": [],
                    "carried_gaps": [],
                    "tasks": [
                        {
                            "id": "C02-T01",
                            "title": "完成下一节可读内容",
                            "kind": "content",
                            "priority": "must",
                            "status": "done",
                            "dependencies": [],
                            "acceptance": ["一节内容完成审校并关联证据"],
                        },
                        {
                            "id": "C02-T02",
                            "title": "运行并更新一次实验",
                            "kind": "experiment",
                            "priority": "must",
                            "status": "ready",
                            "dependencies": ["C02-T01"],
                            "acceptance": ["命令、输入、输出、指标和结论可复现"],
                        },
                        {
                            "id": "C02-T03",
                            "title": "完成一次构建与审校",
                            "kind": "build-review",
                            "priority": "must",
                            "status": "backlog",
                            "dependencies": ["C02-T02"],
                            "acceptance": ["CI、链接、构建和审校门禁通过"],
                        },
                    ],
                }
            ],
        }
        self.assertEqual([], continuity.validate_cycle_document(document, "fixture"))

    def test_feedback_and_cycle_changes_create_stable_events(self):
        previous = core.load_facts(REPO_ROOT)
        previous["cycles"]["active_cycle"] = None
        previous["cycles"]["cycles"][0]["status"] = "preview"
        previous["cycles"]["cycles"][0]["origin_release"] = None
        current = copy.deepcopy(previous)
        current["feedback"]["decisions"] = [
            {
                "id": "FB-001",
                "object": "sample",
                "decision": "accepted",
            }
        ]
        current["cycles"]["cycles"][0]["status"] = "active"
        events = core.detect_events(previous, current, "source", "tester", TIMESTAMP)
        self.assertEqual(
            {"feedback_decided", "cycle_opened"},
            {event["type"] for event in events},
        )
        self.assertEqual(
            [event["id"] for event in events],
            [event["id"] for event in core.detect_events(previous, current, "source", "tester", TIMESTAMP)],
        )

    def test_active_cycle_owns_next_action_while_should_is_carried(self):
        facts = core.load_facts(REPO_ROOT)
        for task in facts["tasks"]["tasks"]:
            task["status"] = "done" if task["id"] != "D14-T03" else "backlog"
        cycle = facts["cycles"]["cycles"][0]
        cycle["status"] = "active"
        cycle["origin_release"] = {"status": "published"}
        facts["cycles"]["active_cycle"] = cycle["id"]
        for task in cycle["tasks"]:
            if task["id"] == "C02-T01":
                task["status"] = "ready"
            elif task["id"] in {"C02-T02", "C02-T03"}:
                task["status"] = "backlog"
        projection = core.aggregate_progress(facts, "source", TIMESTAMP)
        self.assertEqual("C02-T01", projection["next_actions"][0]["id"])
        self.assertIn("下一周期", projection["release_message"])

    def test_dirty_fact_source_gets_a_distinct_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = copy_fixture(Path(temp))
            commit = initialize_git(root)
            facts = core.load_facts(root)
            self.assertEqual(commit, core.source_identity(root, facts))
            facts["cycles"]["updated"] = TIMESTAMP
            write_json(root / "progress/cycles.json", facts["cycles"])
            dirty = core.source_identity(root, facts)
            self.assertTrue(dirty.startswith(f"{commit[:12]}-working-tree-"))
            self.assertNotEqual(commit, dirty)


class ReadinessAndReleaseTests(unittest.TestCase):
    def test_real_repository_readiness_and_audit_do_not_change_tasks(self):
        before = digest(REPO_ROOT / "progress/tasks.json")
        report = readiness_gate.build_report(
            REPO_ROOT,
            REPO_ROOT / "planning/releases/v0.1-policy.json",
            TIMESTAMP,
        )
        audit = evidence_audit.build_report(REPO_ROOT, TIMESTAMP)
        self.assertIn(report["status"], {"ready", "blocked"})
        if report["status"] == "blocked":
            self.assertGreater(report["summary"]["blockers"], 0)
            self.assertTrue(
                {"MUST-NOT-DONE", "MUST-BLOCKED"}
                & {item["code"] for item in report["gaps"]}
            )
        else:
            self.assertEqual(0, report["summary"]["blockers"])
        source_task_count = len(json.loads((REPO_ROOT / "progress/tasks.json").read_text(encoding="utf-8"))["tasks"])
        self.assertEqual(source_task_count, len(audit["tasks"]))
        self.assertEqual(before, digest(REPO_ROOT / "progress/tasks.json"))

    def test_blocked_readiness_cannot_build_a_release_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            report = readiness_gate.build_report(
                REPO_ROOT,
                REPO_ROOT / "planning/releases/v0.1-policy.json",
                TIMESTAMP,
            )
            report["status"] = "blocked"
            report["summary"]["blockers"] = max(1, report["summary"].get("blockers", 0))
            report["gaps"].insert(
                0,
                {
                    "code": "MUST-NOT-DONE",
                    "priority": "must-missing",
                    "object": "D14-T02",
                    "evidence": "status=backlog",
                    "fix": "完成依赖、产物与全部二元验收后设为 done。",
                    "owner": "author",
                },
            )
            readiness_path = base / "readiness.json"
            write_json(readiness_path, report)
            args = argparse.Namespace(
                version="v0.1",
                root=REPO_ROOT,
                output=base / "candidate",
                pdf=None,
                book_html=None,
                readiness=readiness_path,
                release_notes=None,
                generated_at=TIMESTAMP,
                commit_sha=report["source_id"],
            )
            with self.assertRaisesRegex(RuntimeError, "不是 ready"):
                release.build_release(args)
            self.assertFalse((base / "candidate").exists())

    def test_complete_fixture_builds_ready_notes_and_same_source_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = copy_fixture(base)
            make_ready(root)
            source_sha = initialize_git(root)
            report = readiness_gate.build_report(
                root, root / "planning/releases/v0.1-policy.json", TIMESTAMP
            )
            self.assertEqual("ready", report["status"])
            self.assertEqual(source_sha, report["source_id"])
            self.assertEqual(0, report["summary"]["blockers"])
            self.assertEqual(1, report["summary"]["known_gaps"])
            readiness_path = base / "readiness.json"
            notes_path = base / "release-notes.md"
            write_json(readiness_path, report)
            notes_path.write_text(release_notes.render(root, report), encoding="utf-8")
            args = argparse.Namespace(
                version="v0.1",
                root=root,
                output=base / "candidate",
                pdf=None,
                book_html=None,
                readiness=readiness_path,
                release_notes=notes_path,
                generated_at=TIMESTAMP,
                commit_sha=source_sha,
            )
            manifest = release.build_release(args)
            self.assertEqual("ready", manifest["readiness"]["status"])
            self.assertEqual(report["source_id"], manifest["source_id"])
            self.assertEqual("included", manifest["html"]["status"])
            self.assertEqual("skipped", manifest["pdf"]["status"])

    def test_ready_report_from_another_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = copy_fixture(base)
            make_ready(root)
            report = readiness_gate.build_report(
                root, root / "planning/releases/v0.1-policy.json", TIMESTAMP
            )
            report["source_id"] = "different-source"
            readiness_path = base / "readiness.json"
            write_json(readiness_path, report)
            args = argparse.Namespace(
                version="v0.1",
                root=root,
                output=base / "candidate",
                pdf=None,
                book_html=None,
                readiness=readiness_path,
                release_notes=None,
                generated_at=TIMESTAMP,
                commit_sha="different-source",
            )
            with self.assertRaisesRegex(RuntimeError, "source"):
                release.build_release(args)


class PublishedCycleTests(unittest.TestCase):
    def test_draft_release_event_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "event.json"
            release_event(path)
            value = json.loads(path.read_text(encoding="utf-8"))
            value["release"]["draft"] = True
            write_json(path, value)
            with self.assertRaisesRegex(ValueError, "非 draft"):
                next_cycle.receipt_from_event(path, "source")

    def test_blocked_source_cannot_activate_cycle(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = copy_fixture(base)
            (root / "releases/v0.1/release.json").unlink(missing_ok=True)
            event = base / "event.json"
            release_event(event)
            cycles_before = digest(root / "progress/cycles.json")
            result = quiet_call(
                next_cycle.main,
                [
                    "--root",
                    str(root),
                    "--release-event",
                    str(event),
                    "--source-sha",
                    core.source_identity(root, core.load_facts(root)),
                    "--generated-at",
                    TIMESTAMP,
                    "--apply",
                ],
            )
            self.assertEqual(1, result)
            self.assertEqual(cycles_before, digest(root / "progress/cycles.json"))
            self.assertFalse((root / "releases/v0.1/release.json").exists())

    def test_published_release_activates_idempotently_and_preserves_v01(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = copy_fixture(base)
            make_ready(root)
            reset_v02_cycle_preview(root)
            source_sha = initialize_git(root)
            event = base / "event.json"
            release_event(event)
            tasks_before = digest(root / "progress/tasks.json")
            arguments = [
                "--root",
                str(root),
                "--release-event",
                str(event),
                "--source-sha",
                source_sha,
                "--generated-at",
                TIMESTAMP,
                "--apply",
            ]
            self.assertEqual(0, quiet_call(next_cycle.main, arguments))
            cycles_path = root / "progress/cycles.json"
            receipt_path = root / "releases/v0.1/release.json"
            first = (cycles_path.read_bytes(), receipt_path.read_bytes())
            self.assertEqual(0, quiet_call(next_cycle.main, arguments))
            self.assertEqual(first, (cycles_path.read_bytes(), receipt_path.read_bytes()))
            self.assertEqual(tasks_before, digest(root / "progress/tasks.json"))

            cycles = json.loads(cycles_path.read_text(encoding="utf-8"))
            active = cycles["cycles"][0]
            self.assertEqual("active", active["status"])
            self.assertEqual(["D14-T03"], [item["id"] for item in active["carried_tasks"]])
            self.assertEqual(["FB-001"], active["accepted_feedback"])
            self.assertIn("C02-T04", {item["id"] for item in active["tasks"]})

            result = generator.generate(
                SimpleNamespace(
                    root=root,
                    actor="fixture",
                    generated_at="2026-07-22T04:05:00Z",
                    event_type="release_published",
                    event_object="v0.1",
                    event_summary="v0.1 published",
                    dry_run=False,
                )
            )
            current = json.loads((root / "progress/generated/current.json").read_text())
            event_types = {
                json.loads(line)["type"]
                for line in (root / "progress/events/events.jsonl").read_text().splitlines()
                if line.strip()
            }
            self.assertEqual("C02-T01", current["next_actions"][0]["id"])
            self.assertEqual(2, result["new_event_count"])
            self.assertTrue({"cycle_opened", "release_published"}.issubset(event_types))
            self.assertIn("working-tree", current["source_id"])


class PagesAndWorkflowTests(unittest.TestCase):
    def test_link_audit_scans_output_under_dot_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / ".artifacts/pages"
            root.mkdir(parents=True)
            (root / "index.html").write_text(
                '<a href="missing.html">missing</a>\n', encoding="utf-8"
            )
            report = links.check_links(root, ["."])
            self.assertEqual(1, report["files"])
            self.assertEqual(1, len(report["issues"]))

    def test_pages_contains_github_drilldowns_and_nojekyll(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "pages"
            manifest = pages.build_pages(REPO_ROOT, output, TIMESTAMP, "sha", "run")
            self.assertTrue((output / ".nojekyll").is_file())
            self.assertTrue((output / ".github/workflows/release.yml").is_file())
            self.assertTrue((output / ".github/pull_request_template.md").is_file())
            report = links.check_links(output, ["site", ".github"])
            self.assertEqual([], report["issues"])
            self.assertEqual(len(manifest["files"]), manifest["file_count"])

    def test_release_permissions_are_isolated_from_pull_requests(self):
        workflows = REPO_ROOT / ".github/workflows"
        validate = (workflows / "validate.yml").read_text(encoding="utf-8")
        release_text = (workflows / "release.yml").read_text(encoding="utf-8")
        post = (workflows / "post-release.yml").read_text(encoding="utf-8")
        self.assertNotIn("pull_request_target:", validate + release_text + post)
        self.assertNotIn("secrets.", validate)
        self.assertIn("needs: [validate, readiness]", release_text)
        self.assertIn("types: [published]", post)
        self.assertIn("pull-requests: write", post)
        self.assertIn("next-cycle-record", post)


if __name__ == "__main__":
    unittest.main()
