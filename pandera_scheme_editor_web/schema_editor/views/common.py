"""Shared helpers used by every view in the schema editor app.

The single most important piece here is `with_friendly_errors` +
`load_contract_or_error`: unlike the GTK app (one long-lived in-memory
contract per process), every Django view independently reloads the
contract from disk on every request, since the working path travels as a
`?src=` query parameter rather than server-side session state (see
`schema_editor.context_processors.working_src` for why). That means many
more call sites than the GTK app ever had can hit a missing/renamed/
malformed file, so this module exists to make that a friendly redirect
everywhere, in one place, rather than an occasional 500.
"""

from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode

import yaml
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme

from pandera_core.adapters.yaml_schema_repository import YamlSchemaRepository, _validate_root
from pandera_core.application.use_cases import SchemaEditorUseCases
from pandera_core.domain.contract import ColumnContract, PanderaSchemaContract
from pandera_core.domain.pandera_checks import PANDERA_DTYPES


class WorkingFileError(Exception):
    """Raised when the working file/column/check cannot be resolved.

    Carries a user-facing Spanish message; always caught by
    `with_friendly_errors` and turned into a flashed message + redirect,
    never a 500.
    """


def get_use_cases() -> SchemaEditorUseCases:
    return SchemaEditorUseCases(YamlSchemaRepository())


def with_friendly_errors(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
    """Catch `WorkingFileError` anywhere in a view and redirect to the loader."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            return view_func(request, *args, **kwargs)
        except WorkingFileError as exc:
            messages.error(request, str(exc))
            return redirect("schema_editor:load")

    return wrapper


def load_contract_at(src: str) -> PanderaSchemaContract:
    """Load a contract from an already-resolved path string.

    Raises `WorkingFileError` (never a raw filesystem/YAML exception) if
    `src` does not point at a real file or does not parse as a valid
    Pandera schema YAML. Used both by `load_contract_or_error` below (the
    `?src=`-from-request case) and by the load screen, which must load a
    just-resolved candidate path before `?src=` even exists in the URL.
    """
    path = Path(src).expanduser()
    if not path.is_file():
        raise WorkingFileError(f"No se encontró el archivo: {src}")

    try:
        return get_use_cases().load_contract(path)
    except (ValueError, OSError) as exc:
        raise WorkingFileError(f"No se pudo cargar el YAML: {exc}") from exc


def load_contract_or_error(request: HttpRequest) -> tuple[PanderaSchemaContract, str]:
    """Resolve `?src=`, load it, and return `(contract, src)`.

    `src` itself is returned unchanged (so links/headers keep showing the
    original path), but if a checkpoint already exists for it, the contract
    is loaded from the checkpoint instead of the pristine original. Every
    editor view (columns, checks, templates, globals, save-as) reaches the
    working contract through this function and `src` never gets rewritten
    to the checkpoint path during normal navigation, so without this, each
    request would reload the untouched original and each mutation's
    checkpoint save would clobber every earlier edit from the same
    session with only its own single change.

    The explicit resume-or-not choice on the "Progreso encontrado" screen
    (`load.py`) intentionally bypasses this by calling `load_contract_at`
    directly, so a user who picks "No, partir del original" there still
    gets the true original, not this auto-preference.

    Raises `WorkingFileError` (never a raw filesystem/YAML exception) if
    `src` is missing, does not point at a real file, or does not parse as a
    valid Pandera schema YAML.
    """
    src = request.GET.get("src", "").strip()
    if not src:
        raise WorkingFileError("No hay un archivo cargado. Carga un YAML para comenzar.")

    checkpoint = YamlSchemaRepository().find_checkpoint(src)
    load_path = str(checkpoint) if checkpoint is not None else src
    return load_contract_at(load_path), src


def get_column_or_error(contract: PanderaSchemaContract, column_name: str) -> ColumnContract:
    """Fetch a column, turning a bad/missing name into a `WorkingFileError`.

    The original GTK code never guarded `get_column`'s `KeyError`/`TypeError`
    at all; every Django view goes through this instead, so a stale link to
    a renamed/removed column is a friendly redirect, not a crash.
    """
    try:
        return contract.get_column(column_name)
    except (KeyError, TypeError) as exc:
        raise WorkingFileError(f"No se pudo acceder a la columna «{column_name}»: {exc}") from exc


def base_editor_context(
    contract: PanderaSchemaContract, src: str, *, selected_column: str | None = None
) -> dict[str, Any]:
    """Context shared by every editor page: sidebar data + checkpoint status.

    The checkpoint's existence is recomputed fresh on every request (rather
    than tracked as state) since every mutating view already calls
    `save_checkpoint` immediately, so "does a checkpoint exist for this src"
    is always cheaply answerable straight from disk.
    """
    checkpoint = YamlSchemaRepository().find_checkpoint(src)
    return {
        "contract": contract,
        "src": src,
        "selected_column": selected_column,
        "checkpoint_path": str(checkpoint) if checkpoint is not None else None,
    }


def dtype_choices_for(current_value: Any) -> list[str]:
    """`PANDERA_DTYPES` plus the current value if it isn't already listed.

    Mirrors the GTK adapter's `_set_combo_value`: the canonical dtype list
    is a UI convenience, not a hard constraint, so a schema authored outside
    this tool can never have its dtype silently dropped from the dropdown.
    """
    choices = list(PANDERA_DTYPES)
    if current_value is not None and str(current_value) not in choices:
        choices.append(str(current_value))
    return choices


def resolve_next(request: HttpRequest, fallback_url: str) -> str:
    """Return a safe post-mutation redirect target.

    `next` is only ever honored if it passes Django's own open-redirect
    check; otherwise (missing, blank, or pointing off-site) the caller's
    own canonical URL is used instead.
    """
    candidate = request.POST.get("next") or request.GET.get("next")
    if candidate and url_has_allowed_host_and_scheme(
        candidate, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return candidate
    return fallback_url


def with_src(url: str, src: str, **extra_params: str) -> str:
    """Append `?src=...` (plus any extra query params) onto a URL."""
    params = {"src": src, **extra_params}
    return f"{url}?{urlencode(params)}"


def list_workspace_files() -> list[str]:
    """List `*.yaml`/`*.yml` file names directly under the workspace dir."""
    workspace = Path(settings.SCHEMA_EDITOR_WORKSPACE_DIR)
    if not workspace.is_dir():
        return []
    names = {entry.name for entry in workspace.glob("*.yaml") if entry.is_file()}
    names.update(entry.name for entry in workspace.glob("*.yml") if entry.is_file())
    return sorted(names)


def save_uploaded_file_to_workspace(uploaded) -> Path:
    """Validate and save an uploaded YAML file into the workspace dir.

    Never silently overwrites a same-name file, strips any directory
    components from the uploaded name (so a crafted `"../../evil.yaml"`
    filename cannot escape the workspace directory), and validates the
    content as a minimally-structured Pandera schema *before* writing
    anything to disk, reusing `_validate_root` so the accepted structure
    and error messages exactly match `YamlSchemaRepository.load`.
    """
    workspace = Path(settings.SCHEMA_EDITOR_WORKSPACE_DIR)
    workspace.mkdir(parents=True, exist_ok=True)

    filename = Path(uploaded.name).name
    if not filename:
        raise WorkingFileError("El archivo subido no tiene un nombre válido.")

    target = workspace / filename
    if target.exists():
        raise WorkingFileError(
            f"Ya existe un archivo llamado «{filename}» en el workspace. "
            "Renómbralo antes de subirlo, o cárgalo directamente desde el workspace."
        )

    raw_bytes = uploaded.read()
    try:
        parsed = yaml.safe_load(raw_bytes)
        _validate_root(parsed)
    except yaml.YAMLError as exc:
        raise WorkingFileError(f"El archivo subido no es un YAML válido: {exc}") from exc
    except ValueError as exc:
        raise WorkingFileError(f"El archivo subido no tiene la estructura esperada: {exc}") from exc

    with target.open("wb") as file:
        file.write(raw_bytes)
    return target
