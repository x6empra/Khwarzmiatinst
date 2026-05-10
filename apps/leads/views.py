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
from rest_framework import filters, generics, status as drf_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsManager, IsSupervisor

from .forms import LeadForm
from .models import Lead, LeadStatus
from .recaptcha import verify_recaptcha
from .serializers import LeadListSerializer, LeadStatusUpdateSerializer


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
            return render(request, "leads/_error.html", {"message": msg})
        return JsonResponse({"success": False, "message": msg}, status=429)

    form = LeadForm(request.POST)
    if not form.is_valid():
        if _is_htmx(request):
            # HTMX يحتاج 200 لإجراء الـ swap — الأخطاء تُعرَض داخل الـ HTML
            return render(request, "leads/_form.html", {"form": form})
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
            return render(request, "leads/_error.html", {"message": msg})
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


# ── DRF endpoints لـ Dashboard (F5 + F6) ────────────────────────────────────


class LeadListAPIView(generics.ListAPIView):
    """GET /api/leads/ — IsSupervisor (API.md §Leads)."""

    serializer_class = LeadListSerializer
    permission_classes = [IsAuthenticated, IsSupervisor]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "phone", "email", "notes"]
    ordering_fields = ["created_at", "status", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Lead.objects.select_related("package", "investor").all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        package_filter = self.request.query_params.get("package")
        if package_filter:
            qs = qs.filter(package_id=package_filter)
        return qs


class LeadStatusUpdateAPIView(APIView):
    """PATCH /api/leads/<id>/status/ — IsSupervisor.
    إلغاء (cancelled) → IsManager فقط.
    """

    permission_classes = [IsAuthenticated, IsSupervisor]

    def patch(self, request, pk: int):
        try:
            lead = Lead.objects.get(pk=pk)
        except Lead.DoesNotExist:
            return Response({"detail": "غير موجود"}, status=drf_status.HTTP_404_NOT_FOUND)

        serializer = LeadStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]
        note = serializer.validated_data.get("note", "")

        # cancellation → Manager only
        if new_status == LeadStatus.CANCELLED and not getattr(request.user, "is_manager", False):
            return Response(
                {"detail": "إلغاء الطلب صلاحية المدير فقط."},
                status=drf_status.HTTP_403_FORBIDDEN,
            )

        if new_status != lead.status:
            lead.update_status(new_status, changed_by=request.user, note=note)

        return Response(LeadListSerializer(lead).data, status=drf_status.HTTP_200_OK)


class LeadDeleteAPIView(generics.DestroyAPIView):
    """DELETE /api/leads/<id>/ — IsManager only."""

    queryset = Lead.objects.all()
    permission_classes = [IsAuthenticated, IsManager]
    lookup_field = "pk"
