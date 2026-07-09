"""Declarative validation template picker + apply."""

from __future__ import annotations

import json
from dataclasses import asdict

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from pandera_core.domain.validation_templates import VALIDATION_TEMPLATES, apply_template_to_column

from ..dynamic_fields import read_specs_from_post, template_parameter_field_specs
from .common import (
    base_editor_context,
    get_column_or_error,
    get_use_cases,
    load_contract_or_error,
    resolve_next,
    with_friendly_errors,
    with_src,
)

_TEMPLATE_KEYS = list(VALIDATION_TEMPLATES.keys())


def _column_url(column_name: str, src: str) -> str:
    return with_src(reverse("schema_editor:column_detail", kwargs={"column_name": column_name}), src)


@with_friendly_errors
@require_http_methods(["GET", "POST"])
def template_picker_view(request: HttpRequest, column_name: str) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    column = get_column_or_error(contract, column_name)
    own_url = with_src(reverse("schema_editor:column_template", kwargs={"column_name": column.name}), src)
    column_url = _column_url(column.name, src)

    if request.method == "POST":
        # The template key that's actually applied is the one posted here,
        # re-validated against VALIDATION_TEMPLATES - not whatever the GET
        # query param last showed - so field specs are always rebuilt from
        # a value this request itself validated.
        template_key = request.POST.get("template_key", "")
        if template_key not in VALIDATION_TEMPLATES:
            messages.error(request, "Selecciona una plantilla válida.")
            return redirect(own_url)

        specs = template_parameter_field_specs(template_key)
        values = read_specs_from_post(specs, request.POST)
        values["nullable"] = "nullable" in request.POST
        replace_existing_checks = "replace_existing_checks" in request.POST

        apply_template_to_column(column, template_key, values, replace_existing_checks=replace_existing_checks)
        get_use_cases().save_checkpoint(contract)
        template_label = VALIDATION_TEMPLATES[template_key].label
        messages.success(request, f"Plantilla «{template_label}» aplicada a «{column.name}».")
        return redirect(resolve_next(request, column_url))

    requested_key = request.GET.get("template", "")
    template_key = requested_key if requested_key in VALIDATION_TEMPLATES else _TEMPLATE_KEYS[0]
    template = VALIDATION_TEMPLATES[template_key]
    specs = template_parameter_field_specs(template_key)

    # (key, label) pairs for the <select> - Django templates can't do a
    # variable-key dict lookup, so labels travel alongside their key here.
    template_choices = [(key, VALIDATION_TEMPLATES[key].label) for key in _TEMPLATE_KEYS]

    # Data for the vanilla-JS instant template-switch preview (progressive
    # enhancement only - the server always rebuilds specs from the posted
    # template_key on submit regardless of what this displayed).
    template_data = {
        key: {
            "description": VALIDATION_TEMPLATES[key].description,
            "default_nullable": bool(VALIDATION_TEMPLATES[key].default_nullable),
            "params": [asdict(spec) for spec in template_parameter_field_specs(key)],
        }
        for key in _TEMPLATE_KEYS
    }

    context = base_editor_context(contract, src, selected_column=column.name)
    context.update(
        {
            "column": column,
            "own_url": own_url,
            "column_url": column_url,
            "template_choices": template_choices,
            "template_key": template_key,
            "template": template,
            "specs": specs,
            "default_nullable": bool(template.default_nullable),
            "template_data_json": json.dumps(template_data),
        }
    )
    return render(request, "schema_editor/template_picker.html", context)
