"""Development settings — local machine only."""

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Console email backend (no real sending)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Toolbar etc. can be added later
INTERNAL_IPS = ["127.0.0.1"]
