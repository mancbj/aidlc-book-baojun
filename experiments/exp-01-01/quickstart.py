#!/usr/bin/env python3
"""Build a deterministic variance baseline from frozen generation artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-01-01"
SCHEMA_VERSION = "1.0.0"
MISSING_VALUE = "<missing>"
LIMITATION = (
    "本报告仅对仓库内冻结的多次生成快照做结构化差分与通过率方差统计；"
    "它不证明模型或流程已稳定到可依赖单次生成交付。"
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="同一 Intent 多次生成方差基线报告。")
    parser.add_argument("--input", type=Path, help="输入 JSON 路径。")
    parser.add_argument("--output", type=Path, help="输出 JSON 路径。")
    parser.add_argument("--sample", action="store_true", help="使用内置样例路径。")
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


def require_nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非空字符串")
    return value.strip()


def require_object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_COLLECTION", f"{path} 必须是非空数组")
    return value


def flatten_paths(value: Any, prefix: str = "") -> Dict[str, str]:
    """Map dot-path keys to canonical leaf values for structure comparison."""
    if isinstance(value, dict):
        paths: Dict[str, str] = {}
        for key in sorted(value):
            child_prefix = f"{prefix}.{key}" if prefix else key
            paths.update(flatten_paths(value[key], child_prefix))
        return paths
    path = prefix or "$"
    return {path: canonical_json(value)}


def population_variance(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sum((item - mean) ** 2 for item in values) / len(values)


def parse_intent(value: Any) -> Dict[str, str]:
    intent = require_object(value, "$.intent")
    return {
        "id": require_nonempty_string(intent.get("id"), "$.intent.id"),
        "statement": require_nonempty_string(intent.get("statement"), "$.intent.statement"),
    }


def parse_generation_context(value: Any) -> Dict[str, Any]:
    context = require_object(value, "$.generation_context")
    parsed: Dict[str, Any] = {
        "model": require_nonempty_string(context.get("model"), "$.generation_context.model"),
        "prompt_id": require_nonempty_string(
            context.get("prompt_id"), "$.generation_context.prompt_id"
        ),
    }
    temperature = context.get("temperature")
    if temperature is not None:
        if not isinstance(temperature, (int, float)):
            raise InputError("E_INVALID_FIELD", "$.generation_context.temperature 必须是数字")
        parsed["temperature"] = temperature
    return parsed


def parse_generations(value: Any) -> List[Dict[str, Any]]:
    raw_generations = require_list(value, "$.generations")
    if len(raw_generations) < 2:
        raise InputError("E_INSUFFICIENT_GENERATIONS", "$.generations 至少需要 2 次冻结生成")
    generations: List[Dict[str, Any]] = []
    seen = set()
    for index, raw in enumerate(raw_generations):
        path = f"$.generations[{index}]"
        generation = require_object(raw, path)
        generation_id = require_nonempty_string(generation.get("id"), f"{path}.id")
        if generation_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{generation_id}")
        seen.add(generation_id)
        structured_output = generation.get("structured_output")
        if structured_output is None:
            raise InputError("E_INVALID_FIELD", f"{path}.structured_output 必须存在")
        test_pass = generation.get("test_pass")
        if test_pass is not None and not isinstance(test_pass, bool):
            raise InputError("E_INVALID_FIELD", f"{path}.test_pass 必须是布尔值或省略")
        generations.append(
            {
                "id": generation_id,
                "structured_output": structured_output,
                "canonical_paths": flatten_paths(structured_output),
                "test_pass": test_pass,
            }
        )
    return generations


def compare_structures(
    generations: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], int, int]:
    all_paths = sorted({path for item in generations for path in item["canonical_paths"]})
    comparisons: List[Dict[str, Any]] = []
    differing = 0
    total = 0
    for left_index in range(len(generations)):
        for right_index in range(left_index + 1, len(generations)):
            left = generations[left_index]
            right = generations[right_index]
            for path in all_paths:
                value_left = left["canonical_paths"].get(path, MISSING_VALUE)
                value_right = right["canonical_paths"].get(path, MISSING_VALUE)
                matches = value_left == value_right
                total += 1
                if not matches:
                    differing += 1
                comparisons.append(
                    {
                        "generation_a": left["id"],
                        "generation_b": right["id"],
                        "path": path,
                        "value_a": value_left,
                        "value_b": value_right,
                        "matches": matches,
                    }
                )
    return comparisons, differing, total


def build_report(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")

    intent = parse_intent(data.get("intent"))
    generation_context = parse_generation_context(data.get("generation_context"))
    generations = parse_generations(data.get("generations"))

    comparisons, differing, total = compare_structures(generations)
    difference_rate = round(differing / total, 4) if total else 0.0

    observed = [1.0 if item["test_pass"] else 0.0 for item in generations if item["test_pass"] is not None]
    pass_rate = round(sum(observed) / len(observed), 4) if observed else None
    pass_variance = round(population_variance(observed), 4) if observed else None

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "intent": intent,
        "generation_context": generation_context,
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "generation_count": len(generations),
        "generations": [
            {
                "id": item["id"],
                "canonical_path_count": len(item["canonical_paths"]),
                "canonical_paths": sorted(item["canonical_paths"]),
                "test_pass": item["test_pass"],
            }
            for item in generations
        ],
        "structure_difference_report": {
            "pairwise_path_comparisons": comparisons,
            "differing_pairs": differing,
            "total_pairs": total,
            "difference_rate": difference_rate,
        },
        "metrics": {
            "structure_difference_rate": difference_rate,
            "test_pass_rate": pass_rate,
            "test_pass_rate_variance": pass_variance,
            "test_pass_observations": len(observed),
        },
        "variance_basis": {
            "structure_difference_rate": "无序生成对 × 并集路径；值不等或一侧缺失计为差异",
            "test_pass_rate_variance": "对含 test_pass 的冻结生成使用总体方差（除以 N，非样本 n-1）",
        },
        "limitation": LIMITATION,
    }


def load_input(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError("E_INPUT_NOT_FOUND", f"输入文件不存在：{path}") from exc
    except OSError as exc:
        raise InputError("E_INPUT_READ", f"无法读取输入文件：{path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError("E_INVALID_JSON", f"输入不是有效 JSON（第 {exc.lineno} 行）") from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(load_input(args.input))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(pretty_json(report), encoding="utf-8")
    except InputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError:
        print("[ERROR E_OUTPUT_WRITE] 无法写入输出文件", file=sys.stderr)
        return 1
    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
