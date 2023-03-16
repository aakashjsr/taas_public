import json
import pytest

from accounts.tests.fixtures import admin_user_token
from common.tests_helpers import perform_api_call, assert_dict_with_object
from tickets.models import RequestTicket

from .fixtures import setup_tickets_data


def do_nothing(*args, **kwargs):
    return "Mocked data"


@pytest.mark.django_db
def test_request_tickets_list(admin_user_token):
    url = "/api/tickets/request-tickets/"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 9


@pytest.mark.django_db
def test_request_tickets_create(admin_user_token):
    url = "/api/tickets/request-tickets/"
    data = {
        "title": "test ticket",
        "gender": "male",
        "first_name": "Test",
        "last_name": "User",
        "company_name": "Test company",
        "email": "customer@example.com",
        "phone": "+815538858",
    }
    response = perform_api_call(url, "post", data, admin_user_token)
    assert response.status_code == 201

    assert RequestTicket.objects.count() == 10
    req_ticket = RequestTicket.objects.last()
    assert_dict_with_object(data, req_ticket)
    assert req_ticket.history.first().description == f"Ticket was created by app_admin"


@pytest.mark.django_db
def test_filtering(admin_user_token, monkeypatch):
    RequestTicket.objects.all().update(status="new")
    ticket = RequestTicket.objects.last()
    ticket.status = "closed"
    ticket.save()

    # filter for new tickets
    url = "/api/tickets/request-tickets/?status=new"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 8

    # filter for closed tickets
    url = "/api/tickets/request-tickets/?status=closed"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 1
