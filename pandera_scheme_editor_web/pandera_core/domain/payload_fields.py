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
