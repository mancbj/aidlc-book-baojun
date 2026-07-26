"""Regression, failure-path, packaging and mocked GitHub tests for Bolt 003."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LINKS = load_module("bolt003_check_internal_links", "check_internal_links.py")
GITHUB_CONFIG = load_module("bolt003_validate_github_config", "validate_github_config.py")
PR_METADATA = load_module("bolt003_validate_pr_metadata", "validate_pr_metadata.py")
PAGES = load_module("bolt003_prepare_pages", "prepare_pages.py")
RELEASE = load_module("bolt003_prepare_release", "prepare_release.py")
SYNC = load_module("bolt003_sync_github_project", "sync_github_project.py")


class CollaborationAndSecurityTests(unittest.TestCase):
    def test_repository_github_contract_passes(self):
        self.assertEqual(0, GITHUB_CONFIG.main())

    def test_unpinned_action_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workflows = root / ".github" / "workflows"
            workflows.parent.mkdir(parents=True)
            shutil.copytree(REPO_ROOT / ".github" / "workflows", workflows)
            path = workflows / "validate.yml"
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1",
                    "actions/checkout@v7",
                ),
                encoding="utf-8",
            )
            errors = []
            with mock.patch.object(GITHUB_CONFIG, "ROOT", root), mock.patch.object(
                GITHUB_CONFIG, "WORKFLOW_DIR", workflows
            ):
                GITHUB_CONFIG.validate_workflows(errors)
        self.assertTrue(any("40 位提交 SHA" in error for error in errors))

    def test_pull_request_metadata_accepts_completed_template(self):
        body = """## 关联任务
D15-T01
## 产物
README.md
## 测试与构建
- [x] python3 scripts/ci_check.py
## 验收
- [x] 验收通过
"""
        self.assertEqual([], PR_METADATA.validate_body(body))

    def test_pull_request_metadata_rejects_missing_evidence(self):
        issues = PR_METADATA.validate_body("## 验收\n- [ ] 待完成\n")
        combined = "\n".join(issues)
        self.assertIn("Task ID", combined)
        self.assertIn("## 产物", combined)
        self.assertIn("已确认项", combined)

    def test_workflows_never_use_privileged_pull_request_target(self):
        text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((REPO_ROOT / ".github/workflows").glob("*.yml"))
        )
        self.assertNotIn("pull_request_target:", text)
        validate = (REPO_ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        self.assertNotIn("contents: write", validate)
        self.assertNotIn("secrets.", validate)

        project = (REPO_ROOT / ".github/workflows/project-sync.yml").read_text(encoding="utf-8")
        dry_run_block, apply_block = project.split(
            "      - name: Apply the explicitly authorized one-way projection", maxsplit=1
        )
        self.assertNotIn("secrets.PROJECT_TOKEN", dry_run_block)
        self.assertIn("if: ${{ inputs.apply == true }}", apply_block)
        self.assertIn("secrets.PROJECT_TOKEN", apply_block)

    def test_label_names_and_colors_are_unique(self):
        errors = []
        GITHUB_CONFIG.validate_taxonomy(errors)
        self.assertEqual([], errors)


class LinkAndPagesTests(unittest.TestCase):
    def test_missing_link_and_fragment_are_reported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(
                "[missing](missing.md) [fragment](page.html#absent)\n", encoding="utf-8"
            )
            (root / "page.html").write_text("<main id=\"present\"></main>\n", encoding="utf-8")
            report = LINKS.check_links(root, ["README.md"])
        messages = "\n".join(issue["message"] for issue in report["issues"])
        self.assertIn("目标不存在", messages)
        self.assertIn("fragment 不存在", messages)

    def test_pages_tree_is_complete_and_link_clean(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "pages"
            manifest = PAGES.build_pages(
                REPO_ROOT,
                output,
                generated_at="2026-07-22T00:00:00Z",
                commit_sha="test-sha",
                workflow_run="test-run",
            )
            report = LINKS.check_links(
                output,
                ["README.md", "README.en.md", "book", "docs", "planning", "progress", "site", ".github/workflows/README.md"],
            )
            self.assertTrue((output / "tests/test_validate_project.py").is_file())
            self.assertTrue((output / "docs/CI-RUNBOOK.md").is_file())
            self.assertTrue((output / "experiments/sample/README.md").is_file())
            self.assertTrue((output / "LICENSE").is_file())
            self.assertTrue((output / "README.en.md").is_file())
            self.assertEqual([], report["issues"])
            index = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn("Source commit", index)
            self.assertIn("test-sha", index)
            self.assertIn("Source facts", index)
            self.assertEqual("test-sha", manifest["commit_sha"])
            self.assertEqual(len(manifest["files"]), manifest["file_count"])

    def test_pages_refuses_to_replace_unmarked_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "pages"
            output.mkdir()
            (output / "human.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "拒绝替换"):
                PAGES.build_pages(REPO_ROOT, output)
            self.assertEqual("preserve", (output / "human.txt").read_text(encoding="utf-8"))


class ReleaseTests(unittest.TestCase):
    def args(self, output: Path, version="v0.1-rc.1", pdf=None, book_html=None):
        return argparse.Namespace(
            version=version,
            root=REPO_ROOT,
            output=output,
            pdf=pdf,
            book_html=book_html,
            readiness=None,
            release_notes=None,
            generated_at="2026-07-22T00:00:00Z",
            commit_sha="release-test-sha",
        )

    def test_html_first_candidate_has_manifest_and_valid_zip(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "candidate"
            manifest = RELEASE.build_release(self.args(output))
            archive = output / manifest["html"]["file"]
            with zipfile.ZipFile(archive) as bundle:
                self.assertIsNone(bundle.testzip())
                names = bundle.namelist()
            self.assertTrue(any(name.endswith("/site/index.html") for name in names))
            self.assertEqual("included", manifest["html"]["status"])
            self.assertEqual("skipped", manifest["pdf"]["status"])
            self.assertEqual("release-test-sha", manifest["commit_sha"])

    def test_invalid_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError, "版本必须符合"):
                RELEASE.build_release(self.args(Path(temp) / "candidate", version="latest"))

    def test_renamed_text_file_is_rejected_as_fake_pdf(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fake = root / "book.pdf"
            fake.write_text("this is not a PDF but is long enough", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "header/EOF"):
                RELEASE.build_release(self.args(root / "candidate", pdf=fake))

    def test_structurally_valid_pdf_is_included(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pdf = root / "book.pdf"
            pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n")
            output = root / "candidate"
            manifest = RELEASE.build_release(self.args(output, pdf=pdf))
            self.assertEqual("included", manifest["pdf"]["status"])
            self.assertTrue((output / manifest["pdf"]["file"]).is_file())

    def test_fixed_inputs_produce_identical_html_archive(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = RELEASE.build_release(self.args(root / "first"))
            second = RELEASE.build_release(self.args(root / "second"))
            self.assertEqual(first["html"]["sha256"], second["html"]["sha256"])
            self.assertEqual(
                (root / "first" / first["html"]["file"]).read_bytes(),
                (root / "second" / second["html"]["file"]).read_bytes(),
            )

    def test_release_refuses_to_replace_unmarked_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "candidate"
            output.mkdir()
            (output / "human.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "拒绝替换"):
                RELEASE.build_release(self.args(output))
            self.assertTrue((output / "human.txt").is_file())


class FakeGitHubClient:
    def __init__(self, project, issues=None, failure=None):
        self.project = project
        self.issues = list(issues or [])
        self.failure = failure
        self.created = []
        self.added = []
        self.updated = []

    def list_issues(self, repository):
        if self.failure:
            raise self.failure
        return list(self.issues)

    def create_issue(self, repository, task):
        issue = {
            "number": 100 + len(self.created),
            "node_id": f"issue-node-{len(self.created)}",
            "body": task["body"],
        }
        self.created.append(issue)
        return issue

    def graphql(self, query, variables):
        if query == SYNC.PROJECT_QUERY:
            return {"user": {"projectV2": self.project}, "organization": None}
        if query == SYNC.ADD_ITEM_MUTATION:
            item_id = f"item-{len(self.added)}"
            self.added.append(variables)
            return {"addProjectV2ItemById": {"item": {"id": item_id}}}
        if query == SYNC.UPDATE_FIELD_MUTATION:
            self.updated.append(variables)
            return {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": variables["item"]}}}
        raise AssertionError("unexpected GraphQL operation")


class ProjectSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "progress").mkdir()
        (self.root / "planning").mkdir()
        shutil.copy2(REPO_ROOT / "planning/github-project.json", self.root / "planning/github-project.json")
        task = {
            "id": "D01-T01",
            "title": "测试任务",
            "type": "writing",
            "phase": "foundation",
            "status": "ready",
            "priority": "must",
            "day": 1,
            "chapter": "CH-01",
            "experiment": "",
            "artifacts": [{"path": "README.md", "required": True}],
            "acceptance": [{"text": "通过", "passed": False}],
        }
        documents = {
            "tasks.json": {"tasks": [task]},
            "chapters.json": {"chapters": []},
            "experiments.json": {"experiments": []},
        }
        for name, value in documents.items():
            (self.root / "progress" / name).write_text(
                json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8"
            )

    def tearDown(self):
        self.temp_dir.cleanup()

    def args(self, *, apply=False, force=False, configured=True):
        return argparse.Namespace(
            root=self.root,
            repository="owner/repo" if configured else None,
            project_owner="owner" if configured else None,
            project_number=1 if configured else None,
            project_owner_type="user",
            token_env="BOLT003_TEST_TOKEN",
            apply=apply,
            force_reproject=force,
            report=None,
        )

    def project(self, *, status=None, missing_field=None, has_next=False):
        config = json.loads((self.root / "planning/github-project.json").read_text(encoding="utf-8"))
        fields = []
        for index, definition in enumerate(config["fields"]):
            if definition["name"] == missing_field:
                continue
            field = {"id": f"field-{index}", "name": definition["name"]}
            if definition["type"] == "single-select":
                field["options"] = [
                    {"id": f"{index}-{option}", "name": option}
                    for option in definition["options"]
                ]
            fields.append(field)
        nodes = []
        if status is not None:
            nodes.append(
                {
                    "id": "existing-item",
                    "content": {
                        "id": "issue-id",
                        "number": 1,
                        "body": "<!-- aidlc-task:D01-T01 -->",
                    },
                    "fieldValues": {
                        "nodes": [{"name": status, "field": {"name": "Status"}}]
                    },
                }
            )
        return {
            "id": "project-id",
            "fields": {"nodes": fields},
            "items": {"pageInfo": {"hasNextPage": has_next}, "nodes": nodes},
        }

    def existing_issue(self):
        return {
            "number": 1,
            "node_id": "issue-node",
            "body": "<!-- aidlc-task:D01-T01 -->",
        }

    def test_missing_configuration_degrades_without_network(self):
        with mock.patch.object(SYNC, "GitHubClient", side_effect=AssertionError("network called")):
            report = SYNC.run(self.args(configured=False))
        self.assertEqual("degraded", report["status"])
        self.assertEqual(report["fact_hashes_before"], report["fact_hashes_after"])

    def test_dry_run_lists_stable_ids_without_network(self):
        with mock.patch.object(SYNC, "GitHubClient", side_effect=AssertionError("network called")):
            report = SYNC.run(self.args())
        self.assertEqual("dry-run", report["status"])
        self.assertEqual(["D01-T01"], report["desired_ids"])
        self.assertEqual(report["fact_hashes_before"], report["fact_hashes_after"])

    def test_apply_without_token_degrades_without_network(self):
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            SYNC, "GitHubClient", side_effect=AssertionError("network called")
        ):
            report = SYNC.run(self.args(apply=True))
        self.assertEqual("degraded", report["status"])
        self.assertIn("BOLT003_TEST_TOKEN", report["missing_configuration"])

    def test_duplicate_issue_markers_are_reported(self):
        issues = [
            {"number": 1, "body": "<!-- aidlc-task:D01-T01 -->"},
            {"number": 2, "body": "<!-- aidlc-task:D01-T01 -->"},
        ]
        index, divergences = SYNC.issue_index(issues)
        self.assertEqual(1, len(index))
        self.assertEqual(1, len(divergences))

    def test_remote_status_divergence_stops_before_mutation(self):
        fake = FakeGitHubClient(self.project(status="Done"), [self.existing_issue()])
        with mock.patch.dict(os.environ, {"BOLT003_TEST_TOKEN": "secret"}), mock.patch.object(
            SYNC, "GitHubClient", return_value=fake
        ):
            report = SYNC.run(self.args(apply=True))
        self.assertEqual("diverged", report["status"])
        self.assertIn("Status divergence", report["divergences"][0])
        self.assertEqual([], fake.updated)

    def test_force_reproject_applies_repository_status(self):
        fake = FakeGitHubClient(self.project(status="Done"), [self.existing_issue()])
        with mock.patch.dict(os.environ, {"BOLT003_TEST_TOKEN": "secret"}), mock.patch.object(
            SYNC, "GitHubClient", return_value=fake
        ):
            report = SYNC.run(self.args(apply=True, force=True))
        self.assertEqual("applied", report["status"])
        self.assertTrue(any(update["field"] == "field-0" for update in fake.updated))
        self.assertEqual(report["fact_hashes_before"], report["fact_hashes_after"])

    def test_missing_remote_field_is_a_divergence(self):
        fake = FakeGitHubClient(self.project(missing_field="Artifact"), [self.existing_issue()])
        with mock.patch.dict(os.environ, {"BOLT003_TEST_TOKEN": "secret"}), mock.patch.object(
            SYNC, "GitHubClient", return_value=fake
        ):
            report = SYNC.run(self.args(apply=True))
        self.assertEqual("diverged", report["status"])
        self.assertTrue(any("Artifact" in item for item in report["divergences"]))

    def test_existing_stable_identity_does_not_create_duplicate_issue_or_item(self):
        fake = FakeGitHubClient(self.project(status="Ready"), [self.existing_issue()])
        with mock.patch.dict(os.environ, {"BOLT003_TEST_TOKEN": "secret"}), mock.patch.object(
            SYNC, "GitHubClient", return_value=fake
        ):
            report = SYNC.run(self.args(apply=True))
        self.assertEqual("applied", report["status"])
        self.assertEqual([], fake.created)
        self.assertEqual([], fake.added)
        self.assertEqual(report["fact_hashes_before"], report["fact_hashes_after"])

    def test_new_task_creates_one_issue_and_one_item(self):
        fake = FakeGitHubClient(self.project())
        with mock.patch.dict(os.environ, {"BOLT003_TEST_TOKEN": "secret"}), mock.patch.object(
            SYNC, "GitHubClient", return_value=fake
        ):
            report = SYNC.run(self.args(apply=True))
        self.assertEqual("applied", report["status"])
        self.assertEqual(1, len(fake.created))
        self.assertEqual(1, len(fake.added))
        self.assertEqual(9, report["updated_fields"])
        self.assertEqual(report["fact_hashes_before"], report["fact_hashes_after"])

    def test_permission_error_returns_degraded_report_without_fact_write(self):
        fake = FakeGitHubClient(
            self.project(), failure=SYNC.GitHubError("GitHub HTTP 403: permission denied")
        )
        with mock.patch.dict(os.environ, {"BOLT003_TEST_TOKEN": "do-not-print"}), mock.patch.object(
            SYNC, "GitHubClient", return_value=fake
        ):
            report = SYNC.run(self.args(apply=True))
        self.assertEqual("degraded", report["status"])
        self.assertFalse(report["partial_remote_changes_possible"])
        self.assertNotIn("do-not-print", json.dumps(report))
        self.assertEqual(report["fact_hashes_before"], report["fact_hashes_after"])

    def test_mid_apply_error_reports_possible_partial_remote_changes(self):
        class PartialFailureClient(FakeGitHubClient):
            def graphql(self, query, variables):
                if query == SYNC.UPDATE_FIELD_MUTATION:
                    raise SYNC.GitHubError("GitHub HTTP 403: field permission denied")
                return super().graphql(query, variables)

        fake = PartialFailureClient(self.project())
        with mock.patch.dict(os.environ, {"BOLT003_TEST_TOKEN": "secret"}), mock.patch.object(
            SYNC, "GitHubClient", return_value=fake
        ):
            report = SYNC.run(self.args(apply=True))
        self.assertEqual("degraded", report["status"])
        self.assertTrue(report["partial_remote_changes_possible"])
        self.assertEqual(1, len(report["created_issues"]))
        self.assertEqual(1, len(report["added_items"]))
        self.assertEqual(report["fact_hashes_before"], report["fact_hashes_after"])

    def test_project_pagination_limit_stops_safely(self):
        fake = FakeGitHubClient(self.project(has_next=True))
        with self.assertRaisesRegex(SYNC.GitHubError, "超过 100"):
            SYNC.project_data(fake, "owner", 1, "user")


if __name__ == "__main__":
    unittest.main()
