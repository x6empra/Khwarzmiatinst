# خوارزميات (Khawarizmiat)

> منصة الاشتراكات للمعاهد التعليمية والمستثمرين في التعليم.
> Django · PostgreSQL · Tailwind · HTMX · Spline 3D.

---

## 📚 الوثائق

| الملف | الغرض |
|---|---|
| [CLAUDE.md](CLAUDE.md) | تعليمات Claude Code (Plan Mode + Hooks + 8 قواعد) |
| [ROADMAP.md](ROADMAP.md) | خطة Phase 1 (15 خطوة، ~18 يوم) |
| [FEATURES.md](FEATURES.md) | قائمة الميزات F1-F13 + الحالة |
| [TECH_STACK.md](TECH_STACK.md) | Tech Stack المحسوم — لا تغيير بدون موافقة |
| [DESIGN_GUIDE.md](DESIGN_GUIDE.md) | الألوان + Tokens + Components + WCAG |
| [DATABASE.md](DATABASE.md) | تصميم Models — مصدره `models.py` |
| [API.md](API.md) | عقد API — مصدره `drf-spectacular` |
| [PERMISSIONS.md](PERMISSIONS.md) | 4 أدوار + Auth Flow + الأمان |
| [INFRASTRUCTURE.md](INFRASTRUCTURE.md) | Cloudinary + reCAPTCHA + Telegram + Deploy |
| [TESTING.md](TESTING.md) | pytest + Playwright + QA Checklist |

---

## 🚀 البدء السريع

### المتطلبات
- Python 3.12+
- PostgreSQL 16
- Redis 7
- Node 20 (لـ Tailwind)
- [uv](https://github.com/astral-sh/uv) — مدير الحزم

### التثبيت

```bash
# 1. متغيرات البيئة
cp .env.example .env
# املأ القيم في .env

# 2. تثبيت Python deps
uv sync --all-extras

# 3. تثبيت Tailwind
npm install

# 4. إنشاء قاعدة البيانات
createdb khawarizmiat_dev

# 5. Migrations
uv run python manage.py migrate

# 6. تشغيل Tailwind في خلفية
npm run watch:css &

# 7. تشغيل الخادم
uv run python manage.py runserver
```

افتح [http://localhost:8000](http://localhost:8000).

---

## 🧪 الاختبارات

```bash
# Unit + integration
uv run pytest

# مع coverage
uv run pytest --cov --cov-report=html

# E2E (Playwright)
uv run playwright install chromium
uv run pytest tests/e2e
```

---

## 🛠️ أوامر مفيدة

```bash
# Lint + Format
uv run ruff check --fix .
uv run black .
uv run mypy .
uv run djlint --reformat templates/

# Migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Superuser
uv run python manage.py createsuperuser

# Tailwind build
npm run build:css
```

---

## 🗂️ هيكل المشروع

```
خوارزميات للمعاهد/
├── apps/
│   ├── core/           # validators + base templates + health
│   ├── accounts/       # F4 — User/Investor/Supervisor/Manager
│   ├── packages/       # F2 — الباقات
│   ├── leads/          # F3, F6 — الطلبات + Status Pipeline
│   ├── notifications/  # F7 — Signals + Telegram + Email
│   ├── dashboard/      # F5 — لوحة الإدارة
│   ├── landing/        # F1 — Hero 3D + الصفحة الرئيسية
│   └── api/            # DRF endpoints
├── config/
│   ├── settings/       # base/development/production
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── templates/          # base.html
├── static/
│   ├── src/input.css   # Tailwind source
│   └── dist/           # Tailwind compiled
├── locale/ar/          # ترجمات
├── tests/              # smoke + E2E
└── pyproject.toml
```

---

## 🔐 الأمان

- CSRF protection على كل POST (Django مدمج)
- ORM فقط — لا raw SQL
- reCAPTCHA v3 على نموذج الحجز
- Rate limiting (5/min)
- HTTPS only في production
- Django Admin محمي بـ MFA (`django-otp`)

---

## 📜 التراخيص
داخلي — كل الحقوق محفوظة لفريق خوارزميات.
