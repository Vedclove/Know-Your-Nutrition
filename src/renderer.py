from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Sequence

FIXED_WIDTH = 560
DEFAULT_HEIGHT = 720
OUTPUT_PATH = Path("images/nutrition_facts.svg")

DEFAULT_ROWS = (
    ("Total Fat", "total_fat", "total_fat_dv", 0, True),
    ("Saturated Fat", "sat_fat", "sat_fat_dv", 16, False),
    ("Trans Fat", "trans_fat", None, 16, False),
    ("Cholesterol", "cholesterol", "cholesterol_dv", 0, True),
    ("Sodium", "sodium", "sodium_dv", 0, True),
    ("Total Carbohydrate", "total_carb", "total_carb_dv", 0, True),
    ("Dietary Fiber", "dietary_fiber", "dietary_fiber_dv", 16, False),
    ("Total Sugars", "total_sugars", None, 16, False),
    ("Protein", "protein", None, 0, True),
)
DEFAULT_MICRONUTRIENTS = (
    ("Vitamin D", "vitamin_d", "vitamin_d_dv"),
    ("Calcium", "calcium", "calcium_dv"),
    ("Iron", "iron", "iron_dv"),
    ("Potassium", "potassium", "potassium_dv"),
)


def create_nutrition_facts_svg(
    values: dict[str, str],
    rows: Sequence[tuple[str, str, str | None, int, bool]] = DEFAULT_ROWS,
    output_path: Path = OUTPUT_PATH,
    micronutrients: Sequence[tuple[str, str, str | None]] | None = None,
    width: int = FIXED_WIDTH,
    height: int = DEFAULT_HEIGHT,
) -> Path:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive integers")

    pad = 18
    right = width - pad
    per_serving_x = right - 200
    per_box_x = right - 100
    y = 44
    lines: list[str] = []

    def t(
        text: str,
        x: int,
        y_pos: int,
        size: int = 16,
        weight: str = "normal",
        anchor: str = "start",
    ) -> str:
        return (
            f'<text x="{x}" y="{y_pos}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(text)}</text>'
        )

    def hline(y_pos: int, stroke: int = 2) -> str:
        return f'<line x1="{pad}" y1="{y_pos}" x2="{right}" y2="{y_pos}" stroke="black" stroke-width="{stroke}" />'

    def v(key: str) -> str:
        value = values.get(key)
        if value is None:
            return ""
        return str(value)

    lines.append(t("Nutrition Facts", pad, y, size=48, weight="700"))
    y += 12
    lines.append(hline(y, stroke=10))
    y += 28
    lines.append(t(f"Servings per container {v('servings_per_container')}", pad, y, size=15))
    y += 28
    lines.append(t("Serving size", pad, y, size=18, weight="700"))
    lines.append(t(v("serving_size"), right, y, size=18, weight="700", anchor="end"))
    y += 16
    lines.append(hline(y, stroke=6))
    y += 26
    lines.append(t("Amount per serving", pad, y, size=13))
    y += 38
    lines.append(t("Calories", pad, y, size=44, weight="700"))
    lines.append(t(v("calories"), per_serving_x, y, size=34, weight="700", anchor="end"))
    lines.append(t(v("calories_entire"), per_box_x, y, size=34, weight="700", anchor="end"))
    y += 18
    lines.append(hline(y, stroke=4))
    y += 24
    lines.append(t("Per serving", per_serving_x, y, size=11, weight="700", anchor="end"))
    lines.append(t("Per box", per_box_x, y, size=11, weight="700", anchor="end"))
    lines.append(t("% Daily Value*", right, y, size=11, weight="700", anchor="end"))

    for label, value_key, dv_key, indent, bold in rows:
        y += 30
        lines.append(hline(y - 18, stroke=1))
        weight = "700" if bold else "normal"
        lines.append(t(label, pad + indent, y, size=16, weight=weight))
        lines.append(t(v(value_key), per_serving_x, y, size=16, weight=weight, anchor="end"))
        lines.append(t(v(f"{value_key}_entire"), per_box_x, y, size=16, weight=weight, anchor="end"))
        if dv_key:
            lines.append(t(v(dv_key), right, y, size=16, weight="700", anchor="end"))

    y += 22
    lines.append(hline(y, stroke=4))

    if micronutrients is None:
        micronutrients = DEFAULT_MICRONUTRIENTS

    for label, value_key, dv_key in micronutrients:
        y += 28
        lines.append(hline(y - 18, stroke=1))
        lines.append(t(label, pad, y, size=14))
        lines.append(t(v(value_key), per_serving_x, y, size=14, anchor="end"))
        lines.append(t(v(f"{value_key}_entire"), per_box_x, y, size=14, anchor="end"))
        if dv_key:
            lines.append(t(v(dv_key), right, y, size=14, anchor="end"))

    y += 36
    lines.append(
        t(
            "* The % Daily Value tells you how much a nutrient in a serving of food contributes to a daily diet.",
            pad,
            y,
            size=11,
        )
    )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" fill="white" '
        f'stroke="black" stroke-width="2" />'
        + "".join(lines)
        + "</svg>"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    return output_path
