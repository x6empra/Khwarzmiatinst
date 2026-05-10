"""Playwright E2E fixtures — TESTING.md §E2E."""

from __future__ import annotations

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from apps.accounts.factories import (
    InvestorFactory,
    ManagerFactory,
    SupervisorFactory,
)
from apps.packages.factories import PackageFactory


@pytest.fixture(scope="session")
def browser_context_args():
    """RTL-friendly defaults — DESIGN_GUIDE.md §RTL."""
    return {
        "viewport": {"width": 1280, "height": 800},
        "locale": "ar-SA",
        "ignore_https_errors": True,
    }


@pytest.fixture
def live_server_url(live_server):
    return live_server.url


@pytest.fixture
def seeded_packages(db):
    """3 باقات نشطة + 1 مخفية."""
    return [
        PackageFactory(name="الباقة الذهبية", display_order=1, is_featured=True, price="2999"),
        PackageFactory(name="الباقة الفضية", display_order=2, price="1499"),
        PackageFactory(name="الباقة البرونزية", display_order=3, price="599"),
        PackageFactory(name="مخفية", display_order=99, is_active=False),
    ]


@pytest.fixture
def investor(db):
    return InvestorFactory(email="investor@e2e.test", password="Test1234!")


@pytest.fixture
def supervisor(db):
    return SupervisorFactory(email="sup@e2e.test", password="Test1234!")


@pytest.fixture
def manager(db):
    return ManagerFactory(email="mgr@e2e.test", password="Test1234!")
