from django.db.models import Choices


class TicketType(Choices):
    order_ticket = "order_ticket"
    request_ticket = "request_ticket"
    internal_ticket = "internal_ticket"


class TicketStatus(Choices):
    new = "new"
    on_hold = "on_hold"
    waiting_for_answer = "waiting_for_answer"
    closed = "closed"
