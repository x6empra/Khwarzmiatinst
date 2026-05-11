"""Template context processors for shared public settings."""

from django.http import HttpRequest

from .models import SiteSettings


def site_settings(request: HttpRequest) -> dict[str, SiteSettings]:
    return {"site_settings": SiteSettings.load()}
