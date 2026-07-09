"""Entrypoint for the Pandera YAML GTK editor."""

from __future__ import annotations

from src.adapters.gtk_gui import run


if __name__ == "__main__":
    raise SystemExit(run())
