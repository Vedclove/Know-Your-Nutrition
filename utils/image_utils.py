from __future__ import annotations

import base64
import json
import mimetypes
import re
from pathlib import Path


def to_data_url(image_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type:
        mime_type = "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def extract_json(raw_text: str) -> dict:
    match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Model output did not include JSON: {raw_text}")
    return json.loads(match.group(0))
