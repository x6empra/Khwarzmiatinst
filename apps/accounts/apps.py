from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "الحسابات"

    def ready(self) -> None:
        from . import signals  # noqa: F401  — ربط Signals
