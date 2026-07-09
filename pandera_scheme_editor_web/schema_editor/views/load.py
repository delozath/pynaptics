"""Load screen and checkpoint-resume confirmation.

This is the only pair of views that runs before a `?src=` exists in the
URL - every other view in the app requires it (see `common.py`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from pandera_core.adapters.yaml_schema_repository import YamlSchemaRepository

from ..forms import LoadSchemaForm
from .common import (
    WorkingFileError,
    get_use_cases,
    list_workspace_files,
    load_contract_at,
    save_uploaded_file_to_workspace,
    with_src,
)


def _resolve_candidate_path(cleaned_data: dict[str, Any], upload: Any) -> Path:
    """Resolve the chosen source path, precedence upload > path > workspace."""
    if upload is not None:
        return save_uploaded_file_to_workspace(upload)

    path_text = cleaned_data.get("path", "").strip()
    if path_text:
        return Path(path_text).expanduser()

    workspace_choice = cleaned_data.get("workspace_choice", "").strip()
    if workspace_choice:
        return Path(settings.SCHEMA_EDITOR_WORKSPACE_DIR) / workspace_choice

    # form.clean() already guarantees one of the three is present.
    raise WorkingFileError("Indica una ruta, elige un archivo del workspace o sube un archivo.")


def _entry_point_url(src: str) -> str:
    """URL for wherever editing begins for `src`: its first column, or globals."""
    contract = load_contract_at(src)
    column_names = contract.column_names()
    if column_names:
        target = reverse("schema_editor:column_detail", kwargs={"column_name": column_names[0]})
    else:
        target = reverse("schema_editor:globals_edit")
    return with_src(target, src)


def _redirect_to_entry_or_error(request: HttpRequest, src: str) -> HttpResponse:
    try:
        return redirect(_entry_point_url(src))
    except WorkingFileError as exc:
        messages.error(request, str(exc))
        return redirect("schema_editor:load")


@require_http_methods(["GET", "POST"])
def load_view(request: HttpRequest) -> HttpResponse:
    workspace_files = list_workspace_files()

    if request.method == "POST":
        form = LoadSchemaForm(request.POST, request.FILES, workspace_files=workspace_files)
        if form.is_valid():
            try:
                candidate_path = _resolve_candidate_path(form.cleaned_data, request.FILES.get("upload"))
            except WorkingFileError as exc:
                messages.error(request, str(exc))
                return render(request, "schema_editor/load.html", {"form": form})

            checkpoint = YamlSchemaRepository().find_checkpoint(candidate_path)
            if checkpoint is not None:
                return redirect(with_src(reverse("schema_editor:resume"), str(candidate_path)))
            return _redirect_to_entry_or_error(request, str(candidate_path))
    else:
        form = LoadSchemaForm(workspace_files=workspace_files)

    return render(request, "schema_editor/load.html", {"form": form})


@require_http_methods(["GET"])
def resume_confirm_view(request: HttpRequest) -> HttpResponse:
    original = request.GET.get("src", "").strip()
    if not original:
        messages.error(request, "No hay un archivo para reanudar.")
        return redirect("schema_editor:load")

    checkpoint = YamlSchemaRepository().find_checkpoint(original)
    if checkpoint is None:
        # Defensive: the checkpoint existed when load_view redirected here
        # but has since vanished (e.g. deleted concurrently) - fall through
        # to the original instead of showing a resume prompt with nothing
        # to resume from.
        return _redirect_to_entry_or_error(request, original)

    try:
        yes_url = _entry_point_url(str(checkpoint))
    except WorkingFileError as exc:
        messages.error(request, str(exc))
        return redirect("schema_editor:load")

    return render(
        request,
        "schema_editor/resume_confirm.html",
        {
            "original": original,
            "checkpoint_name": checkpoint.name,
            "yes_url": yes_url,
            "discard_url": with_src(reverse("schema_editor:resume_discard"), original),
        },
    )


@require_http_methods(["POST"])
def discard_checkpoint_view(request: HttpRequest) -> HttpResponse:
    """Delete the checkpoint for `?src=` and enter the editor at the true original.

    This is the "No, partir del original" action from the resume-confirm
    screen. It must actually delete the checkpoint file (rather than just
    redirecting to the original path) - otherwise `load_contract_or_error`'s
    checkpoint-preference would resurface the discarded progress as soon as
    the user navigates to a second column, silently overriding this choice.
    """
    original = request.GET.get("src", "").strip()
    if not original:
        messages.error(request, "No hay un archivo para reanudar.")
        return redirect("schema_editor:load")

    get_use_cases().discard_checkpoint(original)
    messages.success(request, "Progreso guardado descartado; se partió del YAML original.")
    return _redirect_to_entry_or_error(request, original)
