"""Investor-only decorator — PERMISSIONS.md."""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def investor_required(view_func):
    """يسمح للمستثمر فقط (المشرف/المدير لهم لوحة الإدارة)."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not getattr(request.user, "is_investor", False):
            raise PermissionDenied("هذه الصفحة مخصصة للمستثمرين.")
        return view_func(request, *args, **kwargs)

    return _wrapped
