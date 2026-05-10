# ROADMAP.md — خطة Phase 1 لـ خوارزميات

> Phase 1 = أبسط نسخة شغالة End-to-End. مرتبة حسب التبعيات.
> **إجمالي تقديري: ~18 يوم عمل**.

## Phase 1 — ترتيب التنفيذ المعتمد

| الترتيب | الميزة | التبعية | تقدير الأيام |
|---|---|---|---|
| 1 | إعداد المشروع + Tech Stack + DB | — | 1 يوم |
| 2 | **F4** — تسجيل/دخول المستثمر (Auth) | إعداد المشروع | 2 أيام |
| 3 | Model: `Package` + Migration | Auth | 0.5 يوم |
| 4 | **F2** — عرض الباقات (Public) | Package model | 1 يوم |
| 5 | Model: `Lead` + Migration | Package | 0.5 يوم |
| 6 | **F3** — نموذج الحجز (AJAX + reCAPTCHA) | Lead model + F2 | 2 أيام |
| 7 | **F8** — حماية reCAPTCHA | F3 | 0.5 يوم |
| 8 | **F7** — Django Signals للإشعارات | F3 | 1 يوم |
| 9 | **F5** — لوحة التحكم (Dashboard) | F3 + Auth + Roles | 2 أيام |
| 10 | **F6** — تحديث حالة الطلب | F5 | 1 يوم |
| 11 | **F1** — Landing + Spline 3D + التصميم النهائي | F2 + F3 | 2 أيام |
| 12 | **F9** — صفحة الملف الشخصي | F4 | 1 يوم |
| 13 | **F10** — متابعة المستثمر لطلباته | F9 + F3 | 1 يوم |
| 14 | اختبارات شاملة + QA | كل الميزات | 2 أيام |
| 15 | Deploy على Railway/Render | QA passed | 1 يوم |

## فلسفة الترتيب
1. **البنية التحتية أولاً**: المشروع → Auth → Models.
2. **القلب أولاً**: عرض الباقات → نموذج الحجز (Lead Generation).
3. **الإدارة بعد البيانات**: Dashboard يحتاج Leads حقيقية.
4. **التصميم النهائي أخيراً**: Spline 3D و Hero بعد التحقق من المنطق.
5. **القياس قبل النشر**: QA شامل + اختبارات قبل Deploy.

## Phase 2 (لاحقاً — لا تبدأ قبل اكتمال Phase 1)
- F11 — تقارير وإحصائيات للمدير
- F12 — نظام دفع مدمج
- دعم اللغة الإنجليزية
- F13 — تطبيق جوال (Won't الآن)

## ⚠️ تحذير
بعد إعداد ROADMAP — **توقف ولا تبدأ التنفيذ قبل المراجعة**.
كل ميزة لاحقاً تتبع الطبقات الثماني End-to-End المعرّفة في `CLAUDE.md`.

## تعريف اكتمال الميزة End-to-End
في خوارزميات، لا تعتبر أي ميزة مكتملة إلا إذا تحقق التالي بالكامل:

- [ ] موجودة في `FEATURES.md`
- [ ] تابعة لـ Phase 1
- [ ] Model في `models.py` + migration مُطبَّق على Postgres
- [ ] Form/Serializer مع validators كاملة
- [ ] Permission class محدد ومُختبَر
- [ ] View/API endpoint شغال + status codes صحيحة
- [ ] URL pattern في `urls.py`
- [ ] Admin Dashboard page (إذا قابلة للإدارة)
- [ ] Frontend template مع Tailwind + RTL
- [ ] HTMX/AJAX integration (إذا تفاعلية)
- [ ] Loading state موجودة
- [ ] Error state موجودة
- [ ] Empty state موجودة
- [ ] Success state موجودة
- [ ] Django Signal (إذا تحتاج إشعار)
- [ ] Unit tests تمر (pytest, ≥ 80% coverage)
- [ ] E2E test يمر (Playwright)
- [ ] Hooks تنجح كلها (ruff, black, mypy, djlint)
- [ ] `FEATURES.md` محدّث (✅ Done)
- [ ] `TESTING.md` محدّث (سيناريو + النتيجة)
