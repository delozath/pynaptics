"""URL routes for the schema editor app.

Every `/editor/...` route requires and consumes a `?src=` query parameter
(the working YAML path) - see `schema_editor.context_processors.working_src`
and `schema_editor.views.common.load_contract_or_error` for why it lives in
the URL rather than the session.
"""

from __future__ import annotations

from django.urls import path

from .views import checks, columns, globals_save, load, template_editor

app_name = "schema_editor"

urlpatterns = [
    path("", load.load_view, name="load"),
    path("resume/", load.resume_confirm_view, name="resume"),
    path("resume/discard/", load.discard_checkpoint_view, name="resume_discard"),
    path("editor/column/<str:column_name>/", columns.column_detail_view, name="column_detail"),
    path("editor/column/<str:column_name>/checks/add/", checks.add_check_view, name="check_add"),
    path(
        "editor/column/<str:column_name>/checks/<str:check_key>/",
        checks.check_payload_edit_view,
        name="check_payload_edit",
    ),
    path(
        "editor/column/<str:column_name>/checks/<str:check_key>/delete/",
        checks.delete_check_view,
        name="check_delete",
    ),
    path(
        "editor/column/<str:column_name>/template/",
        template_editor.template_picker_view,
        name="column_template",
    ),
    path("editor/globals/", globals_save.globals_edit_view, name="globals_edit"),
    path("editor/save-as/", globals_save.save_as_view, name="save_as"),
]
