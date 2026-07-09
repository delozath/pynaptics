"""Pure domain model for editing a Pandera YAML schema contract.

This module intentionally does not import GTK, YAML, Pandera, pandas, or
filesystem APIs. It only manipulates plain Python data structures.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, MutableMapping


RawMapping = MutableMapping[str, Any]


@dataclass(slots=True)
class ColumnContract:
    """Editable contract for a single Pandera dataframe column.

    The column is backed by the mutable mapping extracted from the YAML
    document. Setters keep edits synchronized with that mapping so the final
    serialized YAML preserves unknown Pandera keys instead of rebuilding the
    schema from scratch.
    """

    name: str
    raw: RawMapping

    @property
    def dtype(self) -> Any:
        return self.raw.get("dtype")

    @dtype.setter
    def dtype(self, value: Any) -> None:
        self.raw["dtype"] = value

    @property
    def nullable(self) -> bool:
        return bool(self.raw.get("nullable", False))

    @nullable.setter
    def nullable(self, value: bool) -> None:
        self.raw["nullable"] = bool(value)

    @property
    def required(self) -> bool:
        return bool(self.raw.get("required", True))

    @required.setter
    def required(self, value: bool) -> None:
        self.raw["required"] = bool(value)

    @property
    def unique(self) -> bool:
        return bool(self.raw.get("unique", False))

    @unique.setter
    def unique(self, value: bool) -> None:
        self.raw["unique"] = bool(value)

    @property
    def coerce(self) -> bool:
        return bool(self.raw.get("coerce", False))

    @coerce.setter
    def coerce(self, value: bool) -> None:
        self.raw["coerce"] = bool(value)

    @property
    def regex(self) -> bool:
        return bool(self.raw.get("regex", False))

    @regex.setter
    def regex(self, value: bool) -> None:
        self.raw["regex"] = bool(value)

    @property
    def checks(self) -> RawMapping:
        """Return the checks mapping, creating it if missing or null."""
        checks = self.raw.get("checks")
        if checks is None:
            checks = {}
            self.raw["checks"] = checks
        if not isinstance(checks, MutableMapping):
            raise TypeError(f"Los checks de la columna {self.name!r} no son un dict")
        return checks

    def set_check(self, key: str, payload: RawMapping | dict[str, Any]) -> None:
        """Create or replace a check payload."""
        self.checks[key] = deepcopy(dict(payload))

    def remove_check(self, key: str) -> None:
        """Remove a check if it exists."""
        self.checks.pop(key, None)

    def clear_checks(self) -> None:
        """Remove all checks from the column."""
        self.raw["checks"] = {}


@dataclass(slots=True)
class PanderaSchemaContract:
    """Editable contract for the whole Pandera YAML schema.

    `source_path` is stored as an opaque string resolved by the persistence
    adapter. The domain layer does not inspect or access the filesystem.
    """

    raw: RawMapping
    source_path: str

    def column_names(self) -> list[str]:
        """Return column names in YAML order."""
        columns = self.raw.get("columns")
        if not isinstance(columns, MutableMapping):
            raise TypeError("El contrato no contiene un mapeo válido en 'columns'")
        return list(columns.keys())

    def get_column(self, name: str) -> ColumnContract:
        """Return a column contract by name."""
        columns = self.raw.get("columns")
        if not isinstance(columns, MutableMapping):
            raise TypeError("El contrato no contiene un mapeo válido en 'columns'")
        if name not in columns:
            raise KeyError(f"No existe la columna {name!r}")
        column_raw = columns[name]
        if not isinstance(column_raw, MutableMapping):
            raise TypeError(f"La columna {name!r} no está representada como dict")
        return ColumnContract(name=name, raw=column_raw)

    def set_global_coerce(self, value: bool) -> None:
        """Set root-level Pandera `coerce`."""
        self.raw["coerce"] = bool(value)

    def set_global_strict(self, value: bool) -> None:
        """Set root-level Pandera `strict`."""
        self.raw["strict"] = bool(value)

    def set_unique_column_names(self, value: bool) -> None:
        """Set root-level Pandera `unique_column_names`."""
        self.raw["unique_column_names"] = bool(value)

    def clone_raw(self) -> dict[str, Any]:
        """Return a deep copy suitable for serialization."""
        return deepcopy(dict(self.raw))
