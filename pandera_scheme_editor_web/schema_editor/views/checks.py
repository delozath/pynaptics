"""Manual check management: add/activate, edit payload, delete."""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from pandera_core.domain.pandera_checks import default_check_payload

from ..dynamic_fields import check_payload_field_specs, read_specs_from_post
from ..forms import AddCheckForm
from .common import (
    base_editor_context,
    get_column_or_error,
    get_use_cases,
    load_contract_or_error,
    resolve_next,
    with_friendly_errors,
    with_src,
)


def _column_url(column_name: str, src: str) -> str:
    return with_src(reverse("schema_editor:column_detail", kwargs={"column_name": column_name}), src)


@with_friendly_errors
@require_http_methods(["POST"])
def add_check_view(request: HttpRequest, column_name: str) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    column = get_column_or_error(contract, column_name)
    own_url = _column_url(column.name, src)

    form = AddCheckForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Selecciona un check válido.")
        return redirect(own_url)

    check_key = form.cleaned_data["check_key"]
    column.set_check(check_key, default_check_payload(check_key))
    get_use_cases().save_checkpoint(contract)
    messages.success(request, f"Check «{check_key}» agregado/activado.")

    edit_url = with_src(
        reverse(
            "schema_editor:check_payload_edit",
            kwargs={"column_name": column.name, "check_key": check_key},
        ),
        src,
    )
    return redirect(edit_url)


@with_friendly_errors
@require_http_methods(["GET", "POST"])
def check_payload_edit_view(request: HttpRequest, column_name: str, check_key: str) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    column = get_column_or_error(contract, column_name)
    own_url = _column_url(column.name, src)

    if check_key not in column.checks:
        messages.error(request, f"El check «{check_key}» ya no está activo en «{column.name}».")
        return redirect(own_url)

    payload = column.checks.get(check_key)
    if not isinstance(payload, dict):
        payload = {}
    # Rebuilt from the current on-disk payload on every request (GET or
    # POST) - never trusted from the client - so only known field names are
    # ever read back out of a POST body.
    specs = check_payload_field_specs(check_key, payload)

    if request.method == "POST":
        values = read_specs_from_post(specs, request.POST)
        column.set_check(check_key, values)
        get_use_cases().save_checkpoint(contract)
        messages.success(request, f"Check «{check_key}» aplicado.")
        return redirect(resolve_next(request, own_url))

    context = base_editor_context(contract, src, selected_column=column.name)
    context.update({"column": column, "check_key": check_key, "specs": specs, "own_url": own_url})
    return render(request, "schema_editor/check_payload_edit.html", context)


@with_friendly_errors
@require_http_methods(["POST"])
def delete_check_view(request: HttpRequest, column_name: str, check_key: str) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    column = get_column_or_error(contract, column_name)
    own_url = _column_url(column.name, src)

    column.remove_check(check_key)  # No-op if already absent: back-button-replay safe.
    get_use_cases().save_checkpoint(contract)
    messages.success(request, f"Check «{check_key}» eliminado.")
    return redirect(resolve_next(request, own_url))
