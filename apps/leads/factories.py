"""Factory — TESTING.md."""

import factory

from apps.packages.factories import PackageFactory

from .models import Lead, LeadStatus


class LeadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Lead

    name = factory.Faker("name")
    phone = "0501234567"
    email = factory.Sequence(lambda n: f"lead{n}@khawarizmiat.test")
    package = factory.SubFactory(PackageFactory)
    status = LeadStatus.NEW
    notes = ""
    source = "landing"
