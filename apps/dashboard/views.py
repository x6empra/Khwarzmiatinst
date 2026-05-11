"""
Dashboard views — F5 + F6 (PERMISSIONS.md, API.md).

كل صفحة تستخدم decorator @staff_required أو @manager_required.
HTMX endpoints (تحديث الحالة) ترجّع HTML partial.
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from apps.leads.models import Lead, LeadStatus
from apps.packages.models import Package

from .decorators import manager_required, staff_required
from .forms import PackageEditForm

User = get_user_model()


# ── /dashboard/ — الصفحة الرئيسية ───────────────────────────────────────────


@require_GET
@staff_required
def dashboard_home(request: HttpRequest) -> HttpResponse:
    counts = dict(
        Lead.objects.values_list("status").annotate(c=Count("id")).values_list("status", "c")
    )
    stats = {
        "total": Lead.objects.count(),
        "new": counts.get(LeadStatus.NEW, 0),
        "in_progress": counts.get(LeadStatus.IN_PROGRESS, 0),
        "closed": counts.get(LeadStatus.CLOSED, 0),
        "cancelled": counts.get(LeadStatus.CANCELLED, 0),
    }
    recent = Lead.objects.select_related("package").order_by("-created_at")[:5]
    return render(request, "dashboard/home.html", {"stats": stats, "recent": recent})


# ── /dashboard/leads/ — جدول الطلبات ────────────────────────────────────────


@require_GET
@staff_required
def leads_list(request: HttpRequest) -> HttpResponse:
    qs = Lead.objects.select_related("package", "investor").order_by("-created_at")

    status_filter = request.GET.get("status", "")
    if status_filter:
        qs = qs.filter(status=status_filter)

    search = request.GET.get("q", "").strip()
    if search:
        from django.db.models import Q

        qs = qs.filter(
            Q(name__icontains=search) | Q(phone__icontains=search) | Q(email__icontains=search)
        )

    return render(
        request,
        "dashboard/leads/list.html",
        {
            "leads": qs,
            "current_status": status_filter,
            "search": search,
            "status_choices": LeadStatus.choices,
        },
    )


@require_GET
@staff_required
def lead_detail(request: HttpRequest, pk: int) -> HttpResponse:
    lead = get_object_or_404(
        Lead.objects.select_related("package", "investor").prefetch_related("history__changed_by"),
        pk=pk,
    )
    return render(
        request,
        "dashboard/leads/detail.html",
        {"lead": lead, "status_choices": LeadStatus.choices},
    )


# ── HTMX endpoints (F6) ─────────────────────────────────────────────────────


@require_http_methods(["POST"])
@staff_required
def lead_status_change(request: HttpRequest, pk: int) -> HttpResponse:
    """POST /dashboard/leads/<id>/status/ — يبدّل بادج الحالة فوراً."""
    lead = get_object_or_404(Lead, pk=pk)
    new_status = request.POST.get("status")

    if new_status not in {c[0] for c in LeadStatus.choices}:
        return HttpResponse("status غير صالح", status=400)

    if new_status == LeadStatus.CANCELLED and not getattr(request.user, "is_manager", False):
        raise PermissionDenied("إلغاء الطلب صلاحية المدير فقط.")

    if new_status != lead.status:
        lead.update_status(new_status, changed_by=request.user)

    return render(request, "dashboard/leads/_row.html", {"lead": lead})


@require_http_methods(["DELETE", "POST"])  # POST مع _method=DELETE لـ legacy
@manager_required
def lead_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """DELETE /dashboard/leads/<id>/ — Manager only."""
    lead = get_object_or_404(Lead, pk=pk)
    lead.delete()
    return HttpResponse("", status=200)  # HTMX يحذف الصف من DOM


# ── /dashboard/packages/ — Manager only ─────────────────────────────────────


@require_GET
@manager_required
def packages_list(request: HttpRequest) -> HttpResponse:
    packages = Package.objects.annotate(leads_count=Count("leads")).order_by("display_order")
    return render(request, "dashboard/packages/list.html", {"packages": packages})


@require_http_methods(["GET", "POST"])
@manager_required
def package_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """تحرير باقة من Dashboard — Manager only.
    features تأتي عبر request.POST.getlist('features') (مدخلات متعددة بنفس الاسم).
    """
    package = get_object_or_404(Package, pk=pk)

    if request.method == "POST":
        form = PackageEditForm(
            request.POST,
            request.FILES,
            instance=package,
            features_list=request.POST.getlist("features"),
        )
        if form.is_valid():
            form.save()
            messages.success(request, f"✓ تم حفظ التعديلات على باقة «{package.name}».")
            return redirect("dashboard:packages")
    else:
        form = PackageEditForm(instance=package)

    return render(
        request,
        "dashboard/packages/edit.html",
        {"form": form, "package": package, "features_list": form.features_list},
    )


@require_http_methods(["GET", "POST"])
@manager_required
def package_create(request: HttpRequest) -> HttpResponse:
    """إضافة باقة جديدة من Dashboard — Manager only."""
    if request.method == "POST":
        form = PackageEditForm(
            request.POST,
            request.FILES,
            features_list=request.POST.getlist("features"),
        )
        if form.is_valid():
            pkg = form.save()
            messages.success(request, f"✓ تم إنشاء باقة «{pkg.name}» بنجاح.")
            return redirect("dashboard:packages")
    else:
        form = PackageEditForm()

    return render(
        request,
        "dashboard/packages/edit.html",
        {"form": form, "package": None, "features_list": form.features_list},
    )


# ── /dashboard/users/ — Manager only ────────────────────────────────────────


@require_GET
@manager_required
def users_list(request: HttpRequest) -> HttpResponse:
    users = User.objects.all().order_by("-date_joined")
    role_filter = request.GET.get("role", "")
    if role_filter in {"investor", "supervisor", "manager"}:
        users = users.filter(role=role_filter)
    return render(
        request,
        "dashboard/users/list.html",
        {"users": users, "current_role": role_filter},
    )
