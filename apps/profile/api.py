"""DRF API for profile — F10 (API.md §Profile)."""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsInvestor
from apps.leads.models import Lead
from apps.leads.serializers import LeadListSerializer


class OrdersListAPIView(generics.ListAPIView):
    """GET /api/profile/orders/ — IsInvestor + own only (API.md)."""

    serializer_class = LeadListSerializer
    permission_classes = [IsAuthenticated, IsInvestor]

    def get_queryset(self):
        # Own only — مرجع PERMISSIONS.md §IsOwnerInvestor
        return (
            Lead.objects.filter(investor=self.request.user)
            .select_related("package")
            .order_by("-created_at")
        )
