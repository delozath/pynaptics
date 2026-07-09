"""URL configuration for the Pandera schema editor web project.

This is the only app in the project, mounted at the root.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("schema_editor.urls")),
]
