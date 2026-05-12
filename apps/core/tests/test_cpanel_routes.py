from pathlib import Path

from django.test import override_settings

from apps.core.cpanel_routes import ensure_cpanel_route_dirs


def test_route_sync_disabled(tmp_path: Path) -> None:
    with override_settings(CPANEL_ROUTE_SYNC_ENABLED=False, CPANEL_PUBLIC_DIR=tmp_path):
        assert ensure_cpanel_route_dirs(("admin",)) == 0
        assert not (tmp_path / "admin").exists()


def test_route_sync_creates_safe_dirs(tmp_path: Path) -> None:
    with override_settings(CPANEL_ROUTE_SYNC_ENABLED=True, CPANEL_PUBLIC_DIR=tmp_path):
        count = ensure_cpanel_route_dirs(
            (
                "dashboard/leads/1",
                "/admin/accounts/user/4/change/",
                "../ignored",
                "bad/../ignored",
            )
        )
        assert count == 2
        assert (tmp_path / "dashboard/leads/1").is_dir()
        assert (tmp_path / "admin/accounts/user/4/change").is_dir()
        assert not (tmp_path / "ignored").exists()


def test_admin_deep_url_without_trailing_slash_reaches_django(client) -> None:
    response = client.get("/admin/accounts/user")
    assert response.status_code == 302
    assert response["Location"].startswith("/admin/login/")
