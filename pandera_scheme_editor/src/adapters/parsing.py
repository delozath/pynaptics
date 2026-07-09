"""Parsing helpers for GUI-entered scalar and list values."""

from __future__ import annotations

import ast
from typing import Any


def parse_scalar(value: str) -> Any:
    """Parse one scalar text field into a Python value.

    Required conversions:
    - ``""``, ``"null"`` and ``"None"`` -> ``None``
    - ``"true"`` / ``"false"`` -> booleans
    - numeric literals -> int/float
    - quoted literals -> their literal value
    - fallback -> raw string
    """
    text = value.strip()
    if text in {"", "null", "None"}:
        return None
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return text


def parse_list_text(text: str) -> list[Any]:
    """Parse a list from Python-list syntax or one item per line."""
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, list):
                return parsed
        except (ValueError, SyntaxError):
            pass
    return [parse_scalar(line) for line in stripped.splitlines() if line.strip()]


def format_value(value: Any) -> str:
    """Format a scalar value for text editing."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def format_list(values: Any) -> str:
    """Format a list-like value as one item per line."""
    if values is None:
        return ""
    if isinstance(values, list):
        return "\n".join(format_value(value) for value in values)
    return format_value(values)
