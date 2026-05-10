"""Core views — health check + temporary landing placeholder."""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    """Temporary landing placeholder until F1 is built."""
    from apps.leads.forms import LeadForm
    from apps.packages.models import Package

    return render(
        request,
        "core/home.html",
        {
            "lead_form": LeadForm(),
            "packages": Package.objects.filter(is_active=True)[:3],
        },
    )


@require_GET
def healthz(request):
    """Liveness probe for Railway/Render."""
    return JsonResponse({"status": "ok", "service": "khawarizmiat"})
