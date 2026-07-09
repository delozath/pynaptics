"""Global schema flags editor + save-as."""

from __future__ import annotations

from pathlib import Path

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from pandera_core.adapters.yaml_schema_repository import compute_original_path

from ..forms import GlobalsForm, SaveAsForm
from .common import (
    base_editor_context,
    get_use_cases,
    load_contract_or_error,
    resolve_next,
    with_friendly_errors,
    with_src,
)


@with_friendly_errors
@require_http_methods(["GET", "POST"])
def globals_edit_view(request: HttpRequest) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    own_url = with_src(reverse("schema_editor:globals_edit"), src)

    if request.method == "POST":
        form = GlobalsForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            contract.set_global_strict(data["strict"])
            contract.set_global_coerce(data["coerce"])
            contract.set_unique_column_names(data["unique_column_names"])
            get_use_cases().save_checkpoint(contract)
            messages.success(request, "Globales aplicados: strict, coerce y unique_column_names.")
            return redirect(resolve_next(request, own_url))
    else:
        form = GlobalsForm(
            initial={
                "strict": bool(contract.raw.get("strict", False)),
                "coerce": bool(contract.raw.get("coerce", False)),
                "unique_column_names": bool(contract.raw.get("unique_column_names", False)),
            }
        )

    context = base_editor_context(contract, src, selected_column=None)
    context.update({"form": form, "own_url": own_url})
    return render(request, "schema_editor/globals_edit.html", context)


@with_friendly_errors
@require_http_methods(["GET", "POST"])
def save_as_view(request: HttpRequest) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    own_url = with_src(reverse("schema_editor:save_as"), src)

    source_path = Path(contract.source_path)
    true_original = compute_original_path(source_path)
    protected_paths = sorted({str(source_path), str(true_original)})

    if request.method == "POST":
        form = SaveAsForm(request.POST)
        if form.is_valid():
            destination = form.cleaned_data["destination_path"]
            try:
                get_use_cases().save_contract_as(contract, destination)
            except ValueError as exc:
                # Surfaces the repository's exact overwrite-protection
                # message inline, e.g. "No se permite sobrescribir el YAML
                # original" - never a 500.
                form.add_error(None, str(exc))
            else:
                messages.success(request, f"YAML guardado como: {destination}")
                return redirect(own_url)
    else:
        form = SaveAsForm()

    context = base_editor_context(contract, src, selected_column=None)
    context.update({"form": form, "own_url": own_url, "protected_paths": protected_paths})
    return render(request, "schema_editor/save_as.html", context)
