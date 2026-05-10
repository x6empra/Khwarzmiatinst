"""
Custom User model — see DATABASE.md §1.

3 roles: investor / supervisor / manager.
Email is the unique identifier (no username).
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.validators import phone_validator

from .managers import UserManager


class Role(models.TextChoices):
    INVESTOR = "investor", _("مستثمر")
    SUPERVISOR = "supervisor", _("مشرف")
    MANAGER = "manager", _("مدير")


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("الإيميل"), unique=True)
    first_name = models.CharField(_("الاسم الأول"), max_length=50)
    last_name = models.CharField(_("الاسم الأخير"), max_length=50)
    phone = models.CharField(
        _("رقم الجوال"),
        max_length=20,
        blank=True,
        validators=[phone_validator],
        help_text=_("الصيغة: 05XXXXXXXX أو +9665XXXXXXXX"),
    )
    role = models.CharField(
        _("الدور"),
        max_length=20,
        choices=Role.choices,
        default=Role.INVESTOR,
        db_index=True,
    )

    is_active = models.BooleanField(_("نشط"), default=True)
    is_staff = models.BooleanField(_("موظف"), default=False)
    is_email_verified = models.BooleanField(_("تم تأكيد الإيميل"), default=False)

    date_joined = models.DateTimeField(_("تاريخ التسجيل"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("مستخدم")
        verbose_name_plural = _("المستخدمون")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.email})"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.first_name

    @property
    def is_investor(self) -> bool:
        return self.role == Role.INVESTOR

    @property
    def is_supervisor(self) -> bool:
        return self.role == Role.SUPERVISOR

    @property
    def is_manager(self) -> bool:
        return self.role == Role.MANAGER

    @property
    def is_staff_role(self) -> bool:
        """Supervisor or Manager — انتباه: غير is_staff الافتراضي."""
        return self.role in (Role.SUPERVISOR, Role.MANAGER)


class UserProfile(models.Model):
    """
    ملف المستثمر — DATABASE.md §2.
    OneToOne مع User. يُنشأ تلقائياً عبر post_save signal.
    """

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("المستخدم"),
    )
    company_name = models.CharField(_("اسم المعهد/الشركة"), max_length=150, blank=True, default="")
    city = models.CharField(_("المدينة"), max_length=50, blank=True, default="")
    bio = models.TextField(_("نبذة"), blank=True, default="")
    avatar = models.ImageField(_("الصورة الشخصية"), upload_to="avatars/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("ملف شخصي")
        verbose_name_plural = _("الملفات الشخصية")

    def __str__(self) -> str:
        return f"Profile<{self.user.email}>"
