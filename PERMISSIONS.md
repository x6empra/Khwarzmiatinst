# PERMISSIONS.md — الأدوار والصلاحيات والأمان

## الأدوار الأربعة

| الدور | ماذا يفعل؟ | الصلاحيات |
|---|---|---|
| **Visitor** (زائر) | يتصفح الموقع — يرى الباقات والـ 3D | قراءة فقط — يقدر يرسل نموذج حجز بدون تسجيل (اختياري) |
| **Investor** (مستثمر) | يسجل + يطلب الخدمة + يتابع طلبه | يسجل دخول، يقدم طلب اشتراك، يرى حالة طلباته الشخصية، يحدّث ملفه الشخصي |
| **Supervisor** (مشرف) | يدير الطلبات الواردة ويتواصل مع المستثمرين | يرى كل الطلبات، يحدّث حالة الطلب (جديد/جاري/تم الإغلاق)، يضيف ملاحظات داخلية |
| **Manager** (مدير) | السلطة الكاملة على المنصة | كل صلاحيات المشرف + إدارة الباقات + إدارة المشرفين + التقارير + إعدادات النظام |

## 💡 ملاحظة جوهرية
- **المستثمر** هو الوحيد الذي يسجل عبر الواجهة العامة.
- **المشرف والمدير** لا يسجلان عبر الواجهة العامة — يُنشَآن من **Django Admin** مباشرة.
- هذا يفصل واجهة الجمهور عن واجهة الإدارة بشكل آمن.

---

## مصفوفة الصلاحيات

| العملية | Visitor | Investor | Supervisor | Manager |
|---|:---:|:---:|:---:|:---:|
| تصفح الباقات | ✅ | ✅ | ✅ | ✅ |
| إرسال نموذج حجز | ✅ | ✅ | ✅ | ✅ |
| التسجيل | ✅ | — | ❌ | ❌ |
| تسجيل الدخول | ❌ | ✅ | ✅ | ✅ |
| رؤية ملفه الشخصي | ❌ | ✅ | — | — |
| رؤية طلباته الشخصية | ❌ | ✅ | — | — |
| رؤية كل الطلبات | ❌ | ❌ | ✅ | ✅ |
| تحديث حالة طلب (جديد/جاري/مغلق) | ❌ | ❌ | ✅ | ✅ |
| إلغاء طلب | ❌ | ❌ | ❌ | ✅ |
| حذف طلب | ❌ | ❌ | ❌ | ✅ |
| إدارة الباقات | ❌ | ❌ | ❌ | ✅ |
| إدارة المستخدمين والمشرفين | ❌ | ❌ | ❌ | ✅ |
| تقارير وإحصائيات | ❌ | ❌ | ❌ | ✅ |

---

## Django Permission Classes

### `apps/accounts/permissions.py`

```python
from rest_framework import permissions

class IsInvestor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'investor'

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('supervisor', 'manager')

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'

class IsOwnerInvestor(permissions.BasePermission):
    """المستثمر يرى طلباته فقط."""
    def has_object_permission(self, request, view, obj):
        return obj.investor == request.user
```

---

## Authentication Flow (django-allauth)

| السؤال | الإجابة لخوارزميات |
|---|---|
| طريقة التسجيل | إيميل + كلمة مرور (Django allauth) |
| تأكيد الإيميل | نعم — رابط تفعيل بعد التسجيل |
| سياسة كلمة المرور | 8 أحرف على الأقل + رقم + رمز |
| نسيت كلمة المرور | نعم — إيميل reset مع token صالح 1h |
| مدة الجلسة | 14 يوم + "تذكرني" (30 يوم) |
| Onboarding | بعد التفعيل → صفحة الباقات مباشرة |
| تسجيل المشرف/المدير | ❌ غير متاح من الواجهة — فقط من Django Admin |

### Auth URLs
- `/accounts/register/` — تسجيل مستثمر جديد
- `/accounts/login/` — تسجيل دخول
- `/accounts/logout/` — خروج
- `/accounts/password/reset/` — استعادة كلمة المرور
- `/accounts/email/confirm/<key>/` — تفعيل الإيميل

---

## API Permissions Matrix

| Endpoint | Method | Permission |
|---|---|---|
| `/api/packages/` | GET | `AllowAny` |
| `/api/leads/create/` | POST | `AllowAny` + reCAPTCHA |
| `/api/leads/` | GET | `IsSupervisor` (المشرف + المدير) |
| `/api/leads/<id>/status/` | PATCH | `IsSupervisor` |
| `/api/leads/<id>/` | DELETE | `IsManager` only |
| `/api/profile/orders/` | GET | `IsInvestor` + `IsOwnerInvestor` |

---

## Security Rules (مهمة جداً)

### CSRF & XSS
- **CSRF protection** على كل POST (Django مدمج).
- **XSS**: استخدم `{% autoescape %}` (مفعّل افتراضياً).
- لا تستخدم `mark_safe` على input مستخدم.

### SQL Injection
- **ORM فقط** — لا raw SQL.
- إذا اضطررت لـ raw SQL، استخدم parameterized queries.

### Rate Limiting
- نموذج الحجز: `django-ratelimit` بمعدل **5/min** لكل IP.
- API endpoints الحساسة: 100/min.

### reCAPTCHA
- **reCAPTCHA v3** مخفي على نموذج الحجز.
- threshold: 0.5 (يمكن ضبطه).

### HTTPS
- HTTPS only في production (`SECURE_SSL_REDIRECT = True`).
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`

### Secrets
- Secrets في `.env` — **لا في الكود**.
- استخدم `python-decouple` أو `django-environ`.
- لا ترفع `.env` على Git (مضاف لـ `.gitignore`).

### Django Admin
- محمي بـ **MFA** (`django-otp`).
- URL مخصص (ليس `/admin/`) في production.
- تسجيل دخول الـ superuser فقط.

### Password Policy
- 8 أحرف على الأقل
- يحتوي رقم
- يحتوي رمز خاص
- لا يحتوي اسم المستخدم
- استخدم Django's `AUTH_PASSWORD_VALIDATORS`

### Session Security
- Cookie `HttpOnly` + `Secure` + `SameSite=Lax`
- تجديد الجلسة بعد تسجيل الدخول (`session_key` rotation)
- إنهاء الجلسات الأخرى عند تغيير كلمة المرور

---

## Permissions on Pages

| الصفحة | Permission |
|---|---|
| `/` | `AllowAny` |
| `/accounts/*` | `AllowAny` |
| `/profile/` | `IsInvestor` (login required) |
| `/profile/orders/` | `IsInvestor` + `IsOwnerInvestor` |
| `/dashboard/` | `IsSupervisor` (Supervisor + Manager) |
| `/dashboard/leads/` | `IsSupervisor` |
| `/dashboard/leads/<id>/` | `IsSupervisor` |
| `/dashboard/packages/` | `IsManager` only |
| `/dashboard/users/` | `IsManager` only |
| `/admin/` | `is_staff` + MFA |

---

## Audit Trail (موصى)
- كل تحديث حالة Lead يُسجَّل: `who`, `when`, `from_status`, `to_status`.
- كل حذف يحتاج تأكيد + سجل (`django-simple-history`).
- Manager فقط يقدر يحذف.
