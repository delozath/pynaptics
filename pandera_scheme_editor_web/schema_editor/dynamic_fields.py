"""Dynamic field rendering/parsing shared by the check-payload and
template-parameter editors.

Both editors are the same underlying problem: a small ordered list of
(field_name, kind) pairs, kind being "list" (one item per line) or "scalar"
(single value), rendered pre-filled from current values and parsed back on
submit. This module is the one place that problem is solved.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pandera_core.adapters.parsing import format_list, format_value, parse_list_text, parse_scalar
from pandera_core.domain import payload_fields
from pandera_core.domain.validation_templates import VALIDATION_TEMPLATES

FieldKind = Literal["list", "scalar"]


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """Widget metadata for one dynamically-rendered payload/parameter field."""

    name: str
    kind: FieldKind
    label: str
    initial_text: str
    css_class: str = "field-scalar"


def check_payload_field_specs(check_key: str, current_payload: dict[str, Any]) -> list[FieldSpec]:
    """Build the field specs for editing a check's current payload."""
    specs: list[FieldSpec] = []
    for name, kind in payload_fields.fields_for(check_key, current_payload):
        value = current_payload.get(name)
        initial = format_list(value) if kind == "list" else format_value(value)
        css_class = "field-mono" if check_key == "str_matches" and name == "pattern" else "field-scalar"
        specs.append(FieldSpec(name=name, kind=kind, label=name, initial_text=initial, css_class=css_class))
    return specs


def template_parameter_field_specs(template_key: str) -> list[FieldSpec]:
    """Build the field specs for a template's parameters.

    The synthetic `nullable` parameter is excluded here - it is always
    rendered as its own dedicated checkbox instead of a generic field,
    mirroring the GTK adapter's special-casing of it.
    """
    template = VALIDATION_TEMPLATES[template_key]
    specs: list[FieldSpec] = []
    for parameter in template.parameters:
        if parameter.key == "nullable":
            continue
        kind: FieldKind = "list" if parameter.value_type == "list" else "scalar"
        initial = format_list(parameter.default) if kind == "list" else format_value(parameter.default)
        specs.append(FieldSpec(name=parameter.key, kind=kind, label=parameter.label, initial_text=initial))
    return specs


def read_specs_from_post(specs: list[FieldSpec], post: Any) -> dict[str, Any]:
    """Parse each spec's field out of `post` by its exact name.

    `specs` must always be rebuilt server-side from current on-disk state
    (or from a validated template key), never trusted from the client -
    that is what stops a hand-crafted POST from injecting extra/renamed
    payload keys, since only names present in `specs` are ever read here.
    """
    values: dict[str, Any] = {}
    for spec in specs:
        text = post.get(spec.name, "")
        values[spec.name] = parse_list_text(text) if spec.kind == "list" else parse_scalar(text)
    return values
