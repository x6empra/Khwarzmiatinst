"""
Signals for Lead — F7 active.

عند إنشاء Lead جديد:
  - send_telegram_to_admin (أساسي)
  - send_email_to_admin   (احتياطي)

كلتا المهمتين تُرسَلان عبر Celery (.delay) لتجنّب تعطيل الردّ على الزائر.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.cpanel_routes import ensure_admin_instance_route_dirs, ensure_lead_route_dirs

from .models import Lead

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lead, dispatch_uid="leads.on_lead_created")
def on_lead_created(sender, instance: Lead, created: bool, **kwargs) -> None:
    ensure_lead_route_dirs(instance.id)
    ensure_admin_instance_route_dirs(instance)

    if not created:
        return

    # Lazy import — يكسر دورة استيراد محتملة (apps.notifications → apps.leads)
    from apps.notifications.tasks import send_email_to_admin, send_telegram_to_admin

    try:
        send_telegram_to_admin.delay(instance.id)
        send_email_to_admin.delay(instance.id)
    except Exception:
        logger.exception("Failed to dispatch notifications for lead #%s", instance.id)
