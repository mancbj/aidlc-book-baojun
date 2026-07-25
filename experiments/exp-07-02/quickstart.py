#!/usr/bin/env python3
"""Build a deterministic multi-party review disagreement matrix (CH-07 Verify)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-07-02"
SCHEMA_VERSION = "1.0.0"
LIMITATION = (
    "分歧矩阵仅比较冻结的测试证据、独立模型评审与人工 Rubric 夹具；"
    "它不证明模型评审可以替代人工判断，也不构成 Runtime Verify。"
)

VERDICT_VALUES = ("approve", "reject", "defer")
DIMENSION_VERDICT = ("pass", "fail", "unknown", "na")
TEST_STATUS = ("passed", "failed", "partial")
SEVERITY = ("critical", "major", "minor")

TEST_STATUS_TO_VERDICT = {
    "passed": "approve",
    "failed": "reject",
    "partial": "defer",
}

DIMENSION_TO_RELEASE = {
    "pass": "approve",
    "fail": "reject",
    "unknown": "defer",
    "na": "defer",
}

ATTRIBUTION_CODES = (
    "ALIGNED_ALL",
    "TEST_HUMAN_DISAGREEMENT",
    "TEST_MODEL_DISAGREEMENT",
    "MODEL_MODEL_DISAGREEMENT",
    "HUMAN_OVERRIDES_AUTOMATED",
    "MODEL_ONLY_RISK",
    "HUMAN_DEFERS_RISK",
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成交付候选独立评审分歧矩阵。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="矩阵输出 JSON。")
    parser.add_argument("--sample", action="store_true", help="使用仓库内默认样例路径。")
    args = parser.parse_args(argv)
    if args.sample:
        root = Path(__file__).resolve().parent
        args.input = root / "samples" / "input.json"
        args.output = root / "output" / "sample.json"
    if not args.input or not args.output:
        parser.error("必须提供 --input/--output，或使用 --sample。")
    return args


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def source_digest(value: Any) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def require_object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError("E_EXPECTED_OBJECT", f"{path} 必须是对象。")
    return value


def require_list(value: Any, path: str, *, non_empty: bool = False) -> List[Any]:
    if not isinstance(value, list):
        raise InputError("E_EXPECTED_ARRAY", f"{path} 必须是数组。")
    if non_empty and not value:
        raise InputError("E_REQUIRED_COLLECTION", f"{path} 必须是非空数组。")
    return value


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_EXPECTED_STRING", f"{path} 必须是非空字符串。")
    return value.strip()


def require_field(parent: Dict[str, Any], field: str, path: str) -> Any:
    if field not in parent:
        raise InputError("E_REQUIRED_FIELD", f"{path}.{field} 是必填字段。")
    return parent[field]


def require_enum(value: Any, path: str, allowed: Sequence[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        allowed_text = ", ".join(allowed)
        raise InputError("E_INVALID_ENUM", f"{path} 必须是以下之一：{allowed_text}")
    return value


def parse_delivery_candidate(value: Any) -> Dict[str, str]:
    root = require_object(value, "$.delivery_candidate")
    return {
        "id": require_string(require_field(root, "id", "$.delivery_candidate"), "$.delivery_candidate.id"),
        "summary": require_string(
            require_field(root, "summary", "$.delivery_candidate"), "$.delivery_candidate.summary"
        ),
    }


def parse_test_evidence(value: Any) -> Dict[str, Any]:
    root = require_object(value, "$.test_evidence")
    status = require_enum(
        require_field(root, "status", "$.test_evidence"), "$.test_evidence.status", TEST_STATUS
    )
    linked = require_list(
        require_field(root, "linked_rubric_ids", "$.test_evidence"),
        "$.test_evidence.linked_rubric_ids",
    )
    linked_ids = []
    seen: Set[str] = set()
    for index, raw in enumerate(linked):
        rubric_id = require_string(raw, f"$.test_evidence.linked_rubric_ids[{index}]")
        if rubric_id in seen:
            raise InputError("E_DUPLICATE_ID", f"测试证据关联 Rubric 重复：{rubric_id}")
        seen.add(rubric_id)
        linked_ids.append(rubric_id)
    confirmed: List[str] = []
    if "confirmed_risk_ids" in root:
        for index, raw in enumerate(
            require_list(root["confirmed_risk_ids"], "$.test_evidence.confirmed_risk_ids")
        ):
            risk_id = require_string(raw, f"$.test_evidence.confirmed_risk_ids[{index}]")
            confirmed.append(risk_id)
    return {
        "summary": require_string(
            require_field(root, "summary", "$.test_evidence"), "$.test_evidence.summary"
        ),
        "status": status,
        "linked_rubric_ids": linked_ids,
        "confirmed_risk_ids": sorted(set(confirmed)),
    }


def parse_dimension_verdicts(
    value: Any, path: str, rubric_ids: Set[str]
) -> Dict[str, str]:
    entries = require_list(value, path)
    verdicts: Dict[str, str] = {}
    for index, raw in enumerate(entries):
        item_path = f"{path}[{index}]"
        entry = require_object(raw, item_path)
        rubric_id = require_string(
            require_field(entry, "rubric_id", item_path), f"{item_path}.rubric_id"
        )
        if rubric_id not in rubric_ids:
            raise InputError("E_UNKNOWN_RUBRIC_ID", f"{item_path}.rubric_id 未知：{rubric_id}")
        if rubric_id in verdicts:
            raise InputError("E_DUPLICATE_ID", f"模型维度评审重复：{rubric_id}")
        verdicts[rubric_id] = require_enum(
            require_field(entry, "verdict", item_path), f"{item_path}.verdict", ("pass", "fail")
        )
    return verdicts


def parse_risk_findings(value: Any, path: str) -> List[Dict[str, str]]:
    entries = require_list(value, path)
    findings: List[Dict[str, str]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(entries):
        item_path = f"{path}[{index}]"
        entry = require_object(raw, item_path)
        risk_id = require_string(require_field(entry, "id", item_path), f"{item_path}.id")
        if risk_id in seen:
            raise InputError("E_DUPLICATE_ID", f"风险 ID 重复：{risk_id}")
        seen.add(risk_id)
        findings.append(
            {
                "id": risk_id,
                "statement": require_string(
                    require_field(entry, "statement", item_path), f"{item_path}.statement"
                ),
                "severity": require_enum(
                    require_field(entry, "severity", item_path),
                    f"{item_path}.severity",
                    SEVERITY,
                ),
            }
        )
    findings.sort(key=lambda item: item["id"])
    return findings


def parse_model_reviews(value: Any, rubric_ids: Set[str]) -> List[Dict[str, Any]]:
    reviews = require_list(value, "$.independent_model_reviews", non_empty=True)
    parsed: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(reviews):
        path = f"$.independent_model_reviews[{index}]"
        entry = require_object(raw, path)
        reviewer_id = require_string(
            require_field(entry, "reviewer_id", path), f"{path}.reviewer_id"
        )
        if reviewer_id in seen:
            raise InputError("E_DUPLICATE_ID", f"评审者 ID 重复：{reviewer_id}")
        seen.add(reviewer_id)
        parsed.append(
            {
                "reviewer_id": reviewer_id,
                "fixture_label": require_string(
                    require_field(entry, "fixture_label", path), f"{path}.fixture_label"
                ),
                "overall_verdict": require_enum(
                    require_field(entry, "overall_verdict", path),
                    f"{path}.overall_verdict",
                    VERDICT_VALUES,
                ),
                "dimension_verdicts": parse_dimension_verdicts(
                    require_field(entry, "dimension_verdicts", path),
                    f"{path}.dimension_verdicts",
                    rubric_ids,
                ),
                "risk_findings": parse_risk_findings(
                    require_field(entry, "risk_findings", path), f"{path}.risk_findings"
                ),
            }
        )
    parsed.sort(key=lambda item: item["reviewer_id"])
    return parsed


def parse_human_rubric(value: Any) -> Dict[str, Any]:
    root = require_object(value, "$.human_rubric")
    judgments_raw = require_list(
        require_field(root, "judgments", "$.human_rubric"), "$.human_rubric.judgments", non_empty=True
    )
    judgments: List[Dict[str, str]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(judgments_raw):
        path = f"$.human_rubric.judgments[{index}]"
        entry = require_object(raw, path)
        rubric_id = require_string(require_field(entry, "rubric_id", path), f"{path}.rubric_id")
        if rubric_id in seen:
            raise InputError("E_DUPLICATE_ID", f"Rubric ID 重复：{rubric_id}")
        seen.add(rubric_id)
        judgments.append(
            {
                "rubric_id": rubric_id,
                "criterion": require_string(
                    require_field(entry, "criterion", path), f"{path}.criterion"
                ),
                "verdict": require_enum(
                    require_field(entry, "verdict", path), f"{path}.verdict", ("pass", "fail", "na")
                ),
            }
        )
    judgments.sort(key=lambda item: item["rubric_id"])
    acknowledged: List[str] = []
    if "acknowledged_risk_ids" in root:
        for index, raw in enumerate(
            require_list(root["acknowledged_risk_ids"], "$.human_rubric.acknowledged_risk_ids")
        ):
            acknowledged.append(
                require_string(raw, f"$.human_rubric.acknowledged_risk_ids[{index}]")
            )
    return {
        "judgments": judgments,
        "overall_verdict": require_enum(
            require_field(root, "overall_verdict", "$.human_rubric"),
            "$.human_rubric.overall_verdict",
            VERDICT_VALUES,
        ),
        "acknowledged_risk_ids": sorted(set(acknowledged)),
    }


def validate_input(data: Any) -> Dict[str, Any]:
    root = require_object(data, "$")
    experiment_id = require_string(require_field(root, "experiment_id", "$"), "$.experiment_id")
    if experiment_id != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}。")

    human_rubric = parse_human_rubric(require_field(root, "human_rubric", "$"))
    rubric_ids = {item["rubric_id"] for item in human_rubric["judgments"]}

    return {
        "experiment_id": experiment_id,
        "delivery_candidate": parse_delivery_candidate(
            require_field(root, "delivery_candidate", "$")
        ),
        "test_evidence": parse_test_evidence(require_field(root, "test_evidence", "$")),
        "independent_model_reviews": parse_model_reviews(
            require_field(root, "independent_model_reviews", "$"), rubric_ids
        ),
        "human_rubric": human_rubric,
    }


def test_signal_for_rubric(test_evidence: Dict[str, Any], rubric_id: str) -> str:
    if rubric_id not in test_evidence["linked_rubric_ids"]:
        return "unknown"
    status = test_evidence["status"]
    if status == "passed":
        return "pass"
    if status == "failed":
        return "fail"
    return "unknown"


def normalize_party_verdict(signal: str) -> str:
    return DIMENSION_TO_RELEASE.get(signal, "defer")


def attribute_row(
    test_signal: str,
    model_signals: Dict[str, str],
    human_signal: str,
    *,
    is_risk_row: bool,
) -> Tuple[bool, List[str]]:
    codes: List[str] = []
    model_values = list(model_signals.values())
    human_release = normalize_party_verdict(human_signal)
    test_release = normalize_party_verdict(test_signal)

    if is_risk_row:
        codes.append("MODEL_ONLY_RISK")
        if human_signal == "na":
            codes.append("HUMAN_DEFERS_RISK")
        aligned = len(codes) == 1 and human_signal != "na"
        if human_signal == "na":
            aligned = False
        return aligned, codes

    all_dimension = [test_signal] + model_values + [human_signal]
    if len(set(all_dimension)) == 1:
        return True, ["ALIGNED_ALL"]

    if test_signal != "unknown" and human_signal not in ("na",) and test_signal != human_signal:
        codes.append("TEST_HUMAN_DISAGREEMENT")
    if test_signal != "unknown" and model_values and any(test_signal != value for value in model_values):
        codes.append("TEST_MODEL_DISAGREEMENT")
    if len(set(model_values)) > 1:
        codes.append("MODEL_MODEL_DISAGREEMENT")

    automated = [test_signal] if test_signal != "unknown" else []
    automated.extend(model_values)
    automated = [value for value in automated if value in ("pass", "fail")]
    if automated and human_signal in ("pass", "fail"):
        if len(set(automated)) == 1 and automated[0] != human_signal:
            codes.append("HUMAN_OVERRIDES_AUTOMATED")

    if not codes:
        codes.append("MODEL_MODEL_DISAGREEMENT")
    return False, sorted(set(codes))


def collect_risk_rows(
    reviews: List[Dict[str, Any]], acknowledged: Set[str], confirmed: Set[str]
) -> List[Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for review in reviews:
        for finding in review["risk_findings"]:
            risk_id = finding["id"]
            if risk_id not in by_id:
                by_id[risk_id] = {
                    "dimension_id": risk_id,
                    "dimension_label": finding["statement"],
                    "severity": finding["severity"],
                    "flagged_by": [],
                    "is_new_risk": risk_id not in acknowledged and risk_id not in confirmed,
                }
            by_id[risk_id]["flagged_by"].append(review["reviewer_id"])
    rows = list(by_id.values())
    rows.sort(key=lambda item: item["dimension_id"])
    for row in rows:
        row["flagged_by"] = sorted(set(row["flagged_by"]))
    return rows


def model_agreement_rate(reviews: List[Dict[str, Any]], rubric_ids: List[str]) -> float:
    if len(reviews) < 2:
        return 100.0
    agree = 0
    total = 0
    for left in range(len(reviews)):
        for right in range(left + 1, len(reviews)):
            left_map = reviews[left]["dimension_verdicts"]
            right_map = reviews[right]["dimension_verdicts"]
            for rubric_id in rubric_ids:
                if rubric_id in left_map and rubric_id in right_map:
                    total += 1
                    if left_map[rubric_id] == right_map[rubric_id]:
                        agree += 1
    if total == 0:
        return 100.0
    return round(agree / total * 100, 2)


def human_override_rate(
    matrix_rows: List[Dict[str, Any]], rubric_row_count: int
) -> float:
    if rubric_row_count == 0:
        return 0.0
    overrides = sum(
        1
        for row in matrix_rows
        if row["dimension_kind"] == "rubric"
        and "HUMAN_OVERRIDES_AUTOMATED" in row["attribution_codes"]
    )
    return round(overrides / rubric_row_count * 100, 2)


def build_report(raw_data: Any) -> Dict[str, Any]:
    data = validate_input(raw_data)
    candidate = data["delivery_candidate"]
    test_evidence = data["test_evidence"]
    reviews = data["independent_model_reviews"]
    human = data["human_rubric"]
    human_by_rubric = {item["rubric_id"]: item for item in human["judgments"]}
    rubric_ids = sorted(human_by_rubric)

    matrix_rows: List[Dict[str, Any]] = []
    for rubric_id in rubric_ids:
        judgment = human_by_rubric[rubric_id]
        test_signal = test_signal_for_rubric(test_evidence, rubric_id)
        model_signals = {
            review["reviewer_id"]: review["dimension_verdicts"].get(rubric_id, "unknown")
            for review in reviews
        }
        human_signal = judgment["verdict"]
        aligned, codes = attribute_row(
            test_signal, model_signals, human_signal, is_risk_row=False
        )
        parties: Dict[str, Any] = {
            "test_evidence": {
                "source": "test_evidence",
                "signal": test_signal,
                "release_stance": normalize_party_verdict(test_signal),
            },
            "human_rubric": {
                "source": "human_rubric",
                "signal": human_signal,
                "release_stance": normalize_party_verdict(human_signal),
            },
        }
        for review in reviews:
            reviewer_id = review["reviewer_id"]
            signal = model_signals[reviewer_id]
            parties[reviewer_id] = {
                "source": "independent_model_review",
                "fixture_label": review["fixture_label"],
                "signal": signal,
                "release_stance": normalize_party_verdict(signal),
            }
        matrix_rows.append(
            {
                "dimension_id": rubric_id,
                "dimension_kind": "rubric",
                "dimension_label": judgment["criterion"],
                "parties": parties,
                "aligned": aligned,
                "attribution_codes": codes,
            }
        )

    risk_rows = collect_risk_rows(
        reviews,
        set(human["acknowledged_risk_ids"]),
        set(test_evidence["confirmed_risk_ids"]),
    )
    for risk in risk_rows:
        model_signals = {
            reviewer_id: ("fail" if reviewer_id in risk["flagged_by"] else "pass")
            for reviewer_id in [review["reviewer_id"] for review in reviews]
        }
        human_signal = "fail" if risk["dimension_id"] in human["acknowledged_risk_ids"] else "na"
        aligned, codes = attribute_row(
            "unknown", model_signals, human_signal, is_risk_row=True
        )
        parties = {
            "test_evidence": {
                "source": "test_evidence",
                "signal": "unknown",
                "release_stance": "defer",
            },
            "human_rubric": {
                "source": "human_rubric",
                "signal": human_signal,
                "release_stance": normalize_party_verdict(human_signal),
            },
        }
        for review in reviews:
            reviewer_id = review["reviewer_id"]
            signal = model_signals[reviewer_id]
            parties[reviewer_id] = {
                "source": "independent_model_review",
                "fixture_label": review["fixture_label"],
                "signal": signal,
                "release_stance": normalize_party_verdict(signal),
            }
        matrix_rows.append(
            {
                "dimension_id": risk["dimension_id"],
                "dimension_kind": "model_risk",
                "dimension_label": risk["dimension_label"],
                "severity": risk["severity"],
                "parties": parties,
                "aligned": aligned,
                "attribution_codes": codes,
                "is_new_risk": risk["is_new_risk"],
            }
        )

    new_risk_count = sum(1 for row in risk_rows if row["is_new_risk"])
    agreement_rate = model_agreement_rate(reviews, rubric_ids)
    override_rate = human_override_rate(matrix_rows, len(rubric_ids))

    multi_party_summary = {
        "test_evidence": {
            "status": test_evidence["status"],
            "release_stance": TEST_STATUS_TO_VERDICT[test_evidence["status"]],
        },
        "human_rubric": {
            "release_stance": human["overall_verdict"],
        },
        "independent_model_reviews": [
            {
                "reviewer_id": review["reviewer_id"],
                "fixture_label": review["fixture_label"],
                "release_stance": review["overall_verdict"],
            }
            for review in reviews
        ],
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "verification_framing": "CH-07 delivery candidate verification",
        "delivery_candidate_id": candidate["id"],
        "source_digest": source_digest(raw_data),
        "valid": True,
        "metrics": {
            "review_agreement_rate": agreement_rate,
            "new_risk_count": new_risk_count,
            "human_override_rate": override_rate,
        },
        "multi_party_summary": multi_party_summary,
        "disagreement_matrix": matrix_rows,
        "attribution_code_catalog": list(ATTRIBUTION_CODES),
        "limitation": LIMITATION,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        raw_data = json.loads(args.input.read_text(encoding="utf-8"))
        report = build_report(raw_data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(pretty_json(report), encoding="utf-8")
    except json.JSONDecodeError as exc:
        print(f"[ERROR E_INVALID_JSON] 输入不是有效 JSON：{exc.msg}", file=sys.stderr)
        return 1
    except InputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[ERROR E_IO] 文件操作失败：{exc}", file=sys.stderr)
        return 1

    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
