"""
Signals for Lead.

F3 (هذا الملف): يُسجِّل حدث post_save فقط — البنية جاهزة للاستقبال.
F7 (لاحقاً): apps.notifications يربط handler يرسل Telegram + Email.

تعمَّداً نتركها فارغة حتى لا نضيف تنفيذاً جزئياً قبل F7.
"""

from django.db.models.signals import post_save  # noqa: F401
from django.dispatch import receiver  # noqa: F401

# F7 سيضيف:
# @receiver(post_save, sender=Lead)
# def on_lead_created(sender, instance, created, **kwargs):
#     if created:
#         send_telegram_to_admin.delay(instance.id)
#         send_email_to_admin.delay(instance.id)
