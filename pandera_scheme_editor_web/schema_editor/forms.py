"""Plain Django forms for the schema editor screens.

There are no Django models in this project (everything lives in YAML files
on disk), so every form here is a plain `forms.Form`, not a `ModelForm`.
"""

from __future__ import annotations

from typing import Any

from django import forms

from pandera_core.domain.pandera_checks import CHECK_KEYS


class FlexibleChoiceField(forms.ChoiceField):
    """A ChoiceField whose dropdown is a UI convenience, not a hard constraint.

    Mirrors the GTK adapter's `_set_combo_value`, which appends and selects
    an out-of-list value onto the combo box instead of rejecting it - a
    Pandera YAML can legitimately contain a dtype string that isn't in our
    curated `PANDERA_DTYPES` list, and editing such a column must not be
    blocked. A normal user only ever picks a rendered `<option>`; this only
    matters for a hand-crafted POST, which is consistent with this app's
    established no-sandbox, single-operator trust model (see the load-path
    and save-as fields below, which are equally permissive about paths).
    """

    def valid_value(self, value: Any) -> bool:
        return True


class LoadSchemaForm(forms.Form):
    """The load screen: a server-side path, a workspace dropdown, or an upload.

    Precedence when more than one is filled in is upload > path > workspace
    choice. `clean()` only enforces "at least one was given" - resolving
    which path to actually load (including saving an upload into the
    workspace directory) is the view's job, since it requires filesystem
    access this form does not perform itself.
    """

    path = forms.CharField(label="Ruta del archivo", required=False)
    workspace_choice = forms.ChoiceField(label="Archivos en el workspace", required=False, choices=())
    upload = forms.FileField(label="Subir archivo YAML", required=False)

    def __init__(self, *args: Any, workspace_files: list[str] = (), **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["workspace_choice"].choices = [("", "(ninguno)")] + [
            (name, name) for name in workspace_files
        ]

    def clean(self) -> dict[str, Any]:
        cleaned = super().clean()
        if not cleaned.get("upload") and not cleaned.get("path") and not cleaned.get("workspace_choice"):
            raise forms.ValidationError(
                "Indica una ruta, elige un archivo del workspace o sube un archivo."
            )
        return cleaned


class ColumnPropertiesForm(forms.Form):
    """Editable properties for a single column."""

    dtype = FlexibleChoiceField(label="dtype", choices=())
    nullable = forms.BooleanField(label="nullable", required=False)
    required = forms.BooleanField(label="required", required=False)
    unique = forms.BooleanField(label="unique", required=False)
    coerce = forms.BooleanField(label="coerce", required=False)
    regex = forms.BooleanField(label="regex", required=False)

    def __init__(self, *args: Any, dtype_choices: list[str] = (), **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["dtype"].choices = [(value, value) for value in dtype_choices]


class AddCheckForm(forms.Form):
    """Choose a check key to add/activate on the current column.

    Validated against the *full* `CHECK_KEYS` regardless of whichever
    dtype-filtered subset is currently displayed - filtering which checks
    are *offered* is a display convenience only (see
    `pandera_core.domain.pandera_checks.relevant_check_keys_for_dtype`); it
    must never block a check that simply isn't in that subset.
    """

    check_key = forms.ChoiceField(label="Check", choices=[(key, key) for key in CHECK_KEYS])


class GlobalsForm(forms.Form):
    """Root-level Pandera schema flags."""

    strict = forms.BooleanField(label="strict", required=False)
    coerce = forms.BooleanField(label="coerce", required=False)
    unique_column_names = forms.BooleanField(label="unique_column_names", required=False)


class ColumnMetadataForm(forms.Form):
    """Free-form `unit`/`description` tag for a column.

    Both fields are optional: an empty submission is a valid way to clear a
    field's value without removing the whole metadata tag (use the separate
    delete action for that).
    """

    unit = forms.CharField(label="Unidad de medición", required=False, max_length=120)
    description = forms.CharField(
        label="Descripción", required=False, widget=forms.Textarea(attrs={"rows": 4})
    )


class SaveAsForm(forms.Form):
    """Destination path for a save-as operation."""

    destination_path = forms.CharField(label="Guardar como")

    def clean_destination_path(self) -> str:
        value: str = self.cleaned_data["destination_path"].strip()
        if not value:
            raise forms.ValidationError("Indica una ruta de destino.")
        return value
