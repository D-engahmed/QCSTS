"""
Login throttling.

Account lockout on its own is not a brute-force defence — it is a denial of
service lever. Without a rate limit an attacker can lock every address they
know, for free, as fast as the network allows. The throttle is the control
that makes the lockout safe to have.
"""

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

from apps.accounts.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def clear_throttle_history():
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_repeated_login_attempts_are_throttled(monkeypatch):
    # Patch the rate on the throttle class itself: override_settings does not
    # reliably reach DRF's cached rate table once the view class is imported.
    monkeypatch.setattr(
        ScopedRateThrottle, "THROTTLE_RATES", {"login": "3/min", "signature": "100/min"}
    )
    user = UserFactory()
    client = APIClient(REMOTE_ADDR="203.0.113.77")
    statuses = []
    for _ in range(6):
        response = client.post(
            "/api/v1/auth/login/", {"email": user.email, "password": "WrongPassword!"}
        )
        statuses.append(response.status_code)

    assert 429 in statuses, (
        f"Login was never throttled across 6 attempts (statuses: {statuses}). "
        "An unthrottled login endpoint makes the 5-strike lockout a free DoS."
    )
    assert statuses.index(429) <= 4

    # And the lockout it backstops must not soft-delete the account: is_active
    # is the GxP soft-delete flag, not a security control.
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
def test_login_view_pins_its_own_throttle():
    """Regression guard: the rate limit must not depend on global defaults."""
    from apps.accounts.views import LoginView

    assert ScopedRateThrottle in LoginView.throttle_classes
    assert LoginView.throttle_scope == "login"
