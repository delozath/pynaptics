"""Column detail page: properties form + the checks panel (checks themselves
are added/edited/deleted via checks.py, but listed here)."""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from pandera_core.domain.pandera_checks import CHECK_KEYS, CHECK_TEMPLATES, relevant_check_keys_for_dtype

from ..forms import ColumnPropertiesForm
from .common import (
    base_editor_context,
    dtype_choices_for,
    get_column_or_error,
    get_use_cases,
    load_contract_or_error,
    resolve_next,
    with_friendly_errors,
    with_src,
)


@with_friendly_errors
@require_http_methods(["GET", "POST"])
def column_detail_view(request: HttpRequest, column_name: str) -> HttpResponse:
    contract, src = load_contract_or_error(request)
    column = get_column_or_error(contract, column_name)
    dtype_choices = dtype_choices_for(column.dtype)
    own_url = with_src(reverse("schema_editor:column_detail", kwargs={"column_name": column.name}), src)

    if request.method == "POST":
        form = ColumnPropertiesForm(request.POST, dtype_choices=dtype_choices)
        if form.is_valid():
            data = form.cleaned_data
            column.dtype = data["dtype"]
            column.nullable = data["nullable"]
            column.required = data["required"]
            column.unique = data["unique"]
            column.coerce = data["coerce"]
            column.regex = data["regex"]
            get_use_cases().save_checkpoint(contract)
            messages.success(request, f"Propiedades aplicadas a «{column.name}».")
            return redirect(resolve_next(request, own_url))
    else:
        form = ColumnPropertiesForm(
            initial={
                "dtype": column.dtype,
                "nullable": column.nullable,
                "required": column.required,
                "unique": column.unique,
                "coerce": column.coerce,
                "regex": column.regex,
            },
            dtype_choices=dtype_choices,
        )

    show_all_checks = request.GET.get("show_all_checks") == "1"
    offered_check_keys = list(CHECK_KEYS) if show_all_checks else relevant_check_keys_for_dtype(column.dtype)

    # Pre-zipped (key, label) pairs: Django templates can't do a variable-key
    # dict lookup (`some_dict.loop_var`) without a custom filter, so the
    # label is attached here instead of passing a separate lookup dict.
    active_checks = [(key, CHECK_TEMPLATES[key].label) for key in column.checks.keys()]
    offered_checks = [(key, CHECK_TEMPLATES[key].label) for key in offered_check_keys]

    context = base_editor_context(contract, src, selected_column=column.name)
    context.update(
        {
            "column": column,
            "form": form,
            "own_url": own_url,
            "active_checks": active_checks,
            "offered_checks": offered_checks,
            "show_all_checks": show_all_checks,
            "template_url": with_src(
                reverse("schema_editor:column_template", kwargs={"column_name": column.name}), src
            ),
        }
    )
    return render(request, "schema_editor/column_detail.html", context)
