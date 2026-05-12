"""cPanel/Passenger settings for demo3.alkhwarzmi.com."""

from .base import *  # noqa: F403
from .base import BASE_DIR, Csv, config, dj_database_url

try:
    import pymysql
except ImportError:
    pymysql = None

if pymysql is not None:
    pymysql.install_as_MySQLdb()

DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="demo3.alkhwarzmi.com,www.demo3.alkhwarzmi.com",
    cast=Csv(),
)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://demo3.alkhwarzmi.com,https://www.demo3.alkhwarzmi.com",
    cast=Csv(),
)

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

PUBLIC_DIR = BASE_DIR.parent / "public"
STATIC_ROOT = PUBLIC_DIR / "static"
MEDIA_ROOT = PUBLIC_DIR / "media"

DATABASES = {
    "default": dj_database_url.parse(
        config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        conn_health_checks=True,
    ),
}

MYSQL_UNIX_SOCKET = config("MYSQL_UNIX_SOCKET", default="")
if MYSQL_UNIX_SOCKET and DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    DATABASES["default"].setdefault("OPTIONS", {})
    DATABASES["default"]["OPTIONS"]["unix_socket"] = MYSQL_UNIX_SOCKET

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "khawarizmiat-cpanel",
    },
}

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=False, cast=bool)
