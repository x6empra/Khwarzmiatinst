# TESTING.md — استراتيجية الاختبار لخوارزميات

## الفلسفة
> كل ميزة تمر بطبقتي اختبار: **Unit (pytest) + E2E (Playwright)**.
> لا ميزة تُعتبر مكتملة بدون الاثنين.

## الأدوات
- **Unit / Integration**: `pytest` + `pytest-django` + `pytest-cov`
- **Factory**: `factory_boy` لإنشاء بيانات اختبارية
- **E2E**: `playwright-python`
- **Coverage Target**: ≥ 80% (`pytest-cov`)

---

## أنواع الـ Unit Tests

| # | النوع | أمثلة لخوارزميات |
|---|---|---|
| 1 | **Model tests** | `test_lead_str` / `test_lead_default_status_is_new` |
| 2 | **Form/Serializer tests** | `test_lead_form_invalid_phone` / `test_email_required` |
| 3 | **View tests** | `test_create_lead_anonymous` / `test_dashboard_403_for_investor` |
| 4 | **Permission tests** | `test_only_manager_can_delete_lead` |
| 5 | **Signal tests** | `test_signal_sends_telegram_on_new_lead` |
| 6 | **تغطية مستهدفة** | ≥ 80% (`pytest-cov`) |

---

## E2E Scenarios (Playwright) — إلزامية لـ Phase 1

| # | السيناريو | النتيجة المتوقعة | الميزة |
|---|---|---|---|
| 1 | زائر يفتح `/` ويرى Hero 3D + الباقات | كل العناصر تظهر بدون أخطاء | F1, F2 |
| 2 | زائر يملأ نموذج الحجز ويرسل | Modal نجاح أخضر + Lead في DB | F3 |
| 3 | مستثمر يسجل ويفعّل إيميله | ينتقل لصفحة الباقات | F4 |
| 4 | مستثمر يقدم طلب وهو مسجّل | Lead مرتبط بحسابه + يظهر في `/profile/orders/` | F4 + F10 |
| 5 | مشرف يدخل `/dashboard/leads/` | يرى كل الطلبات الجديدة | F5 |
| 6 | مشرف يحدّث حالة طلب من جديد إلى جاري | اللون يتغير فوراً (HTMX) + المستثمر يرى التحديث | F6 |
| 7 | مستثمر يحاول الوصول لـ `/dashboard/` | 403 Forbidden | Permissions |
| 8 | محاولة spam على نموذج الحجز | reCAPTCHA يرفض | F8 |

---

## بنية المجلدات

```
khawarizmiat/
├── apps/
│   ├── leads/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_forms.py
│   │   │   ├── test_serializers.py
│   │   │   ├── test_views.py
│   │   │   ├── test_permissions.py
│   │   │   └── test_signals.py
│   │   └── factories.py
│   ├── packages/
│   │   └── tests/...
│   └── ...
└── tests/
    └── e2e/
        ├── conftest.py
        ├── test_lead_flow.py
        ├── test_auth_flow.py
        ├── test_dashboard_flow.py
        └── test_permissions_flow.py
```

---

## أمثلة Unit Tests

### Model Test
```python
# apps/leads/tests/test_models.py
import pytest
from apps.leads.models import Lead

@pytest.mark.django_db
def test_lead_default_status_is_new(package):
    lead = Lead.objects.create(
        name="أحمد",
        phone="0501234567",
        email="ahmed@test.com",
        package=package,
    )
    assert lead.status == 'new'
```

### Form Test
```python
# apps/leads/tests/test_forms.py
import pytest
from apps.leads.forms import LeadForm

@pytest.mark.django_db
def test_lead_form_invalid_phone(package):
    form = LeadForm(data={
        'name': 'أحمد',
        'phone': '123',  # invalid
        'email': 'ahmed@test.com',
        'package': package.id,
    })
    assert not form.is_valid()
    assert 'phone' in form.errors
```

### View Test
```python
# apps/leads/tests/test_views.py
import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_create_lead_anonymous(package):
    client = APIClient()
    response = client.post('/api/leads/create/', {
        'name': 'أحمد',
        'phone': '0501234567',
        'email': 'ahmed@test.com',
        'package': package.id,
        'recaptcha_token': 'mock-valid-token',
    })
    assert response.status_code == 201
```

### Permission Test
```python
@pytest.mark.django_db
def test_dashboard_403_for_investor(investor_user, client):
    client.force_login(investor_user)
    response = client.get('/dashboard/')
    assert response.status_code == 403
```

### Signal Test
```python
# apps/notifications/tests/test_signals.py
from unittest.mock import patch

@pytest.mark.django_db
@patch('apps.notifications.tasks.send_telegram_to_admin.delay')
def test_signal_sends_telegram_on_new_lead(mock_telegram, package):
    Lead.objects.create(name='x', phone='0501234567', email='x@x.com', package=package)
    mock_telegram.assert_called_once()
```

---

## مثال E2E Test (Playwright)

```python
# tests/e2e/test_lead_flow.py
from playwright.sync_api import Page, expect

def test_complete_lead_flow(page: Page, live_server):
    # 1. زائر يفتح Landing
    page.goto(live_server.url)
    expect(page.get_by_text('خوارزميات')).to_be_visible()

    # 2. يملأ النموذج
    page.fill('input[name=name]', 'أحمد محمد')
    page.fill('input[name=phone]', '0501234567')
    page.fill('input[name=email]', 'ahmed@test.com')
    page.select_option('select[name=package]', value='1')

    # 3. يرسل
    page.click('button[type=submit]')

    # 4. يرى Modal نجاح
    expect(page.get_by_text('تم استلام طلبك')).to_be_visible()
```

---

## Fixtures (conftest.py)

```python
# conftest.py
import pytest
from apps.accounts.factories import UserFactory, InvestorFactory, SupervisorFactory, ManagerFactory
from apps.packages.factories import PackageFactory

@pytest.fixture
def investor_user():
    return InvestorFactory()

@pytest.fixture
def supervisor_user():
    return SupervisorFactory()

@pytest.fixture
def manager_user():
    return ManagerFactory()

@pytest.fixture
def package():
    return PackageFactory()
```

---

## QA Checklist (قبل النشر)

### الميزة الواحدة
- [ ] Unit tests تمر (pytest)
- [ ] Coverage ≥ 80%
- [ ] E2E test يمر (Playwright)
- [ ] Loading state يظهر
- [ ] Error state يظهر
- [ ] Empty state يظهر
- [ ] Success state يظهر
- [ ] RTL يعمل
- [ ] Mobile (320px) يعمل
- [ ] Tablet (768px) يعمل
- [ ] Desktop (1280px+) يعمل
- [ ] Tab navigation تعمل
- [ ] Focus indicators ظاهرة
- [ ] Screen reader يقرأ المحتوى صحيح

### قبل Deploy
- [ ] كل الميزات في `FEATURES.md` ✅
- [ ] كل اختبارات pytest تمر
- [ ] كل اختبارات Playwright تمر
- [ ] Coverage ≥ 80%
- [ ] لا linting errors (Ruff + Black + mypy + djlint)
- [ ] LCP < 2.5s
- [ ] لا أخطاء في Sentry
- [ ] HTTPS مفعّل
- [ ] reCAPTCHA يعمل
- [ ] Telegram notifications تصل
- [ ] DB backup مفعّل
- [ ] Admin محمي بـ MFA
- [ ] SECRET_KEY قوي + DEBUG=False
- [ ] `.env` في `.gitignore`

---

## CI Configuration (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run ruff check
      - run: uv run black --check .
      - run: uv run mypy .
      - run: uv run pytest --cov --cov-report=xml
      - run: uv run playwright install --with-deps chromium
      - run: uv run pytest tests/e2e
```

---

## سجل الاختبارات (يُحدَّث بعد كل ميزة)

| Feature | Unit Tests | Coverage | E2E | Status |
|---|---|---|---|---|
| F1 — Landing | — | — | — | ⏳ |
| F2 — Packages | 24 ✅ | — | ⏳ | 🟡 unit done, E2E pending |
| F3 — Lead Form | 35 ✅ | — | ⏳ | 🟡 unit done, E2E pending |
| F4 — Auth | 35 ✅ | — | ⏳ | 🟡 unit done, E2E pending |
| F5 — Dashboard | — | — | — | ⏳ |
| F6 — Status Pipeline | — | — | — | ⏳ |
| F7 — Signals | 14 ✅ | — | ⏳ | ✅ telegram + tasks + signals |
| F8 — reCAPTCHA | 6 ✅ | — | ⏳ | ✅ utility + integration |
| F9 — Profile | — | — | — | ⏳ |
| F10 — Order Tracking | — | — | — | ⏳ |
