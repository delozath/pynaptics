"""Per-column `unit`/`description` metadata tag: save and delete.

Not a Pandera-recognized column field - see `ColumnContract.metadata` for why
that's safe. Uses the same checkpoint autosave as every other mutating view.
"""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from ..forms import ColumnMetadataForm
from .common import (
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
def metadata_save_view(request: HttpRequest, column_name: str) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    column = get_column_or_error(contract, column_name)
    own_url = _column_url(column.name, src)

    form = ColumnMetadataForm(request.POST)
    if not form.is_valid():
        messages.error(request, "No se pudo guardar la metadata.")
        return redirect(own_url)

    column.set_metadata(unit=form.cleaned_data["unit"], description=form.cleaned_data["description"])
    get_use_cases().save_checkpoint(contract)
    messages.success(request, f"Metadata guardada para «{column.name}».")
    return redirect(resolve_next(request, own_url))


@with_friendly_errors
@require_http_methods(["POST"])
def metadata_delete_view(request: HttpRequest, column_name: str) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    column = get_column_or_error(contract, column_name)
    own_url = _column_url(column.name, src)

    column.clear_metadata()  # No-op if already absent: back-button-replay safe.
    get_use_cases().save_checkpoint(contract)
    messages.success(request, f"Metadata eliminada de «{column.name}».")
    return redirect(resolve_next(request, own_url))
