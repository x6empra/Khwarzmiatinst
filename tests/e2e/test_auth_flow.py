"""
E2E — Auth flows (TESTING.md §E2E).

السيناريو 3: مستثمر يسجل ويدخل.
السيناريو 4: مستثمر مسجَّل يقدم طلب → يظهر في /profile/orders/.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

pytestmark = pytest.mark.django_db(transaction=True)


def test_investor_can_register_and_login(
    page: Page, live_server_url: str
) -> None:
    """السيناريو 3: تسجيل + دخول."""
    page.goto(live_server_url + "/accounts/register/")

    page.fill('input[name="first_name"]', "مستثمر")
    page.fill('input[name="last_name"]', "جديد")
    page.fill('input[name="email"]', "newinv@e2e.test")
    page.fill('input[name="phone"]', "0501112233")
    page.fill('input[name="password1"]', "StrongP@ssw0rd")
    page.fill('input[name="password2"]', "StrongP@ssw0rd")
    page.click('button[type="submit"]')

    # بعد النجاح يُحوَّل للصفحة الرئيسية
    expect(page).to_have_url(live_server_url + "/")
    # Header يعرض اسمه
    expect(page.get_by_text("مرحباً، مستثمر")).to_be_visible()

    from apps.accounts.models import User

    assert User.objects.filter(email="newinv@e2e.test").exists()


def test_logged_in_investor_lead_appears_in_profile_orders(
    page: Page, live_server_url: str, investor, seeded_packages
) -> None:
    """السيناريو 4: مستثمر مسجَّل يقدم طلب → يربطه به → /profile/orders/ يعرضه."""
    # 1) دخول
    page.goto(live_server_url + "/accounts/login/")
    page.fill('input[name="email"]', "investor@e2e.test")
    page.fill('input[name="password"]', "Test1234!")
    page.click('button[type="submit"]')
    expect(page).to_have_url(live_server_url + "/")

    # 2) إرسال طلب
    page.goto(live_server_url + "/#booking")
    page.fill('input[name="name"]', "مستثمر مسجَّل")
    page.fill('input[name="phone"]', "0509998877")
    page.fill('input[name="email"]', "investor@e2e.test")
    page.select_option('select[name="package"]', label="الباقة الفضية")
    page.click('#booking-form button[type="submit"]')
    expect(page.get_by_text("تم استلام طلبك")).to_be_visible(timeout=5_000)

    # 3) التحقق من profile/orders
    page.goto(live_server_url + "/profile/orders/")
    expect(page.get_by_role("heading", name="طلباتي")).to_be_visible()
    expect(page.get_by_text("الباقة الفضية").first).to_be_visible()
