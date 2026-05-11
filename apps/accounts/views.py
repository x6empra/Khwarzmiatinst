"""
Auth views — register / login / logout.

تستخدم Django Forms (PERMISSIONS.md). كل نموذج عام يجب أن يحتوي validators.
"""

from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, RegisterForm

REMEMBER_ME_AGE = 30 * 24 * 60 * 60  # 30 يوماً (PERMISSIONS.md)


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect(_post_login_redirect(request.user))

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        # يدخل تلقائياً بعد التسجيل (يمكن لاحقاً اشتراط تفعيل الإيميل)
        login(request, user)
        return redirect("landing:home")

    return render(request, "account/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(_post_login_redirect(request.user))

    form = LoginForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if not form.cleaned_data.get("remember_me"):
            request.session.set_expiry(0)  # على إغلاق المتصفح
        else:
            request.session.set_expiry(REMEMBER_ME_AGE)
        next_url = request.GET.get("next") or _post_login_redirect(user)
        return redirect(next_url)

    return render(request, "account/login.html", {"form": form})


@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("landing:home")


def _post_login_redirect(user) -> str:
    """مكان التوجيه بعد الدخول حسب الدور (يُحدَّث في المراحل اللاحقة)."""
    if getattr(user, "is_staff_role", False):
        return "/dashboard/" if _has_dashboard() else reverse("landing:home")
    return reverse("landing:home")


def _has_dashboard() -> bool:
    return "apps.dashboard" in settings.INSTALLED_APPS
