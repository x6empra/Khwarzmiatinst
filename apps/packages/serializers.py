"""DRF serializers — see API.md §Packages."""

from rest_framework import serializers

from .models import Package


class PackageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Package
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "price",
            "duration_months",
            "features",
            "image_url",
            "is_featured",
        )
        read_only_fields = fields

    def get_image_url(self, obj: Package) -> str | None:
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url
