from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class TAASTokenAuthBackend(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        time_elapsed = timezone.now() - token.created
        left_time = (
            timedelta(seconds=settings.TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
        )
        if left_time < timedelta(seconds=0) and not user.remember_me:
            token.delete()
            exceptions.AuthenticationFailed("Token expired")

        return user, token
