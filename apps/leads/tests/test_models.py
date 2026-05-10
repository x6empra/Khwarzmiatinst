"""Lead model tests — TESTING.md §Unit (DATABASE.md §4)."""

import pytest
from django.db import IntegrityError
from django.db.models import ProtectedError

from apps.leads.factories import LeadFactory
from apps.leads.models import Lead, LeadStatus
from apps.packages.factories import PackageFactory


@pytest.mark.django_db
class TestLeadModel:
    def test_default_status_is_new(self):
        lead = LeadFactory()
        assert lead.status == LeadStatus.NEW
        assert lead.is_new

    def test_default_ordering_by_created_desc(self):
        a = LeadFactory(name="A")
        b = LeadFactory(name="B")
        assert list(Lead.objects.all()) == [b, a]

    def test_str_includes_name_package_status(self):
        pkg = PackageFactory(name="الذهبية")
        lead = LeadFactory(name="أحمد", package=pkg)
        s = str(lead)
        assert "أحمد" in s
        assert "الذهبية" in s
        assert "جديد" in s  # display value

    def test_package_protect_on_delete(self):
        """DATABASE.md §Relations: Lead → Package on_delete=PROTECT."""
        pkg = PackageFactory()
        LeadFactory(package=pkg)
        with pytest.raises(ProtectedError):
            pkg.delete()

    def test_investor_set_null_on_delete(self):
        """DATABASE.md §Relations: Lead → User(investor) on_delete=SET_NULL."""
        from apps.accounts.factories import InvestorFactory
        investor = InvestorFactory()
        lead = LeadFactory(investor=investor)

        investor.delete()
        lead.refresh_from_db()
        assert lead.investor is None

    def test_status_choices_are_four(self):
        assert {choice[0] for choice in LeadStatus.choices} == {
            "new", "in_progress", "closed", "cancelled"
        }
