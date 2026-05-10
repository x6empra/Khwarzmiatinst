"""Factory Boy factories for tests — TESTING.md."""

import factory
from django.contrib.auth import get_user_model

from .models import Role

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence(lambda n: f"user{n}@khawarizmiat.test")
    role = Role.INVESTOR
    is_active = True
    is_email_verified = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if not create:
            return
        self.set_password(extracted or "Test1234!")
        self.save()


class InvestorFactory(UserFactory):
    role = Role.INVESTOR


class SupervisorFactory(UserFactory):
    role = Role.SUPERVISOR


class ManagerFactory(UserFactory):
    role = Role.MANAGER
