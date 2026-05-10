"""
Decorators for dashboard views — PERMISSIONS.md.

نستخدم decorators بدلاً من DRF permission classes لأن الـ views صفحات HTML.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_required(view_func):
    """Supervisor + Manager."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not getattr(request.user, "is_staff_role", False):
            raise PermissionDenied("هذه الصفحة مخصصة لطاقم الإدارة.")
        return view_func(request, *args, **kwargs)

    return _wrapped


def manager_required(view_func):
    """Manager only."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not getattr(request.user, "is_manager", False):
            raise PermissionDenied("هذا الإجراء يحتاج صلاحية المدير.")
        return view_func(request, *args, **kwargs)

    return _wrapped
