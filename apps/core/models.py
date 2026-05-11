"""Core site-wide settings shown across public templates."""

import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.validators import phone_validator

DEFAULT_COPYRIGHT_TEXT = "خوارزميات — منصة المعاهد · جميع الحقوق محفوظة"


def _phone_digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def _normalize_sa_phone(value: str) -> str:
    digits = _phone_digits(value)
    if digits.startswith("05"):
        return f"966{digits[1:]}"
    if digits.startswith("00966"):
        return digits[2:]
    if digits.startswith("966"):
        return digits
    return digits


class SiteSettings(models.Model):
    """Singleton settings record managed from Django Admin."""

    contact_phone = models.CharField(
        _("رقم التواصل"),
        max_length=20,
        blank=True,
        default="",
        validators=[phone_validator],
        help_text=_("الصيغة: 05XXXXXXXX أو +9665XXXXXXXX"),
    )
    whatsapp_number = models.CharField(
        _("رقم واتساب"),
        max_length=20,
        blank=True,
        default="",
        validators=[phone_validator],
        help_text=_("يُستخدم لزر واتساب العائم وفي الفوتر."),
    )
    snapchat_url = models.URLField(
        _("رابط سناب شات"),
        blank=True,
        default="",
        validators=[URLValidator()],
    )
    x_url = models.URLField(
        _("رابط X"),
        blank=True,
        default="",
        validators=[URLValidator()],
    )
    instagram_url = models.URLField(
        _("رابط إنستقرام"),
        blank=True,
        default="",
        validators=[URLValidator()],
    )
    tiktok_url = models.URLField(
        _("رابط تيك توك"),
        blank=True,
        default="",
        validators=[URLValidator()],
    )
    copyright_text = models.CharField(
        _("نص الحقوق"),
        max_length=160,
        default=DEFAULT_COPYRIGHT_TEXT,
    )
    updated_at = models.DateTimeField(_("آخر تحديث"), auto_now=True)

    class Meta:
        verbose_name = _("إعدادات الموقع")
        verbose_name_plural = _("إعدادات الموقع")
        ordering = ["-updated_at"]  # noqa: RUF012 - Django Meta expects list-like options.

    def __str__(self) -> str:
        return "إعدادات الموقع"

    def save(self, *args: object, **kwargs: object) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        super().clean()
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(_("يمكن إنشاء سجل إعدادات واحد فقط."))

    @classmethod
    def load(cls) -> "SiteSettings":
        settings = cls.objects.first()
        if settings is not None:
            return settings
        return cls(copyright_text=DEFAULT_COPYRIGHT_TEXT)

    @property
    def contact_phone_href(self) -> str:
        if not self.contact_phone:
            return ""
        return f"tel:+{_normalize_sa_phone(self.contact_phone)}"

    @property
    def whatsapp_url(self) -> str:
        if not self.whatsapp_number:
            return ""
        return f"https://wa.me/{_normalize_sa_phone(self.whatsapp_number)}"

    @property
    def has_social_links(self) -> bool:
        return any((self.snapchat_url, self.x_url, self.instagram_url, self.tiktok_url))
