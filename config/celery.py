"""Celery app — used by apps.notifications later (F7)."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("khawarizmiat")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
