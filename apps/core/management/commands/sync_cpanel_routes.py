"""Synchronize cPanel public route directories."""

from django.core.management.base import BaseCommand

from apps.core.cpanel_routes import sync_all_cpanel_route_dirs


class Command(BaseCommand):
    help = "Create cPanel public directories required for Passenger clean URLs."

    def handle(self, *args: object, **options: object) -> None:
        count = sync_all_cpanel_route_dirs()
        self.stdout.write(self.style.SUCCESS(f"Synced {count} cPanel route directories."))
