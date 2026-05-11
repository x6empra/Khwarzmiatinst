"""LeadForm — server-side validation (PERMISSIONS.md, FEATURES.md F3)."""

from typing import ClassVar

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.packages.models import Package

from .models import Lead

_BASE_INPUT = (
    "block w-full rounded-md border border-neutral-400 px-4 py-3 "
    "text-base text-neutral-900 placeholder-neutral-400 "
    "focus:border-accent focus:ring-2 focus:ring-accent"
)


class LeadForm(forms.ModelForm):
    recaptcha_token = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Lead
        fields = ("name", "phone", "email", "package", "notes")
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "name": forms.TextInput(attrs={"class": _BASE_INPUT, "placeholder": _("الاسم الكامل")}),
            "phone": forms.TextInput(attrs={"class": _BASE_INPUT, "placeholder": "05XXXXXXXX"}),
            "email": forms.EmailInput(
                attrs={"class": _BASE_INPUT, "placeholder": "you@example.com"}
            ),
            "package": forms.Select(attrs={"class": _BASE_INPUT}),
            "notes": forms.Textarea(
                attrs={
                    "class": _BASE_INPUT,
                    "rows": 3,
                    "placeholder": _("أي تفاصيل إضافية (اختياري)"),
                }
            ),
        }
        labels: ClassVar[dict[str, object]] = {
            "name": _("الاسم"),
            "phone": _("رقم الجوال"),
            "email": _("البريد الإلكتروني"),
            "package": _("الباقة المطلوبة"),
            "notes": _("ملاحظات"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # only active packages selectable
        self.fields["package"].queryset = Package.objects.filter(is_active=True)
        self.fields["package"].empty_label = _("— اختر باقة —")
        self.fields["notes"].required = False

    def clean_email(self) -> str:
        return self.cleaned_data["email"].lower().strip()

    def clean_name(self) -> str:
        return self.cleaned_data["name"].strip()
