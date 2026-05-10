# CLAUDE.md — خوارزميات (Khawarizmiat)

## Project Overview
**خوارزميات** — منصة اشتراكات (Subscription Platform) للمعاهد التعليمية والمستثمرين في التعليم.
- **Core**: Lead Generation + Admin Dashboard + Real-time Notifications.
- **Roles (3)**: Manager (مدير) — Supervisor (مشرف) — Investor (مستثمر).
- **Phase 1**: 10 ميزات (8 Must + 2 Should) — End-to-End فقط.

## Tech Stack (محسوم — لا تغيير بدون موافقة مكتوبة)
- **Backend**: Django 5.x + Python 3.12+
- **Database**: PostgreSQL 16 (Django ORM فقط — لا raw SQL)
- **Frontend**: HTML + Tailwind CSS + HTMX + Vanilla JS
- **3D**: Spline.design (embed + lazy load)
- **Auth**: django-allauth
- **Forms**: Django Forms + DRF + Pydantic
- **Anti-Spam**: Google reCAPTCHA v3 (مخفي)
- **Notifications**: Django Signals + Email + Telegram Bot
- **Async**: Celery + Redis
- **Tests**: pytest + pytest-django + Playwright (Python)
- **Lint**: Ruff + Black + mypy + djlint
- **Storage**: Cloudinary (CDN + معالجة تلقائية)
- **Deploy**: Railway أو Render
- **Package Manager**: uv (موصى)

## Commands
- `uv run python manage.py runserver` — تشغيل التطوير
- `uv run pytest` — تشغيل الاختبارات
- `uv run ruff check --fix` — تنسيق وفحص
- `uv run python manage.py makemigrations && migrate`

## Workflow
1. **Plan Mode إلزامي** (Shift+Tab) قبل أي ميزة.
2. اقرأ: `@ROADMAP.md` `@FEATURES.md` `@PERMISSIONS.md` `@TECH_STACK.md`.
3. حدد الميزة من FEATURES.md (مثل F3).
4. اعرض **Implementation Plan ≤ 15 سطر** يحتوي:
   Feature ID + Goal + Models + Validation + Permissions + URL + Admin + Frontend + States + Tests + Files.
5. انتظر الموافقة قبل التنفيذ.

## القاعدة الجوهرية — End-to-End
كل ميزة تُبنى عبر **8 طبقات** في دورة واحدة:
`Database → Validation+Permissions → Backend API → Admin Dashboard → Frontend Template → States → Tests (Unit) → E2E (Playwright)`.
**لا ميزة جزئية. لا ربط ناقص. لا انتقال للتالية قبل اكتمال الطبقات الثماني.**

## Code Style
- Type hints **إلزامية** على كل function (`mypy strict`).
- لا `any` في Python — استخدم `Protocol` أو `TypeVar`.
- Django apps منفصلة لكل domain (لا app واحدة عملاقة).
- Models: `verbose_name` عربي + `Meta.ordering` واضح.
- Signals في `apps/<app>/signals.py` + ربطها في `apps.py`.
- Async tasks في `tasks.py` مع Celery.

## Critical Rules (8)
1. ❌ ممنوع mock data في أي طبقة (Hook PreToolUse).
2. ❌ ممنوع View بدون `permission_classes` أو `@login_required`.
3. ❌ ممنوع Form/Serializer بدون validators.
4. ❌ ممنوع نموذج عام بدون reCAPTCHA.
5. ❌ ممنوع تجاهل Loading / Error / Empty / Success states.
6. ❌ ممنوع تعديل Tech Stack بدون إذن.
7. ❌ ممنوع كتابة كود قبل Implementation Plan.
8. ❌ ممنوع ترك ميزة جزئية (يجب End-to-End).

## Security (مهم جداً)
- CSRF على كل POST (Django مدمج).
- ORM فقط — لا raw SQL (SQL injection).
- Rate limiting على نموذج الحجز (`django-ratelimit: 5/min`).
- reCAPTCHA v3 مخفي على نموذج الحجز.
- HTTPS only في production (`SECURE_SSL_REDIRECT`).
- Secrets في `.env` — لا في الكود.
- Django Admin محمي بـ MFA (`django-otp`).

## File References
`@CLAUDE.md` `@ROADMAP.md` `@FEATURES.md` `@TECH_STACK.md`
`@DESIGN_GUIDE.md` `@PERMISSIONS.md` `@INFRASTRUCTURE.md` `@TESTING.md`

## Hooks الإلزامية
- `PostToolUse: Edit|Write *.py` → ruff + black + mypy
- `PostToolUse: Edit|Write *.html` → djlint --reformat
- `PreToolUse: Bash` → يمنع `DROP TABLE`, `rm -rf`, `DELETE` بدون WHERE
- `PreToolUse: Edit` → يرفض `mock_data`, `fake_`, `dummy_`
- `PostToolUse: Edit views.py` → يتحقق من `permission_classes`
- `PostToolUse: Edit serializers.py` → يتحقق من validators
- `Stop` → `uv run pytest --tb=short` تلقائياً

## القاعدة الذهبية
> الميزة الواحدة المكتملة End-to-End أفضل من 10 ميزات نصف-مكتملة.
> كل سطر في Frontend يقابله Backend + DB + Admin + Tests.
