"""Model tests — TESTING.md §Unit (DATABASE.md §3)."""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.packages.factories import PackageFactory
from apps.packages.models import Package


@pytest.mark.django_db
class TestPackageModel:
    def test_str_returns_name(self):
        pkg = PackageFactory(name="باقة تجريبية")
        assert str(pkg) == "باقة تجريبية"

    def test_slug_auto_generated_from_arabic_name(self):
        pkg = PackageFactory(name="الباقة الذهبية", slug="")
        assert pkg.slug != ""
        assert pkg.slug.startswith("الباقة")

    def test_slug_unique(self):
        PackageFactory(name="X", slug="duplicate")
        with pytest.raises(IntegrityError):
            PackageFactory(name="Y", slug="duplicate")

    def test_default_ordering_by_display_order(self):
        a = PackageFactory(display_order=10, name="A")
        b = PackageFactory(display_order=1, name="B")
        c = PackageFactory(display_order=5, name="C")
        ordered = list(Package.objects.all())
        assert ordered == [b, c, a]

    def test_negative_price_rejected(self):
        pkg = PackageFactory.build(price=Decimal("-1.00"))
        with pytest.raises(ValidationError):
            pkg.full_clean()

    def test_short_name_rejected(self):
        pkg = PackageFactory.build(name="AB")
        with pytest.raises(ValidationError):
            pkg.full_clean()

    def test_features_count_property(self):
        pkg = PackageFactory(features=["a", "b", "c"])
        assert pkg.features_count == 3

        empty = PackageFactory(features=[])
        assert empty.features_count == 0

    def test_is_active_default_true(self):
        pkg = PackageFactory()
        assert pkg.is_active is True

    def test_is_featured_default_false(self):
        pkg = PackageFactory()
        assert pkg.is_featured is False
