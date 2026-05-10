"""Permission tests — TESTING.md §Unit + PERMISSIONS.md."""

import pytest
from rest_framework.test import APIRequestFactory

from apps.accounts.factories import InvestorFactory, ManagerFactory, SupervisorFactory
from apps.accounts.permissions import (
    IsInvestor,
    IsManager,
    IsOwnerInvestor,
    IsSupervisor,
)


@pytest.fixture
def rf():
    return APIRequestFactory()


@pytest.mark.django_db
class TestIsInvestor:
    def test_investor_passes(self, rf):
        req = rf.get("/")
        req.user = InvestorFactory()
        assert IsInvestor().has_permission(req, None)

    def test_supervisor_fails(self, rf):
        req = rf.get("/")
        req.user = SupervisorFactory()
        assert not IsInvestor().has_permission(req, None)


@pytest.mark.django_db
class TestIsSupervisor:
    """Supervisor + Manager (staff_roles) — مرجع PERMISSIONS.md."""

    def test_supervisor_passes(self, rf):
        req = rf.get("/")
        req.user = SupervisorFactory()
        assert IsSupervisor().has_permission(req, None)

    def test_manager_passes(self, rf):
        req = rf.get("/")
        req.user = ManagerFactory()
        assert IsSupervisor().has_permission(req, None)

    def test_investor_fails(self, rf):
        req = rf.get("/")
        req.user = InvestorFactory()
        assert not IsSupervisor().has_permission(req, None)


@pytest.mark.django_db
class TestIsManager:
    def test_only_manager_passes(self, rf):
        req = rf.get("/")
        req.user = ManagerFactory()
        assert IsManager().has_permission(req, None)

    def test_supervisor_fails_at_manager_only(self, rf):
        req = rf.get("/")
        req.user = SupervisorFactory()
        assert not IsManager().has_permission(req, None)


@pytest.mark.django_db
class TestIsOwnerInvestor:
    """Object-level: investor sees only own objects."""

    def test_owner_passes(self, rf):
        owner = InvestorFactory()

        class Obj:
            investor = owner

        req = rf.get("/")
        req.user = owner
        assert IsOwnerInvestor().has_object_permission(req, None, Obj())

    def test_other_investor_fails(self, rf):
        owner = InvestorFactory(email="o@x.com")
        other = InvestorFactory(email="other@x.com")

        class Obj:
            investor = owner

        req = rf.get("/")
        req.user = other
        assert not IsOwnerInvestor().has_object_permission(req, None, Obj())
