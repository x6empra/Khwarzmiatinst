"""
Signals for accounts.

- pre_save: staff_role → is_staff=True (للدخول لـ Django Admin).
- post_save: ضمان وجود UserProfile للمستثمرين (F9).
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.core.cpanel_routes import ensure_admin_instance_route_dirs

from .models import Role, User, UserProfile


@receiver(pre_save, sender=User)
def sync_is_staff_with_role(sender, instance: User, **kwargs) -> None:
    """Supervisor/Manager → is_staff=True (للدخول لـ Django Admin)."""
    if instance.role in (Role.SUPERVISOR, Role.MANAGER):
        instance.is_staff = True


@receiver(post_save, sender=User, dispatch_uid="accounts.ensure_profile")
def ensure_profile_exists(sender, instance: User, created: bool, **kwargs) -> None:
    """ينشئ UserProfile تلقائياً عند إنشاء مستخدم جديد (F9)."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
    ensure_admin_instance_route_dirs(instance)
