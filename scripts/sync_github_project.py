#!/usr/bin/env python3
"""Project repository tasks into GitHub Issues/Projects without reverse writes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


MARKER_RE = re.compile(r"<!--\s*aidlc-task:(D\d{2}-T\d{2})\s*-->")
API_VERSION = "2026-03-10"


class GitHubError(RuntimeError):
    pass


def fact_hashes(root: Path) -> Dict[str, str]:
    result = {}
    for name in ("tasks.json", "chapters.json", "experiments.json"):
        path = root / "progress" / name
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise GitHubError(f"{path} 顶层必须是 object")
    return value


def desired_tasks(root: Path, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    tasks = load_json(root / "progress/tasks.json").get("tasks", [])
    status_mapping = config["status_mapping"]
    result = []
    for task in tasks:
        artifacts = [item["path"] for item in task.get("artifacts", [])]
        milestone = "v0.0.1" if int(task["day"]) <= 7 else "v0.1"
        fields = {
            "Status": status_mapping[task["status"]],
            "Priority": str(task["priority"]).title(),
            "Type": str(task["type"]).title(),
            "Day": int(task["day"]),
            "Chapter": task.get("chapter", ""),
            "Experiment": task.get("experiment", ""),
            "Milestone": milestone,
            "Artifact": ", ".join(artifacts),
            "Task ID": task["id"],
        }
        body = "\n".join(
            [
                f"<!-- aidlc-task:{task['id']} -->",
                f"# {task['id']} · {task['title']}",
                "",
                f"- Priority: `{task['priority']}`",
                f"- Type: `{task['type']}`",
                f"- Phase: `{task['phase']}`",
                f"- Day: `{task['day']}`",
                f"- Repository status: `{task['status']}`",
                "",
                "## Artifacts",
                *(f"- `{path}`" for path in artifacts),
                "",
                "## Acceptance",
                *(f"- [{'x' if item.get('passed') else ' '}] {item['text']}" for item in task.get("acceptance", [])),
                "",
                "> This Issue is a GitHub projection. Repository JSON remains authoritative.",
            ]
        )
        result.append(
            {
                "id": task["id"],
                "title": f"[{task['id']}] {task['title']}",
                "body": body,
                "fields": fields,
            }
        )
    return result


class GitHubClient:
    def __init__(self, token: str) -> None:
        self.token = token

    def request(self, method: str, url: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": API_VERSION,
                "User-Agent": "aidlc-book-project-sync",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            raise GitHubError(f"GitHub HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GitHubError(f"GitHub network error: {exc.reason}") from exc

    def graphql(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        value = self.request(
            "POST", "https://api.github.com/graphql", {"query": query, "variables": variables}
        )
        if value.get("errors"):
            raise GitHubError(f"GitHub GraphQL error: {value['errors']}")
        return value["data"]

    def list_issues(self, repository: str) -> List[Dict[str, Any]]:
        issues = []
        for page in range(1, 11):
            url = (
                f"https://api.github.com/repos/{repository}/issues?state=all&per_page=100&page={page}"
            )
            values = self.request("GET", url)
            page_values = [item for item in values if "pull_request" not in item]
            issues.extend(page_values)
            if len(values) < 100:
                return issues
        raise GitHubError("Issue 数超过 1000；为避免漏检重复项，同步停止。")

    def create_issue(self, repository: str, task: Dict[str, Any]) -> Dict[str, Any]:
        return self.request(
            "POST",
            f"https://api.github.com/repos/{repository}/issues",
            {"title": task["title"], "body": task["body"]},
        )


PROJECT_QUERY = """
query($owner:String!, $number:Int!, $organization:Boolean!) {
  organization(login:$owner) @include(if:$organization) {
    projectV2(number:$number) { ...ProjectData }
  }
  user(login:$owner) @skip(if:$organization) {
    projectV2(number:$number) { ...ProjectData }
  }
}
fragment ProjectData on ProjectV2 {
  id
  title
  fields(first:50) {
    nodes {
      ... on ProjectV2Field { id name dataType }
      ... on ProjectV2SingleSelectField { id name options { id name } }
    }
  }
  items(first:100) {
    pageInfo { hasNextPage }
    nodes {
      id
      content { ... on Issue { id number url body } }
      fieldValues(first:50) {
        nodes {
          ... on ProjectV2ItemFieldSingleSelectValue {
            name
            field { ... on ProjectV2SingleSelectField { name } }
          }
        }
      }
    }
  }
}
"""

ADD_ITEM_MUTATION = """
mutation($project:ID!, $content:ID!) {
  addProjectV2ItemById(input:{projectId:$project, contentId:$content}) { item { id } }
}
"""

UPDATE_FIELD_MUTATION = """
mutation($project:ID!, $item:ID!, $field:ID!, $value:ProjectV2FieldValue!) {
  updateProjectV2ItemFieldValue(input:{projectId:$project, itemId:$item, fieldId:$field, value:$value}) { projectV2Item { id } }
}
"""


def issue_index(issues: Iterable[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    index: Dict[str, Dict[str, Any]] = {}
    divergences = []
    for issue in issues:
        match = MARKER_RE.search(issue.get("body") or "")
        if not match:
            continue
        task_id = match.group(1)
        if task_id in index:
            divergences.append(
                f"duplicate Issue marker for {task_id}: #{index[task_id]['number']} and #{issue['number']}"
            )
        else:
            index[task_id] = issue
    return index, divergences


def project_data(client: GitHubClient, owner: str, number: int, owner_type: str) -> Dict[str, Any]:
    data = client.graphql(
        PROJECT_QUERY,
        {"owner": owner, "number": number, "organization": owner_type == "organization"},
    )
    container = data.get("organization") if owner_type == "organization" else data.get("user")
    if not container or not container.get("projectV2"):
        raise GitHubError("找不到目标 Project V2；检查 owner、number 和 Token 权限。")
    project = container["projectV2"]
    if project["items"]["pageInfo"]["hasNextPage"]:
        raise GitHubError("Project items 超过 100；为避免重复创建，同步停止并要求分页实现。")
    return project


def field_index(project: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {field["name"]: field for field in project["fields"]["nodes"] if field and field.get("name")}


def project_item_index(project: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    result = {}
    for item in project["items"]["nodes"]:
        content = item.get("content") or {}
        match = MARKER_RE.search(content.get("body") or "")
        if not match:
            continue
        values = {}
        for value in item.get("fieldValues", {}).get("nodes", []):
            if value and value.get("field"):
                values[value["field"]["name"]] = value.get("name")
        result[match.group(1)] = {"id": item["id"], "content": content, "values": values}
    return result


def value_for_field(field: Dict[str, Any], desired: Any) -> Dict[str, Any]:
    options = field.get("options")
    if options is not None:
        option = next((item for item in options if item["name"] == str(desired)), None)
        if not option:
            raise GitHubError(f"字段 {field['name']} 缺少选项 {desired}")
        return {"singleSelectOptionId": option["id"]}
    if isinstance(desired, int):
        return {"number": desired}
    return {"text": str(desired)[:1024]}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把仓库任务单向投影到 GitHub Projects。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--project-owner", default=os.environ.get("PROJECT_OWNER"))
    parser.add_argument("--project-number", type=int, default=int(os.environ["PROJECT_NUMBER"]) if os.environ.get("PROJECT_NUMBER") else None)
    parser.add_argument("--project-owner-type", choices=("user", "organization"), default=os.environ.get("PROJECT_OWNER_TYPE", "user"))
    parser.add_argument("--token-env", default="PROJECT_TOKEN")
    parser.add_argument("--apply", action="store_true", help="显式允许远程创建 Issue/Project item 和字段投影。")
    parser.add_argument("--force-reproject", action="store_true", help="显式允许 repository 状态覆盖已报告的 Project 状态分叉。")
    parser.add_argument("--report", type=Path)
    return parser.parse_args(argv)


def write_report(root: Path, path: Optional[Path], report: Dict[str, Any]) -> None:
    if not path:
        return
    target = path if path.is_absolute() else root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def degraded_remote_report(
    root: Path, report: Dict[str, Any], error: GitHubError
) -> Dict[str, Any]:
    """Preserve an actionable report when GitHub is unavailable or unauthorized."""
    report["status"] = "degraded"
    report["remote_error"] = str(error)
    report["partial_remote_changes_possible"] = bool(
        report["created_issues"] or report["added_items"] or report["updated_fields"]
    )
    report["next_action"] = (
        "检查 repository、Project owner/number、字段与 Token 最小权限后重跑 dry-run；"
        "若报告提示可能已有部分远端变更，先按稳定 Task ID 审计后再 apply。"
    )
    report["fact_hashes_after"] = fact_hashes(root)
    if report["fact_hashes_before"] != report["fact_hashes_after"]:
        raise GitHubError("Project sync unexpectedly modified repository fact sources")
    return report


def run(args: argparse.Namespace) -> Dict[str, Any]:
    root = args.root.resolve()
    before = fact_hashes(root)
    config = load_json(root / "planning/github-project.json")
    desired = desired_tasks(root, config)
    token = os.environ.get(args.token_env, "")
    missing = []
    if not args.repository:
        missing.append("repository")
    if not args.project_owner:
        missing.append("project_owner")
    if not args.project_number:
        missing.append("project_number")
    if args.apply and not token:
        missing.append(args.token_env)

    report: Dict[str, Any] = {
        "schema_version": "1.0.0",
        "mode": "apply" if args.apply else "dry-run",
        "status": "planned",
        "authority": config["authority"],
        "desired_task_count": len(desired),
        "repository": args.repository,
        "project_owner": args.project_owner,
        "project_number": args.project_number,
        "token_present": bool(token),
        "missing_configuration": missing,
        "created_issues": [],
        "added_items": [],
        "updated_fields": 0,
        "divergences": [],
        "fact_hashes_before": before,
    }
    if missing:
        report["status"] = "degraded"
        report["next_action"] = (
            "配置 repository、Project owner/number；仅在 --apply 时通过环境变量提供 PROJECT_TOKEN。"
        )
        report["fact_hashes_after"] = fact_hashes(root)
        return report
    if not args.apply:
        report["status"] = "dry-run"
        report["desired_ids"] = [task["id"] for task in desired]
        report["next_action"] = "审阅配置后显式使用 --apply；dry-run 未发起网络请求。"
        report["fact_hashes_after"] = fact_hashes(root)
        return report

    try:
        client = GitHubClient(token)
        issues = client.list_issues(args.repository)
        issues_by_task, divergences = issue_index(issues)
        project = project_data(client, args.project_owner, args.project_number, args.project_owner_type)
        fields = field_index(project)
        required_fields = {field["name"] for field in config["fields"]}
        missing_fields = sorted(required_fields - set(fields))
        if missing_fields:
            divergences.append(f"Project missing fields: {', '.join(missing_fields)}")
        items = project_item_index(project)
        desired_by_id = {task["id"]: task for task in desired}
        for task_id, item in items.items():
            if task_id in desired_by_id:
                remote_status = item["values"].get("Status")
                expected = desired_by_id[task_id]["fields"]["Status"]
                if remote_status and remote_status != expected:
                    divergences.append(
                        f"{task_id} Status divergence: repository={expected}, project={remote_status}"
                    )
        report["divergences"] = divergences
        if divergences and not args.force_reproject:
            report["status"] = "diverged"
            report["next_action"] = "先审阅差异；若仓库事实确定权威，再显式增加 --force-reproject。"
            report["fact_hashes_after"] = fact_hashes(root)
            return report

        project_id = project["id"]
        for task in desired:
            issue = issues_by_task.get(task["id"])
            if not issue:
                issue = client.create_issue(args.repository, task)
                issues_by_task[task["id"]] = issue
                report["created_issues"].append(issue["number"])
            item = items.get(task["id"])
            if not item:
                added = client.graphql(
                    ADD_ITEM_MUTATION, {"project": project_id, "content": issue["node_id"]}
                )
                item_id = added["addProjectV2ItemById"]["item"]["id"]
                item = {"id": item_id, "values": {}}
                report["added_items"].append(task["id"])
            for name, desired_value in task["fields"].items():
                if name not in fields:
                    continue
                if name == "Status" and item.get("values", {}).get(name) == desired_value:
                    continue
                client.graphql(
                    UPDATE_FIELD_MUTATION,
                    {
                        "project": project_id,
                        "item": item["id"],
                        "field": fields[name]["id"],
                        "value": value_for_field(fields[name], desired_value),
                    },
                )
                report["updated_fields"] += 1
    except GitHubError as exc:
        return degraded_remote_report(root, report, exc)
    report["status"] = "applied"
    report["fact_hashes_after"] = fact_hashes(root)
    if report["fact_hashes_before"] != report["fact_hashes_after"]:
        raise GitHubError("Project sync unexpectedly modified repository fact sources")
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    try:
        report = run(args)
        write_report(root, args.report, report)
    except (OSError, ValueError, json.JSONDecodeError, GitHubError) as exc:
        print(f"[ERROR] Project sync failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if report["status"] == "diverged" else 0


if __name__ == "__main__":
    raise SystemExit(main())
