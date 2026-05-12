"""Helpers that keep cPanel Passenger clean URLs reachable.

cPanel's Passenger routing on this host only dispatches a clean nested URL after
the matching directory exists under ``public``. These helpers create empty route
directories only when enabled by the cPanel settings module.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from pathlib import Path

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)

DEFAULT_MAX_ROUTE_DIRS_PER_MODEL = 5000

STATIC_ROUTE_DIRS = (
    "admin",
    "admin/login",
    "accounts/login",
    "accounts/logout",
    "accounts/register",
    "api/leads/create",
    "api/packages",
    "api/profile/orders",
    "core/healthz",
    "dashboard",
    "dashboard/leads",
    "dashboard/leads/new",
    "dashboard/packages",
    "dashboard/packages/new",
    "dashboard/users",
    "packages",
    "profile",
    "profile/orders",
    "profile/password",
)


def sync_all_cpanel_route_dirs() -> int:
    """Create static, dashboard, and admin route directories for cPanel."""
    routes = list(STATIC_ROUTE_DIRS)
    routes.extend(_dashboard_object_routes())
    routes.extend(_admin_model_routes())
    return ensure_cpanel_route_dirs(routes)


def ensure_cpanel_route_dirs(routes: Iterable[str]) -> int:
    """Create safe route directories under the configured cPanel public dir."""
    if not getattr(settings, "CPANEL_ROUTE_SYNC_ENABLED", False):
        return 0

    public_dir = Path(getattr(settings, "CPANEL_PUBLIC_DIR", ""))
    if not public_dir.exists():
        return 0

    created_or_existing = 0
    for route in routes:
        safe_route = _normalize_route(route)
        if safe_route is None:
            continue
        try:
            (public_dir / safe_route).mkdir(parents=True, exist_ok=True)
            created_or_existing += 1
        except OSError:
            logger.exception("Failed to create cPanel route directory: %s", safe_route)

    return created_or_existing


def ensure_lead_route_dirs(lead_id: int) -> int:
    """Create dashboard/admin cPanel directories for one lead."""
    return ensure_cpanel_route_dirs(
        (
            f"dashboard/leads/{lead_id}",
            f"dashboard/leads/{lead_id}/delete",
            f"dashboard/leads/{lead_id}/status",
            f"admin/leads/lead/{lead_id}/change",
            f"admin/leads/lead/{lead_id}/delete",
            f"admin/leads/lead/{lead_id}/history",
        )
    )


def ensure_package_route_dirs(package_id: int, slug: str = "") -> int:
    """Create dashboard/admin/public API cPanel directories for one package."""
    routes = [
        f"dashboard/packages/{package_id}/edit",
        f"admin/packages/package/{package_id}/change",
        f"admin/packages/package/{package_id}/delete",
        f"admin/packages/package/{package_id}/history",
    ]
    if slug:
        routes.append(f"api/packages/{slug}")
    return ensure_cpanel_route_dirs(routes)


def ensure_admin_instance_route_dirs(instance: models.Model) -> int:
    """Create Django admin cPanel directories for any registered model object."""
    model = instance.__class__
    base = _admin_model_base(model)
    pk = str(instance.pk)
    return ensure_cpanel_route_dirs(
        (
            base,
            f"{base}/add",
            f"{base}/{pk}/change",
            f"{base}/{pk}/delete",
            f"{base}/{pk}/history",
        )
    )


def _dashboard_object_routes() -> list[str]:
    routes: list[str] = []
    try:
        from apps.leads.models import Lead
        from apps.packages.models import Package

        for lead_id in _limited_ids(Lead):
            routes.extend(
                (
                    f"dashboard/leads/{lead_id}",
                    f"dashboard/leads/{lead_id}/delete",
                    f"dashboard/leads/{lead_id}/status",
                )
            )

        for package in Package.objects.only("id", "slug")[: _max_route_dirs_per_model()]:
            routes.append(f"dashboard/packages/{package.id}/edit")
            if package.slug:
                routes.append(f"api/packages/{package.slug}")
    except Exception:
        logger.exception("Failed to collect dashboard cPanel route directories")
    return routes


def _admin_model_routes() -> list[str]:
    routes: list[str] = []
    try:
        from django.contrib import admin

        for model in admin.site._registry:
            base = _admin_model_base(model)
            routes.extend((base, f"{base}/add"))
            for pk in _limited_ids(model):
                routes.extend(
                    (
                        f"{base}/{pk}/change",
                        f"{base}/{pk}/delete",
                        f"{base}/{pk}/history",
                    )
                )
    except Exception:
        logger.exception("Failed to collect admin cPanel route directories")
    return routes


def _admin_model_base(model: type[models.Model]) -> str:
    meta = model._meta
    return f"admin/{meta.app_label}/{meta.model_name}"


def _limited_ids(model: type[models.Model]) -> list[str]:
    limit = _max_route_dirs_per_model()
    return [
        str(pk) for pk in model._default_manager.order_by("pk").values_list("pk", flat=True)[:limit]
    ]


def _max_route_dirs_per_model() -> int:
    return int(
        getattr(settings, "CPANEL_MAX_ROUTE_DIRS_PER_MODEL", DEFAULT_MAX_ROUTE_DIRS_PER_MODEL)
    )


def _normalize_route(route: str) -> str | None:
    normalized = route.strip().strip("/")
    if not normalized:
        return None

    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    if normalized.startswith("."):
        return None
    return normalized
