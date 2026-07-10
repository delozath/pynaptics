"""Field specs for editing check payloads.

This mirrors the field-shape knowledge that lived inline in the GTK
adapter's `_payload_field_specs` (see `pandera_scheme_editor/src/adapters/gtk_gui.py`):
a small ordered list of (field_name, kind) pairs per check key, where kind
is either "list" (edited as one item per line) or "scalar" (edited as a
single value). The GTK code nominally had a third "text" label for
`str_matches`'s `pattern` field and for free-text template parameters, but
every real code path there treats "text" identically to "scalar" (a
single-line widget parsed with `parse_scalar`) - so this module only ever
uses the two kinds that actually behave differently.
"""

from __future__ import annotations

from typing import Any

PAYLOAD_FIELDS_BY_CHECK_KEY: dict[str, list[tuple[str, str]]] = {
    "isin": [("allowed_values", "list")],
    "greater_than_or_equal_to": [("min_value", "scalar")],
    "greater_than": [("min_value", "scalar")],
    "less_than_or_equal_to": [("max_value", "scalar")],
    "less_than": [("max_value", "scalar")],
    "str_matches": [("pattern", "scalar")],
    "str_length": [("min_value", "scalar"), ("max_value", "scalar")],
}


def fields_for(check_key: str, payload: dict[str, Any]) -> list[tuple[str, str]]:
    """Return the (field_name, kind) pairs describing a check's payload.

    Unrecognized check keys fall back to inferring fields from the payload's
    own shape - "list" if the current value is a list, else "scalar" - so a
    valid but uncommon check payload is never left without editable fields.
    """
    if check_key in PAYLOAD_FIELDS_BY_CHECK_KEY:
        return list(PAYLOAD_FIELDS_BY_CHECK_KEY[check_key])
    return [
        (key, "list" if isinstance(value, list) else "scalar")
        for key, value in payload.items()
    ]


def normalize_payload(check_key: str, raw_value: Any) -> dict[str, Any]:
    """Coerce a check's raw YAML value into the named-field payload dict.

    Modern Pandera (see ``pandera.io._flat_checks`` upstream) serializes a
    check with exactly one stat - every numeric comparator, ``str_matches``,
    ``isin`` - as a bare scalar/list instead of ``{param_name: value}``, e.g.
    ``greater_than_or_equal_to: 30000.0`` instead of
    ``greater_than_or_equal_to: {min_value: 30000.0}``. Both shapes are valid
    Pandera YAML (its own loader accepts either). Without this, opening an
    existing check stored in the bare shape for editing silently showed an
    empty field instead of its real value, because the rest of this module
    assumes a dict.

    Checks with more than one named field (e.g. ``str_length``) still need a
    dict - Pandera itself never collapses those - so a non-dict value there
    is left as an empty payload, same as before this function existed.
    """
    if isinstance(raw_value, dict):
        return dict(raw_value)
    fields = PAYLOAD_FIELDS_BY_CHECK_KEY.get(check_key)
    if fields is not None and len(fields) == 1:
        (field_name, _kind) = fields[0]
        return {field_name: raw_value}
    return {}


def collapse_payload(check_key: str, payload: dict[str, Any]) -> Any:
    """Inverse of `normalize_payload`: collapse a single-field payload back
    to the bare scalar/list Pandera's modern serialization uses, so editing
    or adding a check writes the same shape Pandera itself would produce
    instead of "upgrading" it to the older, more verbose nested-dict form.

    Checks with more than one named field (e.g. ``str_length``) keep the
    named-field dict, matching Pandera's own behavior for those.
    """
    fields = PAYLOAD_FIELDS_BY_CHECK_KEY.get(check_key)
    if fields is not None and len(fields) == 1:
        (field_name, _kind) = fields[0]
        return payload.get(field_name)
    return payload
