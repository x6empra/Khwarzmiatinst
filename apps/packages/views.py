"""
Package views — see API.md §Packages and FEATURES.md F2.

Public API: GET /api/packages/  + GET /api/packages/<slug>/
Public Page: GET /packages/  (Django template)
"""

from django.shortcuts import render
from django.views.decorators.http import require_GET
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from .models import Package
from .serializers import PackageSerializer


class PackageViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Read-only public endpoint — only active packages."""

    serializer_class = PackageSerializer
    permission_classes = (AllowAny,)
    lookup_field = "slug"

    def get_queryset(self):
        return Package.objects.filter(is_active=True)


@require_GET
def packages_page(request):
    """صفحة عامة تعرض الباقات النشطة (FEATURES.md F2)."""
    packages = Package.objects.filter(is_active=True)
    return render(
        request,
        "packages/list.html",
        {"packages": packages},
    )
