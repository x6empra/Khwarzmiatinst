"""Root pytest fixtures."""

import os

# يجب ضبطه قبل أي استيراد Django (Playwright + live_server)
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

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

    # Celery — تشغيل synchronous بدون broker خارجي (TESTING.md).
    # نضبط الإعدادات على settings + app نفسه (config_from_object قد يكون cached).
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True
    settings.CELERY_BROKER_URL = "memory://"
    settings.CELERY_RESULT_BACKEND = "cache+memory://"

    from config.celery import app as celery_app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    celery_app.conf.broker_url = "memory://"
    celery_app.conf.result_backend = "cache+memory://"

    # Email في الاختبارات → locmem outbox
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


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


@pytest.fixture(autouse=True)
def _clear_mail_outbox():
    """يفرغ صندوق البريد بين الاختبارات."""
    from django.core import mail

    mail.outbox = []
    yield
    mail.outbox = []
