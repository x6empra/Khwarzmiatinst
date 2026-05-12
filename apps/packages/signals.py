"""Signals for package route synchronization."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.cpanel_routes import ensure_admin_instance_route_dirs, ensure_package_route_dirs

from .models import Package


@receiver(post_save, sender=Package, dispatch_uid="packages.ensure_cpanel_routes")
def ensure_package_cpanel_routes(
    sender: type[Package], instance: Package, **kwargs: object
) -> None:
    ensure_package_route_dirs(instance.id, instance.slug)
    ensure_admin_instance_route_dirs(instance)
