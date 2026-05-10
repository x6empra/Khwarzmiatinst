# FEATURES.md — قائمة ميزات خوارزميات

> **حالة الميزة**: ⏳ Pending · 🟡 In Progress · ✅ Done

## Phase 1 — Must Have (8)

| ID | الميزة | MoSCoW | المرحلة | الحالة |
|---|---|---|---|---|
| **F1** | صفحة هبوط (Landing) بكحلي + Spline 3D | Must | Phase 1 | ✅ |
| **F2** | عرض الباقات (Packages Display) | Must | Phase 1 | ✅ |
| **F3** | نموذج حجز ذكي (AJAX — بدون reload) | Must | Phase 1 | ✅ |
| **F4** | تسجيل/دخول المستثمر | Must | Phase 1 | ✅ |
| **F5** | لوحة تحكم الإدارة (Admin Dashboard) | Must | Phase 1 | ✅ |
| **F6** | تحديث حالة الطلب (Status Pipeline) | Must | Phase 1 | ✅ |
| **F7** | إشعارات فورية للإدارة (Django Signals) | Must | Phase 1 | ✅ |
| **F8** | حماية reCAPTCHA على نموذج الحجز | Must | Phase 1 | ✅ |

## Phase 1 — Should Have (2)

| ID | الميزة | MoSCoW | المرحلة | الحالة |
|---|---|---|---|---|
| **F9** | صفحة الملف الشخصي للمستثمر | Should | Phase 1 | ✅ |
| **F10** | متابعة المستثمر لحالة طلباته | Should | Phase 1 | ✅ |

## Phase 2 — Could Have

| ID | الميزة | MoSCoW | المرحلة | الحالة |
|---|---|---|---|---|
| **F11** | تقارير وإحصائيات للمدير | Could | Phase 2 | ⏳ |
| **F12** | نظام دفع مدمج | Could | Phase 2 | ⏳ |

## مستبعد

| ID | الميزة | MoSCoW | الحالة |
|---|---|---|---|
| **F13** | تطبيق جوال | Won't | لاحقاً |

---

## نطاق Phase 1
🎯 **8 ميزات Must + 2 Should = 10 ميزات.**
هذا هو الحد الأدنى لمنصة شغالة End-to-End. **لا تضف Phase 2 قبل اكتمال Phase 1.**

---

## تفاصيل الميزات

### F1 — صفحة الهبوط (Landing) ✅
- ✅ Hero بـ Gradient كحلي + Glassmorphism + 3 orbs متحركة + grid أيقونات تعليمية.
- ✅ Spline 3D lazy-load عبر `IntersectionObserver` — يُحقن فقط عند الـ viewport + وجود `SPLINE_SCENE_URL`.
- ✅ Fallback Glassmorphism أنيق (CSS-only) لو لا Spline أو الجوال أو reduced-motion.
- ✅ `prefers-reduced-motion: reduce` يعطّل كل الـ animations.
- ✅ Mobile fallback: orb-3 hidden + لا Spline.
- ✅ Sections: Hero · Features (6) · Packages (F2) · FAQ (6 سؤال) · Booking (F3) · Footer (4-cols).
- ✅ SEO كامل: Open Graph + Twitter Card + canonical + Schema.org (Organization + Service + FAQPage JSON-LD) + meta robots.
- ✅ `sitemap.xml` (Django sitemaps) + `robots.txt` (يحجب admin/dashboard/api).
- ✅ Performance: preconnect للخطوط + `dns-prefetch` لـ unpkg + Spline lazy + lazy images.
- ✅ Tests: 18 (page sections + SEO meta + Schema.org + sitemap + robots + Spline fallback + reduced-motion).

### F2 — عرض الباقات (Packages Display) ✅
- ✅ Model: `Package` بكل حقول DATABASE.md §3 (slug auto بدعم Unicode + indexes).
- ✅ Serializer: `PackageSerializer` يطابق عقد API.md (image_url مع build_absolute_uri).
- ✅ Endpoints: `GET /api/packages/` + `GET /api/packages/<slug>/` (AllowAny, only `is_active=True`).
- ✅ صفحة HTML: `/packages/` تعرض قائمة بطاقات Tailwind RTL.
- ✅ States: Default / Hover (translate + shadow) / Empty (📭 + رابط للتواصل).
- ✅ Admin: `PackageAdmin` (Manager only) مع image preview + slug auto.
- ✅ Tests: 24 اختبار (model + serializer + API + HTML page).

### F3 — نموذج الحجز الذكي ✅
- ✅ Lead model (DATABASE.md §4) كامل مع status pipeline (4 حالات) + indexes.
- ✅ HTMX (بدون reload) — content negotiation: HTML partial أو JSON.
- ✅ Validators: phone regex سعودي/خليجي + email + name min=3 + package active.
- ✅ States: Default + Loading (spinner) + Error (Toast) + Success (Modal أخضر).
- ✅ Endpoint: `POST /api/leads/create/` (AllowAny + CSRF) + `GET` لإعادة النموذج.
- ✅ التقاط IP + User-Agent + ربط investor تلقائياً لو مسجَّل.
- ✅ Signal stub جاهز (post_save) — handler في F7.
- ✅ Tests: 22 (model + form + view JSON/HTMX + investor link).

### F4 — تسجيل/دخول المستثمر ✅
- ✅ Custom User بـ email + role (investor/supervisor/manager).
- ✅ كلمة مرور ≥ 8 (Django password validators).
- ✅ Permission classes: `IsInvestor`, `IsSupervisor`, `IsManager`, `IsOwnerInvestor`.
- ✅ Forms: `RegisterForm` + `LoginForm` بـ Tailwind RTL.
- ✅ Views: `/accounts/register/`, `/accounts/login/`, `/accounts/logout/`.
- ✅ Signal: Supervisor/Manager → `is_staff=True` تلقائياً.
- ✅ "تذكرني" → 30 يوم session.
- ✅ Django Admin: إنشاء supervisor/manager (Manager فقط — لا تسجيل عام).
- ✅ Tests: 35 اختبار (models + forms + views + permissions).
- ⏳ تأكيد الإيميل + استعادة كلمة المرور — تأجَّلت لتكامل allauth في المرحلة 7.

### F5 — Admin Dashboard ✅
- ✅ `/dashboard/` — overview بإحصائيات (الإجمالي + 4 حالات + آخر 5 طلبات).
- ✅ `/dashboard/leads/` — جدول + فلترة بالحالة + بحث (الاسم/الجوال/الإيميل).
- ✅ `/dashboard/leads/<id>/` — تفاصيل + سجل تغيير الحالة (StatusHistory).
- ✅ `/dashboard/packages/` — إدارة الباقات (Manager only) + leads_count.
- ✅ `/dashboard/users/` — إدارة المستخدمين (Manager only) + filter بالدور.
- ✅ Sidebar navigation + base layout بـ Tailwind RTL.
- ✅ Decorators: `@staff_required` + `@manager_required` (لا DRF لصفحات HTML).
- ✅ Tests: 22 (auth + perm + filter + render + role-based content).

### F6 — تحديث حالة الطلب (Status Pipeline) ✅
- ✅ 4 حالات: 🟠 جديد · 🔵 جاري التواصل · 🟢 تم الإغلاق · ❌ ملغي.
- ✅ HTMX inline update عبر `<select>` — البادج يتبدّل فوراً (أو من تفاصيل الطلب).
- ✅ Audit trail: `StatusHistory` model — from_status, to_status, changed_by, note, changed_at.
- ✅ `Lead.update_status(...)` atomic helper.
- ✅ Endpoints DRF: `GET /api/leads/`, `PATCH /api/leads/<id>/status/`, `DELETE /api/leads/<id>/`.
- ✅ Endpoints HTMX: `POST /dashboard/leads/<id>/status/`, `DELETE /dashboard/leads/<id>/delete/`.
- ✅ Cancellation (`cancelled`) + Delete = Manager only — على API و HTMX (مرجع PERMISSIONS.md).
- ✅ Tests: 21 (model 6 + DRF API 12 + HTMX 6 + history cascade + SET_NULL).

### F7 — Django Signals للإشعارات ✅
- ✅ `@receiver(post_save, sender=Lead)` → `on_lead_created` (created=True فقط).
- ✅ Celery task `send_telegram_to_admin(lead_id)` — أساسي، رسالة عربية بـ HTML.
- ✅ Celery task `send_email_to_admin(lead_id)` — احتياطي، قالبا txt + html.
- ✅ Retry: `autoretry_for=(TelegramError,)` + `retry_backoff` + `max_retries=3`.
- ✅ Dev bypass تلقائي: بدون `TELEGRAM_BOT_TOKEN` → log + skip بدون فشل.
- ✅ helper `apps/notifications/telegram.py` (urllib، لا dependency).
- ✅ Signal لا يكسر إنشاء Lead لو Celery مُعطَّل (catch + log).
- ✅ Tests: 14 (telegram 5 + tasks 6 + signals 3) — locmem outbox + EAGER mode.

### F8 — حماية reCAPTCHA ✅
- ✅ Google reCAPTCHA v3 utility (`apps/leads/recaptcha.py`) عبر Google siteverify.
- ✅ Threshold قابل للضبط (`RECAPTCHA_REQUIRED_SCORE=0.5`).
- ✅ Dev bypass تلقائي عند غياب الـ key (للاختبارات).
- ✅ Rate limiting 5/min/IP عبر `django-ratelimit` (`429 Too Many Requests`).
- ✅ حقل token مخفي في النموذج جاهز للتعبئة من JS عند الإصدار.
- ✅ Tests: 5 لـ recaptcha + 1 لـ rate-limit + integration tests.

### F9 — صفحة الملف الشخصي ✅
- ✅ Model `accounts.UserProfile` (DATABASE.md §2): OneToOne User + company_name + city + bio + avatar.
- ✅ Signal `post_save User` ينشئ Profile تلقائياً عند التسجيل.
- ✅ `/profile/` — `ProfileForm` يجمع User (first/last/phone) + Profile (company/city/bio/avatar).
- ✅ `/profile/password/` — Django `PasswordChangeForm` + `update_session_auth_hash` (لا خروج).
- ✅ Sidebar layout (3 روابط) + messages framework (success/error toasts).
- ✅ `UserProfileInline` في Django Admin.
- ✅ Permission: `@investor_required` decorator (لا supervisor/manager).
- ✅ Tests: 14 (model + signal + overview + password + cascades).

### F10 — متابعة طلبات المستثمر ✅
- ✅ `/profile/orders/` — قائمة بطاقات الطلبات للمستثمر فقط (`investor=request.user`).
- ✅ يُعيد استخدام F6 `_badge.html` للحالات الأربع.
- ✅ سجل الحالة (StatusHistory) قابل للطيّ في `<details>`.
- ✅ Empty state واضح + رابط "احجز الآن".
- ✅ JSON: `GET /api/profile/orders/` — `IsInvestor` + own-only queryset.
- ✅ Tests: 9 (HTML view + API + own-only enforcement + empty state).

---

## API Endpoints (Phase 1)

| # | Endpoint | Method | Permission |
|---|---|---|---|
| 1 | `/api/packages/` | GET | AllowAny |
| 2 | `/api/leads/create/` | POST | AllowAny + reCAPTCHA |
| 3 | `/api/leads/` | GET | Supervisor / Manager |
| 4 | `/api/leads/<id>/status/` | PATCH | Supervisor / Manager |
| 5 | `/api/leads/<id>/` | DELETE | Manager only |
| 6 | `/api/profile/orders/` | GET | IsInvestor (own only) |

---

## صفحات Dashboard

| # | الصفحة | Permission | المحتوى |
|---|---|---|---|
| 1 | `/dashboard/` | Supervisor + Manager | نظرة عامة + إحصائيات |
| 2 | `/dashboard/leads/` | Supervisor + Manager | جدول الطلبات + فلترة |
| 3 | `/dashboard/leads/<id>/` | Supervisor + Manager | تفاصيل الطلب + ملاحظات |
| 4 | `/dashboard/packages/` | Manager only | CRUD للباقات |
| 5 | `/dashboard/users/` | Manager only | إدارة المستثمرين والمشرفين |
