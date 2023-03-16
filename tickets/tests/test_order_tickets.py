import datetime
import json
import pytest
import os

from accounts.tests.fixtures import admin_user_token, customer_care_user_token
from common.tests_helpers import perform_api_call, assert_dict_with_object
from common.models import File
from tickets.models import OrderTicket

from .fixtures import setup_tickets_data, create_ticket_comment, create_file


def do_nothing(*args, **kwargs):
    return "Mocked data"


@pytest.mark.django_db
def test_order_tickets_list(admin_user_token):
    url = "/api/tickets/order-tickets/"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 10


@pytest.mark.django_db
def test_order_tickets_create(admin_user_token):
    url = "/api/tickets/order-tickets/"
    data = {
        "title": "test ticket",
        "market_name": "ebay",
        "market_id": "1",
        "order_id": "1234",
        "external_order_id": "EXT1234",
        "invoice_number": "IN7684",
        "invoice_date": "2018-02-01",
        "gender": "male",
        "first_name": "Test",
        "last_name": "User",
        "company_name": "Test company",
        "email": "customer@example.com",
        "phone": "+815538858",
        "products": [
            {
                "name": "Apple iPhone 13 Mini Smartphone 256GB Blau",
                "quantity": 1,
                "ext_id": 80443,
                "variation_id": 11183,
                "ext_created_at": "2022-08-24T12:02:49+02:00",
                "ext_updated_at": "2022-08-24T12:02:49+02:00",
                "vat_rate": 0,
                "price_gross": 689,
                "price_net": 689,
                "discount": 0,
            }
        ],
    }
    response = perform_api_call(url, "post", data, admin_user_token)
    assert response.status_code == 201

    response_data = json.loads(response.content)

    ordered_ticket = OrderTicket.objects.get(id=response_data["id"])

    assert ordered_ticket.products.count() == 1
    assert OrderTicket.objects.count() == 11
    order_ticket = OrderTicket.objects.last()
    assert_dict_with_object(data, order_ticket)
    assert (
        order_ticket.history.first().description == f"Ticket was created by app_admin"
    )


@pytest.mark.django_db
def test_order_ticket_comment(admin_user_token):
    ticket = OrderTicket.objects.last()
    url = f"/api/tickets/{ticket.id}/comments/"

    assert ticket.comments.count() == 0

    # create comment
    comment_data = {"comment": "comment 1 for testing"}
    response = perform_api_call(url, "post", comment_data, admin_user_token)
    assert response.status_code == 201
    assert ticket.comments.count() == 1

    # get comments
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content.decode())
    assert len(response_data) == 1


@pytest.mark.django_db
def test_doc_upload_in_comment(admin_user_token, monkeypatch):
    ticket = OrderTicket.objects.last()
    comment = create_ticket_comment(ticket)

    # upload doc to comment
    monkeypatch.setattr('common.serializers.upload_file_to_s3', do_nothing)
    monkeypatch.setattr('common.serializers.get_s3_signed_url', do_nothing)

    f = open("attachment.txt", "w")
    f.write("Hello World")
    f.close()

    with open('attachment.txt') as fp:
        url = f"/api/tickets/comments/{comment.id}/documents/"
        response = perform_api_call(
            url, "post", {"attachment": fp}, admin_user_token, False
        )
        assert response.status_code == 200

    # check if file was uploaded
    response = perform_api_call(url, "get", {}, admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content.decode())
    assert len(response_data) == 1
    assert response_data[0]["name"] == "attachment.txt"
    assert response_data[0]["uploaded_by"] == "app_admin"

    os.remove("attachment.txt")


@pytest.mark.django_db
def test_doc_upload_in_ticket(admin_user_token, monkeypatch):
    monkeypatch.setattr('common.serializers.upload_file_to_s3', do_nothing)
    monkeypatch.setattr('common.serializers.get_s3_signed_url', do_nothing)

    ticket = OrderTicket.objects.last()

    f = open("attachment.txt", "w")
    f.write("Hello World")
    f.close()

    assert ticket.documents.count() == 0
    with open('attachment.txt') as fp:
        url = f"/api/tickets/{ticket.pk}/documents/"
        response = perform_api_call(
            url, "post", {"attachment": fp}, admin_user_token, False
        )
        assert response.status_code == 200

    # check if file was uploaded
    response = perform_api_call(url, "get", {}, admin_user_token)
    assert response.status_code == 200
    assert ticket.documents.count() == 1
    doc = ticket.documents.first()
    assert doc.name == "attachment.txt"
    assert doc.uploaded_by.username == "app_admin"

    os.remove("attachment.txt")


@pytest.mark.django_db
def test_doc_delete_in_ticket_by_customer_agent(customer_care_user_token, monkeypatch):
    monkeypatch.setattr('common.models.delete_files_from_s3', do_nothing)

    ticket = OrderTicket.objects.last()
    f = create_file()
    ticket.documents.add(f)
    url = f"/api/tickets/documents/{f.id}/"

    # test delete by customer agent is not possible if file is created before 5 mins
    response = perform_api_call(url, "delete", {}, customer_care_user_token)
    assert response.status_code == 403

    File.objects.filter(id=f.id).update(created_at=datetime.datetime.now())
    response = perform_api_call(url, "delete", {}, customer_care_user_token)
    assert response.status_code == 204


@pytest.mark.django_db
def test_doc_delete_in_ticket_by_app_admin(admin_user_token, monkeypatch):
    monkeypatch.setattr('common.models.delete_files_from_s3', do_nothing)

    ticket = OrderTicket.objects.last()
    f = create_file()
    ticket.documents.add(f)
    url = f"/api/tickets/documents/{f.id}/"

    response = perform_api_call(url, "delete", {}, admin_user_token)
    assert response.status_code == 204


@pytest.mark.django_db
def test_filtering(admin_user_token, monkeypatch):
    OrderTicket.objects.all().update(status="new")
    ticket = OrderTicket.objects.last()
    ticket.status = "closed"
    ticket.save()

    # filter for new tickets
    url = "/api/tickets/order-tickets/?status=new"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 9

    # filter for closed tickets
    url = "/api/tickets/order-tickets/?status=closed"
    response = perform_api_call(url, "get", "", admin_user_token)
    assert response.status_code == 200
    response_data = json.loads(response.content)
    assert response_data["count"] == 1
