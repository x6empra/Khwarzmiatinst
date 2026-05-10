"""
Celery tasks — F7.

كل مهمة:
  - bind=True → تتلقى self كـ task instance.
  - max_retries=3 + exponential backoff.
  - تستهلك Lead.id (لا تمرر الكائن — لا يُسلسَل عبر JSON).
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .telegram import TelegramError, send_message

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(TelegramError,),
    retry_backoff=True,        # 1, 2, 4, ... ثانية
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
)
def send_telegram_to_admin(self, lead_id: int) -> None:
    """يرسل تنبيه Telegram للإدارة عن طلب جديد (F7 الأساسي)."""
    from apps.leads.models import Lead  # تجنّب الـ circular import

    try:
        lead = Lead.objects.select_related("package").get(pk=lead_id)
    except Lead.DoesNotExist:
        logger.warning("send_telegram: lead %s not found (deleted?)", lead_id)
        return

    text = (
        "🆕 <b>طلب جديد على خوارزميات</b>\n\n"
        f"👤 <b>الاسم:</b> {lead.name}\n"
        f"📱 <b>الجوال:</b> {lead.phone}\n"
        f"📧 <b>البريد:</b> {lead.email}\n"
        f"📦 <b>الباقة:</b> {lead.package.name}\n"
        f"🏷️ <b>المصدر:</b> {lead.get_source_display()}\n\n"
        f"📝 <b>ملاحظات:</b>\n{lead.notes or '—'}\n\n"
        f"🆔 <b>رقم الطلب:</b> #{lead.id}"
    )

    send_message(text)
    logger.info("telegram sent for lead #%s", lead_id)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    max_retries=3,
)
def send_email_to_admin(self, lead_id: int) -> None:
    """يرسل بريد للإدارة (F7 — احتياطي)."""
    from apps.leads.models import Lead

    try:
        lead = Lead.objects.select_related("package").get(pk=lead_id)
    except Lead.DoesNotExist:
        logger.warning("send_email: lead %s not found", lead_id)
        return

    context = {"lead": lead}
    subject = f"🆕 طلب جديد — {lead.name} ({lead.package.name})"
    text_body = render_to_string("notifications/email/new_lead.txt", context)
    html_body = render_to_string("notifications/email/new_lead.html", context)

    recipient = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", None) or settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject=subject,
        message=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        html_message=html_body,
        fail_silently=False,
    )
    logger.info("email sent for lead #%s to %s", lead_id, recipient)
