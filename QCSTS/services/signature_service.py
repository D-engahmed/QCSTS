import uuid
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SignatureService:
    """
    Issues and validates short-lived electronic signature tokens.

    Flow:
        1. Analyst POSTs password to /api/v1/results/signature/verify/
        2. SignatureService.issue(user) → stores token in cache for 5 min
        3. Analyst includes X-Signature-Token header when submitting results
        4. SignatureService.validate(user, token) → True or False

    Token lifetime: 5 minutes (300 seconds)
    Storage: Django cache (locmem in dev, Redis in production)
    """

    TOKEN_TTL = 300  # seconds

    @classmethod
    def issue(cls, user) -> str:
        """
        Generates a new signature token for the user and stores it in cache.
        Returns the token string to send back to the frontend.
        """
        token = str(uuid.uuid4())
        cache_key = cls._cache_key(user.id, token)
        cache.set(cache_key, True, timeout=cls.TOKEN_TTL)
        logger.info("SignatureService: issued token for user %s", user.email)
        return token

    @classmethod
    def validate(cls, user, token: str) -> bool:
        """
        Returns True if the token is valid and not expired.
        Consumes the token on success — one-time use.
        """
        if not token:
            return False
        cache_key = cls._cache_key(user.id, token)
        is_valid = cache.get(cache_key)
        if is_valid:
            cache.delete(cache_key)
            logger.info("SignatureService: token validated for user %s", user.email)
            return True
        logger.warning("SignatureService: invalid/expired token for user %s", user.email)
        return False

    @staticmethod
    def _cache_key(user_id, token: str) -> str:
        return f"sig_token:{user_id}:{token}"
