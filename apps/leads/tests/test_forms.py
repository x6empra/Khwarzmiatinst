"""LeadForm tests — TESTING.md §Unit (validators)."""

import pytest

from apps.leads.forms import LeadForm
from apps.packages.factories import PackageFactory


@pytest.fixture
def base_data(db):
    pkg = PackageFactory(is_active=True)
    return {
        "name": "أحمد محمد",
        "phone": "0501234567",
        "email": "ahmed@test.com",
        "package": pkg.id,
        "notes": "أرغب بمعرفة المزيد",
    }


@pytest.mark.django_db
class TestLeadForm:
    def test_valid_form_passes(self, base_data):
        form = LeadForm(base_data)
        assert form.is_valid(), form.errors

    def test_short_name_rejected(self, base_data):
        form = LeadForm({**base_data, "name": "A"})
        assert not form.is_valid()
        assert "name" in form.errors

    def test_invalid_phone_rejected(self, base_data):
        form = LeadForm({**base_data, "phone": "12345"})
        assert not form.is_valid()
        assert "phone" in form.errors

    @pytest.mark.parametrize(
        "phone", ["0501234567", "00966501234567", "+966501234567", "966501234567"]
    )
    def test_valid_phone_formats(self, base_data, phone):
        form = LeadForm({**base_data, "phone": phone})
        assert form.is_valid(), form.errors

    def test_invalid_email_rejected(self, base_data):
        form = LeadForm({**base_data, "email": "not-an-email"})
        assert not form.is_valid()
        assert "email" in form.errors

    def test_inactive_package_rejected(self, base_data):
        inactive = PackageFactory(is_active=False)
        form = LeadForm({**base_data, "package": inactive.id})
        assert not form.is_valid()
        assert "package" in form.errors

    def test_email_normalized_to_lowercase(self, base_data):
        form = LeadForm({**base_data, "email": "AHMED@TEST.COM"})
        assert form.is_valid(), form.errors
        assert form.cleaned_data["email"] == "ahmed@test.com"

    def test_name_stripped(self, base_data):
        form = LeadForm({**base_data, "name": "  أحمد  "})
        assert form.is_valid(), form.errors
        assert form.cleaned_data["name"] == "أحمد"

    def test_notes_optional(self, base_data):
        form = LeadForm({**base_data, "notes": ""})
        assert form.is_valid(), form.errors
