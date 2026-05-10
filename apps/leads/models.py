"""
Lead model — قلب المشروع.
See DATABASE.md §4 (status pipeline + indexes + on_delete behavior).
"""

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.validators import phone_validator


class LeadStatus(models.TextChoices):
    NEW = "new", _("جديد 🟠")
    IN_PROGRESS = "in_progress", _("جاري التواصل 🔵")
    CLOSED = "closed", _("تم الإغلاق 🟢")
    CANCELLED = "cancelled", _("ملغي ❌")


class LeadSource(models.TextChoices):
    LANDING = "landing", _("الصفحة الرئيسية")
    PROFILE = "profile", _("ملف المستثمر")
    OTHER = "other", _("آخر")


class Lead(models.Model):
    name = models.CharField(_("الاسم"), max_length=100, validators=[MinLengthValidator(3)])
    phone = models.CharField(_("رقم الجوال"), max_length=20, validators=[phone_validator])
    email = models.EmailField(_("الإيميل"))

    package = models.ForeignKey(
        "packages.Package",
        on_delete=models.PROTECT,  # لا تحذف باقة فيها طلبات (DATABASE.md §Relations)
        related_name="leads",
        verbose_name=_("الباقة"),
    )
    investor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
        verbose_name=_("المستثمر (إن وُجد)"),
        help_text=_("يُربَط تلقائياً لو كان المستخدم مسجَّلاً وقت الإرسال"),
    )

    status = models.CharField(
        _("الحالة"),
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
        db_index=True,
    )
    notes = models.TextField(_("ملاحظات داخلية"), blank=True, default="")

    source = models.CharField(
        _("المصدر"),
        max_length=30,
        choices=LeadSource.choices,
        default=LeadSource.LANDING,
    )
    ip_address = models.GenericIPAddressField(_("IP"), null=True, blank=True)
    user_agent = models.CharField(_("User Agent"), max_length=255, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("طلب")
        verbose_name_plural = _("الطلبات")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} — {self.package.name} ({self.get_status_display()})"

    @property
    def is_new(self) -> bool:
        return self.status == LeadStatus.NEW
