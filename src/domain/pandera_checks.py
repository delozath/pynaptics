"""Editable Pandera dtypes and check payload templates."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


PANDERA_DTYPES: list[str] = [
    #"string",
    "str",
    "int",
    "float",
    "bool",
    "datetime64[ns]",
    "category",
    "object",
    "Int64",
    "Float64",
    #"int64",
    #"Float64",
    "Int32",
    "Float32"
]

CHECK_KEYS: list[str] = [
    "isin",
    "greater_than_or_equal_to",
    "greater_than",
    "less_than_or_equal_to",
    "less_than",
    "str_matches",
    "str_length",
]


@dataclass(frozen=True, slots=True)
class CheckTemplate:
    """Declarative description of an editable check."""

    key: str
    label: str
    description: str
    default_payload: dict[str, Any]


CHECK_TEMPLATES: dict[str, CheckTemplate] = {
    "isin": CheckTemplate(
        key="isin",
        label="Valores permitidos",
        description="Valida que el valor pertenezca a una lista cerrada.",
        default_payload={"allowed_values": ["A", "B"]},
    ),
    "greater_than_or_equal_to": CheckTemplate(
        key="greater_than_or_equal_to",
        label="Mayor o igual que",
        description="Valida un límite inferior inclusivo.",
        default_payload={"min_value": 0},
    ),
    "greater_than": CheckTemplate(
        key="greater_than",
        label="Mayor que",
        description="Valida un límite inferior estricto.",
        default_payload={"min_value": 0},
    ),
    "less_than_or_equal_to": CheckTemplate(
        key="less_than_or_equal_to",
        label="Menor o igual que",
        description="Valida un límite superior inclusivo.",
        default_payload={"max_value": 100},
    ),
    "less_than": CheckTemplate(
        key="less_than",
        label="Menor que",
        description="Valida un límite superior estricto.",
        default_payload={"max_value": 100},
    ),
    "str_matches": CheckTemplate(
        key="str_matches",
        label="Regex",
        description="Valida que un string cumpla una expresión regular.",
        default_payload={"pattern": r"^\d{5}$"},
    ),
    "str_length": CheckTemplate(
        key="str_length",
        label="Longitud de string",
        description="Valida longitud mínima y máxima de un string.",
        default_payload={"min_value": 1, "max_value": 50},
    ),
}


def default_check_payload(check_key: str) -> dict[str, Any]:
    """Return a defensive copy of the default payload for a check key."""
    if check_key not in CHECK_TEMPLATES:
        raise KeyError(f"Check no soportado: {check_key!r}")
    return deepcopy(CHECK_TEMPLATES[check_key].default_payload)


_NUMERIC_RANGE_CHECKS: list[str] = [
    "greater_than_or_equal_to",
    "greater_than",
    "less_than_or_equal_to",
    "less_than",
]
_CATEGORICAL_CHECKS: list[str] = ["isin", "str_matches", "str_length"]
_TEMPORAL_CHECKS: list[str] = ["greater_than_or_equal_to", "less_than_or_equal_to"]
_CATEGORICAL_DTYPES: frozenset[str] = frozenset(
    {"string", "str", "object", "category", "boolean", "bool"}
)


def relevant_check_keys_for_dtype(dtype: Any) -> list[str]:
    """Return the CHECK_KEYS subset most relevant to a given dtype.

    Continuous numeric dtypes (Float64/float64) rarely use `isin`; discrete
    numeric dtypes (Int64/int64) commonly encode small categorical codes, so
    `isin` stays available alongside range checks; text/categorical dtypes get
    `isin`/`str_matches`/`str_length`; datetime gets range checks only.
    An unrecognized dtype falls back to the full `CHECK_KEYS` list so a valid
    check is never hidden by mistake.
    """
    normalized = "" if dtype is None else str(dtype).strip().lower()
    if normalized == "float64":
        return list(_NUMERIC_RANGE_CHECKS)
    if normalized == "int64":
        return [*_NUMERIC_RANGE_CHECKS, "isin"]
    if normalized in _CATEGORICAL_DTYPES:
        return list(_CATEGORICAL_CHECKS)
    if normalized == "datetime64[ns]":
        return list(_TEMPORAL_CHECKS)
    return list(CHECK_KEYS)
