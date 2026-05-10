"""
Profile views — F9 + F10.

كل views محمية بـ @investor_required.
المستثمر يصل لملفه + طلباته فقط — لا غيره.
"""

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from apps.accounts.models import UserProfile
from apps.leads.models import Lead

from .decorators import investor_required
from .forms import ProfileForm


@require_http_methods(["GET", "POST"])
@investor_required
def overview(request: HttpRequest) -> HttpResponse:
    """/profile/ — عرض + تعديل بيانات المستثمر (F9)."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "✓ تم حفظ بياناتك بنجاح.")
            return redirect("investor_profile:overview")
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, "profile/overview.html", {"form": form, "profile": profile})


@require_http_methods(["GET", "POST"])
@investor_required
def password_change(request: HttpRequest) -> HttpResponse:
    """/profile/password/ — تغيير كلمة المرور (F9)."""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # لا تخرج المستخدم
            messages.success(request, "✓ تم تحديث كلمة المرور بنجاح.")
            return redirect("investor_profile:overview")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "profile/password.html", {"form": form})


@require_GET
@investor_required
def orders(request: HttpRequest) -> HttpResponse:
    """/profile/orders/ — جدول طلبات المستثمر فقط (F10)."""
    qs = (
        Lead.objects.filter(investor=request.user)
        .select_related("package")
        .prefetch_related("history")
        .order_by("-created_at")
    )
    return render(request, "profile/orders.html", {"orders": qs})
