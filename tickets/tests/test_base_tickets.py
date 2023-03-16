import json
import pytest

from accounts.tests.fixtures import admin_user_token
from common.tests_helpers import perform_api_call
from tickets.models import InternalTicket, Tag, Label

from .fixtures import setup_tickets_data, create_ticket_history


@pytest.mark.django_db
def test_adding_tags_to_ticket(admin_user_token):
    ticket = InternalTicket.objects.first()
    url = f"/api/tickets/{ticket.id}/tags/"
    assert ticket.tags.count() == 0

    response = perform_api_call(url, "post", {"name": "tag_1"}, admin_user_token)
    assert response.status_code == 200
    assert ticket.tags.count() == 1
    assert Tag.objects.all().count() == 1
    assert Tag.objects.all().first().name == "tag_1"

    # same tag should not be added twice
    response = perform_api_call(url, "post", {"name": "tag_1"}, admin_user_token)
    assert response.status_code == 200
    assert Tag.objects.all().count() == 1

    # test list api
    response = perform_api_call(url, "get", {}, admin_user_token)
    assert response.status_code == 200
    response = json.loads(response.content)
    assert len(response) == 1
    assert response[0] == "tag_1"

    # test delete API
    response = perform_api_call(url, "patch", {"name": "tag_1"}, admin_user_token)
    assert response.status_code == 200
    assert ticket.tags.count() == 0


@pytest.mark.django_db
def test_adding_labels_to_ticket(admin_user_token):
    ticket = InternalTicket.objects.first()
    url = f"/api/tickets/{ticket.id}/labels/"
    assert ticket.labels.count() == 0

    response = perform_api_call(url, "post", {"name": "label_1"}, admin_user_token)
    assert response.status_code == 200
    assert ticket.labels.count() == 1
    assert Label.objects.all().count() == 1
    assert Label.objects.all().first().name == "label_1"

    # same label should not be added twice
    response = perform_api_call(url, "post", {"name": "label_1"}, admin_user_token)
    assert response.status_code == 200
    assert Label.objects.all().count() == 1

    # test list api
    response = perform_api_call(url, "get", {}, admin_user_token)
    assert response.status_code == 200
    response = json.loads(response.content)
    assert len(response) == 1
    assert response[0] == "label_1"

    # test delete API
    response = perform_api_call(url, "patch", {"name": "label_1"}, admin_user_token)
    assert response.status_code == 200
    assert ticket.labels.count() == 0


@pytest.mark.django_db
def test_ticket_history(admin_user_token):
    ticket = InternalTicket.objects.first()
    create_ticket_history(ticket)
    url = f"/api/tickets/{ticket.id}/history/"
    response = perform_api_call(url, "get", {}, admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert len(response_data) == 1
    assert response_data[0]["description"] == "Ticket was created by app_admin"
    assert response_data[0]["updated_by"] == "app_admin"


@pytest.mark.django_db
def test_ticket_checklist(admin_user_token):
    ticket = InternalTicket.objects.first()
    # create checklist item
    url = f"/api/tickets/{ticket.id}/checklist/"
    assert ticket.checklist_items.count() == 0
    response = perform_api_call(url, "post", {"text": "New task"}, admin_user_token)
    assert response.status_code == 201
    assert ticket.checklist_items.count() == 1

    # get checklist item
    url = f"/api/tickets/{ticket.id}/checklist/"
    response = perform_api_call(url, "get", {}, admin_user_token)
    assert response.status_code == 200
    checklist_item = json.loads(response.content)[0]
    assert checklist_item["text"] == "New task"
    assert checklist_item["completed"] is False

    # update checklist item
    url = f"/api/tickets/checklist/{checklist_item['id']}/"
    response = perform_api_call(url, "patch", {"completed": True}, admin_user_token)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ticket_search(admin_user_token):
    ticket_1 = InternalTicket.objects.first()
    ticket_2 = InternalTicket.objects.last()
    ticket_1.title = "Testing title"
    ticket_1.save()

    url = f"/api/tickets/search/"
    response = perform_api_call(
        url, "get", {"query": "random string"}, admin_user_token
    )
    assert response.status_code == 200
    response_content = json.loads(response.content)
    assert len(response_content) == 0

    # test search using title
    url = f"/api/tickets/search/"
    response = perform_api_call(url, "get", {"query": "testing t"}, admin_user_token)
    assert response.status_code == 200
    response_content = json.loads(response.content)
    assert len(response_content) == 1
    assert response_content[0]["id"] == ticket_1.id

    # test search using id
    url = f"/api/tickets/search/"
    response = perform_api_call(url, "get", {"query": ticket_2.id}, admin_user_token)
    assert response.status_code == 200
    response_content = json.loads(response.content)
    assert len(response_content) == 1
    assert response_content[0]["id"] == ticket_2.id
