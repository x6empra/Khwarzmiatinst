# FEATURES.md — قائمة ميزات خوارزميات

> **حالة الميزة**: ⏳ Pending · 🟡 In Progress · ✅ Done

## Phase 1 — Must Have (8)

| ID | الميزة | MoSCoW | المرحلة | الحالة |
|---|---|---|---|---|
| **F1** | صفحة هبوط (Landing) بكحلي + Spline 3D | Must | Phase 1 | ⏳ |
| **F2** | عرض الباقات (Packages Display) | Must | Phase 1 | ⏳ |
| **F3** | نموذج حجز ذكي (AJAX — بدون reload) | Must | Phase 1 | ⏳ |
| **F4** | تسجيل/دخول المستثمر | Must | Phase 1 | ⏳ |
| **F5** | لوحة تحكم الإدارة (Admin Dashboard) | Must | Phase 1 | ⏳ |
| **F6** | تحديث حالة الطلب (Status Pipeline) | Must | Phase 1 | ⏳ |
| **F7** | إشعارات فورية للإدارة (Django Signals) | Must | Phase 1 | ⏳ |
| **F8** | حماية reCAPTCHA على نموذج الحجز | Must | Phase 1 | ⏳ |

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

### F2 — عرض الباقات (Packages Display)
- جلب الباقات من Postgres عبر `/api/packages/`.
- بطاقات Tailwind مع لون كحلي + برتقالي للزر.
- States: Default / Hover / Empty.
- **Permission**: AllowAny.

### F3 — نموذج الحجز الذكي
- AJAX (HTMX) — بدون reload.
- حقول: name, phone, email, package, notes.
- Validation: phone regex سعودي/خليجي + email valid.
- reCAPTCHA v3 مخفي.
- بعد الإرسال: Modal أخضر "تم استلام طلبك".
- يطلق Django Signal للإشعارات.
- **Endpoint**: `POST /api/leads/create/` (AllowAny).

### F4 — تسجيل/دخول المستثمر
- django-allauth.
- إيميل + كلمة مرور ≥ 8 + رقم + رمز.
- تأكيد إيميل بعد التسجيل.
- استعادة كلمة المرور (token صالح 1h).
- مدة الجلسة: 14 يوم + "تذكرني" 30 يوم.

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

### F7 — Django Signals للإشعارات
- `@receiver(post_save, sender=Lead)` → `on_lead_created`.
- Celery task: `send_telegram_to_admin(lead)`.
- Celery task: `send_email_to_admin(lead)` (نسخة احتياطية).
- إعادة محاولة عند الفشل (3 مرات).

### F8 — حماية reCAPTCHA
- Google reCAPTCHA v3 (مخفي).
- على نموذج الحجز فقط في Phase 1.
- threshold: 0.5 (يمكن ضبطه).
- Rate limiting 5/min على الـ endpoint.

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
