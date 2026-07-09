"""Template context processors for the schema editor app."""

from __future__ import annotations

from django.http import HttpRequest


def working_src(request: HttpRequest) -> dict[str, str]:
    """Expose the working YAML path (`?src=`) to every template.

    The working path deliberately lives in the URL query string, not in the
    session, so every page/tab is independently authoritative about which
    file it is editing (see the architecture notes in the project README).
    This processor just saves every view/template from repeating
    `request.GET.get("src", "")`.
    """
    return {"src": request.GET.get("src", "")}
