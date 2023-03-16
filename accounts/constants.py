from django.db import models


class UserTypeChoice(models.TextChoices):
    admin = "admin"
    customer_care = "customer_care"
