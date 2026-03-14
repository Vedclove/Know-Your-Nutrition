from __future__ import annotations

import re
from decimal import Decimal, ROUND_HALF_UP


def parse_number(text: str) -> Decimal | None:
    if not text:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(text))
    return Decimal(m.group()) if m else None


def split_value_and_unit(text: str) -> tuple[Decimal | None, str]:
    if not text:
        return None, ""
    s = str(text).strip()
    m = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*([a-zA-Z%]*)\s*$", s)
    if not m:
        n = parse_number(s)
        if n is None:
            return None, ""
        unit = re.sub(r"[-\d.\s]", "", s)
        return n, unit
    return Decimal(m.group(1)), m.group(2)


def fmt_decimal(n: Decimal) -> str:
    q = n.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    s = format(q, "f").rstrip("0").rstrip(".")
    return "0" if s in {"", "-0"} else s


def multiply_value(text: str, factor: Decimal) -> str:
    n, unit = split_value_and_unit(text)
    if n is None:
        return ""
    return f"{fmt_decimal(n * factor)}{unit}"
