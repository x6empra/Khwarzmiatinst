"""
E2E — Dashboard flows (TESTING.md §E2E).

السيناريو 5: مشرف يدخل /dashboard/leads/ ويرى الطلبات.
السيناريو 6: مشرف يحدّث حالة طلب (HTMX) → اللون يتغير فوراً.
السيناريو 7: مستثمر يحاول /dashboard/ → 403.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from apps.leads.factories import LeadFactory
from apps.leads.models import LeadStatus

pytestmark = pytest.mark.django_db(transaction=True)


def _login(page: Page, base: str, email: str, password: str = "Test1234!") -> None:
    page.goto(base + "/accounts/login/")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')


def test_supervisor_sees_leads_in_dashboard(
    page: Page, live_server_url: str, supervisor, seeded_packages
) -> None:
    """السيناريو 5: مشرف يرى الطلبات."""
    LeadFactory(name="ZooLead", phone="0501112222", email="zoo@x.com")

    _login(page, live_server_url, "sup@e2e.test")
    page.goto(live_server_url + "/dashboard/leads/")

    expect(page.get_by_role("heading", name="إدارة الطلبات")).to_be_visible()
    expect(page.get_by_text("ZooLead")).to_be_visible()


def test_supervisor_updates_status_via_htmx(
    page: Page, live_server_url: str, supervisor, seeded_packages
) -> None:
    """السيناريو 6: تحديث حالة عبر <select> + HTMX."""
    lead = LeadFactory(name="StatusTest", status=LeadStatus.NEW)

    _login(page, live_server_url, "sup@e2e.test")
    page.goto(live_server_url + "/dashboard/leads/")

    row = page.locator(f'#lead-row-{lead.id}')
    expect(row).to_be_visible()
    expect(row.locator(".badge-status-new")).to_be_visible()

    # غيّر إلى "جاري التواصل"
    row.locator('select[name="status"]').select_option("in_progress")

    # HTMX يُعيد render الصف — ننتظر البادج الجديد
    expect(row.locator(".badge-status-progress")).to_be_visible(timeout=5_000)

    # تحقق من DB
    lead.refresh_from_db()
    assert lead.status == LeadStatus.IN_PROGRESS


def test_investor_blocked_from_dashboard(
    page: Page, live_server_url: str, investor
) -> None:
    """السيناريو 7: مستثمر يحاول الوصول → 403."""
    _login(page, live_server_url, "investor@e2e.test")
    page.goto(live_server_url + "/dashboard/")

    # 403 Forbidden — Django default error page
    expect(page.get_by_text("403", exact=False).first).to_be_visible()
