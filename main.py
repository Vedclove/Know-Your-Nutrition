from __future__ import annotations

import argparse
from pathlib import Path

from src.detector import DEFAULT_MODEL, extract_nutrition_facts_json
from src.calculator import calculate_nutrition
from src.renderer import create_nutrition_facts_svg


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract nutrition facts from an image and generate an SVG label."
    )
    parser.add_argument("image", type=Path, help="Path to the nutrition facts image")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("images/nutrition_facts.svg"),
        help="Output SVG path (default: images/nutrition_facts.svg)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    nutrition = extract_nutrition_facts_json(image_path=args.image, model=args.model)
    enriched = calculate_nutrition(nutrition)
    svg_path = create_nutrition_facts_svg(values=enriched, output_path=args.output)
    print(f"Nutrition facts SVG saved to: {svg_path.resolve()}")


if __name__ == "__main__":
    main()
