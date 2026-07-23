#!/usr/bin/env python3
"""Audit editable SVG diagrams against the publication-grade skill contract."""

from __future__ import annotations

import argparse
import colorsys
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")
CSS_VAR_RE = re.compile(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})")
CLASS_RULE_RE = re.compile(r"\.([A-Za-z_][\w-]*)\s*\{([^}]*)\}", re.S)
DECL_RE = re.compile(r"([\w-]+)\s*:\s*([^;]+)")
TRANSLATE_RE = re.compile(
    r"translate\(\s*(-?\d+(?:\.\d+)?)"
    r"(?:[ ,]+(-?\d+(?:\.\d+)?))?\s*\)"
)
PATH_TOKEN_RE = re.compile(r"[MLHVZmlhvz]|-?\d+(?:\.\d+)?")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def classes(node: ET.Element) -> set[str]:
    return set(node.attrib.get("class", "").split())


def declarations(raw: str) -> dict[str, str]:
    return {key.strip(): value.strip() for key, value in DECL_RE.findall(raw)}


def number(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    match = re.match(r"\s*(-?\d+(?:\.\d+)?)", value)
    return float(match.group(1)) if match else default


def is_grid_value(value: float, unit: float = 4.0, tolerance: float = 0.01) -> bool:
    return abs(value / unit - round(value / unit)) <= tolerance


def saturation(hex_color: str) -> float:
    raw = hex_color.lstrip("#")
    red, green, blue = (int(raw[index : index + 2], 16) / 255 for index in (0, 2, 4))
    return colorsys.rgb_to_hsv(red, green, blue)[1]


def parse_translate(node: ET.Element) -> tuple[float, float]:
    match = TRANSLATE_RE.fullmatch(node.attrib.get("transform", "").strip())
    if not match:
        return (0.0, 0.0)
    return (float(match.group(1)), float(match.group(2) or 0.0))


def parse_path_points(path_data: str) -> tuple[list[list[tuple[float, float]]], bool]:
    """Parse absolute M/L/H/V paths into subpaths; return (subpaths, unsupported)."""
    tokens = PATH_TOKEN_RE.findall(path_data)
    subpaths: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    x = y = 0.0
    command = ""
    index = 0
    unsupported = bool(re.search(r"[CQASTcqast]", path_data))

    while index < len(tokens):
        token = tokens[index]
        if token.isalpha():
            command = token
            index += 1
            if command in "Zz":
                if current and current[-1] != current[0]:
                    current.append(current[0])
                continue
            if command.islower():
                unsupported = True
                break
            continue
        if command in ("M", "L") and index + 1 < len(tokens):
            x, y = float(tokens[index]), float(tokens[index + 1])
            if command == "M":
                if current:
                    subpaths.append(current)
                current = [(x, y)]
                command = "L"
            else:
                current.append((x, y))
            index += 2
        elif command == "H":
            x = float(token)
            current.append((x, y))
            index += 1
        elif command == "V":
            y = float(token)
            current.append((x, y))
            index += 1
        else:
            unsupported = True
            break
    if current:
        subpaths.append(current)
    return subpaths, unsupported


@dataclass
class Audit:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, object] = field(default_factory=dict)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


class SvgAuditor:
    def __init__(self, path: Path, required_text: list[str]):
        self.path = path
        self.required_text = required_text
        self.audit = Audit()
        self.raw = path.read_text(encoding="utf-8")
        self.root = ET.fromstring(self.raw)
        self.nodes = list(self.root.iter())
        self.parent = {child: parent for parent in self.nodes for child in parent}
        self.style_text = "\n".join(
            node.text or "" for node in self.nodes if local_name(node.tag) == "style"
        )
        self.variables = {name: value.upper() for name, value in CSS_VAR_RE.findall(self.style_text)}
        self.class_rules = {
            name: declarations(body) for name, body in CLASS_RULE_RE.findall(self.style_text)
        }
        self.view_x = self.view_y = self.width = self.height = 0.0

    def global_offset(self, node: ET.Element) -> tuple[float, float]:
        x = y = 0.0
        cursor: ET.Element | None = node
        while cursor is not None:
            dx, dy = parse_translate(cursor)
            x += dx
            y += dy
            cursor = self.parent.get(cursor)
        return x, y

    def in_defs(self, node: ET.Element) -> bool:
        cursor: ET.Element | None = node
        while cursor is not None:
            if local_name(cursor.tag) == "defs":
                return True
            cursor = self.parent.get(cursor)
        return False

    def property(self, node: ET.Element, key: str) -> str | None:
        if key in node.attrib:
            return node.attrib[key]
        inline = declarations(node.attrib.get("style", ""))
        if key in inline:
            return inline[key]
        for class_name in classes(node):
            value = self.class_rules.get(class_name, {}).get(key)
            if value is not None:
                return value
        return None

    def resolve_color(self, value: str | None) -> str | None:
        if not value:
            return None
        value = value.strip()
        variable = re.fullmatch(r"var\((--[\w-]+)\)", value)
        if variable:
            return self.variables.get(variable.group(1))
        if HEX_RE.fullmatch(value):
            return value.upper()
        return None

    def rect_box(self, node: ET.Element) -> tuple[float, float, float, float]:
        dx, dy = self.global_offset(node)
        return (
            dx + number(node.attrib.get("x")),
            dy + number(node.attrib.get("y")),
            number(node.attrib.get("width")),
            number(node.attrib.get("height")),
        )

    def run(self) -> Audit:
        self.check_root_and_accessibility()
        self.check_engineering_contract()
        self.check_palette()
        self.check_cards_and_typography()
        self.check_grid_and_balance()
        self.check_paths_and_semantics()
        return self.audit

    def check_root_and_accessibility(self) -> None:
        if local_name(self.root.tag) != "svg":
            self.audit.error("root element is not <svg>")
            return
        values = self.root.attrib.get("viewBox", "").split()
        if len(values) != 4:
            self.audit.error("missing or invalid viewBox")
            return
        try:
            self.view_x, self.view_y, self.width, self.height = map(float, values)
        except ValueError:
            self.audit.error("viewBox must contain four numeric values")
            return
        if self.width <= 0 or self.height <= 0:
            self.audit.error("viewBox width and height must be positive")
        if self.root.attrib.get("role") != "img":
            self.audit.error('root must use role="img"')
        names = {local_name(node.tag) for node in self.nodes}
        if "title" not in names or "desc" not in names:
            self.audit.error("SVG must include both <title> and <desc>")
        all_text = " ".join("".join(node.itertext()) for node in self.nodes)
        for required in self.required_text:
            if required not in all_text:
                self.audit.error(f"protected text missing: {required!r}")
        if "Engineering with Execution" in all_text:
            self.audit.error("protected term was normalized to Execution; preserve Exsecutio")

    def check_engineering_contract(self) -> None:
        forbidden = {
            local_name(node.tag)
            for node in self.nodes
            if local_name(node.tag) in {"foreignObject", "image", "script", "animate", "animateTransform"}
        }
        if forbidden:
            self.audit.error(f"forbidden SVG elements present: {', '.join(sorted(forbidden))}")
        names = [local_name(node.tag) for node in self.nodes]
        for required in ("defs", "style", "marker"):
            if required not in names:
                self.audit.error(f"missing required <{required}> definition")
        if not any(local_name(node.tag) == "text" for node in self.nodes):
            self.audit.error("no editable <text> labels found")
        inline_styles = [node for node in self.nodes if node.attrib.get("style")]
        if inline_styles:
            self.audit.warn(f"found {len(inline_styles)} inline style attributes; reuse classes")
        for class_name, body in CLASS_RULE_RE.findall(self.style_text):
            for property_name in ("fill", "stroke"):
                values = [
                    value.strip()
                    for key, value in DECL_RE.findall(body)
                    if key.strip() == property_name
                ]
                if any("var(" in value for value in values):
                    first_variable = next(index for index, value in enumerate(values) if "var(" in value)
                    if not any(HEX_RE.fullmatch(value) for value in values[:first_variable]):
                        self.audit.error(
                            f"class .{class_name} uses {property_name}:var(...) without a literal PNG fallback"
                        )
        ids = [node.attrib["id"] for node in self.nodes if "id" in node.attrib]
        if len(ids) != len(set(ids)):
            self.audit.error("duplicate id values found")

        stroked = []
        for node in self.nodes:
            stroke = self.property(node, "stroke")
            if stroke and stroke.strip().lower() not in {"none", "transparent"}:
                stroked.append(node)
                vector_effect = self.property(node, "vector-effect")
                if vector_effect != "non-scaling-stroke":
                    label = node.attrib.get("id") or node.attrib.get("class") or local_name(node.tag)
                    self.audit.error(f"stroked element lacks non-scaling-stroke: {label}")
        self.audit.metrics["stroked_elements"] = len(stroked)

    def check_palette(self) -> None:
        colors = sorted({color.upper() for color in HEX_RE.findall(self.raw)})
        self.audit.metrics["colors"] = colors
        if len(colors) > 8:
            self.audit.warn(f"palette contains {len(colors)} colors; target is at most 8")
        saturated = [color for color in colors if saturation(color) > 0.72]
        if len(saturated) > 3:
            self.audit.warn(f"more than three high-saturation colors: {', '.join(saturated)}")

        canvas_area = self.width * self.height
        for node in self.nodes:
            if local_name(node.tag) != "rect" or canvas_area <= 0:
                continue
            _, _, width, height = self.rect_box(node)
            fill = self.resolve_color(self.property(node, "fill"))
            if fill and saturation(fill) > 0.72 and width * height > canvas_area * 0.05:
                self.audit.error(f"large saturated rectangle detected: {fill} at {width:g}×{height:g}")

    def check_cards_and_typography(self) -> None:
        card_groups = [node for node in self.nodes if node.attrib.get("data-card")]
        card_area = 0.0
        for group in card_groups:
            descendants = list(group.iter())
            cards = [node for node in descendants if local_name(node.tag) == "rect" and "card" in classes(node)]
            accents = [node for node in descendants if local_name(node.tag) == "rect" and "accent" in classes(node)]
            texts = [node for node in descendants if local_name(node.tag) == "text"]
            label = group.attrib.get("data-card", "unnamed")
            if len(cards) != 1:
                self.audit.error(f"card group {label!r} must contain exactly one rect.card")
                continue
            if len(accents) != 1:
                self.audit.error(f"card group {label!r} must contain exactly one left rect.accent")
                continue
            if len(texts) != 2:
                self.audit.error(f"card group {label!r} must contain exactly two text lines")

            card_x, card_y, card_width, card_height = self.rect_box(cards[0])
            accent_x, accent_y, accent_width, accent_height = self.rect_box(accents[0])
            card_area += card_width * card_height
            if not (4 <= accent_width <= 6):
                self.audit.error(f"card {label!r} accent width must be 4–6px")
            if abs(accent_x - card_x) > 0.01 or abs(accent_y - card_y) > 0.01:
                self.audit.error(f"card {label!r} accent must start at the top-left edge")
            if abs(accent_height - card_height) > 0.01:
                self.audit.error(f"card {label!r} accent must be a full-height left stripe")
            if self.property(cards[0], "fill") not in {"var(--surface)", "#FFFFFF", "#ffffff"}:
                self.audit.warn(f"card {label!r} does not use the shared white surface")

            for text_node in texts:
                font_size = number(self.property(text_node, "font-size"), 16)
                content = "".join(text_node.itertext()).strip()
                estimated = sum(
                    font_size
                    * (1.0 if "\u2e80" <= char <= "\u9fff" else 0.32 if char.isspace() else 0.56)
                    for char in content
                )
                text_x = self.global_offset(text_node)[0] + number(text_node.attrib.get("x"))
                if text_node.attrib.get("text-anchor") == "middle":
                    left, right = text_x - estimated / 2, text_x + estimated / 2
                else:
                    left, right = text_x, text_x + estimated
                if left < card_x + 16 or right > card_x + card_width - 16:
                    self.audit.error(f"estimated text overflow in card {label!r}: {content!r}")

        if self.width and self.height:
            ratio = card_area / (self.width * self.height)
            self.audit.metrics["card_area_ratio"] = round(ratio, 3)
            if ratio > 0.45:
                self.audit.warn(f"card area ratio {ratio:.1%} is crowded; target is below 45%")

        title_sizes = [
            number(self.property(node, "font-size"))
            for node in self.nodes
            if local_name(node.tag) == "text" and "title" in classes(node)
        ]
        body_sizes = [
            number(self.property(node, "font-size"))
            for node in self.nodes
            if local_name(node.tag) == "text" and "body" in classes(node)
        ]
        note_sizes = [
            number(self.property(node, "font-size"))
            for node in self.nodes
            if local_name(node.tag) == "text" and "note" in classes(node)
        ]
        if not title_sizes or not body_sizes or not note_sizes:
            self.audit.warn("typography should expose title, body, and note classes")
        elif not (max(title_sizes) > max(body_sizes) > min(note_sizes)):
            self.audit.error("title, body, and note sizes do not form three levels")

    def check_grid_and_balance(self) -> None:
        card_groups = [node for node in self.nodes if node.attrib.get("data-card")]
        boxes = []
        for group in card_groups:
            card = next(
                (node for node in group.iter() if local_name(node.tag) == "rect" and "card" in classes(node)),
                None,
            )
            if card is None:
                continue
            box = self.rect_box(card)
            boxes.append((group, box))
            for value, name in zip(box, ("x", "y", "width", "height")):
                if not is_grid_value(value):
                    self.audit.warn(f"card {group.attrib.get('data-card')!r} {name}={value:g} misses 4px grid")
            x, y, width, height = box
            if self.width and (x < self.view_x + 40 or x + width > self.view_x + self.width - 40):
                self.audit.error(f"card {group.attrib.get('data-card')!r} violates horizontal safe margin")
            if self.height and (y < self.view_y + 40 or y + height > self.view_y + self.height - 40):
                self.audit.error(f"card {group.attrib.get('data-card')!r} violates vertical safe margin")

        main_boxes = [box for group, box in boxes if group.attrib.get("data-stage") == "main"]
        if len(main_boxes) > 1:
            y_values = {round(box[1], 3) for box in main_boxes}
            heights = {round(box[3], 3) for box in main_boxes}
            if len(y_values) != 1 or len(heights) != 1:
                self.audit.error("main-stage cards do not share top edge and height")

        section_labels = [
            node for node in self.nodes if local_name(node.tag) == "text" and "section-label" in classes(node)
        ]
        if len(section_labels) > 1:
            baselines = {
                round(self.global_offset(node)[1] + number(node.attrib.get("y")), 3)
                for node in section_labels
            }
            if len(baselines) != 1:
                self.audit.error("section labels do not share a baseline")

        y_values: list[float] = []
        for _, (x, y, width, height) in boxes:
            del x, width
            y_values.extend((y, y + height))
        for node in self.nodes:
            if local_name(node.tag) != "path" or self.in_defs(node):
                continue
            paths, unsupported = parse_path_points(node.attrib.get("d", ""))
            if unsupported:
                continue
            dx, dy = self.global_offset(node)
            y_values.extend(point_y + dy for path in paths for _, point_y in path)
        if y_values and self.height:
            content_top, content_bottom = min(y_values), max(y_values)
            self.audit.metrics["content_vertical_span"] = [content_top, content_bottom]
            if content_top > self.view_y + self.height * 0.24:
                self.audit.warn("top region is underused")
            if content_bottom < self.view_y + self.height * 0.78:
                self.audit.warn("bottom region is too empty or composition is top-heavy")

    def check_paths_and_semantics(self) -> None:
        card_boxes = []
        for group in [node for node in self.nodes if node.attrib.get("data-card")]:
            card = next(
                (node for node in group.iter() if local_name(node.tag) == "rect" and "card" in classes(node)),
                None,
            )
            if card is not None:
                card_boxes.append((group.attrib.get("data-card", "unnamed"), self.rect_box(card)))

        for node in self.nodes:
            if local_name(node.tag) != "path" or not ({"flow", "feedback", "rail"} & classes(node)):
                continue
            paths, unsupported = parse_path_points(node.attrib.get("d", ""))
            if unsupported:
                self.audit.warn("audited connectors should prefer absolute M/L/H/V commands")
                continue
            dx, dy = self.global_offset(node)
            for path in paths:
                absolute = [(x + dx, y + dy) for x, y in path]
                for start, end in zip(absolute, absolute[1:]):
                    for label, box in card_boxes:
                        if self.segment_crosses_card(start, end, box):
                            self.audit.error(f"connector crosses card interior: {label!r}")

        input_groups = [node for node in self.nodes if node.attrib.get("data-role") == "inputs"]
        input_cards = sum(
            1 for group in input_groups for node in group.iter() if node.attrib.get("data-card")
        )
        shared = [node for node in self.nodes if node.attrib.get("data-role") == "shared-input"]
        if input_cards > 1 and not shared:
            self.audit.error("multiple inputs must converge through a data-role='shared-input' rail")

        feedback_groups = [node for node in self.nodes if node.attrib.get("data-role") == "feedback"]
        ids = {node.attrib.get("id"): node for node in self.nodes if node.attrib.get("id")}
        for group in feedback_groups:
            target = group.attrib.get("data-target")
            if not target or target not in ids:
                self.audit.error("feedback group must target an existing semantic region")
            elif ids[target].attrib.get("data-role") not in {"shared-input", "constraints"}:
                self.audit.error("feedback must return to shared input or constraints, not one input card")
            feedback_widths = [
                number(self.property(node, "stroke-width"))
                for node in group.iter()
                if local_name(node.tag) == "path"
            ]
            flow_widths = [
                number(self.property(node, "stroke-width"))
                for node in self.nodes
                if local_name(node.tag) == "path" and "flow" in classes(node)
            ]
            if feedback_widths and flow_widths and max(feedback_widths) >= min(flow_widths):
                self.audit.error("feedback stroke must be lighter than the main flow")

    @staticmethod
    def segment_crosses_card(
        start: tuple[float, float],
        end: tuple[float, float],
        box: tuple[float, float, float, float],
    ) -> bool:
        x1, y1 = start
        x2, y2 = end
        left, top, width, height = box
        right, bottom = left + width, top + height
        epsilon = 0.5
        if abs(y1 - y2) <= epsilon:
            y = y1
            if not (top + epsilon < y < bottom - epsilon):
                return False
            overlap = min(max(x1, x2), right - epsilon) - max(min(x1, x2), left + epsilon)
            return overlap > epsilon
        if abs(x1 - x2) <= epsilon:
            x = x1
            if not (left + epsilon < x < right - epsilon):
                return False
            overlap = min(max(y1, y2), bottom - epsilon) - max(min(y1, y2), top + epsilon)
            return overlap > epsilon
        return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="SVG file to audit")
    parser.add_argument(
        "--required-text",
        action="append",
        default=[],
        help="protected text that must occur verbatim; repeat as needed",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat warnings as failures",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        report = SvgAuditor(args.svg, args.required_text).run()
    except (OSError, ET.ParseError, UnicodeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    for message in report.errors:
        print(f"[ERROR] {message}")
    for message in report.warnings:
        print(f"[WARN] {message}")
    print(
        f"[INFO] svg={args.svg} errors={len(report.errors)} "
        f"warnings={len(report.warnings)} metrics={report.metrics}"
    )
    return 1 if report.errors or (args.strict and report.warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
