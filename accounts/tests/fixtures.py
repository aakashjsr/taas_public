import pytest
import faker
from rest_framework.authtoken.models import Token

from accounts.models import User
from accounts.constants import UserTypeChoice


data_generator = faker.Faker()


@pytest.fixture
def admin_user_token():
    user = User.objects.create_user(
        first_name=data_generator.first_name(),
        last_name=data_generator.last_name(),
        username="app_admin",
        email="app_admin@example.com",
        password="app_admin",
        user_type=UserTypeChoice.admin.value,
    )
    token, _ = Token.objects.get_or_create(user=user)
    return token.key


@pytest.fixture
def customer_care_user_token():
    user = User.objects.create_user(
        first_name=data_generator.first_name(),
        last_name=data_generator.last_name(),
        username="app_customer_care",
        password="app_customer_care",
        user_type=UserTypeChoice.customer_care.value,
    )
    token, _ = Token.objects.get_or_create(user=user)
    return token.key
