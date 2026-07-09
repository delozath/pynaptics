"""GTK 4 adapter for editing Pandera YAML contracts.

The GUI delegates persistence to application use cases and delegates column
mutations to the domain objects. It contains only presentation glue and parsing
helpers for user-entered check/template values.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk  # noqa: E402

from src.application.use_cases import SchemaEditorUseCases
from src.adapters.yaml_schema_repository import YamlSchemaRepository
from src.domain.contract import ColumnContract, PanderaSchemaContract
from src.domain.pandera_checks import (
    CHECK_KEYS,
    PANDERA_DTYPES,
    default_check_payload,
    relevant_check_keys_for_dtype,
)
from src.adapters.parsing import format_list, format_value, parse_list_text, parse_scalar
from src.domain.validation_templates import (
    VALIDATION_TEMPLATES,
    TemplateParameter,
    ValidationTemplate,
    apply_template_to_column,
)


@dataclass(slots=True)
class PayloadEditorField:
    """Widget metadata for one editable payload field."""

    key: str
    widget: Gtk.Widget
    value_type: str



class PanderaYamlEditorWindow(Gtk.ApplicationWindow):
    """Main GTK window for editing a loaded Pandera YAML contract."""

    def __init__(self, app: Gtk.Application, use_cases: SchemaEditorUseCases) -> None:
        super().__init__(application=app, title="Pandera YAML GTK Editor")
        self.use_cases = use_cases
        self.contract: PanderaSchemaContract | None = None
        self.current_column_name: str | None = None
        self.current_check_key: str | None = None
        self.check_payload_fields: dict[str, PayloadEditorField] = {}
        self.template_parameter_fields: dict[str, PayloadEditorField] = {}
        self._dtype_choices: list[str] = list(PANDERA_DTYPES)

        self.set_default_size(1200, 820)
        self._build_ui()

    def _build_ui(self) -> None:
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        root.set_margin_top(10)
        root.set_margin_bottom(10)
        root.set_margin_start(10)
        root.set_margin_end(10)
        self.set_child(root)

        root.append(self._build_header())

        self.checkpoint_status_label = Gtk.Label(label="Sin progreso guardado")
        self.checkpoint_status_label.set_xalign(0)
        root.append(self.checkpoint_status_label)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(320)
        paned.set_resize_start_child(False)
        paned.set_shrink_start_child(False)
        paned.set_resize_end_child(True)
        root.append(paned)

        self.column_list = Gtk.ListBox()
        self.column_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.column_list.connect("row-selected", self._on_column_selected)
        left_scroll = Gtk.ScrolledWindow()
        left_scroll.set_min_content_width(260)
        left_scroll.set_child(self.column_list)
        paned.set_start_child(left_scroll)

        right_scroll = Gtk.ScrolledWindow()
        right_scroll.set_vexpand(True)
        self.editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.editor_box.set_margin_start(10)
        right_scroll.set_child(self.editor_box)
        paned.set_end_child(right_scroll)

        self.editor_box.append(self._build_column_properties_editor())
        self.editor_box.append(self._build_manual_checks_editor())
        self.editor_box.append(self._build_template_editor())
        self.editor_box.append(self._build_globals_editor())

        self._set_editor_enabled(False)

    def _build_header(self) -> Gtk.Widget:
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        load_button = Gtk.Button(label="Cargar YAML inferido")
        load_button.connect("clicked", self._on_load_clicked)
        header.append(load_button)

        self.save_button = Gtk.Button(label="Guardar como YAML editado")
        self.save_button.connect("clicked", self._on_save_clicked)
        self.save_button.set_sensitive(False)
        header.append(self.save_button)

        self.source_label = Gtk.Label(label="Sin YAML cargado")
        self.source_label.set_xalign(0)
        self.source_label.set_hexpand(True)
        header.append(self.source_label)
        return header

    def _build_section(self, title: str) -> Gtk.Box:
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.add_css_class("card")
        section.set_margin_bottom(4)
        label = Gtk.Label(label=f"<b>{title}</b>")
        label.set_use_markup(True)
        label.set_xalign(0)
        section.append(label)
        return section

    def _build_column_properties_editor(self) -> Gtk.Widget:
        section = self._build_section("Propiedades de columna")
        grid = Gtk.Grid(column_spacing=10, row_spacing=8)
        section.append(grid)

        self.column_name_entry = Gtk.Entry()
        self.column_name_entry.set_editable(False)
        self.column_name_entry.set_hexpand(True)
        self._add_labeled(grid, 0, "Nombre", self.column_name_entry)

        self.dtype_combo = self._combo(self._dtype_choices)
        self.dtype_combo.set_hexpand(True)
        self.dtype_combo.connect("changed", self._on_dtype_combo_changed)
        self._add_labeled(grid, 1, "dtype", self.dtype_combo)

        self.nullable_check = Gtk.CheckButton(label="nullable")
        self.required_check = Gtk.CheckButton(label="required")
        self.unique_check = Gtk.CheckButton(label="unique")
        self.coerce_check = Gtk.CheckButton(label="coerce")
        self.regex_check = Gtk.CheckButton(label="regex")
        checks_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        for widget in (
            self.nullable_check,
            self.required_check,
            self.unique_check,
            self.coerce_check,
            self.regex_check,
        ):
            checks_box.append(widget)
        grid.attach(checks_box, 1, 2, 1, 1)

        apply_button = Gtk.Button(label="Aplicar propiedades")
        apply_button.connect("clicked", self._on_apply_column_properties)
        section.append(apply_button)
        return section

    def _build_manual_checks_editor(self) -> Gtk.Widget:
        section = self._build_section("Checks manuales")

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.check_combo = self._combo(CHECK_KEYS)
        row.append(self.check_combo)
        self.show_all_checks_toggle = Gtk.CheckButton(label="Mostrar todos los checks")
        self.show_all_checks_toggle.connect("toggled", self._on_show_all_checks_toggled)
        row.append(self.show_all_checks_toggle)
        add_button = Gtk.Button(label="Agregar/activar check")
        add_button.connect("clicked", self._on_add_check)
        row.append(add_button)
        section.append(row)

        split = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        split.set_position(280)
        split.set_resize_start_child(False)
        split.set_shrink_start_child(False)
        split.set_resize_end_child(True)
        section.append(split)

        self.active_checks_list = Gtk.ListBox()
        self.active_checks_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.active_checks_list.connect("row-selected", self._on_active_check_selected)
        checks_scroll = Gtk.ScrolledWindow()
        checks_scroll.set_min_content_width(260)
        checks_scroll.set_min_content_height(140)
        checks_scroll.set_child(self.active_checks_list)
        split.set_start_child(checks_scroll)

        payload_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.payload_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        payload_container.append(self.payload_box)

        payload_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        apply_payload_button = Gtk.Button(label="Aplicar check editado")
        apply_payload_button.connect("clicked", self._on_apply_check_payload)
        delete_button = Gtk.Button(label="Eliminar check seleccionado")
        delete_button.connect("clicked", self._on_delete_check)
        payload_actions.append(apply_payload_button)
        payload_actions.append(delete_button)
        payload_container.append(payload_actions)
        split.set_end_child(payload_container)
        return section

    def _build_template_editor(self) -> Gtk.Widget:
        section = self._build_section("Plantillas predefinidas")

        self.template_keys = list(VALIDATION_TEMPLATES.keys())
        template_labels = [VALIDATION_TEMPLATES[key].label for key in self.template_keys]
        self.template_combo = self._combo(template_labels)
        self.template_combo.connect("changed", self._on_template_changed)
        section.append(self.template_combo)

        self.template_description = Gtk.Label(label="")
        self.template_description.set_xalign(0)
        self.template_description.set_wrap(True)
        section.append(self.template_description)

        self.template_params_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        section.append(self.template_params_box)

        self.template_nullable_check = Gtk.CheckButton(label="nullable")
        self.template_replace_checks = Gtk.CheckButton(label="Reemplazar checks existentes")
        flags = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        flags.append(self.template_nullable_check)
        flags.append(self.template_replace_checks)
        section.append(flags)

        apply_template_button = Gtk.Button(label="Aplicar plantilla a columna")
        apply_template_button.connect("clicked", self._on_apply_template)
        section.append(apply_template_button)
        self._refresh_template_editor()
        return section

    def _build_globals_editor(self) -> Gtk.Widget:
        section = self._build_section("Propiedades globales")
        flags = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.global_strict_check = Gtk.CheckButton(label="strict")
        self.global_coerce_check = Gtk.CheckButton(label="coerce")
        self.global_unique_names_check = Gtk.CheckButton(label="unique_column_names")
        for widget in (self.global_strict_check, self.global_coerce_check, self.global_unique_names_check):
            flags.append(widget)
        section.append(flags)

        apply_button = Gtk.Button(label="Aplicar globales")
        apply_button.connect("clicked", self._on_apply_globals)
        section.append(apply_button)
        return section

    def _add_labeled(self, grid: Gtk.Grid, row: int, label_text: str, widget: Gtk.Widget) -> None:
        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        grid.attach(label, 0, row, 1, 1)
        grid.attach(widget, 1, row, 1, 1)

    def _combo(self, values: list[str]) -> Gtk.ComboBoxText:
        combo = Gtk.ComboBoxText()
        for value in values:
            combo.append_text(value)
        if values:
            combo.set_active(0)
        return combo

    def _set_combo_value(self, combo: Gtk.ComboBoxText, value: Any, candidates: list[str]) -> None:
        text = "" if value is None else str(value)
        if text not in candidates:
            combo.append_text(text)
            candidates.append(text)
        combo.set_active(candidates.index(text))

    def _clear_box(self, box: Gtk.Box) -> None:
        child = box.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            box.remove(child)
            child = next_child

    def _set_editor_enabled(self, enabled: bool) -> None:
        self.save_button.set_sensitive(enabled)
        self.editor_box.set_sensitive(enabled)

    def _current_column(self) -> ColumnContract | None:
        if self.contract is None or self.current_column_name is None:
            return None
        return self.contract.get_column(self.current_column_name)

    def _on_load_clicked(self, _button: Gtk.Button) -> None:
        self._open_file_dialog()

    def _on_save_clicked(self, _button: Gtk.Button) -> None:
        if self.contract is None:
            self._show_message("No hay YAML cargado", "Primero carga un YAML inferido.", is_error=True)
            return
        self._save_file_dialog()

    def _open_file_dialog(self) -> None:
        if hasattr(Gtk, "FileDialog"):
            dialog = Gtk.FileDialog(title="Cargar YAML inferido")
            dialog.open(self, None, self._on_open_dialog_done)
            return

        dialog = Gtk.FileChooserNative(
            title="Cargar YAML inferido",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="Cargar",
            cancel_label="Cancelar",
        )
        dialog.connect("response", self._on_open_native_response)
        dialog.show()

    def _save_file_dialog(self) -> None:
        if hasattr(Gtk, "FileDialog"):
            dialog = Gtk.FileDialog(title="Guardar como YAML editado")
            dialog.save(self, None, self._on_save_dialog_done)
            return

        dialog = Gtk.FileChooserNative(
            title="Guardar como YAML editado",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="Guardar como",
            cancel_label="Cancelar",
        )
        dialog.connect("response", self._on_save_native_response)
        dialog.show()

    def _on_open_dialog_done(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            file = dialog.open_finish(result)
            path = file.get_path()
            if path:
                self._load_contract(path)
        except Exception as exc:  # noqa: BLE001 - GUI boundary should surface errors
            self._show_message("No se pudo cargar", str(exc), is_error=True)

    def _on_save_dialog_done(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            file = dialog.save_finish(result)
            path = file.get_path()
            if path:
                self._save_contract(path)
        except Exception as exc:  # noqa: BLE001
            self._show_message("No se pudo guardar", str(exc), is_error=True)

    def _on_open_native_response(self, dialog: Gtk.FileChooserNative, response: int) -> None:
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            path = file.get_path() if file else None
            if path:
                self._load_contract(path)
        dialog.destroy()

    def _on_save_native_response(self, dialog: Gtk.FileChooserNative, response: int) -> None:
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            path = file.get_path() if file else None
            if path:
                self._save_contract(path)
        dialog.destroy()

    def _load_contract(self, path: str) -> None:
        try:
            checkpoint_path = self.use_cases.find_checkpoint(path)
        except Exception as exc:  # noqa: BLE001
            self._show_message("No se pudo verificar progreso guardado", str(exc), is_error=True)
            checkpoint_path = None
        if checkpoint_path is not None:
            self._confirm_resume_from_checkpoint(path, checkpoint_path)
        else:
            self._finish_load_contract(path)

    def _confirm_resume_from_checkpoint(self, original_path: str, checkpoint_path: Path) -> None:
        question = f"¿Continuar desde el progreso guardado en {checkpoint_path.name}?"
        if hasattr(Gtk, "AlertDialog"):
            dialog = Gtk.AlertDialog(message="Progreso encontrado", detail=question)
            dialog.set_buttons(["No", "Sí"])
            dialog.set_default_button(1)
            dialog.set_cancel_button(0)
            dialog.choose(
                self,
                None,
                lambda d, r: self._on_resume_choice_done(d, r, original_path, checkpoint_path),
            )
            return

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Progreso encontrado",
        )
        dialog.format_secondary_text(question)
        dialog.connect(
            "response",
            lambda d, response: self._on_resume_dialog_response(d, response, original_path, checkpoint_path),
        )
        dialog.show()

    def _on_resume_choice_done(
        self, dialog: Gtk.AlertDialog, result: Gio.AsyncResult, original_path: str, checkpoint_path: Path
    ) -> None:
        try:
            index = dialog.choose_finish(result)
        except Exception:  # noqa: BLE001
            index = 0
        self._finish_load_contract(str(checkpoint_path) if index == 1 else original_path)

    def _on_resume_dialog_response(
        self, dialog: Gtk.MessageDialog, response: int, original_path: str, checkpoint_path: Path
    ) -> None:
        dialog.destroy()
        chosen = str(checkpoint_path) if response == Gtk.ResponseType.YES else original_path
        self._finish_load_contract(chosen)

    def _finish_load_contract(self, path: str) -> None:
        try:
            self.contract = self.use_cases.load_contract(path)
            self.source_label.set_text(f"Origen: {self.contract.source_path}")
            self._refresh_column_list()
            self._refresh_globals()
            self._set_editor_enabled(True)
            self._set_checkpoint_status("Sin progreso guardado")
            self._show_message("YAML cargado", "El esquema fue cargado correctamente.")
        except Exception as exc:  # noqa: BLE001
            self._show_message("No se pudo cargar", str(exc), is_error=True)

    def _autosave_checkpoint(self) -> None:
        if self.contract is None:
            return
        try:
            checkpoint_path = self.use_cases.save_checkpoint(self.contract)
            self._set_checkpoint_status(f"Progreso guardado en: {checkpoint_path}")
        except Exception as exc:  # noqa: BLE001
            self._set_checkpoint_status(f"No se pudo guardar el progreso: {exc}")

    def _set_checkpoint_status(self, text: str) -> None:
        self.checkpoint_status_label.set_text(text)

    def _save_contract(self, path: str) -> None:
        if self.contract is None:
            return
        try:
            self.use_cases.save_contract_as(self.contract, path)
            self._show_message("YAML guardado", f"Guardado como: {path}")
        except Exception as exc:  # noqa: BLE001
            self._show_message("No se pudo guardar", str(exc), is_error=True)

    def _refresh_column_list(self) -> None:
        self._clear_listbox(self.column_list)
        if self.contract is None:
            return
        for column_name in self.contract.column_names():
            row = Gtk.ListBoxRow()
            row.column_name = column_name  # type: ignore[attr-defined]
            label = Gtk.Label(label=column_name)
            label.set_xalign(0)
            label.set_margin_top(6)
            label.set_margin_bottom(6)
            label.set_margin_start(6)
            label.set_margin_end(6)
            row.set_child(label)
            self.column_list.append(row)
        first = self.column_list.get_row_at_index(0)
        if first is not None:
            self.column_list.select_row(first)

    def _clear_listbox(self, listbox: Gtk.ListBox) -> None:
        child = listbox.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            listbox.remove(child)
            child = next_child

    def _on_column_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if row is None:
            return
        self.current_column_name = getattr(row, "column_name", None)
        self.current_check_key = None
        self._refresh_column_editor()

    def _refresh_column_editor(self) -> None:
        column = self._current_column()
        if column is None:
            return
        self.column_name_entry.set_text(column.name)
        self._set_combo_value(self.dtype_combo, column.dtype, self._dtype_choices)
        self.nullable_check.set_active(column.nullable)
        self.required_check.set_active(column.required)
        self.unique_check.set_active(column.unique)
        self.coerce_check.set_active(column.coerce)
        self.regex_check.set_active(column.regex)
        self._refresh_active_checks()
        self._repopulate_check_combo()

    def _on_apply_column_properties(self, _button: Gtk.Button) -> None:
        column = self._current_column()
        if column is None:
            return
        dtype = self.dtype_combo.get_active_text()
        if dtype is not None:
            column.dtype = dtype
        column.nullable = self.nullable_check.get_active()
        column.required = self.required_check.get_active()
        column.unique = self.unique_check.get_active()
        column.coerce = self.coerce_check.get_active()
        column.regex = self.regex_check.get_active()
        self._show_message("Propiedades aplicadas", f"Columna: {column.name}")
        self._autosave_checkpoint()

    def _refresh_active_checks(self) -> None:
        self._clear_listbox(self.active_checks_list)
        self._clear_box(self.payload_box)
        self.check_payload_fields.clear()
        column = self._current_column()
        if column is None:
            return
        for check_key in column.checks.keys():
            row = Gtk.ListBoxRow()
            row.check_key = check_key  # type: ignore[attr-defined]
            label = Gtk.Label(label=check_key)
            label.set_xalign(0)
            label.set_margin_top(6)
            label.set_margin_bottom(6)
            label.set_margin_start(6)
            label.set_margin_end(6)
            row.set_child(label)
            self.active_checks_list.append(row)

    def _repopulate_check_combo(self) -> None:
        """Refresh the 'add check' dropdown to fit the current dtype.

        Checks already active on the column are never affected here — only
        the list of checks offered to *add* is filtered.
        """
        if self.show_all_checks_toggle.get_active():
            keys = list(CHECK_KEYS)
        else:
            keys = relevant_check_keys_for_dtype(self.dtype_combo.get_active_text())
        previous = self.check_combo.get_active_text()
        self.check_combo.remove_all()
        for key in keys:
            self.check_combo.append_text(key)
        if previous in keys:
            self.check_combo.set_active(keys.index(previous))
        elif keys:
            self.check_combo.set_active(0)

    def _on_dtype_combo_changed(self, _combo: Gtk.ComboBoxText) -> None:
        self._repopulate_check_combo()

    def _on_show_all_checks_toggled(self, _button: Gtk.CheckButton) -> None:
        self._repopulate_check_combo()

    def _on_add_check(self, _button: Gtk.Button) -> None:
        column = self._current_column()
        if column is None:
            return
        check_key = self.check_combo.get_active_text()
        if check_key is None:
            return
        column.set_check(check_key, default_check_payload(check_key))
        self._refresh_active_checks()
        self._select_check(check_key)
        self._autosave_checkpoint()

    def _select_check(self, check_key: str) -> None:
        index = 0
        child = self.active_checks_list.get_first_child()
        while child is not None:
            if isinstance(child, Gtk.ListBoxRow) and getattr(child, "check_key", None) == check_key:
                self.active_checks_list.select_row(child)
                return
            index += 1
            child = child.get_next_sibling()

    def _on_active_check_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        self.current_check_key = getattr(row, "check_key", None) if row else None
        self._refresh_check_payload_editor()

    def _refresh_check_payload_editor(self) -> None:
        self._clear_box(self.payload_box)
        self.check_payload_fields.clear()
        column = self._current_column()
        if column is None or self.current_check_key is None:
            return
        payload = column.checks.get(self.current_check_key, {})
        if not isinstance(payload, dict):
            payload = {}

        fields = self._payload_field_specs(self.current_check_key, payload)
        for key, value_type in fields:
            value = payload.get(key)
            self._append_payload_field(self.payload_box, self.check_payload_fields, key, value, value_type)

    def _payload_field_specs(self, check_key: str, payload: dict[str, Any]) -> list[tuple[str, str]]:
        known: dict[str, list[tuple[str, str]]] = {
            "isin": [("allowed_values", "list")],
            "greater_than_or_equal_to": [("min_value", "scalar")],
            "greater_than": [("min_value", "scalar")],
            "less_than_or_equal_to": [("max_value", "scalar")],
            "less_than": [("max_value", "scalar")],
            "str_matches": [("pattern", "text")],
            "str_length": [("min_value", "scalar"), ("max_value", "scalar")],
        }
        if check_key in known:
            return known[check_key]
        return [(key, "list" if isinstance(value, list) else "scalar") for key, value in payload.items()]

    def _append_payload_field(
        self,
        target_box: Gtk.Box,
        registry: dict[str, PayloadEditorField],
        key: str,
        value: Any,
        value_type: str,
    ) -> None:
        row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        label = Gtk.Label(label=key)
        label.set_xalign(0)
        row.append(label)

        if value_type == "list":
            widget = Gtk.TextView()
            widget.set_monospace(True)
            widget.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            widget.set_size_request(-1, 80)
            widget.get_buffer().set_text(format_list(value))
            row.append(widget)
        else:
            widget = Gtk.Entry()
            widget.set_text(format_value(value))
            row.append(widget)

        registry[key] = PayloadEditorField(key=key, widget=widget, value_type=value_type)
        target_box.append(row)

    def _read_payload_registry(self, registry: dict[str, PayloadEditorField]) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for key, field in registry.items():
            if isinstance(field.widget, Gtk.TextView):
                buffer = field.widget.get_buffer()
                start, end = buffer.get_bounds()
                text = buffer.get_text(start, end, False)
            elif isinstance(field.widget, Gtk.Entry):
                text = field.widget.get_text()
            else:
                continue

            if field.value_type == "list":
                payload[key] = parse_list_text(text)
            else:
                payload[key] = parse_scalar(text)
        return payload

    def _on_apply_check_payload(self, _button: Gtk.Button) -> None:
        column = self._current_column()
        if column is None or self.current_check_key is None:
            return
        column.set_check(self.current_check_key, self._read_payload_registry(self.check_payload_fields))
        self._refresh_active_checks()
        self._select_check(self.current_check_key)
        self._show_message("Check aplicado", self.current_check_key)
        self._autosave_checkpoint()

    def _on_delete_check(self, _button: Gtk.Button) -> None:
        column = self._current_column()
        if column is None or self.current_check_key is None:
            return
        removed = self.current_check_key
        column.remove_check(removed)
        self.current_check_key = None
        self._refresh_active_checks()
        self._show_message("Check eliminado", removed)
        self._autosave_checkpoint()

    def _on_template_changed(self, _combo: Gtk.ComboBoxText) -> None:
        self._refresh_template_editor()

    def _current_template(self) -> ValidationTemplate:
        index = self.template_combo.get_active()
        if index < 0:
            index = 0
        return VALIDATION_TEMPLATES[self.template_keys[index]]

    def _refresh_template_editor(self) -> None:
        self._clear_box(self.template_params_box)
        self.template_parameter_fields.clear()
        template = self._current_template()
        self.template_description.set_text(template.description)
        self.template_nullable_check.set_active(bool(template.default_nullable))

        for parameter in template.parameters:
            if parameter.key == "nullable":
                self.template_nullable_check.set_active(bool(parameter.default))
                continue
            self._append_template_parameter(parameter)

    def _append_template_parameter(self, parameter: TemplateParameter) -> None:
        value_type = "list" if parameter.value_type == "list" else "text"
        self._append_payload_field(
            self.template_params_box,
            self.template_parameter_fields,
            parameter.key,
            parameter.default,
            value_type,
        )

    def _on_apply_template(self, _button: Gtk.Button) -> None:
        column = self._current_column()
        if column is None:
            return
        template = self._current_template()
        values = self._read_payload_registry(self.template_parameter_fields)
        values["nullable"] = self.template_nullable_check.get_active()
        apply_template_to_column(
            column,
            template.key,
            values,
            replace_existing_checks=self.template_replace_checks.get_active(),
        )
        self._refresh_column_editor()
        self._show_message("Plantilla aplicada", f"{template.label} -> {column.name}")
        self._autosave_checkpoint()

    def _refresh_globals(self) -> None:
        if self.contract is None:
            return
        self.global_strict_check.set_active(bool(self.contract.raw.get("strict", False)))
        self.global_coerce_check.set_active(bool(self.contract.raw.get("coerce", False)))
        self.global_unique_names_check.set_active(bool(self.contract.raw.get("unique_column_names", False)))

    def _on_apply_globals(self, _button: Gtk.Button) -> None:
        if self.contract is None:
            return
        self.contract.set_global_strict(self.global_strict_check.get_active())
        self.contract.set_global_coerce(self.global_coerce_check.get_active())
        self.contract.set_unique_column_names(self.global_unique_names_check.get_active())
        self._show_message("Globales aplicados", "strict, coerce y unique_column_names actualizados.")
        self._autosave_checkpoint()

    def _show_message(self, title: str, detail: str, *, is_error: bool = False) -> None:
        if hasattr(Gtk, "AlertDialog"):
            dialog = Gtk.AlertDialog(message=title, detail=detail)
            dialog.show(self)
            return

        message_type = Gtk.MessageType.ERROR if is_error else Gtk.MessageType.INFO
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(detail)
        dialog.connect("response", lambda dialog_, _response: dialog_.destroy())
        dialog.show()


class PanderaYamlGtkApplication(Gtk.Application):
    """GTK application bootstrap."""

    def __init__(self) -> None:
        super().__init__(application_id="org.example.PanderaYamlGtkEditor")

    def do_activate(self) -> None:  # noqa: D401 - GTK callback name
        repository = YamlSchemaRepository()
        use_cases = SchemaEditorUseCases(repository)
        window = PanderaYamlEditorWindow(self, use_cases)
        window.present()


def run(argv: list[str] | None = None) -> int:
    """Run the GTK application."""
    app = PanderaYamlGtkApplication()
    return app.run(argv if argv is not None else sys.argv)
