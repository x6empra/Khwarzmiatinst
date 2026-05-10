"""
Lead views — see API.md §Leads + FEATURES.md F3 + F8.

POST /api/leads/create/ — single endpoint, content-negotiated:
  - HX-Request → returns HTML partial (Modal success / form-with-errors)
  - else       → returns JSON  ({success, message} or {success:false, errors})

Permissions: AllowAny + CSRF + rate-limit 5/min/IP + reCAPTCHA v3.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django_ratelimit.decorators import ratelimit

from .forms import LeadForm
from .recaptcha import verify_recaptcha


def _client_ip(request: HttpRequest) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _is_htmx(request: HttpRequest) -> bool:
    return request.headers.get("HX-Request") == "true"


@ratelimit(key="ip", rate="5/m", method="POST", block=False)
def lead_create(request: HttpRequest) -> HttpResponse:
    """نموذج الحجز العام (F3 + F8)."""
    if request.method == "GET":
        # يرجع نموذج فارغ — مفيد لـ "إرسال طلب آخر" عبر HTMX
        if _is_htmx(request):
            return render(request, "leads/_form.html", {"form": LeadForm()})
        return HttpResponseNotAllowed(["POST"])

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    # rate-limit (django-ratelimit attaches `request.limited`)
    if getattr(request, "limited", False):
        msg = "تجاوزت الحد المسموح من المحاولات. حاول بعد دقيقة."
        if _is_htmx(request):
            return render(request, "leads/_error.html", {"message": msg}, status=429)
        return JsonResponse({"success": False, "message": msg}, status=429)

    form = LeadForm(request.POST)
    if not form.is_valid():
        if _is_htmx(request):
            return render(request, "leads/_form.html", {"form": form}, status=400)
        return JsonResponse(
            {"success": False, "errors": form.errors.get_json_data()},
            status=400,
        )

    # reCAPTCHA (F8)
    token = form.cleaned_data.get("recaptcha_token") or request.POST.get("recaptcha_token")
    passed, err = verify_recaptcha(token, remote_ip=_client_ip(request))
    if not passed:
        msg = "فشل التحقق من أنك لست برنامجاً آلياً. أعد المحاولة."
        if _is_htmx(request):
            return render(request, "leads/_error.html", {"message": msg}, status=400)
        return JsonResponse(
            {"success": False, "errors": {"recaptcha": [msg]}, "_log": err},
            status=400,
        )

    # Save
    lead = form.save(commit=False)
    lead.ip_address = _client_ip(request)
    lead.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:255]
    if request.user.is_authenticated and getattr(request.user, "is_investor", False):
        lead.investor = request.user
    lead.save()

    if _is_htmx(request):
        return render(request, "leads/_success.html", {"lead": lead})
    return JsonResponse(
        {"success": True, "message": "تم استلام طلبك بنجاح ✓ سنتواصل معك", "lead_id": lead.id},
        status=201,
    )
