import pytest
from services.signatureature_service import SignatureService
from django.core.cache import cache

@pytest.mark.django_db
class TestSignatureServiceConcurrency:
    def test_token_replay_is_prevented(self, user):
        cache.clear()
        token = SignatureService.issue(user)
        
        # First validation succeeds
        assert SignatureService.validate(user, token) is True
        
        # Second validation (replay) must fail immediately
        assert SignatureService.validate(user, token) is False