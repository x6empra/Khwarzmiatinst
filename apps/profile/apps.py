from django.apps import AppConfig


class ProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.profile"
    label = "investor_profile"  # تجنّب التضارب مع كلمة محجوزة
    verbose_name = "ملفات المستثمرين"
