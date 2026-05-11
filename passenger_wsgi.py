"""Passenger WSGI entrypoint for cPanel."""

import os
import sys
from pathlib import Path
from typing import (  # noqa: UP035 - loaded by system Python 3.6 before re-exec.
    Callable,
    Iterable,
    MutableMapping,
)

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
    os.execve(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv], env)


_restart_with_venv_python()

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.cpanel")

from django.core.wsgi import get_wsgi_application  # noqa: E402

django_application = get_wsgi_application()
StartResponse = Callable[..., object]


def application(
    environ: MutableMapping[str, object],
    start_response: StartResponse,
) -> Iterable[bytes]:
    script_name = str(environ.get("SCRIPT_NAME") or "")
    path_info = str(environ.get("PATH_INFO") or "")
    if script_name and script_name != "/":
        suffix = path_info or "/"
        environ["PATH_INFO"] = f"{script_name}{suffix}"
        environ["SCRIPT_NAME"] = ""
    return django_application(environ, start_response)
