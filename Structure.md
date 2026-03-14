# Project Structure

## Overview

Know Your Nutrition is a three-stage pipeline that takes a photo of a nutrition label, extracts the data using an AI vision model, computes whole-container totals, and renders a clean SVG nutrition facts panel.

```
Image file
    │
    ▼
src/detector.py       ── Stage 1: Extract per-serving data from image (OpenAI vision)
    │
    ▼
src/calculator.py     ── Stage 2: Calculate whole-container totals (pure arithmetic)
    │
    ▼
src/renderer.py       ── Stage 3: Render SVG nutrition label
    │
    ▼
images/*.svg
```

---

## Directory Layout

```
know-your-nutrition/
├── src/                          # Core application modules
│   ├── __init__.py               # Re-exports all public functions
│   ├── detector.py               # Stage 1 – image → nutrition JSON
│   ├── calculator.py             # Stage 2 – per-serving → whole-container totals
│   └── renderer.py               # Stage 3 – dict → SVG label
│
├── utils/                        # Shared helper functions
│   ├── __init__.py
│   ├── image_utils.py            # Image encoding and JSON parsing helpers
│   └── math_utils.py             # Decimal arithmetic helpers
│
├── main.py                       # CLI entry point (chains all 3 stages)
├── main.ipynb                    # Interactive notebook for exploration
│
├── images/                       # Input images and generated SVG output
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## `src/` — Core Modules

### `src/detector.py` — Stage 1: Image → JSON

Sends the image to an OpenAI vision model and returns a structured dict of per-serving nutrition values.

**Dependencies:** `utils.image_utils`

**Constants:**
- `DEFAULT_MODEL` — OpenAI model used (`gpt-4.1-mini`)
- `NUTRITION_FIELDS` — The 26 canonical field names extracted from the label

**Module-level:**
- `_client` — Single shared `OpenAI` instance (reads `OPENAI_API_KEY` or `OPEN_AI_API_KEY` at import time)

**Public functions:**

| Function | Returns | Description |
|---|---|---|
| `validate_image_to_nutrition(image_path, model)` | `bool` | Returns `True` if the image is a nutrition facts label |
| `extract_nutrition_facts_json(image_path, model)` | `dict[str, str \| None]` | Validates then extracts all 26 nutrition fields as a normalised dict |

---

### `src/calculator.py` — Stage 2: Per-serving → Whole-container

Pure arithmetic. Multiplies every per-serving value by `servings_per_container` to produce `{field}_entire` keys.

**Dependencies:** `utils.math_utils`

**Constants:**
- `ENTIRE_FIELDS` — The 14 numeric fields for which `_entire` totals are computed

**Public function:**

| Function | Returns | Description |
|---|---|---|
| `calculate_nutrition(nutrition_metadata)` | `dict` | Input dict extended with `{field}_entire` keys |

---

### `src/renderer.py` — Stage 3: dict → SVG

Renders a standard-format nutrition facts panel as an SVG file.

**Constants:**
- `FIXED_WIDTH` / `DEFAULT_HEIGHT` — Canvas size (560 × 720 px)
- `OUTPUT_PATH` — Default output path (`images/nutrition_facts.svg`)
- `DEFAULT_ROWS` — 9 standard macronutrient rows
- `DEFAULT_MICRONUTRIENTS` — 4 standard micronutrient rows

**Public function:**

| Function | Returns | Description |
|---|---|---|
| `create_nutrition_facts_svg(values, rows, output_path, micronutrients, width, height)` | `Path` | Writes SVG to disk and returns the output path |

The `values` dict must contain both per-serving keys (e.g. `total_fat`) and whole-container keys (e.g. `total_fat_entire`) so both columns appear in the label.

---

### `src/__init__.py` — Public API

Re-exports all public functions so callers can import directly from `src`:

```python
from src import extract_nutrition_facts_json, calculate_nutrition, create_nutrition_facts_svg
```

---

## `utils/` — Shared Helpers

### `utils/image_utils.py`

| Function | Description |
|---|---|
| `to_data_url(image_path)` | Encodes an image file as a base64 data URL for use in API payloads |
| `extract_json(raw_text)` | Parses the first JSON object found in a model response string |

### `utils/math_utils.py`

| Function | Description |
|---|---|
| `parse_number(text)` | Extracts the first number from a string as a `Decimal` |
| `split_value_and_unit(text)` | Splits `"8g"` → `(Decimal("8"), "g")` |
| `fmt_decimal(n)` | Formats a `Decimal` cleanly, stripping trailing zeros |
| `multiply_value(text, factor)` | Multiplies a value string by a factor, preserving its unit |

---

## `main.py` — CLI Entry Point

Chains all three stages into a single command:

```
python main.py <image_path> [--output <svg_path>] [--model <openai_model>]
```

---

## Data Flow

```
extract_nutrition_facts_json(image_path)
    └─ returns: {
           "servings_per_container": "10",
           "calories": "250",
           "total_fat": "8g",
           ...26 fields...
       }

calculate_nutrition(nutrition)
    └─ returns: {
           ...all 26 original fields...,
           "calories_entire": "2500",
           "total_fat_entire": "80g",
           ...14 _entire fields...
       }

create_nutrition_facts_svg(values=enriched, output_path=Path("images/out.svg"))
    └─ writes SVG to disk, returns Path
```

---

## Environment

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI API key (primary) |
| `OPEN_AI_API_KEY` | OpenAI API key (fallback) |

Dependencies are managed with `uv` and declared in `pyproject.toml`.
