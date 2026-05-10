# DATABASE.md — تصميم قاعدة البيانات لخوارزميات

> **مصدر الحقيقة**: `apps/<app>/models.py` لاحقاً.
> هذا الملف **عقد تصميم** قبل كتابة الكود — يُحدَّث بعد كل migration.

## نظرة عامة على الجداول (Phase 1)

```
accounts_user ──┬─< leads_lead >── packages_package
                │
                └──< accounts_userprofile

leads_lead ──< leads_statushistory >── accounts_user
```

## 1. `accounts_user` (Custom User)

| الحقل | النوع | القيود | ملاحظات |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `email` | EmailField | unique, required | username field |
| `password` | CharField(128) | required | hashed |
| `first_name` | CharField(50) | required | |
| `last_name` | CharField(50) | required | |
| `phone` | CharField(20) | regex سعودي/خليجي | اختياري للـ Investor |
| `role` | CharField(20) | choices | `investor` / `supervisor` / `manager` |
| `is_active` | BooleanField | default=True | |
| `is_staff` | BooleanField | default=False | للوصول لـ Django Admin |
| `is_email_verified` | BooleanField | default=False | يتغير بعد التفعيل |
| `date_joined` | DateTimeField | auto_now_add | |
| `last_login` | DateTimeField | nullable | |

**Indexes**: `email` (unique), `role`
**ROLE_CHOICES**: `[('investor', 'مستثمر'), ('supervisor', 'مشرف'), ('manager', 'مدير')]`

---

## 2. `accounts_userprofile` (ملف المستثمر)

| الحقل | النوع | القيود | ملاحظات |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `user` | OneToOne → User | CASCADE | |
| `company_name` | CharField(150) | nullable | اسم المعهد/الشركة |
| `city` | CharField(50) | nullable | |
| `bio` | TextField | nullable | نبذة |
| `avatar` | CloudinaryField | nullable | صورة |
| `created_at` | DateTimeField | auto_now_add | |
| `updated_at` | DateTimeField | auto_now | |

---

## 3. `packages_package`

| الحقل | النوع | القيود | ملاحظات |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `name` | CharField(100) | required, verbose='اسم الباقة' | |
| `slug` | SlugField(120) | unique | لـ URLs |
| `description` | TextField | required | وصف الباقة |
| `price` | DecimalField(10,2) | ≥ 0 | بالريال |
| `duration_months` | PositiveSmallIntegerField | default=1 | مدة الاشتراك |
| `features` | JSONField | default=list | قائمة المميزات |
| `image` | CloudinaryField | nullable | صورة الباقة |
| `is_featured` | BooleanField | default=False | بارزة في الواجهة |
| `is_active` | BooleanField | default=True | منشورة |
| `display_order` | PositiveIntegerField | default=0 | للترتيب |
| `created_at` | DateTimeField | auto_now_add | |
| `updated_at` | DateTimeField | auto_now | |

**Indexes**: `slug` (unique), `is_active`, `is_featured`
**Meta.ordering**: `['display_order', '-created_at']`

---

## 4. `leads_lead` (الطلبات — قلب المشروع)

| الحقل | النوع | القيود | ملاحظات |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `name` | CharField(100) | required, min_length=3 | اسم العميل |
| `phone` | CharField(20) | regex سعودي/خليجي | إلزامي |
| `email` | EmailField | required | |
| `package` | FK → Package | **PROTECT** | لا تحذف باقة فيها طلبات |
| `investor` | FK → User | **SET_NULL**, nullable | لو زائر بدون تسجيل |
| `status` | CharField(20) | choices, default='new' | حالة الطلب |
| `notes` | TextField | nullable | ملاحظات داخلية للإدارة |
| `source` | CharField(30) | default='landing' | مصدر الطلب |
| `ip_address` | GenericIPAddressField | nullable | لمنع الـ spam |
| `user_agent` | CharField(255) | nullable | |
| `created_at` | DateTimeField | auto_now_add | |
| `updated_at` | DateTimeField | auto_now | |

**STATUS_CHOICES**:
```python
[
    ('new', 'جديد 🟠'),
    ('in_progress', 'جاري التواصل 🔵'),
    ('closed', 'تم الإغلاق 🟢'),
    ('cancelled', 'ملغي ❌'),
]
```

**Indexes**: `status`, `created_at`, `email`, `phone`
**Meta.ordering**: `['-created_at']`

---

## 5. `leads_statushistory` (Audit Trail)

| الحقل | النوع | القيود | ملاحظات |
|---|---|---|---|
| `id` | BigAutoField | PK | |
| `lead` | FK → Lead | CASCADE, related_name='history' | |
| `from_status` | CharField(20) | nullable | الحالة السابقة |
| `to_status` | CharField(20) | required | الحالة الجديدة |
| `changed_by` | FK → User | SET_NULL, nullable | من غيّر |
| `changed_at` | DateTimeField | auto_now_add | |
| `note` | TextField | nullable | تعليق التغيير |

**Indexes**: `lead`, `changed_at`
**Meta.ordering**: `['-changed_at']`

---

## العلاقات (Relationships)

| العلاقة | النوع | on_delete |
|---|---|---|
| `User` ←→ `UserProfile` | OneToOne | CASCADE |
| `Lead` → `Package` | ForeignKey | **PROTECT** |
| `Lead` → `User` (investor) | ForeignKey nullable | SET_NULL |
| `StatusHistory` → `Lead` | ForeignKey | CASCADE |
| `StatusHistory` → `User` (changed_by) | ForeignKey nullable | SET_NULL |

---

## Migrations المتوقعة (Phase 1)

| # | الاسم | المرحلة |
|---|---|---|
| `accounts/0001_initial` | Custom User + Role | المرحلة 1 |
| `accounts/0002_userprofile` | UserProfile | المرحلة 7 |
| `packages/0001_initial` | Package | المرحلة 2 |
| `leads/0001_initial` | Lead | المرحلة 3 |
| `leads/0002_statushistory` | Status audit trail | المرحلة 5 |

---

## قواعد قاعدة البيانات
- ✅ `models.py` هو مصدر الحقيقة — لا `schema.sql`
- ✅ كل migration باسم وصفي (مثل `0003_add_status_to_lead`)
- ✅ Indexes على الحقول المُستعلَمة (`status`, `created_at`)
- ✅ `ForeignKey on_delete` واضح (`PROTECT` للـ Lead → Package)
- ❌ لا تحذف عمود في production — استخدم soft delete
- ❌ لا raw SQL — Django ORM فقط

## Validators المركزية

```python
# apps/core/validators.py
GULF_PHONE_REGEX = r'^(05|009665|9665|\+9665)[0-9]{8}$'
phone_validator = RegexValidator(regex=GULF_PHONE_REGEX, message='رقم جوال غير صحيح')
```
