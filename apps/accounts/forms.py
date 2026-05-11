"""
Auth forms — Tailwind-ready.

استخدم Django Forms (PERMISSIONS.md): server-side validation.
"""

from typing import ClassVar

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

User = get_user_model()


_BASE_INPUT = (
    "block w-full rounded-md border border-neutral-400 px-4 py-3 "
    "text-base text-neutral-900 placeholder-neutral-400 "
    "focus:border-accent focus:ring-2 focus:ring-accent"
)


class RegisterForm(forms.ModelForm):
    """تسجيل مستثمر جديد. الدور دائماً investor — لا يُسمح بتعيينه من الواجهة."""

    password1 = forms.CharField(
        label=_("كلمة المرور"),
        widget=forms.PasswordInput(attrs={"class": _BASE_INPUT, "autocomplete": "new-password"}),
        min_length=8,
    )
    password2 = forms.CharField(
        label=_("تأكيد كلمة المرور"),
        widget=forms.PasswordInput(attrs={"class": _BASE_INPUT, "autocomplete": "new-password"}),
        min_length=8,
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone")
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "first_name": forms.TextInput(attrs={"class": _BASE_INPUT}),
            "last_name": forms.TextInput(attrs={"class": _BASE_INPUT}),
            "email": forms.EmailInput(attrs={"class": _BASE_INPUT, "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"class": _BASE_INPUT, "placeholder": "05XXXXXXXX"}),
        }

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_("هذا الإيميل مسجَّل مسبقاً."))
        return email

    def clean(self) -> dict:
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", _("كلمتا المرور غير متطابقتين."))
        if p1:
            try:
                validate_password(p1)
            except forms.ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = "investor"  # إلزامي — PERMISSIONS.md
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_("الإيميل"),
        widget=forms.EmailInput(attrs={"class": _BASE_INPUT, "autocomplete": "email"}),
    )
    password = forms.CharField(
        label=_("كلمة المرور"),
        widget=forms.PasswordInput(
            attrs={"class": _BASE_INPUT, "autocomplete": "current-password"}
        ),
    )
    remember_me = forms.BooleanField(
        label=_("تذكرني"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "size-5 rounded text-accent focus:ring-accent"}),
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user_cache: User | None = None
        super().__init__(*args, **kwargs)

    def clean(self) -> dict:
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise forms.ValidationError(_("إيميل أو كلمة مرور غير صحيحة."))
            if not user.is_active:
                raise forms.ValidationError(_("هذا الحساب موقوف."))
            self.user_cache = user
        return cleaned

    def get_user(self) -> User | None:
        return self.user_cache
