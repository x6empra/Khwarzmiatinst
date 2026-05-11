"""reCAPTCHA tests — F8 (TESTING.md §Unit)."""

from unittest.mock import patch

from apps.leads.recaptcha import verify_recaptcha


class TestRecaptcha:
    def test_dev_mode_passes_without_key(self, settings):
        """No PRIVATE_KEY → passed=True (dev bypass)."""
        settings.RECAPTCHA_PRIVATE_KEY = ""
        passed, err = verify_recaptcha("any-token")
        assert passed is True
        assert err is None

    def test_missing_token_fails_in_prod(self, settings):
        settings.RECAPTCHA_PRIVATE_KEY = "secret"
        passed, err = verify_recaptcha(None)
        assert passed is False
        assert err == "missing_token"

    def test_low_score_rejected(self, settings):
        settings.RECAPTCHA_PRIVATE_KEY = "secret"
        settings.RECAPTCHA_REQUIRED_SCORE = 0.5
        with patch("apps.leads.recaptcha.urlopen") as mocked:
            mocked.return_value.__enter__.return_value.read.return_value = (
                b'{"success": true, "score": 0.2}'
            )
            passed, err = verify_recaptcha("token")
        assert passed is False
        assert "low_score" in err

    def test_high_score_passes(self, settings):
        settings.RECAPTCHA_PRIVATE_KEY = "secret"
        settings.RECAPTCHA_REQUIRED_SCORE = 0.5
        with patch("apps.leads.recaptcha.urlopen") as mocked:
            mocked.return_value.__enter__.return_value.read.return_value = (
                b'{"success": true, "score": 0.9}'
            )
            passed, err = verify_recaptcha("token")
        assert passed is True
        assert err is None

    def test_google_rejection(self, settings):
        settings.RECAPTCHA_PRIVATE_KEY = "secret"
        with patch("apps.leads.recaptcha.urlopen") as mocked:
            mocked.return_value.__enter__.return_value.read.return_value = (
                b'{"success": false, "error-codes": ["invalid-input-secret"]}'
            )
            passed, err = verify_recaptcha("token")
        assert passed is False
        assert "google_rejected" in err
