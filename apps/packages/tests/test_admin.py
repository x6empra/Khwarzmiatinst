"""Admin tests for package image management."""

import pytest
from django.contrib import admin

from apps.packages.admin import PackageAdmin
from apps.packages.models import Package


@pytest.mark.django_db
class TestPackageAdmin:
    def test_image_field_is_editable_with_preview(self):
        package_admin = admin.site._registry[Package]
        assert isinstance(package_admin, PackageAdmin)
        assert package_admin.readonly_fields == ("thumb_large", "created_at", "updated_at")
        fieldsets = package_admin.get_fieldsets(request=None)
        content_fields = fieldsets[2][1]["fields"]
        assert "image" in content_fields
        assert "thumb_large" in content_fields
