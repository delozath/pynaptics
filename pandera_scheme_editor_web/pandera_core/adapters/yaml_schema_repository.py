"""PyYAML adapter for Pandera schema contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from pandera_core.domain.contract import PanderaSchemaContract
from pandera_core.ports.schema_repository import SchemaRepository

_CHECKPOINT_SUFFIX = "-proc"


def _validate_root(raw: Any) -> None:
    """Validate the minimal structure expected of a parsed Pandera YAML root.

    Extracted so callers that only have an in-memory parsed dict (e.g. the
    web upload flow, which must validate before writing anything to disk)
    can reuse the exact same checks and error messages as `load()`.
    """
    if not isinstance(raw, dict):
        raise ValueError("La raíz del YAML debe ser un dict")
    if "columns" not in raw:
        raise ValueError("El YAML debe contener la clave 'columns'")
    if not isinstance(raw["columns"], dict):
        raise ValueError("La clave 'columns' debe ser un dict")


def compute_checkpoint_path(source_path: str | Path) -> Path:
    """Return the sibling checkpoint path `{stem}-proc{suffix}` for `source_path`.

    Idempotent: a stem already ending in `-proc` is returned unchanged so
    repeated checkpoint saves never chain into `-proc-proc`.
    """
    resolved = Path(source_path).expanduser().resolve()
    if resolved.stem.endswith(_CHECKPOINT_SUFFIX):
        return resolved
    return resolved.with_name(f"{resolved.stem}{_CHECKPOINT_SUFFIX}{resolved.suffix}")


def compute_original_path(path: str | Path) -> Path:
    """Return the true original path a checkpoint was derived from.

    Inverse of `compute_checkpoint_path`: strips one trailing `-proc` from the
    stem if present, else returns the resolved path unchanged.
    """
    resolved = Path(path).expanduser().resolve()
    if resolved.stem.endswith(_CHECKPOINT_SUFFIX):
        stem = resolved.stem[: -len(_CHECKPOINT_SUFFIX)]
        return resolved.with_name(f"{stem}{resolved.suffix}")
    return resolved


class YamlSchemaRepository(SchemaRepository):
    """Load and save Pandera YAML files with source-overwrite protection."""

    def load(self, path: str | Path) -> PanderaSchemaContract:
        """Load a Pandera YAML schema and validate its minimal structure."""
        resolved_path = Path(path).expanduser().resolve()
        with resolved_path.open("r", encoding="utf-8") as file:
            raw: Any = yaml.safe_load(file)

        _validate_root(raw)

        return PanderaSchemaContract(raw=raw, source_path=str(resolved_path))

    def save_as(
        self,
        contract: PanderaSchemaContract,
        target_path: str | Path,
        *,
        allow_overwrite_source: bool = False,
    ) -> None:
        """Save a contract to a new YAML path.

        Raises:
            ValueError: when `target_path` resolves to the original YAML path
                and `allow_overwrite_source` is False.
        """
        resolved_target = Path(target_path).expanduser().resolve()
        source_path = Path(contract.source_path).expanduser().resolve()
        protected_paths = {source_path, compute_original_path(source_path)}

        if resolved_target in protected_paths and not allow_overwrite_source:
            raise ValueError("No se permite sobrescribir el YAML original")

        resolved_target.parent.mkdir(parents=True, exist_ok=True)
        with resolved_target.open("w", encoding="utf-8") as file:
            yaml.safe_dump(
                contract.clone_raw(),
                file,
                sort_keys=False,
                allow_unicode=True,
            )

    def find_checkpoint(self, path: str | Path) -> Path | None:
        """Return the sibling checkpoint path for `path` if it exists on disk."""
        candidate = compute_checkpoint_path(path)
        return candidate if candidate.exists() else None

    def discard_checkpoint(self, path: str | Path) -> None:
        """Delete the sibling checkpoint for `path`, if any.

        Used when a user explicitly chooses to start over from the true
        original instead of resuming: without removing the stale checkpoint,
        `load_contract_or_error`'s checkpoint-preference (see
        `schema_editor.views.common`) would keep resurfacing the discarded
        progress on the very next navigation, silently undoing the user's
        choice. A no-op if no checkpoint exists.
        """
        candidate = compute_checkpoint_path(path)
        candidate.unlink(missing_ok=True)

    def save_checkpoint(self, contract: PanderaSchemaContract) -> Path:
        """Persist an incremental checkpoint next to the contract's source.

        Safe by construction: `compute_checkpoint_path` always differs from
        the true original's filename, so this can never overwrite it even
        though it explicitly bypasses the overwrite guard.
        """
        checkpoint_path = compute_checkpoint_path(contract.source_path)
        self.save_as(contract, checkpoint_path, allow_overwrite_source=True)
        return checkpoint_path
