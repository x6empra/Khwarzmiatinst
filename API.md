# API.md — مرجع الـ API لخوارزميات

> **مصدر الحقيقة**: `drf-spectacular` يولّد OpenAPI من ViewSets لاحقاً.
> هذا الملف **عقد API** قبل كتابة الكود.

## Base URL
- **Development**: `http://localhost:8000/api/`
- **Production**: `https://khawarizmiat.com/api/`

## Authentication
- Session-based (Django) للـ Frontend (HTMX)
- Token-based اختياري (DRF Token / JWT) للـ Mobile لاحقاً

## Response Conventions
- **Success**: `{ "success": true, "data": {...} }`
- **Error**: `{ "success": false, "errors": {...} }`
- **Pagination**: DRF default — `{ count, next, previous, results }`

---

## 📦 Packages

### `GET /api/packages/`
**Permission**: `AllowAny` · **List packages**

```json
// Response 200
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "الباقة الذهبية",
      "slug": "golden",
      "description": "...",
      "price": "1499.00",
      "duration_months": 6,
      "features": ["ميزة 1", "ميزة 2"],
      "image_url": "https://res.cloudinary.com/...",
      "is_featured": true
    }
  ]
}
```

### `GET /api/packages/<slug>/`
**Permission**: `AllowAny` · **Single package**

---

## 📝 Leads

### `POST /api/leads/create/`
**Permission**: `AllowAny` + `reCAPTCHA` · **Rate**: 5/min/IP

```json
// Request
{
  "name": "أحمد محمد",
  "phone": "0501234567",
  "email": "ahmed@example.com",
  "package": 1,
  "notes": "أرغب في معرفة المزيد",
  "recaptcha_token": "03AGdBq..."
}

// Response 201
{ "success": true, "message": "تم استلام طلبك بنجاح ✓ سنتواصل معك" }

// Response 400
{ "success": false, "errors": { "phone": ["رقم جوال غير صحيح"] } }

// Response 429
{ "success": false, "message": "تجاوزت الحد المسموح، حاول لاحقاً" }
```

### `GET /api/leads/`
**Permission**: `IsSupervisor` (Supervisor + Manager)

Query params: `status`, `search`, `package`, `ordering`, `page`

```json
// Response 200
{
  "count": 42,
  "results": [
    {
      "id": 1,
      "name": "أحمد",
      "phone": "0501234567",
      "email": "ahmed@example.com",
      "package": { "id": 1, "name": "الذهبية" },
      "status": "new",
      "investor": null,
      "notes": null,
      "created_at": "2026-05-10T22:48:00Z"
    }
  ]
}
```

### `GET /api/leads/<id>/`
**Permission**: `IsSupervisor`

### `PATCH /api/leads/<id>/status/`
**Permission**: `IsSupervisor`

```json
// Request
{ "status": "in_progress", "note": "تواصلت معه اليوم" }

// Response 200
{
  "id": 1,
  "status": "in_progress",
  "history": [
    { "from_status": "new", "to_status": "in_progress", "changed_by": "محمد", "changed_at": "..." }
  ]
}
```

### `DELETE /api/leads/<id>/`
**Permission**: `IsManager` only · **Response**: 204 No Content

---

## 👤 Profile

### `GET /api/profile/`
**Permission**: `IsInvestor`

```json
{
  "user": { "first_name": "...", "last_name": "...", "email": "...", "phone": "..." },
  "profile": { "company_name": "...", "city": "...", "bio": "...", "avatar_url": "..." }
}
```

### `PATCH /api/profile/`
**Permission**: `IsInvestor` (own only)

### `GET /api/profile/orders/`
**Permission**: `IsInvestor` + own only

```json
{
  "count": 3,
  "results": [
    { "id": 1, "package": "الذهبية", "status": "in_progress", "created_at": "..." }
  ]
}
```

---

## 🔐 Authentication (django-allauth)

| Endpoint | Method | Purpose |
|---|---|---|
| `/accounts/register/` | POST | تسجيل مستثمر جديد |
| `/accounts/login/` | POST | تسجيل دخول |
| `/accounts/logout/` | POST | خروج |
| `/accounts/password/reset/` | POST | استعادة كلمة المرور |
| `/accounts/password/reset/confirm/<key>/` | POST | تأكيد الاستعادة |
| `/accounts/email/confirm/<key>/` | GET | تفعيل الإيميل |

---

## 🎛️ Dashboard (HTML — لا JSON)

| URL | Method | Permission |
|---|---|---|
| `/dashboard/` | GET | `IsSupervisor` |
| `/dashboard/leads/` | GET | `IsSupervisor` |
| `/dashboard/leads/<id>/` | GET | `IsSupervisor` |
| `/dashboard/packages/` | GET | `IsManager` |
| `/dashboard/packages/<id>/edit/` | GET, POST | `IsManager` |
| `/dashboard/users/` | GET | `IsManager` |

> Dashboard يستخدم نفس Endpoints أعلاه عبر **HTMX** — لا API منفصل.

---

## Status Codes

| Code | المعنى | متى |
|---|---|---|
| 200 | OK | GET / PATCH ناجح |
| 201 | Created | POST ناجح |
| 204 | No Content | DELETE ناجح |
| 400 | Bad Request | validation فشل |
| 401 | Unauthorized | غير مسجل دخول |
| 403 | Forbidden | لا يملك صلاحية |
| 404 | Not Found | المورد غير موجود |
| 429 | Too Many Requests | rate limit |
| 500 | Server Error | يُسجَّل في Sentry |

---

## Validation Rules (موحّدة)

| الحقل | القاعدة |
|---|---|
| `name` | required, min=3, max=100, strip whitespace |
| `phone` | regex: `^(05\|009665\|9665\|\+9665)[0-9]{8}$` |
| `email` | `validate_email` (Django) |
| `package` | exists in DB + `is_active=True` |
| `password` | ≥ 8 + رقم + رمز |
| `recaptcha_token` | يُتحقَّق من Google API + score ≥ 0.5 |

---

## Permissions Matrix (سريعة)

| Endpoint | Visitor | Investor | Supervisor | Manager |
|---|:---:|:---:|:---:|:---:|
| `GET /api/packages/` | ✅ | ✅ | ✅ | ✅ |
| `POST /api/leads/create/` | ✅ | ✅ | ✅ | ✅ |
| `GET /api/leads/` | ❌ | ❌ | ✅ | ✅ |
| `PATCH /api/leads/<id>/status/` | ❌ | ❌ | ✅ | ✅ |
| `DELETE /api/leads/<id>/` | ❌ | ❌ | ❌ | ✅ |
| `GET /api/profile/orders/` | ❌ | ✅ (own) | ❌ | ❌ |

---

## drf-spectacular
بعد تثبيته، تتوفر:
- `/api/schema/` — OpenAPI JSON
- `/api/docs/` — Swagger UI
- `/api/redoc/` — ReDoc UI

سيُولّد الملف نفسه تلقائياً من ViewSets/Serializers.
