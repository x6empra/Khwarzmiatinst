"""
Django Admin for User — used by Manager to create Supervisors/Managers
(PERMISSIONS.md: لا تسجيل عام للمشرف/المدير).
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-date_joined"]
    list_display = ("email", "full_name", "role", "is_email_verified", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_email_verified", "is_staff")
    search_fields = ("email", "first_name", "last_name", "phone")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("المعلومات الشخصية"), {"fields": ("first_name", "last_name", "phone")}),
        (
            _("الصلاحيات"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_email_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("التواريخ"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
