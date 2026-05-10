"""Core views — health check + temporary landing placeholder."""

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    """Temporary landing placeholder until F1 is built."""
    return render(request, "core/home.html")


@require_GET
def healthz(request):
    """Liveness probe for Railway/Render."""
    return JsonResponse({"status": "ok", "service": "khawarizmiat"})
