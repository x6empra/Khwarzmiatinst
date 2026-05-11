"""
Landing views — F1.
See FEATURES.md F1 + DESIGN_GUIDE.md + INFRASTRUCTURE.md §3 (SEO).
"""

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from apps.leads.forms import LeadForm
from apps.packages.models import Package

FAQS = [
    {
        "q": "كيف تعمل خوارزميات؟",
        "a": "اختر الباقة المناسبة من صفحتنا، املأ نموذج الحجز، وسيتواصل معك فريقنا "
        "خلال 24 ساعة لتفعيل اشتراكك ومرافقتك في الإطلاق.",
    },
    {
        "q": "هل أحتاج لمعرفة تقنية؟",
        "a": "أبداً. نحن نتولّى الجانب التقني بالكامل — من النشر إلى الصيانة. "
        "أنت تركّز على إدارة معهدك وتطوير محتواك التعليمي.",
    },
    {
        "q": "ما هي مدة العقد؟",
        "a": "كل باقة لها مدتها الخاصة (3 / 6 / 12 شهراً). تستطيع الترقية أو التخفيض "
        "في نهاية كل دورة دون التزامات إضافية.",
    },
    {
        "q": "هل بياناتي آمنة؟",
        "a": "نعم. نستخدم تشفير HTTPS، حماية CSRF/XSS، نسخاً احتياطية يومية، ولا نشارك "
        "بياناتك مع أي طرف ثالث. كل النماذج محمية بـ reCAPTCHA.",
    },
    {
        "q": "هل يوجد دعم فني؟",
        "a": "نعم، فريق الدعم متاح من الأحد إلى الخميس عبر الإيميل وقناة دعم خاصة. "
        "الباقات المميَّزة تشمل دعماً 24/7 عبر تيليغرام.",
    },
    {
        "q": "كيف أُلغي اشتراكي؟",
        "a": "تواصل مع المشرف من لوحتك أو عبر بريد الدعم. نحتفظ بنسخة احتياطية من "
        "بياناتك لمدة 30 يوماً قبل الحذف النهائي.",
    },
]


@require_GET
def landing(request: HttpRequest) -> HttpResponse:
    active = Package.objects.filter(is_active=True).order_by("display_order")
    packages = list(active[:6])
    featured = active.filter(is_featured=True).first()

    return render(
        request,
        "landing/index.html",
        {
            "packages": packages,
            "featured_package": featured,
            "lead_form": LeadForm(),
            "spline_scene_url": getattr(settings, "SPLINE_SCENE_URL", ""),
            "faqs": FAQS,
        },
    )


@cache_page(60 * 60 * 24)  # 24h
@require_GET
def robots_txt(request: HttpRequest) -> HttpResponse:
    content = render_to_string(
        "landing/robots.txt",
        {"site_url": f"{request.scheme}://{request.get_host()}"},
    )
    return HttpResponse(content, content_type="text/plain")
