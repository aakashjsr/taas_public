import pytest
import json

from rest_framework.authtoken.models import Token
from common.tests_helpers import perform_api_call
from accounts.models import User
from accounts.constants import UserTypeChoice
from accounts.tests.fixtures import admin_user_token


@pytest.mark.django_db
def test_user_creation(client, admin_user_token):
    user_data = {
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "User 1",
        "last_name": "Example",
        "password": "Testing@123",
        "alias_name": "User 1 Alias",
    }

    response = perform_api_call(
        url="/api/accounts/users/",
        method="post",
        data=user_data,
        token=admin_user_token,
    )
    assert response.status_code == 201

    user = User.objects.get(username="user1")
    assert user.email == user_data["email"]
    assert user.first_name == user_data["first_name"]
    assert user.last_name == user_data["last_name"]
    assert user.alias_name == user_data["alias_name"]
    assert user.user_type == UserTypeChoice.customer_care.value


@pytest.mark.django_db
def test_user_delete(client, admin_user_token):
    user_data = {
        "username": "user1",
        "email": "user1@example.com",
        "password": "Testing@123",
    }
    perform_api_call(
        url="/api/accounts/users/",
        method="post",
        data=user_data,
        token=admin_user_token,
    )
    user = User.objects.get(username="user1")

    response = perform_api_call(
        url=f"/api/accounts/users/{user.id}/",
        method="delete",
        data={},
        token=admin_user_token,
    )
    assert response.status_code == 204
    assert User.objects.filter(username="user1").count() == 0


@pytest.mark.django_db
def test_user_update(client, admin_user_token):
    user_data = {
        "username": "user1",
        "email": "user1@example.com",
        "password": "Testing@123",
    }
    perform_api_call(
        url="/api/accounts/users/",
        method="post",
        data=user_data,
        token=admin_user_token,
    )
    data = {
        "first_name": "Edited first name",
        "last_name": "Edited last name",
        "user_type": UserTypeChoice.admin.value,
        "email": "EditEmail@example.com",
    }

    user = User.objects.get(username="user1")
    response = perform_api_call(
        url=f"/api/accounts/users/{user.id}/",
        method="patch",
        data=data,
        token=admin_user_token,
    )

    assert response.status_code == 200

    user.refresh_from_db()
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.user_type == data["user_type"]
    assert user.email == data["email"]


@pytest.mark.django_db
def test_login(admin_user_token, client):
    url = "/api/accounts/login/"
    response = perform_api_call(
        url=url,
        method="post",
        data={"email": "app_admin@example.com", "password": "dd"},
        token=admin_user_token,
    )
    assert response.status_code == 403

    response = perform_api_call(
        url=url,
        method="post",
        data={"email": "app_admin@example.com", "password": "app_admin"},
        token=admin_user_token,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout(admin_user_token, client):
    url = "/api/accounts/logout/"
    assert Token.objects.filter(key=admin_user_token).count() == 1
    response = perform_api_call(url=url, method="post", data={}, token=admin_user_token)
    assert response.status_code == 200
    assert Token.objects.filter(key=admin_user_token).count() == 0


@pytest.mark.django_db
def test_taggable_user(admin_user_token, client):
    url = "/api/accounts/taggable-users/"
    response = perform_api_call(
        url=url,
        method="get",
        data={},
        token=admin_user_token,
    )
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data) == 1
    assert "id" in response_data[0]
    assert "display" in response_data[0]
