from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import TimeStampedModel
from .constants import UserTypeChoice


class User(AbstractUser, TimeStampedModel):
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    alias_name = models.CharField(max_length=500, null=True, blank=True)
    user_type = models.CharField(
        max_length=50,
        choices=UserTypeChoice.choices,
        default=UserTypeChoice.customer_care.value,
    )
    remember_me = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.get_full_name()
        super().save(*args, **kwargs)
