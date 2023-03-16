import datetime
import pytest
import random
import faker

from accounts.models import User
from common.models import File
from tickets.models import (
    OrderTicket,
    RequestTicket,
    InternalTicket,
    TicketComment,
    TicketHistory,
)
from tickets.constants import TicketStatus

data_generator = faker.Faker()


def create_ticket_history(ticket):
    user = User.objects.first()
    h = TicketHistory.objects.create(
        updated_by=user,
        description=f"Ticket was created by {user}",
    )
    ticket.history.add(h)


def create_order_ticket():
    d = {
        "title": data_generator.text(100),
        "description": data_generator.text(),
        "status": random.choice(TicketStatus.values),
        "market_name": random.choice(["Amazon", "Ebay", "Backmarket"]),
        "market_id": data_generator.numerify(),
        "order_id": data_generator.numerify(),
        "external_order_id": data_generator.numerify(),
        "invoice_number": "INV" + data_generator.numerify(),
        "invoice_date": data_generator.date(),
        "gender": random.choice(["male", "female"]),
        "first_name": data_generator.first_name(),
        "last_name": data_generator.last_name(),
        "company_name": data_generator.company(),
        "email": data_generator.email(),
        "phone": data_generator.msisdn(),
        "invoice_addr_company_name": data_generator.text(100),
        "invoice_addr_first_name": data_generator.first_name(),
        "invoice_addr_last_name": data_generator.last_name(),
        "invoice_addr_line_1": data_generator.street_address(),
        "invoice_addr_line_2": data_generator.street_address(),
        "invoice_addr_line_3": data_generator.street_address(),
        "invoice_addr_zipcode": data_generator.postcode(),
        "invoice_addr_city": data_generator.city(),
        "shipping_addr_company_name": data_generator.text(100),
        "shipping_addr_first_name": data_generator.first_name(),
        "shipping_addr_last_name": data_generator.last_name(),
        "shipping_addr_line_1": data_generator.street_address(),
        "shipping_addr_line_2": data_generator.street_address(),
        "shipping_addr_line_3": data_generator.street_address(),
        "shipping_addr_zipcode": data_generator.postcode(),
        "shipping_addr_city": data_generator.city(),
    }
    o = OrderTicket.objects.create(**d)


def create_request_ticket():
    d = {
        "title": data_generator.text(100),
        "description": data_generator.text(),
        "status": random.choice(TicketStatus.values),
        "gender": random.choice(["male", "female"]),
        "first_name": data_generator.first_name(),
        "last_name": data_generator.last_name(),
        "company_name": data_generator.company(),
        "email": data_generator.email(),
        "phone": data_generator.msisdn(),
    }
    r = RequestTicket.objects.create(**d)


def create_internal_ticket():
    d = {
        "title": data_generator.text(100),
        "description": data_generator.text(),
        "status": random.choice(TicketStatus.values),
    }
    i = InternalTicket.objects.create(**d)


def create_ticket_comment(ticket):
    c = TicketComment.objects.create(
        comment=data_generator.text(), added_by=User.objects.get(username="app_admin")
    )
    ticket.comments.add(c)
    return c


def create_file():
    data = {
        'name': 'attachment.txt',
        'content_type': 'text/plain',
        'size_kb': 0.01,
        'uploaded_by_id': 1,
        's3_bucket': '',
        'key': 'ticket_documents/1/attachment.txt',
        'url': 'https://.s3.amazonaws.com/ticket_documents/1/attachment.txt',
        'hash': None,
    }
    f = File.objects.create(**data)
    File.objects.filter(id=f.id).update(
        created_at=datetime.datetime.now() - datetime.timedelta(minutes=10)
    )
    return f


@pytest.fixture(autouse=True)
def setup_tickets_data():
    """
    creates 10 order tickets, 9 request tickets, 8 internal tickets
    """
    for _ in range(5):
        create_order_ticket()
    for _ in range(5):
        create_request_ticket()
    for _ in range(5):
        create_internal_ticket()

    for _ in range(5):
        create_order_ticket()
    for _ in range(4):
        create_request_ticket()
    for _ in range(3):
        create_internal_ticket()

    yield
    map(lambda x: x.objects.delete(), [OrderTicket, RequestTicket, InternalTicket])
