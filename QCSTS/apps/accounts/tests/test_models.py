import pytest
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestCustomUser:

    def test_user_str(self):
        user = UserFactory(full_name="Ahmed Ali", email="ahmed@cqsts.com")
        assert str(user) == "Ahmed Ali (ahmed@cqsts.com)"

    def test_increment_failed_attempts(self):
        user = UserFactory()
        user.increment_failed_attempts()
        user.refresh_from_db()
        assert user.failed_login_attempts == 1
        assert user.is_active is True

    def test_account_locks_after_5_attempts(self):
        user = UserFactory()
        for _ in range(5):
            user.increment_failed_attempts()
        user.refresh_from_db()
        assert user.is_active is False

    def test_reset_failed_attempts(self):
        user = UserFactory()
        user.increment_failed_attempts()
        user.increment_failed_attempts()
        user.reset_failed_attempts()
        user.refresh_from_db()
        assert user.failed_login_attempts == 0

    def test_user_has_uuid_id(self):
        user = UserFactory()
        assert user.id is not None
        assert len(str(user.id)) == 36  # UUID format

    def test_default_role_is_analyst(self):
        user = UserFactory()
        assert user.role == "analyst"
