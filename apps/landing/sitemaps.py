"""Django sitemaps — INFRASTRUCTURE.md §3."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.packages.models import Package


class StaticSitemap(Sitemap):
    """صفحات ثابتة عامة فقط — لا dashboard، لا api."""

    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        return ["landing:home", "packages:list", "accounts:login", "accounts:register"]

    def location(self, item: str) -> str:
        return reverse(item)


class PackageSitemap(Sitemap):
    """صفحات الباقات النشطة (لا توجد صفحات منفردة بعد، نشير للقائمة فقط)."""

    priority = 0.6
    changefreq = "monthly"
    protocol = "https"

    def items(self):
        return Package.objects.filter(is_active=True)

    def lastmod(self, obj: Package):
        return obj.updated_at

    def location(self, obj: Package) -> str:
        # لا توجد صفحة منفردة لكل باقة بعد — نوجّه لقائمة الباقات مع slug في URL
        return reverse("packages:list") + f"#package-{obj.slug}"


sitemaps_dict = {
    "static": StaticSitemap,
    "packages": PackageSitemap,
}
