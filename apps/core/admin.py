"""Django Admin for site-wide settings."""

from django.contrib import admin
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "contact_phone", "whatsapp_number", "updated_at")
    readonly_fields = ("updated_at",)

    fieldsets = (
        (_("أرقام التواصل"), {"fields": ("contact_phone", "whatsapp_number")}),
        (
            _("وسائل التواصل الاجتماعي"),
            {"fields": ("snapchat_url", "x_url", "instagram_url", "tiktok_url")},
        ),
        (_("الفوتر"), {"fields": ("copyright_text", "updated_at")}),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not SiteSettings.objects.exists() and super().has_add_permission(request)
