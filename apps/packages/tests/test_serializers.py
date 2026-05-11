"""Serializer tests — TESTING.md §Unit (API.md fields)."""

import pytest

from apps.packages.factories import PackageFactory
from apps.packages.serializers import PackageSerializer


@pytest.mark.django_db
class TestPackageSerializer:
    def test_fields_match_api_contract(self):
        """API.md §Packages — قائمة الحقول الظاهرة للزائر."""
        pkg = PackageFactory()
        data = PackageSerializer(pkg).data
        expected = {
            "id",
            "name",
            "slug",
            "description",
            "price",
            "duration_months",
            "features",
            "image_url",
            "is_featured",
        }
        assert set(data.keys()) == expected

    def test_image_url_is_none_when_no_image(self):
        pkg = PackageFactory(image=None)
        data = PackageSerializer(pkg).data
        assert data["image_url"] is None

    def test_image_url_uses_package_image(self):
        pkg = PackageFactory(image="packages/package-silver.png")
        data = PackageSerializer(pkg).data
        assert data["image_url"] == "/media/packages/package-silver.png"

    def test_features_serialized_as_list(self):
        pkg = PackageFactory(features=["x", "y", "z"])
        data = PackageSerializer(pkg).data
        assert data["features"] == ["x", "y", "z"]

    def test_price_serialized_as_string(self):
        """DRF DecimalField → string لتجنب فقدان الدقة في JSON."""
        pkg = PackageFactory(price="1499.50")
        data = PackageSerializer(pkg).data
        assert data["price"] == "1499.50"
