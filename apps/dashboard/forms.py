"""
Dashboard forms — Manager-only edits.

PackageEditForm: يستهلك features كمصفوفة سلاسل (request.POST.getlist).
الحقول الأخرى تخضع لـ validators DATABASE.md §3.
"""

from decimal import Decimal
from typing import ClassVar

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.packages.models import Package

_BASE_INPUT = (
    "block w-full rounded-md border border-neutral-400 px-3 py-2 "
    "text-sm text-neutral-900 placeholder-neutral-400 "
    "focus:border-accent focus:ring-2 focus:ring-accent"
)
_CHECKBOX = "size-5 rounded text-accent focus:ring-accent"


class PackageEditForm(forms.ModelForm):
    """تحرير باقة من Dashboard — Manager only (PERMISSIONS.md)."""

    class Meta:
        model = Package
        fields = (
            "name",
            "slug",
            "description",
            "price",
            "duration_months",
            "image",
            "is_featured",
            "is_active",
            "display_order",
        )
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "name": forms.TextInput(attrs={"class": _BASE_INPUT}),
            "slug": forms.TextInput(attrs={"class": _BASE_INPUT, "dir": "ltr"}),
            "description": forms.Textarea(attrs={"class": _BASE_INPUT, "rows": 3}),
            "price": forms.NumberInput(attrs={"class": _BASE_INPUT, "step": "0.01", "min": "0"}),
            "duration_months": forms.NumberInput(attrs={"class": _BASE_INPUT, "min": "1"}),
            "display_order": forms.NumberInput(attrs={"class": _BASE_INPUT, "min": "0"}),
            "is_featured": forms.CheckboxInput(attrs={"class": _CHECKBOX}),
            "is_active": forms.CheckboxInput(attrs={"class": _CHECKBOX}),
        }
        labels: ClassVar[dict[str, object]] = {
            "name": _("اسم الباقة"),
            "slug": _("المعرّف (slug)"),
            "description": _("الوصف"),
            "price": _("السعر (ر.س)"),
            "duration_months": _("مدة الاشتراك (شهور)"),
            "image": _("الصورة"),
            "is_featured": _("⭐ مميَّزة"),
            "is_active": _("منشورة"),
            "display_order": _("ترتيب العرض"),
        }

    def __init__(self, *args, features_list: list[str] | None = None, **kwargs):
        """يستقبل features كقائمة (من request.POST.getlist) قبل validation."""
        super().__init__(*args, **kwargs)
        # نخفي features عن ModelForm — نتعامل معها يدوياً
        self.fields.pop("features", None)
        # القائمة الواردة من POST (أو instance لو GET)
        if features_list is not None:
            cleaned = [f.strip() for f in features_list if f and f.strip()]
            self._features = cleaned
        elif self.instance and self.instance.pk:
            self._features = list(self.instance.features or [])
        else:
            self._features = []

    @property
    def features_list(self) -> list[str]:
        return self._features

    def clean_price(self) -> Decimal:
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError(_("السعر لا يمكن أن يكون سالباً."))
        return price

    def clean_duration_months(self) -> int:
        value = self.cleaned_data["duration_months"]
        if value < 1:
            raise forms.ValidationError(_("المدة يجب أن تكون شهراً على الأقل."))
        return value

    def save(self, commit: bool = True) -> Package:
        pkg = super().save(commit=False)
        pkg.features = self._features  # الحفظ كـ JSON list
        if commit:
            pkg.save()
        return pkg
