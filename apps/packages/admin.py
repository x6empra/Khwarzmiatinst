"""Admin for Package — Manager only via Django Admin (PERMISSIONS.md)."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Package


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "duration_months",
        "is_active",
        "is_featured",
        "display_order",
        "thumb",
    )
    list_filter = ("is_active", "is_featured")
    search_fields = ("name", "description")
    ordering = ("display_order", "-created_at")
    list_editable = ("is_active", "is_featured", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("thumb_large", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("name", "slug", "description")}),
        (_("التسعير والمدة"), {"fields": ("price", "duration_months")}),
        (_("المحتوى"), {"fields": ("features", "image", "thumb_large")}),
        (_("النشر"), {"fields": ("is_active", "is_featured", "display_order")}),
        (_("التواريخ"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("صورة"))
    def thumb(self, obj: Package) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" alt="{}">',
                obj.image.url,
                obj.name,
            )
        return "—"

    @admin.display(description=_("معاينة"))
    def thumb_large(self, obj: Package) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;border-radius:12px;" alt="{}">',
                obj.image.url,
                obj.name,
            )
        return "—"

    def has_module_permission(self, request) -> bool:
        # المشرف يرى Admin، لكن إدارة الباقات للمدير فقط (PERMISSIONS.md).
        return bool(getattr(request.user, "is_manager", False) or request.user.is_superuser)

    def has_add_permission(self, request) -> bool:
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None) -> bool:
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None) -> bool:
        return self.has_module_permission(request)
