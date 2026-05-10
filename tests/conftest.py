"""Root pytest fixtures."""

import pytest


def pytest_configure(config):
    """تهيئة عامة للاختبارات."""
    from django.conf import settings

    # locmem لا Redis — أخف وأسرع
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "tests-locmem",
        }
    }

    # افتراضياً نوقف rate-limit حتى لا يتداخل بين tests.
    # الـ class الذي يختبر rate-limit يفعّله صراحةً.
    settings.RATELIMIT_ENABLE = False


@pytest.fixture(autouse=True)
def _media_root(tmp_path, settings):
    """عزل ملفات الميديا أثناء الاختبار."""
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture(autouse=True)
def _clear_cache():
    """يمسح كل caches قبل وبعد كل اختبار (rate-limit counters)."""
    from django.core.cache import caches

    for c in caches.all():
        c.clear()
    yield
    for c in caches.all():
        c.clear()
