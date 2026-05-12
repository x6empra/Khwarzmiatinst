"""Root URL configuration — see API.md + INFRASTRUCTURE.md §3 (SEO)."""

from typing import cast

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import Http404, HttpRequest, HttpResponse
from django.urls import Resolver404, include, path, re_path, resolve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.accounts.views import login_view
from apps.dashboard.views import dashboard_home
from apps.landing.sitemaps import sitemaps_dict
from apps.landing.views import robots_txt
from apps.packages.views import packages_page
from apps.profile.views import overview as profile_overview

admin.site.site_header = "إدارة خوارزميات"
admin.site.site_title = "إدارة خوارزميات"
admin.site.index_title = "لوحة التحكم"


def admin_short(request: HttpRequest) -> HttpResponse:
    if admin.site.has_permission(request):
        return admin.site.index(request)
    return admin.site.login(request)


def admin_no_slash(request: HttpRequest, admin_path: str) -> HttpResponse:
    resolved_path = f"/admin/{admin_path}/"
    original_path_info = request.path_info
    request.path_info = resolved_path
    try:
        match = resolve(resolved_path)
    except Resolver404 as exc:
        raise Http404 from exc
    try:
        return cast(HttpResponse, match.func(request, *match.args, **match.kwargs))
    finally:
        request.path_info = original_path_info


urlpatterns = [
    path("admin", admin_short, name="admin_short"),
    re_path(r"^admin/(?P<admin_path>.+[^/])$", admin_no_slash, name="admin_no_slash"),
    path("admin/", admin.site.urls),
    path("accounts", login_view, name="accounts_login_short"),
    path("accounts/", include("apps.accounts.urls")),
    path("packages", packages_page, name="packages_list_short"),
    path("packages/", include("apps.packages.urls")),
    path("api/packages/", include("apps.packages.api_urls")),
    path("api/leads/", include("apps.leads.urls")),
    path("dashboard", dashboard_home, name="dashboard_home_short"),
    path("dashboard/", include("apps.dashboard.urls")),
    # Profile (F9 + F10)
    path("profile", profile_overview, name="profile_overview_short"),
    path("profile/", include("apps.profile.urls")),
    path("api/profile/", include("apps.profile.api_urls")),
    # SEO (INFRASTRUCTURE.md §3)
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps_dict}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    # API schema (drf-spectacular)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Core (healthz) — non-root mount
    path("core/", include("apps.core.urls")),
    # Landing (F1) — يجب أن يكون آخر include لأنه يُمسك بـ "" root
    path("", include("apps.landing.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
