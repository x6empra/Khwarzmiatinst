"""LeadAdmin — Supervisor + Manager (PERMISSIONS.md §API + Admin)."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Lead, LeadStatus

STATUS_COLORS = {
    LeadStatus.NEW: "#F39C12",          # accent
    LeadStatus.IN_PROGRESS: "#2563EB",  # blue
    LeadStatus.CLOSED: "#27AE60",       # success
    LeadStatus.CANCELLED: "#DC2626",    # red
}


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "package", "status_badge", "investor", "created_at")
    list_filter = ("status", "package", "source")
    search_fields = ("name", "phone", "email", "notes")
    autocomplete_fields = ("package",)
    readonly_fields = ("ip_address", "user_agent", "created_at", "updated_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("name", "phone", "email", "package")}),
        (_("الحالة والملاحظات"), {"fields": ("status", "notes", "investor")}),
        (_("بيانات تقنية"), {"fields": ("source", "ip_address", "user_agent")}),
        (_("التواريخ"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("الحالة"), ordering="status")
    def status_badge(self, obj: Lead) -> str:
        color = STATUS_COLORS.get(obj.status, "#5D6D7E")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:9999px;font-size:12px;font-weight:700;">{}</span>',
            color,
            obj.get_status_display(),
        )

    # Manager only للحذف (PERMISSIONS.md §API.delete)
    def has_delete_permission(self, request, obj=None) -> bool:
        return bool(getattr(request.user, "is_manager", False) or request.user.is_superuser)

    def has_module_permission(self, request) -> bool:
        return bool(getattr(request.user, "is_staff_role", False) or request.user.is_superuser)
