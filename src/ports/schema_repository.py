"""Ports for schema persistence."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from src.domain.contract import PanderaSchemaContract


class SchemaRepository(Protocol):
    """Persistence port for Pandera schema contracts."""

    def load(self, path: str | Path) -> PanderaSchemaContract:
        """Load a contract from a persistence source."""
        ...

    def save_as(
        self,
        contract: PanderaSchemaContract,
        target_path: str | Path,
        *,
        allow_overwrite_source: bool = False,
    ) -> None:
        """Persist a contract to a target path using save-as semantics."""
        ...

    def find_checkpoint(self, path: str | Path) -> Path | None:
        """Return the sibling checkpoint path for `path` if it exists on disk."""
        ...

    def save_checkpoint(self, contract: PanderaSchemaContract) -> Path:
        """Persist an incremental checkpoint next to the contract's source."""
        ...
