"""DRF Serializers — see API.md §Leads."""

from typing import ClassVar

from rest_framework import serializers

from apps.packages.models import Package

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
        fields = ("name", "phone", "email", "package", "notes", "recaptcha_token")
        extra_kwargs: ClassVar[dict[str, dict[str, bool]]] = {
            "notes": {"required": False, "allow_blank": True},
        }


class LeadListSerializer(serializers.ModelSerializer):
    """GET /api/leads/ — IsSupervisor (API.md §Leads)."""

    package_name = serializers.CharField(source="package.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    investor_email = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            "id",
            "name",
            "phone",
            "email",
            "package",
            "package_name",
            "investor",
            "investor_email",
            "status",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_investor_email(self, obj: Lead) -> str | None:
        return obj.investor.email if obj.investor_id else None


class LeadStatusUpdateSerializer(serializers.Serializer):
    """PATCH /api/leads/<id>/status/."""

    status = serializers.ChoiceField(
        choices=[
            ("new", "new"),
            ("in_progress", "in_progress"),
            ("closed", "closed"),
            ("cancelled", "cancelled"),
        ]
    )
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)
