"""
Signals for accounts.

Phase 1: نضمن أن staff_role users يحصلون على is_staff=True تلقائياً ليتمكنوا من
الوصول للوحة الإدارة (Supervisor/Manager).
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Role, User


@receiver(pre_save, sender=User)
def sync_is_staff_with_role(sender, instance: User, **kwargs) -> None:
    """Supervisor/Manager → is_staff=True (للدخول لـ Django Admin)."""
    if instance.role in (Role.SUPERVISOR, Role.MANAGER):
        instance.is_staff = True
