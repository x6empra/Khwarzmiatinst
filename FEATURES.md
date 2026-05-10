# FEATURES.md — قائمة ميزات خوارزميات

> **حالة الميزة**: ⏳ Pending · 🟡 In Progress · ✅ Done

## Phase 1 — Must Have (8)

| ID | الميزة | MoSCoW | المرحلة | الحالة |
|---|---|---|---|---|
| **F1** | صفحة هبوط (Landing) بكحلي + Spline 3D | Must | Phase 1 | ⏳ |
| **F2** | عرض الباقات (Packages Display) | Must | Phase 1 | ✅ |
| **F3** | نموذج حجز ذكي (AJAX — بدون reload) | Must | Phase 1 | ✅ |
| **F4** | تسجيل/دخول المستثمر | Must | Phase 1 | ✅ |
| **F5** | لوحة تحكم الإدارة (Admin Dashboard) | Must | Phase 1 | ⏳ |
| **F6** | تحديث حالة الطلب (Status Pipeline) | Must | Phase 1 | ⏳ |
| **F7** | إشعارات فورية للإدارة (Django Signals) | Must | Phase 1 | ✅ |
| **F8** | حماية reCAPTCHA على نموذج الحجز | Must | Phase 1 | ✅ |

## Phase 1 — Should Have (2)

| ID | الميزة | MoSCoW | المرحلة | الحالة |
|---|---|---|---|---|
| **F9** | صفحة الملف الشخصي للمستثمر | Should | Phase 1 | ⏳ |
| **F10** | متابعة المستثمر لحالة طلباته | Should | Phase 1 | ⏳ |

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

### F1 — صفحة الهبوط (Landing)
- Hero بكحلي + Spline 3D تفاعلي.
- عرض الباقات داخل البطاقات.
- نموذج الحجز مدمج في أسفل الصفحة.
- RTL كامل + Mobile First.
- Lazy load لـ Spline + Fallback صورة ثابتة.
- **Permission**: AllowAny.

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

### F5 — Admin Dashboard
- `/dashboard/` — نظرة عامة (إحصائيات + آخر 5 طلبات).
- `/dashboard/leads/` — جدول كل الطلبات + فلترة.
- `/dashboard/packages/` — إدارة الباقات (Manager only).
- `/dashboard/users/` — إدارة المستخدمين (Manager only).
- **Permission**: Supervisor + Manager.

### F6 — تحديث حالة الطلب (Status Pipeline)
- 4 حالات: 🟠 جديد · 🔵 جاري التواصل · 🟢 تم الإغلاق · ❌ ملغي.
- HTMX inline update — اللون يتغير فوراً.
- تتبع: من حدّث + متى.
- **Endpoint**: `PATCH /api/leads/<id>/status/` (Supervisor / Manager).
- **حذف**: `DELETE /api/leads/<id>/` (Manager only).

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

### F9 — صفحة الملف الشخصي
- `/profile/` — تعديل البيانات الشخصية.
- تغيير كلمة المرور.
- **Permission**: IsInvestor (own only).

### F10 — متابعة طلبات المستثمر
- `/profile/orders/` — جدول طلبات المستثمر فقط.
- Status badge ملوّن.
- **Permission**: IsInvestor (own only).

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
