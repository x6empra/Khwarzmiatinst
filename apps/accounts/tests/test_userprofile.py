"""UserProfile model + signal — F9 (DATABASE.md §2)."""

import pytest

from apps.accounts.factories import InvestorFactory, ManagerFactory, SupervisorFactory
from apps.accounts.models import UserProfile


@pytest.mark.django_db
class TestUserProfileSignal:
    def test_profile_auto_created_for_investor(self):
        user = InvestorFactory()
        assert UserProfile.objects.filter(user=user).exists()

    def test_profile_auto_created_for_supervisor(self):
        user = SupervisorFactory()
        assert UserProfile.objects.filter(user=user).exists()

    def test_profile_auto_created_for_manager(self):
        user = ManagerFactory()
        assert UserProfile.objects.filter(user=user).exists()

    def test_profile_not_duplicated_on_save(self):
        user = InvestorFactory()
        user.first_name = "تحديث"
        user.save()
        assert UserProfile.objects.filter(user=user).count() == 1


@pytest.mark.django_db
class TestUserProfileModel:
    def test_str_includes_email(self):
        user = InvestorFactory(email="ahmed@x.com")
        profile = user.profile
        assert "ahmed@x.com" in str(profile)

    def test_optional_fields_default_blank(self):
        user = InvestorFactory()
        profile = user.profile
        assert profile.company_name == ""
        assert profile.city == ""
        assert profile.bio == ""
        assert not profile.avatar

    def test_cascade_on_user_delete(self):
        user = InvestorFactory()
        profile_id = user.profile.id
        user.delete()
        assert not UserProfile.objects.filter(id=profile_id).exists()
