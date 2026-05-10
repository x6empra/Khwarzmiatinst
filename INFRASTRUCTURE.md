# INFRASTRUCTURE.md — البنية التحتية لخوارزميات

## نظرة عامة
هذا الملف يجمع كل ما يخص: تخزين الملفات، التدويل (i18n + RTL)، SEO، الأداء، التتبع، النشر.

---

## 1. معالجة الملفات والصور (Cloudinary)

| السؤال | الإجابة |
|---|---|
| أنواع الملفات | صور باقات (jpg/png/webp) فقط في Phase 1 |
| الحد الأقصى | 2 MB لكل صورة |
| مزود التخزين | **Cloudinary** (CDN + معالجة تلقائية) |
| الضغط التلقائي | Cloudinary `auto:format` + `auto:quality` |
| الأحجام المتعددة | thumbnail (150px) / medium (600px) / full (1200px) |
| التحقق من النوع | MIME + magic bytes (`python-magic`) |

### إعداد Cloudinary
```python
# settings.py
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

---

## 2. التدويل والاتجاه (i18n + RTL)

| السؤال | الإجابة |
|---|---|
| اللغات | عربي فقط في Phase 1 (إنجليزي في Phase 2) |
| مكتبة الترجمة | Django i18n المدمج + `django.po` files |
| RTL | `dir="rtl"` + Tailwind RTL plugin |
| الخطوط | Cairo (عربي) من Google Fonts |
| تنسيق الأرقام | Western Arabic (123) — أوضح في الفواتير |
| تنسيق التاريخ | هجري + ميلادي معاً (`django-hijri-converter`) |

### إعدادات Django i18n
```python
# settings.py
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [('ar', 'العربية')]
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### RTL Rules
- `dir="rtl"` على عنصر `<html>`.
- استخدم `ms-` و `me-` بدلاً من `ml-` / `mr-`.
- Mobile First: ابدأ بـ 320px ثم وسّع.

---

## 3. SEO والأداء والتتبع

| السؤال | الإجابة |
|---|---|
| فهرسة Google | نعم — صفحة Landing عامة |
| Open Graph | نعم — للمشاركة على لينكدإن وتويتر |
| Schema.org | Organization + Service + FAQPage |
| Analytics | **Plausible** (يحترم الخصوصية، خفيف) |
| Error Tracking | **Sentry** (Django integration + MCP server) |
| أهداف الأداء | LCP < 2.5s / INP < 200ms / CLS < 0.1 |
| Performance Budget | Bundle JS < 200KB / Spline lazy-loaded |
| Caching | Redis + Django cache framework |

### sitemap.xml + robots.txt
- استخدم `django.contrib.sitemaps`.
- `robots.txt` يسمح بـ Landing فقط، يحجب `/admin/` و `/dashboard/`.

### Open Graph Tags (في base.html)
```html
<meta property="og:title" content="خوارزميات — منصة الاشتراكات للمعاهد">
<meta property="og:description" content="...">
<meta property="og:image" content="https://res.cloudinary.com/.../og.jpg">
<meta property="og:type" content="website">
```

---

## 4. الإشعارات (Telegram + Email)

### Telegram Bot
- Bot Token من `@BotFather`.
- Chat ID للإدارة.
- يُرسل: عند إنشاء Lead جديد، عند تحديث الحالة.

### Email
- نسخة احتياطية للإشعارات.
- استخدم SMTP أو SendGrid.
- Django Templates للقوالب.

### Celery Tasks
```python
# apps/notifications/tasks.py
@shared_task(bind=True, max_retries=3)
def send_telegram_to_admin(self, lead_id: int) -> None:
    ...

@shared_task(bind=True, max_retries=3)
def send_email_to_admin(self, lead_id: int) -> None:
    ...
```

---

## 5. متغيرات البيئة (.env)

| المتغير | القيمة |
|---|---|
| `DATABASE_URL` | `postgres://user:pass@host:5432/khawarizmiat` |
| `SECRET_KEY` | django secret (50+ حرف عشوائي) |
| `DEBUG` | `False` في production |
| `ALLOWED_HOSTS` | `khawarizmiat.com,www.khawarizmiat.com` |
| `RECAPTCHA_PUBLIC_KEY` | من Google reCAPTCHA |
| `RECAPTCHA_PRIVATE_KEY` | من Google reCAPTCHA |
| `TELEGRAM_BOT_TOKEN` | للإشعارات |
| `TELEGRAM_ADMIN_CHAT_ID` | chat id للإدارة |
| `CLOUDINARY_URL` | `cloudinary://...` |
| `CLOUDINARY_CLOUD_NAME` | اسم cloud |
| `CLOUDINARY_API_KEY` | api key |
| `CLOUDINARY_API_SECRET` | api secret |
| `SENTRY_DSN` | من Sentry |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `EMAIL_HOST` | SMTP أو SendGrid |
| `EMAIL_HOST_USER` | بريد الإرسال |
| `EMAIL_HOST_PASSWORD` | كلمة مرور البريد |
| `PLAUSIBLE_DOMAIN` | `khawarizmiat.com` |

---

## 6. النشر (Deployment)

### Railway / Render
- **Railway** (موصى) أو **Render** — أبسط من AWS لـ Phase 1.
- خدمات مطلوبة:
  - Django (Web Service) — Python 3.12
  - PostgreSQL 16 (Managed DB)
  - Redis (Managed) للـ Celery
  - Celery Worker (Background Service)
  - Celery Beat (Scheduled Tasks — اختياري)

### إعدادات Production
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Static Files (WhiteNoise)
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### CI/CD
- GitHub Actions على كل push:
  1. Lint (Ruff + Black + mypy + djlint)
  2. Tests (pytest + coverage)
  3. Deploy على main branch (Railway/Render webhook)

---

## 7. النسخ الاحتياطي (Backup)
- **PostgreSQL**: نسخة يومية تلقائية على Railway/Render.
- **Cloudinary**: backup مدمج في الخدمة.
- **Code**: GitHub.

## 8. Monitoring
- **Uptime**: UptimeRobot أو Better Stack.
- **Error Tracking**: Sentry.
- **Analytics**: Plausible.
- **Performance**: Lighthouse CI + Sentry Performance.

## 9. Domains & DNS
- Domain: `khawarizmiat.com` + `www.khawarizmiat.com`.
- SSL: Let's Encrypt (تلقائي على Railway/Render).
- CDN: Cloudinary للصور + WhiteNoise للـ static files.

---

## 10. Performance Checklist
- [ ] LCP < 2.5s (قياس بـ Lighthouse)
- [ ] INP < 200ms
- [ ] CLS < 0.1
- [ ] Bundle JS < 200KB
- [ ] Spline lazy-loaded
- [ ] Images optimized (Cloudinary `auto:format`)
- [ ] Redis caching مفعّل
- [ ] Database indexes على الحقول المُستعلَمة
- [ ] HTTP/2 + Gzip/Brotli
