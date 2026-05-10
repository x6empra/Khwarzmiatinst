# TECH_STACK.md — Tech Stack المحسوم لخوارزميات

> ✅ حُسم لكل طبقة خيار واحد — **لا خلط، لا تغيير بدون موافقة مكتوبة**.

## الطبقات

| الطبقة | التقنية المعتمدة | السبب |
|---|---|---|
| **Backend Framework** | Django 5.x | قوة + سرعة + Admin مدمج + Signals |
| **Language** | Python 3.12+ | اللغة الأساسية المطلوبة |
| **Database** | PostgreSQL 16 | استقرار + سرعة + علاقات قوية |
| **ORM** | Django ORM | مدمج — لا حاجة لـ SQLAlchemy |
| **Frontend** | HTML + Tailwind CSS + Vanilla JS | بساطة + تحكم كامل + لا تعقيد SPA |
| **AJAX Library** | HTMX (موصى) أو Fetch API | نموذج تفاعلي بدون reload |
| **3D Engine** | Spline.design (embed) | مجسم 3D تفاعلي يتحرك مع الماوس |
| **Auth** | Django allauth | تسجيل + دخول + استعادة كلمة المرور |
| **Forms Validation** | Django Forms + Pydantic (للـ API) | Validation مزدوج (server + serializer) |
| **REST API** | Django REST Framework (DRF) | للـ AJAX endpoints |
| **API Docs** | drf-spectacular | OpenAPI تلقائياً من ViewSets |
| **Anti-Spam** | Google reCAPTCHA v3 (مخفي) | حماية بدون إزعاج المستخدم |
| **Notifications** | Django Signals + Email + Telegram Bot | تنبيهات فورية للإدارة |
| **Async Tasks** | Celery + Redis | للإشعارات والمهام الخلفية |
| **Caching** | Redis + Django cache framework | أداء سريع |
| **Testing (Unit)** | pytest + pytest-django | اختبارات Unit + Integration |
| **Testing (E2E)** | Playwright (Python) | اختبار المسار الكامل |
| **Linting** | Ruff + Black + mypy | عبر Hooks تلقائياً |
| **Templates Lint** | djlint | تنسيق Django templates |
| **Static Files** | WhiteNoise + Cloudinary | بساطة + CDN |
| **MFA** | django-otp | حماية Django Admin |
| **Rate Limiting** | django-ratelimit | حماية النماذج العامة |
| **Hijri Date** | django-hijri-converter | تواريخ هجرية + ميلادية |
| **Deployment** | Railway أو Render | أبسط من AWS لـ Phase 1 |
| **Package Manager** | uv (موصى) أو pip + requirements.txt | أسرع من pip |
| **Error Tracking** | Sentry | + MCP server |
| **Analytics** | Plausible | يحترم الخصوصية، خفيف |

## هيكل المشروع المعتمد — Django apps منفصلة

```
khawarizmiat/
├── apps/
│   ├── accounts/        # تسجيل وأدوار المستخدمين (Investor/Supervisor/Manager)
│   ├── packages/        # جدول الباقات وعرضها
│   ├── leads/           # جدول الطلبات (Leads) والـ Status Pipeline
│   ├── notifications/   # Django Signals + Telegram + Email
│   ├── dashboard/       # لوحة الإدارة المخصصة (للمشرف والمدير)
│   ├── landing/         # الصفحة الرئيسية + Spline 3D + نموذج الحجز
│   └── api/             # Django REST Framework (للـ AJAX endpoints)
├── config/              # settings, urls, wsgi
├── locale/              # ar/LC_MESSAGES/django.po
├── static/              # Tailwind output, JS, images
├── templates/           # base.html + shared
├── tests/               # E2E (Playwright)
├── manage.py
├── pyproject.toml
└── .env
```

## Frontend Architecture
- ❌ **لا React/Vue** — Tailwind + HTMX كافيان لـ Phase 1.
- استخدم Tailwind tokens من `DESIGN_GUIDE.md` (لا custom CSS عشوائي).
- RTL: `ms-/me-` بدلاً من `ml-/mr-` + `dir="rtl"` على html.
- Mobile First: ابدأ بـ 320px ثم وسّع.
- لا تكرر مكونات — استخدم `{% include %}` في Django templates.
- كل تفاعل HTMX له `hx-indicator` (Loading state).

## Database Rules
- `schema.sql` ليس مصدر الحقيقة — `models.py` هو.
- كل migration باسم وصفي (مثل `0003_add_status_to_lead`).
- لا تحذف عمود في production — استخدم soft delete.
- Indexes على الحقول المُستعلَمة (`status`, `created_at`).
- ForeignKey `on_delete` واضح (`PROTECT` للـ `Lead → Package`).
- لا raw SQL — Django ORM فقط (أمان CSRF/SQL injection).

## Validation Rules
كل نموذج يستقبل بيانات يجب أن يحتوي على validators:
- Required fields محددة
- Phone regex: `^(05|009665|9665|\+9665)[0-9]{8}$` (سعودي/خليجي)
- Email: `validate_email`
- Min/Max length واضح
- ForeignKey يجب أن يكون موجود
- reCAPTCHA token على كل نموذج عام

## ⚠️ قواعد ثابتة
1. **لا تغيير في Tech Stack بدون سبب موثق.**
2. أي مكتبة جديدة تتطلب إدخالها في `requirements.txt` + شرح.
3. **لا SPA framework** (React/Vue) — Tailwind + HTMX كافيان.
4. **لا تستبدل Postgres بـ SQLite** حتى للتطوير المحلي.
5. **لا تستخدم raw SQL** — Django ORM فقط.

## Git / Commit Convention
Conventional Commits بالإنجليزية:
- `feat(leads): add lead creation form with reCAPTCHA`
- `fix(dashboard): repair status update HTMX endpoint`
- `test(leads): add E2E test for lead pipeline`
- `refactor(packages): extract PackageCard component`
- `docs: update FEATURES.md after F3 completion`
- `chore: update Django to 5.1`
