"""Custom user manager — email is the unique identifier (no username)."""

from typing import Any

from django.contrib.auth.base_user import BaseUserManager
from django.db.models import QuerySet


class UserManager(BaseUserManager):
    """Manager that uses email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: Any):
        if not email:
            raise ValueError("الإيميل مطلوب")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", "investor")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "manager")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)

    # Convenience filters used across apps
    def investors(self) -> QuerySet:
        return self.filter(role="investor")

    def supervisors(self) -> QuerySet:
        return self.filter(role="supervisor")

    def managers(self) -> QuerySet:
        return self.filter(role="manager")

    def staff_roles(self) -> QuerySet:
        """Supervisor + Manager."""
        return self.filter(role__in=["supervisor", "manager"])
