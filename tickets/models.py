from django.db import models

from common.models import TimeStampedModel, File
from .constants import TicketType, TicketStatus


class Tag(TimeStampedModel):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, null=True, blank=True)

    def __str__(self):
        return self.name


class Label(TimeStampedModel):
    name = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, null=True, blank=True)

    def __str__(self):
        return self.name


class TicketHistory(TimeStampedModel):
    description = models.TextField(null=True, blank=True)
    updated_by = models.ForeignKey(
        "accounts.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="ticket_updates",
    )


class TicketComment(TimeStampedModel):
    comment = models.TextField()
    added_by = models.ForeignKey(
        "accounts.User",
        null=True,
        on_delete=models.SET_NULL,
        related_name="ticket_comments",
    )
    tagged_users = models.ManyToManyField(
        "accounts.User", related_name="tagged_comments", null=True, blank=True
    )
    documents = models.ManyToManyField(File, null=True, blank=True)


class BaseTicket(TimeStampedModel):
    ticket_type = models.CharField(max_length=20, choices=TicketType.choices)
    title = models.CharField(max_length=1000)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=TicketStatus.choices, default=TicketStatus.new.value
    )
    tags = models.ManyToManyField(Tag, related_name="tickets", null=True, blank=True)
    labels = models.ManyToManyField(
        Label, related_name="tickets", null=True, blank=True
    )

    linked_tickets = models.ManyToManyField("self", null=True, blank=True)
    documents = models.ManyToManyField(File, null=True, blank=True)
    comments = models.ManyToManyField(TicketComment, null=True, blank=True)
    history = models.ManyToManyField(TicketHistory, null=True, blank=True)


class TicketChecklistItem(TimeStampedModel):
    ticket = models.ForeignKey(
        BaseTicket, related_name="checklist_items", on_delete=models.CASCADE
    )
    text = models.TextField()
    completed = models.BooleanField(default=False)


class OrderTicket(BaseTicket):
    # Order related fields
    market_name = models.CharField(max_length=50)
    market_id = models.CharField(max_length=20)
    order_id = models.CharField(max_length=20)
    external_order_id = models.CharField(max_length=20, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    invoice_date = models.DateTimeField(null=True, blank=True)

    # Customer related fields
    gender = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    # invoice address
    invoice_addr_company_name = models.CharField(max_length=200, null=True, blank=True)
    invoice_addr_first_name = models.CharField(max_length=200, null=True, blank=True)
    invoice_addr_last_name = models.CharField(max_length=200, null=True, blank=True)
    invoice_addr_line_1 = models.CharField(max_length=200, null=True, blank=True)
    invoice_addr_line_2 = models.CharField(max_length=200, null=True, blank=True)
    invoice_addr_line_3 = models.CharField(max_length=200, null=True, blank=True)
    invoice_addr_zipcode = models.CharField(max_length=200, null=True, blank=True)
    invoice_addr_city = models.CharField(max_length=200, null=True, blank=True)

    # delivery address
    shipping_addr_company_name = models.CharField(max_length=200, null=True, blank=True)
    shipping_addr_first_name = models.CharField(max_length=200, null=True, blank=True)
    shipping_addr_last_name = models.CharField(max_length=200, null=True, blank=True)
    shipping_addr_line_1 = models.CharField(max_length=200, null=True, blank=True)
    shipping_addr_line_2 = models.CharField(max_length=200, null=True, blank=True)
    shipping_addr_line_3 = models.CharField(max_length=200, null=True, blank=True)
    shipping_addr_zipcode = models.CharField(max_length=200, null=True, blank=True)
    shipping_addr_city = models.CharField(max_length=200, null=True, blank=True)

    dhl_return_shipment_number = models.CharField(max_length=500, null=True, blank=True)
    dhl_return_label_data = models.TextField(null=True, blank=True)
    dhl_return_label_created_at = models.DateTimeField(null=True, blank=True)

    dhl_shipping_label_number = models.CharField(max_length=500, null=True, blank=True)
    dhl_shipping_label_data = models.TextField(null=True, blank=True)
    dhl_shipping_label_created_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ticket_type:
            self.ticket_type = TicketType.order_ticket.value
        return super().save(*args, **kwargs)


class OrderedProduct(TimeStampedModel):
    order_ticket = models.ForeignKey(
        OrderTicket, on_delete=models.CASCADE, related_name="products"
    )

    ext_id = models.IntegerField()
    quantity = models.IntegerField()
    name = models.CharField(max_length=200)
    variation_id = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=200, null=True, blank=True)
    vat_rate = models.DecimalField(max_digits=10, decimal_places=2)
    price_gross = models.DecimalField(max_digits=10, decimal_places=2)
    price_net = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    ext_created_at = models.DateTimeField()
    ext_updated_at = models.DateTimeField()

    def __str__(self) -> str:
        return self.name


class RequestTicket(BaseTicket):
    # Customer related fields
    gender = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    market_name = models.CharField(max_length=50, null=True, blank=True)
    company_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.ticket_type:
            self.ticket_type = TicketType.request_ticket.value
        return super().save(*args, **kwargs)


class InternalTicket(BaseTicket):
    def save(self, *args, **kwargs):
        if not self.ticket_type:
            self.ticket_type = TicketType.internal_ticket.value
        return super().save(*args, **kwargs)
