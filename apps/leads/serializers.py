"""DRF Serializers — see API.md §Leads."""

from rest_framework import serializers

from apps.packages.models import Package
from apps.packages.serializers import PackageSerializer

from .models import Lead


class LeadCreateSerializer(serializers.ModelSerializer):
    """Used by POST /api/leads/create/."""

    package = serializers.PrimaryKeyRelatedField(
        queryset=Package.objects.filter(is_active=True),
        error_messages={
            "does_not_exist": "الباقة المختارة غير متاحة.",
            "incorrect_type": "الباقة المختارة غير صالحة.",
        },
    )
    recaptcha_token = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Lead
        fields = ["name", "phone", "email", "package", "notes", "recaptcha_token"]
        extra_kwargs = {
            "notes": {"required": False, "allow_blank": True},
        }


class LeadListSerializer(serializers.ModelSerializer):
    """Used by GET /api/leads/ (Supervisor/Manager) — placeholder for F5."""

    package = PackageSerializer(read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "package",
            "investor",
            "status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
