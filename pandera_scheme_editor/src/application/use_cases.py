"""Application use cases for editing Pandera YAML contracts."""

from __future__ import annotations

from pathlib import Path

from src.domain.contract import PanderaSchemaContract
from src.ports.schema_repository import SchemaRepository


class SchemaEditorUseCases:
    """Thin application layer coordinating domain contracts and ports."""

    def __init__(self, repository: SchemaRepository) -> None:
        self._repository = repository

    def load_contract(self, path: str | Path) -> PanderaSchemaContract:
        """Load a Pandera YAML contract through the repository port."""
        return self._repository.load(path)

    def save_contract_as(self, contract: PanderaSchemaContract, target_path: str | Path) -> None:
        """Save using mandatory save-as semantics.

        The source YAML cannot be overwritten from this use case.
        """
        self._repository.save_as(contract, target_path, allow_overwrite_source=False)

    def find_checkpoint(self, path: str | Path) -> Path | None:
        """Return an existing incremental checkpoint sibling path, if any."""
        return self._repository.find_checkpoint(path)

    def save_checkpoint(self, contract: PanderaSchemaContract) -> Path:
        """Autosave an incremental checkpoint through the repository port."""
        return self._repository.save_checkpoint(contract)
