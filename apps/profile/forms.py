"""Profile forms — F9 (PERMISSIONS.md: server-side validation)."""

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserProfile

User = get_user_model()

_BASE_INPUT = (
    "block w-full rounded-md border border-neutral-400 px-4 py-3 "
    "text-base text-neutral-900 placeholder-neutral-400 "
    "focus:border-accent focus:ring-2 focus:ring-accent"
)


class ProfileForm(forms.ModelForm):
    """يجمع حقول User + UserProfile معاً."""

    first_name = forms.CharField(
        label=_("الاسم الأول"),
        max_length=50,
        widget=forms.TextInput(attrs={"class": _BASE_INPUT}),
    )
    last_name = forms.CharField(
        label=_("الاسم الأخير"),
        max_length=50,
        widget=forms.TextInput(attrs={"class": _BASE_INPUT}),
    )
    phone = forms.CharField(
        label=_("رقم الجوال"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": _BASE_INPUT, "placeholder": "05XXXXXXXX"}),
    )

    class Meta:
        model = UserProfile
        fields = ["company_name", "city", "bio", "avatar"]
        widgets = {
            "company_name": forms.TextInput(attrs={"class": _BASE_INPUT}),
            "city": forms.TextInput(attrs={"class": _BASE_INPUT}),
            "bio": forms.Textarea(attrs={"class": _BASE_INPUT, "rows": 4}),
        }
        labels = {
            "company_name": _("اسم المعهد/الشركة"),
            "city": _("المدينة"),
            "bio": _("نبذة"),
            "avatar": _("الصورة الشخصية"),
        }

    def __init__(self, *args, user: User | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["phone"].initial = user.phone
        self._user = user

    def clean_phone(self) -> str:
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return ""
        from apps.core.validators import phone_validator

        phone_validator(phone)
        return phone

    def save(self, commit: bool = True) -> UserProfile:
        profile = super().save(commit=False)
        if self._user is not None and commit:
            self._user.first_name = self.cleaned_data["first_name"]
            self._user.last_name = self.cleaned_data["last_name"]
            self._user.phone = self.cleaned_data.get("phone", "")
            self._user.save(update_fields=["first_name", "last_name", "phone"])
        if commit:
            profile.save()
        return profile
