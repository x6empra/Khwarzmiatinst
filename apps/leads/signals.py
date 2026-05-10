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

from .models import Lead

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lead, dispatch_uid="leads.on_lead_created")
def on_lead_created(sender, instance: Lead, created: bool, **kwargs) -> None:
    if not created:
        return

    # Lazy import — يكسر دورة استيراد محتملة (apps.notifications → apps.leads)
    from apps.notifications.tasks import send_email_to_admin, send_telegram_to_admin

    try:
        send_telegram_to_admin.delay(instance.id)
        send_email_to_admin.delay(instance.id)
    except Exception:  # noqa: BLE001 — لا نريد كسر إنشاء Lead لو Celery معطّل
        logger.exception("Failed to dispatch notifications for lead #%s", instance.id)
