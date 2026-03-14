from __future__ import annotations

from decimal import Decimal
from typing import Any

from utils.math_utils import multiply_value, parse_number

ENTIRE_FIELDS = [
    "calories",
    "total_fat",
    "sat_fat",
    "trans_fat",
    "cholesterol",
    "sodium",
    "total_carb",
    "dietary_fiber",
    "total_sugars",
    "protein",
    "vitamin_d",
    "calcium",
    "iron",
    "potassium",
]


def calculate_nutrition(nutrition_metadata: dict[str, Any]) -> dict[str, Any]:
    result = dict(nutrition_metadata)

    servings = parse_number(str(result.get("servings_per_container", "") or ""))
    if servings is None:
        for key in ENTIRE_FIELDS:
            result[f"{key}_entire"] = ""
        return result

    for key in ENTIRE_FIELDS:
        result[f"{key}_entire"] = multiply_value(str(result.get(key, "") or ""), servings)

    return result
