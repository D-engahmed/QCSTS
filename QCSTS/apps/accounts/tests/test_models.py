from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
import pytest
from apps.accounts.models import CustomUser
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestCustomUser:

    def test_email_is_unique_case_insensitively_in_database(self):
        UserFactory(email="person@example.test")
        with pytest.raises(IntegrityError), transaction.atomic():
            CustomUser.objects.create_user(
                email="PERSON@example.test", password="TestPass123!", full_name="Second User"
            )

    def test_user_str(self):
        user = UserFactory(full_name="Ahmed Ali", email="ahmed@cqsts.com")
        assert str(user) == "Ahmed Ali (ahmed@cqsts.com)"

    def test_failed_login_is_counted_without_disabling_the_account(self):
        user = UserFactory()
        user.register_failed_login()
        user.refresh_from_db()
        assert user.failed_login_attempts == 1
        assert user.is_active is True
        assert user.is_locked_out is False

    def test_account_locks_for_a_window_after_5_attempts(self):
        user = UserFactory()
        for _ in range(5):
            user.register_failed_login()
        user.refresh_from_db()
        assert user.is_locked_out is True
        # is_active is the soft-delete flag and must stay untouched: a locked
        # account and a deleted account must remain distinguishable.
        assert user.is_active is True

    def test_lockout_expires_on_its_own(self):
        user = UserFactory()
        for _ in range(5):
            user.register_failed_login()
        user.locked_until = timezone.now() - timedelta(seconds=1)
        user.save(update_fields=["locked_until"])
        assert user.is_locked_out is False

    def test_reset_clears_counter_and_lock(self):
        user = UserFactory()
        for _ in range(5):
            user.register_failed_login()
        user.reset_failed_attempts()
        user.refresh_from_db()
        assert user.failed_login_attempts == 0
        assert user.locked_until is None
        assert user.is_locked_out is False

    def test_user_has_uuid_id(self):
        user = UserFactory()
        assert user.id is not None
        assert len(str(user.id)) == 36  # UUID format

    def test_default_role_is_analyst(self):
        user = UserFactory()
        assert user.role == "analyst"
