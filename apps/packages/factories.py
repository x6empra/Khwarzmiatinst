"""Factory Boy for Package — TESTING.md."""

from decimal import Decimal

import factory

from .models import Package


class PackageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Package

    name = factory.Sequence(lambda n: f"باقة رقم {n}")
    description = factory.Faker("paragraph", nb_sentences=3)
    price = factory.LazyFunction(lambda: Decimal("999.00"))
    duration_months = 6
    features = factory.LazyFunction(lambda: ["ميزة أ", "ميزة ب", "ميزة ج"])
    is_active = True
    is_featured = False
    display_order = factory.Sequence(lambda n: n)
