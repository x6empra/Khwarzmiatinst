"""
DRF Permission classes — see PERMISSIONS.md.

- IsInvestor   : المستثمر فقط
- IsSupervisor : مشرف أو مدير (staff_roles)
- IsManager    : المدير فقط
- IsOwnerInvestor : المستثمر يصل لأشيائه فقط
"""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsInvestor(BasePermission):
    """authenticated + role == investor."""

    message = "هذه الصفحة مخصصة للمستثمرين."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "is_investor", False))


class IsSupervisor(BasePermission):
    """Supervisor + Manager (staff roles)."""

    message = "هذه الصفحة مخصصة لطاقم الإدارة."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "is_staff_role", False))


class IsManager(BasePermission):
    """Manager only."""

    message = "هذا الإجراء يحتاج صلاحية المدير."

    def has_permission(self, request: Request, view: APIView) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "is_manager", False))


class IsOwnerInvestor(BasePermission):
    """Object-level: investor sees only objects whose `.investor == request.user`."""

    message = "ليس لديك صلاحية على هذا العنصر."

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        owner = getattr(obj, "investor", None)
        return owner is not None and owner == request.user
