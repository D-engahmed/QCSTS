import pytest
import threading
from services.signature_service import SignatureService
from django.core.cache import cache
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestSignatureServiceReplay:
    """Verify one-time-use token cannot be replayed."""

    def _create_user(self):
        User = get_user_model()
        return User.objects.create_user(
            email="test@example.com", 
            password="password123",
            role="analyst"
        )

    def test_token_cannot_be_replayed(self):
        user = self._create_user()
        cache.clear()
        token = SignatureService.issue(user)

        assert SignatureService.validate(user, token) is True
        assert SignatureService.validate(user, token) is False

    def test_concurrent_token_replay_is_blocked(self):
        user = self._create_user()
        cache.clear()
        token = SignatureService.issue(user)
        results = []
        lock = threading.Lock()

        def attempt_validate():
            result = SignatureService.validate(user, token)
            with lock:
                results.append(result)

        threads = [threading.Thread(target=attempt_validate) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        success_count = sum(1 for r in results if r is True)
        failure_count = sum(1 for r in results if r is False)

        assert success_count == 1, f"Expected 1 success, got {success_count}"
        assert failure_count == 9, f"Expected 9 failures, got {failure_count}"

    def test_expired_or_invalid_token_fails(self):
        user = self._create_user()
        cache.clear()

        assert SignatureService.validate(user, "invalid-token-uuid") is False
        assert SignatureService.validate(user, "") is False
        assert SignatureService.validate(user, None) is False