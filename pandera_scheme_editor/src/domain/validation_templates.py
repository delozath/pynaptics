"""Declarative validation templates for frequent Pandera column edits."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .contract import ColumnContract


@dataclass(frozen=True, slots=True)
class TemplateParameter:
    """User-editable parameter for a validation template."""

    key: str
    label: str
    default: Any = None
    value_type: str = "scalar"  # scalar | list | bool | text
    description: str = ""
    optional: bool = False


@dataclass(frozen=True, slots=True)
class ParameterRef:
    """Placeholder resolved from `parameter_values` when a template is applied."""

    key: str
    optional: bool = False


@dataclass(frozen=True, slots=True)
class ValidationTemplate:
    """Declarative column template.

    `checks` may contain `ParameterRef` values. Optional refs with empty values
    are omitted; if a check payload becomes empty, that check is not added.
    """

    key: str
    label: str
    description: str
    recommended_dtype: str
    default_nullable: bool | None
    default_coerce: bool
    default_unique: bool | None
    checks: dict[str, dict[str, Any]] = field(default_factory=dict)
    parameters: tuple[TemplateParameter, ...] = ()


MEXICO_STATES: list[str] = [
    "Aguascalientes",
    "Baja California",
    "Baja California Sur",
    "Campeche",
    "Chiapas",
    "Chihuahua",
    "Ciudad de México",
    "Coahuila",
    "Colima",
    "Durango",
    "Guanajuato",
    "Guerrero",
    "Hidalgo",
    "Jalisco",
    "Estado de México",
    "Michoacán",
    "Morelos",
    "Nayarit",
    "Nuevo León",
    "Oaxaca",
    "Puebla",
    "Querétaro",
    "Quintana Roo",
    "San Luis Potosí",
    "Sinaloa",
    "Sonora",
    "Tabasco",
    "Tamaulipas",
    "Tlaxcala",
    "Veracruz",
    "Yucatán",
    "Zacatecas",
]


def _nullable_parameter(default: bool = False) -> TemplateParameter:
    return TemplateParameter(
        key="nullable",
        label="Permitir nulos",
        default=default,
        value_type="bool",
        description="Define nullable para la columna.",
    )


VALIDATION_TEMPLATES: dict[str, ValidationTemplate] = {
    "human_age": ValidationTemplate(
        key="human_age",
        label="Edad humana",
        description="Entero nullable configurable con rango típico 0 a 100.",
        recommended_dtype="Int64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={
            "greater_than_or_equal_to": {"min_value": ParameterRef("min_value")},
            "less_than_or_equal_to": {"max_value": ParameterRef("max_value")},
        },
        parameters=(
            _nullable_parameter(False),
            TemplateParameter("min_value", "Valor mínimo", 0, "scalar"),
            TemplateParameter("max_value", "Valor máximo", 100, "scalar"),
        ),
    ),
    "sex_binary": ValidationTemplate(
        key="sex_binary",
        label="Sexo biológico simple",
        description="String con valores permitidos F/M.",
        recommended_dtype="string",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={"isin": {"allowed_values": ["F", "M"]}},
        parameters=(_nullable_parameter(False),),
    ),
    "sex_or_gender_extended": ValidationTemplate(
        key="sex_or_gender_extended",
        label="Sexo/género extendido",
        description="String con categorías extendidas: F, M, Otro, No especificado.",
        recommended_dtype="string",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={"isin": {"allowed_values": ["F", "M", "Otro", "No especificado"]}},
        parameters=(_nullable_parameter(False),),
    ),
    "height_cm": ValidationTemplate(
        key="height_cm",
        label="Talla en cm",
        description="Float nullable configurable con rango 30 a 250 cm.",
        recommended_dtype="Float64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={
            "greater_than_or_equal_to": {"min_value": 30},
            "less_than_or_equal_to": {"max_value": 250},
        },
        parameters=(_nullable_parameter(False),),
    ),
    "weight_kg": ValidationTemplate(
        key="weight_kg",
        label="Peso en kg",
        description="Float nullable configurable con rango 0 a 500 kg.",
        recommended_dtype="Float64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={
            "greater_than_or_equal_to": {"min_value": 0},
            "less_than_or_equal_to": {"max_value": 500},
        },
        parameters=(_nullable_parameter(False),),
    ),
    "positive_number": ValidationTemplate(
        key="positive_number",
        label="Número positivo estricto",
        description="Float nullable configurable mayor que cero.",
        recommended_dtype="Float64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={"greater_than": {"min_value": 0}},
        parameters=(_nullable_parameter(False),),
    ),
    "non_negative_number": ValidationTemplate(
        key="non_negative_number",
        label="Número positivo o cero",
        description="Float nullable configurable mayor o igual que cero.",
        recommended_dtype="Float64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={"greater_than_or_equal_to": {"min_value": 0}},
        parameters=(_nullable_parameter(False),),
    ),
    "non_negative_integer": ValidationTemplate(
        key="non_negative_integer",
        label="Entero positivo o cero",
        description="Entero nullable configurable mayor o igual que cero.",
        recommended_dtype="Int64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={"greater_than_or_equal_to": {"min_value": 0}},
        parameters=(_nullable_parameter(False),),
    ),
    "percentage_0_100": ValidationTemplate(
        key="percentage_0_100",
        label="Porcentaje 0 a 100",
        description="Float nullable configurable acotado entre 0 y 100.",
        recommended_dtype="Float64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={
            "greater_than_or_equal_to": {"min_value": 0},
            "less_than_or_equal_to": {"max_value": 100},
        },
        parameters=(_nullable_parameter(False),),
    ),
    "proportion_0_1": ValidationTemplate(
        key="proportion_0_1",
        label="Proporción 0 a 1",
        description="Float nullable configurable acotado entre 0 y 1.",
        recommended_dtype="Float64",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={
            "greater_than_or_equal_to": {"min_value": 0},
            "less_than_or_equal_to": {"max_value": 1},
        },
        parameters=(_nullable_parameter(False),),
    ),
    "mexico_postal_code": ValidationTemplate(
        key="mexico_postal_code",
        label="Código postal México",
        description="String de cinco dígitos; no usar entero para preservar ceros a la izquierda.",
        recommended_dtype="string",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={"str_matches": {"pattern": r"^\d{5}$"}},
        parameters=(_nullable_parameter(True),),
    ),
    "mexico_state": ValidationTemplate(
        key="mexico_state",
        label="Entidad federativa México",
        description="String con las 32 entidades federativas de México.",
        recommended_dtype="string",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={"isin": {"allowed_values": MEXICO_STATES}},
        parameters=(_nullable_parameter(False),),
    ),
    "email": ValidationTemplate(
        key="email",
        label="Email",
        description="String con patrón de correo electrónico práctico para validación de datos tabulares.",
        recommended_dtype="string",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={
            "str_matches": {
                "pattern": r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$"
            }
        },
        parameters=(_nullable_parameter(False),),
    ),
    "date": ValidationTemplate(
        key="date",
        label="Fecha",
        description="Datetime nullable configurable con límites opcionales.",
        recommended_dtype="datetime64[ns]",
        default_nullable=False,
        default_coerce=True,
        default_unique=None,
        checks={
            "greater_than_or_equal_to": {"min_value": ParameterRef("min_value", optional=True)},
            "less_than_or_equal_to": {"max_value": ParameterRef("max_value", optional=True)},
        },
        parameters=(
            _nullable_parameter(False),
            TemplateParameter("min_value", "Fecha mínima opcional", None, "text", optional=True),
            TemplateParameter("max_value", "Fecha máxima opcional", None, "text", optional=True),
        ),
    ),
    "unique_id": ValidationTemplate(
        key="unique_id",
        label="Identificador único",
        description="String no nulo, coercible y único; regex opcional.",
        recommended_dtype="string",
        default_nullable=False,
        default_coerce=True,
        default_unique=True,
        checks={"str_matches": {"pattern": ParameterRef("pattern", optional=True)}},
        parameters=(
            TemplateParameter("pattern", "Patrón regex opcional", None, "text", optional=True),
        ),
    ),
}


def _values_with_defaults(template: ValidationTemplate, parameter_values: dict[str, Any]) -> dict[str, Any]:
    values = {parameter.key: parameter.default for parameter in template.parameters}
    values.update(parameter_values)
    return values


def _is_empty_optional_value(value: Any) -> bool:
    return value is None or value == ""


def _resolve_payload(payload: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, ParameterRef):
            parameter_value = values.get(value.key)
            if value.optional and _is_empty_optional_value(parameter_value):
                continue
            resolved[key] = deepcopy(parameter_value)
        elif isinstance(value, dict):
            nested = _resolve_payload(value, values)
            if nested:
                resolved[key] = nested
        else:
            resolved[key] = deepcopy(value)
    return resolved


def _resolve_checks(template: ValidationTemplate, values: dict[str, Any]) -> dict[str, dict[str, Any]]:
    checks: dict[str, dict[str, Any]] = {}
    for check_key, payload in template.checks.items():
        resolved_payload = _resolve_payload(payload, values)
        if resolved_payload:
            checks[check_key] = resolved_payload
    return checks


def apply_template_to_column(
    column: ColumnContract,
    template_key: str,
    parameter_values: dict[str, Any],
    replace_existing_checks: bool = False,
) -> None:
    """Apply a registered validation template to a column.

    The template always wins on check-key conflicts. When
    `replace_existing_checks=True`, previous checks are removed first.
    """
    if template_key not in VALIDATION_TEMPLATES:
        raise KeyError(f"Plantilla no soportada: {template_key!r}")

    template = VALIDATION_TEMPLATES[template_key]
    values = _values_with_defaults(template, parameter_values)

    column.dtype = template.recommended_dtype
    if "nullable" in values:
        column.nullable = bool(values["nullable"])
    elif template.default_nullable is not None:
        column.nullable = bool(template.default_nullable)
    column.coerce = bool(template.default_coerce)
    if template.default_unique is not None:
        column.unique = bool(template.default_unique)

    if replace_existing_checks:
        column.clear_checks()

    for check_key, payload in _resolve_checks(template, values).items():
        column.set_check(check_key, payload)
