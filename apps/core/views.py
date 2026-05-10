"""Core views — health check (الصفحة الرئيسية انتقلت إلى apps.landing من F1)."""

from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def healthz(request):
    """Liveness probe for Railway/Render."""
    return JsonResponse({"status": "ok", "service": "khawarizmiat"})
