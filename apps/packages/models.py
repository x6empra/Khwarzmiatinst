"""
Package model — see DATABASE.md §3.

ImageField goes through Cloudinary in production (STORAGES default
swap in config/settings/production.py); in dev it stays on local FS.
"""

from decimal import Decimal

from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def _slug_from_name(name: str) -> str:
    """Slugify يدعم العربية بـ allow_unicode."""
    return slugify(name, allow_unicode=True)[:120] or "package"


class Package(models.Model):
    name = models.CharField(
        _("اسم الباقة"),
        max_length=100,
        validators=[MinLengthValidator(3)],
    )
    slug = models.SlugField(
        _("المعرّف (slug)"),
        max_length=120,
        unique=True,
        allow_unicode=True,
        blank=True,
        help_text=_("يُولَّد تلقائياً من الاسم لو تُرك فارغاً"),
    )
    description = models.TextField(_("الوصف"))
    price = models.DecimalField(
        _("السعر (ر.س)"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    duration_months = models.PositiveSmallIntegerField(
        _("مدة الاشتراك (شهور)"),
        default=1,
    )
    features = models.JSONField(
        _("المميزات"),
        default=list,
        blank=True,
        help_text=_("قائمة نصية بالمميزات — سطر لكل ميزة"),
    )
    image = models.ImageField(
        _("الصورة"),
        upload_to="packages/",
        blank=True,
        null=True,
    )
    is_featured = models.BooleanField(_("مميَّزة"), default=False, db_index=True)
    is_active = models.BooleanField(_("منشورة"), default=True, db_index=True)
    display_order = models.PositiveIntegerField(_("ترتيب العرض"), default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("باقة")
        verbose_name_plural = _("الباقات")
        ordering = ["display_order", "-created_at"]  # noqa: RUF012
        indexes = [models.Index(fields=["is_active", "display_order"])]  # noqa: RUF012

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = _slug_from_name(self.name)
        super().save(*args, **kwargs)

    @property
    def features_count(self) -> int:
        return len(self.features or [])
