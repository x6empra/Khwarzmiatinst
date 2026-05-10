"""Root pytest fixtures."""

import pytest


@pytest.fixture(autouse=True)
def _media_root(tmp_path, settings):
    """عزل ملفات الميديا أثناء الاختبار."""
    settings.MEDIA_ROOT = tmp_path / "media"
