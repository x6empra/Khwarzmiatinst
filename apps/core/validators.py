"""
Shared validators — referenced by DATABASE.md and API.md.
"""

from django.core.validators import RegexValidator

GULF_PHONE_REGEX = r"^(05|009665|9665|\+9665)[0-9]{8}$"

phone_validator = RegexValidator(
    regex=GULF_PHONE_REGEX,
    message="رقم الجوال غير صحيح. الصيغة المقبولة: 05XXXXXXXX أو +9665XXXXXXXX",
    code="invalid_phone",
)
