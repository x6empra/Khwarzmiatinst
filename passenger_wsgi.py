"""Passenger WSGI entrypoint for cPanel."""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / "venv" / "bin" / "python"


def _restart_with_venv_python() -> None:
    if not VENV_PYTHON.exists():
        return
    if Path(sys.executable).resolve() == VENV_PYTHON.resolve():
        return

    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env["VIRTUAL_ENV"] = str(BASE_DIR / "venv")
    env["PATH"] = f"{VENV_PYTHON.parent}:{env.get('PATH', '')}"
    os.execve(str(VENV_PYTHON), [str(VENV_PYTHON), __file__], env)


_restart_with_venv_python()

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.cpanel")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
