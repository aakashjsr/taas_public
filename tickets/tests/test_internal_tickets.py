import json
import pytest

from accounts.tests.fixtures import admin_user_token
from common.tests_helpers import perform_api_call, assert_dict_with_object
from tickets.models import InternalTicket, Tag, Label

from .fixtures import setup_tickets_data


def do_nothing(*args, **kwargs):
    return "Mocked data"


@pytest.mark.django_db
def test_internal_tickets_list(admin_user_token):
    url = "/api/tickets/internal-tickets/"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 8


@pytest.mark.django_db
def test_internal_tickets_create(admin_user_token):
    url = "/api/tickets/internal-tickets/"
    data = {
        "title": "test ticket",
    }
    response = perform_api_call(url, "post", data, admin_user_token)
    assert response.status_code == 201

    assert InternalTicket.objects.count() == 9
    req_ticket = InternalTicket.objects.last()
    assert_dict_with_object(data, req_ticket)
    assert req_ticket.history.first().description == f"Ticket was created by app_admin"


@pytest.mark.django_db
def test_filtering(admin_user_token, monkeypatch):
    InternalTicket.objects.all().update(status="new")
    ticket = InternalTicket.objects.last()
    ticket.status = "closed"
    ticket.save()

    # filter for new tickets
    url = "/api/tickets/internal-tickets/?status=new"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 7

    # filter for closed tickets
    url = "/api/tickets/internal-tickets/?status=closed"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 1
