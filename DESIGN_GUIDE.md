# DESIGN_GUIDE.md — دليل التصميم لخوارزميات

## الهوية البصرية

| العنصر | القيمة |
|---|---|
| **Brand Personality** | رسمي + تقني + فاخر — يخاطب أصحاب القرار |
| **Tone of Voice** | احترافي ومباشر — لا محادثة عامية |
| **Color Mood** | كحلي بارد (ثقة) + برتقالي دافئ (تحريض) + أخضر (نجاح) |
| **Visual Style** | Glassmorphism خفيف + Gradient كحلي + 3D تفاعلي |
| **Imagery Style** | Spline 3D (أجهزة لوحية مع أيقونات تعليمية متطايرة) |
| **Typography** | Cairo Bold للعناوين + Cairo Regular للنص |

## الألوان الأساسية

| اللون | الكود | الاستخدام |
|---|---|---|
| **الكحلي** | `#1B2A4E` | الخلفية الأساسية — طابع رسمي وتقني مريح للعين |
| **البرتقالي** | `#F39C12` | أزرار "اشترك الآن" وتنبيهات الإدارة — لكسر الجمود |
| **الأخضر** | `#27AE60` | رسائل النجاح وأيقونات التميز |

## Design Tokens

### Colors

| الفئة | القيم |
|---|---|
| **Primary (Navy)** | `#1B2A4E` (DEFAULT) / `#2C4A7C` / `#3F66A8` / `#5E84C2` |
| **Accent (Orange)** | `#F39C12` (DEFAULT) / `#D68910` / `#F8C471` |
| **Success (Green)** | `#27AE60` (DEFAULT) / `#1E8449` / `#82E0AA` |
| **Neutral** | `#2C3E50` / `#5D6D7E` / `#BFC9CA` / `#F4F6F7` / `#FFFFFF` |

### Spacing (نظام 4pt)
`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 px`

### Border Radius
- `sm`: 4px · `md`: 8px · `lg`: 12px · `xl`: 16px · `full`: 9999px

### Shadows
`sm` / `md` / `lg` / `xl` — مع كحلي خفيف `rgba(27,42,78,0.1)`

### Typography
- **Font**: Cairo (عربي) + Inter (إنجليزي)
- **Font Sizes**: `12 / 14 / 16 / 18 / 24 / 32 / 48 / 64 px`

### Tailwind Config مقترح

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1B2A4E',
          light: '#2C4A7C',
          lighter: '#3F66A8',
          lightest: '#5E84C2',
        },
        accent: {
          DEFAULT: '#F39C12',
          dark: '#D68910',
          light: '#F8C471',
        },
        success: {
          DEFAULT: '#27AE60',
          dark: '#1E8449',
          light: '#82E0AA',
        },
      },
      fontFamily: {
        sans: ['Cairo', 'Inter', 'sans-serif'],
      },
    },
  },
  plugins: [require('tailwindcss-rtl')],
}
```

---

## Components — حالات إلزامية لكل مكون

| الحالة | متى؟ | مثال (زر "اشترك الآن") |
|---|---|---|
| **Default** | الحالة الافتراضية | خلفية برتقالية `#F39C12` |
| **Hover** | عند مرور المؤشر | تغمق للبرتقالي `#D68910` |
| **Focus** | عند التركيز (Tab) | ring برتقالي 2px |
| **Active** | أثناء الضغط | `scale-95` + shadow أعمق |
| **Disabled** | غير قابل للتفاعل | `opacity-50` + `cursor-not-allowed` |
| **Loading** | أثناء إرسال النموذج | spinner أبيض + نص "جاري الإرسال..." |
| **Error** | فشل الإرسال | نص خطأ أحمر تحت الزر |
| **Success** | نجاح الإرسال | تحول لأخضر مع أيقونة ✓ |

## المكونات الأساسية
- **Button** (Primary / Accent / Ghost / Danger)
- **Card** (Package / Lead / Stat)
- **Input** (Text / Email / Phone / Textarea)
- **Modal** (Success / Confirm / Form)
- **Toast** (Success / Error / Warning / Info)
- **Status Badge** (4 حالات للـ Lead Pipeline)

---

## Status Pipeline (مهم جداً)

| الحالة | اللون | متى تُعيَّن | من يستطيع التغيير |
|---|---|---|---|
| 🟠 **جديد (New)** | برتقالي | تلقائياً عند إرسال الطلب | Auto |
| 🔵 **جاري التواصل** | أزرق | عند تواصل المشرف | Supervisor / Manager |
| 🟢 **تم الإغلاق** | أخضر | بعد إنهاء الصفقة (إيجاب أو سلب) | Supervisor / Manager |
| ❌ **ملغي** | أحمر | إذا ألغى المستثمر أو فشلت الصفقة | **Manager فقط** |

---

## Responsive (Mobile First)
- **Mobile**: 320px+
- **Tablet**: 768px+
- **Desktop**: 1280px+

## User Flow
زائر → يرى Hero (3D) → يقرأ الباقات → نموذج حجز → رسالة شكر

## صفحات Phase 1

| الصفحة | URL | الغرض |
|---|---|---|
| Landing | `/` | الصفحة الرئيسية مع Hero 3D + الباقات + نموذج الحجز |
| Login | `/accounts/login/` | تسجيل دخول المستثمر |
| Register | `/accounts/register/` | تسجيل مستثمر جديد |
| Investor Profile | `/profile/` | ملف المستثمر + طلباته السابقة |
| Order Status | `/profile/orders/` | متابعة حالة طلبات المستثمر |
| Admin Dashboard | `/dashboard/` | لوحة المشرف والمدير |
| Leads Management | `/dashboard/leads/` | جدول كل الطلبات + تحديث الحالة |
| Packages Management | `/dashboard/packages/` | إدارة الباقات (مدير فقط) |

---

## Accessibility (WCAG AA — إلزامي)

| # | البند | في خوارزميات |
|---|---|---|
| 1 | تباين النصوص ≥ 4.5:1 | كحلي/أبيض = 11.5:1 ✅ / برتقالي/أبيض = 2.5:1 ⚠️ (نضيف ظل) |
| 2 | `alt` text لكل صورة | إلزامي على كل `<img>` |
| 3 | `label` لكل input | Django Forms يوفرها تلقائياً |
| 4 | Keyboard navigation | Tab + Enter + Esc يعملون في كل مكان |
| 5 | Focus indicator مرئي | ring برتقالي 2px |
| 6 | لا يعتمد على اللون فقط | Status: لون + أيقونة + نص |
| 7 | أحجام النقر ≥ 44×44px | أزرار CTA = 56px ارتفاع ✅ |
| 8 | دعم RTL كامل | Tailwind RTL plugin + `dir="rtl"` |
| 9 | ARIA labels | Modal + Toast + Status badges |
| 10 | اختبار قارئ شاشة | VoiceOver + NVDA قبل الإطلاق |

---

## ⚠️ تحذير حرج بشأن Spline 3D
Spline ثقيل (~500KB+). يجب:
1. **Lazy load** بعد scroll.
2. **Fallback صورة ثابتة** للجوال.
3. `prefers-reduced-motion`: تعطيل التحريك.
4. قياس **LCP** بعد كل تعديل (يجب < 2.5s).

## أهداف الأداء
- **LCP** < 2.5s
- **INP** < 200ms
- **CLS** < 0.1
- **Bundle JS** < 200KB
- **Spline** lazy-loaded

---

## RTL Rules
- `dir="rtl"` على عنصر `<html>`.
- استخدم `ms-` و `me-` بدلاً من `ml-` / `mr-`.
- استخدم `start` / `end` بدلاً من `left` / `right`.
- اختبر كل صفحة بصرياً في RTL.
- الأرقام: Western Arabic (123) — أوضح في الفواتير.
- التواريخ: هجري + ميلادي معاً.
