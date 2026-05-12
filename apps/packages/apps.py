from django.apps import AppConfig


class PackagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.packages"
    verbose_name = "الباقات"

    def ready(self) -> None:
        from . import signals  # noqa: F401
