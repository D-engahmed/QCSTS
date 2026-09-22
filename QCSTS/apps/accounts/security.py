from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


@transaction.atomic
def revoke_user_sessions(user):
    """Revoke every outstanding refresh token issued to this user."""
    User = get_user_model()
    if not isinstance(user, User):
        raise TypeError("revoke_user_sessions expects the configured user model.")

    outstanding = OutstandingToken.objects.filter(user=user)
    for token in outstanding.iterator():
        BlacklistedToken.objects.get_or_create(token=token)
