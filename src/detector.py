from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from openai import OpenAI

from utils.image_utils import extract_json, to_data_url

DEFAULT_MODEL = "gpt-4.1-mini"
NUTRITION_FIELDS = [
    "servings_per_container",
    "serving_size",
    "calories",
    "total_fat",
    "total_fat_dv",
    "sat_fat",
    "sat_fat_dv",
    "trans_fat",
    "cholesterol",
    "cholesterol_dv",
    "sodium",
    "sodium_dv",
    "total_carb",
    "total_carb_dv",
    "dietary_fiber",
    "dietary_fiber_dv",
    "total_sugars",
    "protein",
    "vitamin_d",
    "vitamin_d_dv",
    "calcium",
    "calcium_dv",
    "iron",
    "iron_dv",
    "potassium",
    "potassium_dv",
]

_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPEN_AI_API_KEY")
_client = OpenAI(api_key=_api_key)


def validate_image_to_nutrition(image_path: Path, model: str = DEFAULT_MODEL) -> bool:
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    prompt = (
        "Check if the image is actually an Nutrition Fact image"
        "If the image is actually an Nutrition Facts image return a boolean value"
        "True: Means that the image is an Nutrition Fact Image and False: If it is not an Nutrition Fact Image"
        "Do not include any description only an boolean values should be returned."
    )
    response = _client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": to_data_url(image_path)},
                ],
            }
        ],
    )
    return response.output_text.strip() in ("True", "true")


def extract_nutrition_facts_json(image_path: Path, model: str = DEFAULT_MODEL) -> dict:
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if not validate_image_to_nutrition(image_path=image_path, model=model):
        raise RuntimeError("This request cannot be processed!")

    print("Images is Validated! Let me process this request.")
    fields_text = ", ".join(NUTRITION_FIELDS)
    prompt = (
        "Extract Nutrition Facts values from this image and return only JSON. "
        f"Use exactly these keys: {fields_text}. "
        "If a field is not available, set its value to null. "
        "Keep units if visible (e.g., mg, g, mcg, %). "
        "Do not include any keys other than the listed keys."
    )

    response = _client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": to_data_url(image_path)},
                ],
            }
        ],
    )

    data = extract_json(response.output_text.strip())

    normalized: dict[str, str | None] = {}
    for key in NUTRITION_FIELDS:
        value = data.get(key)
        normalized[key] = str(value).strip() or None if value is not None else None
    return normalized


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract Nutrition Facts JSON fields from an image."
    )
    parser.add_argument("image", type=Path, help="Path to source image")
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model name (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    result = extract_nutrition_facts_json(image_path=args.image, model=args.model)
    print(json.dumps(result, indent=2))
