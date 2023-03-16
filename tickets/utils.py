import base64
import logging
import requests
from common.connectors.dhl import DHLAdapter

logger = logging.getLogger(__name__)


def get_changed_fields(old_data: dict, new_data: dict):
    """
    Compares 2 dicts for keys that have different values
    """
    changes = []
    for key in new_data:
        if key not in old_data:
            continue
        if old_data[key] != new_data[key]:
            changes.append(
                {"field": key, "old_value": old_data[key], "new_value": new_data[key]}
            )
    return changes


def dhl_return_label_from_order_ticket(order_ticket):
    """
    Generates the return for an order ticket
    """
    connector = DHLAdapter()
    response = connector.get_return_label(
        receiver_id="Lager_DE_02",
        customer_reference=f"Ticket {order_ticket.id}",
        shipping_reference=f"Ticket {order_ticket.id}",
        sender_address={
            "name1": order_ticket.invoice_addr_company_name or "",
            "name2": f"{order_ticket.first_name} {order_ticket.last_name}" or "",
            "name3": order_ticket.invoice_addr_line_3 or "",
            "streetName": order_ticket.invoice_addr_line_2 or "",
            "houseNumber": order_ticket.invoice_addr_line_1 or "",
            "postCode": order_ticket.invoice_addr_zipcode or "",
            "city": order_ticket.invoice_addr_city or "",
            "country": {"countryISOCode": "DEU", "country": "Germany"},
        },
        customer_email=order_ticket.email,
        customer_phone=order_ticket.phone,
        weight_in_grams=2000,
    )
    if isinstance(response, dict):
        order_ticket.dhl_return_shipment_number = response["shiptment_number"]
        order_ticket.dhl_return_label_data = response["label_data"]
        order_ticket.save()
        return order_ticket
    else:
        logger.debug(response)
        logger.debug(response.content)


def dhl_shipping_label_from_order_ticket(order_ticket):
    """
    Generates the shipping label for an order ticket
    """
    connector = DHLAdapter()
    response = connector.get_shipping_label_for_address(
        customer_reference=f"Ticket {order_ticket.id}",
        weight_in_kg=2,
        name_1="fg",
        name_2=f"{order_ticket.first_name} {order_ticket.last_name}",
        name_3=order_ticket.invoice_addr_line_3 or "",
        street_with_number=f"{order_ticket.invoice_addr_line_1} {order_ticket.invoice_addr_line_2}"
        or "",
        zip_code=order_ticket.invoice_addr_zipcode or "",
        city=order_ticket.invoice_addr_city or "",
        customer_email=order_ticket.email or "",
    )
    if response and isinstance(response, list):
        dhl_shipping_label_number = response[0]
        dhl_shipping_label_url = response[1]
        pdf_response = requests.get(dhl_shipping_label_url)
        order_ticket.dhl_shipping_label_number = dhl_shipping_label_number
        order_ticket.dhl_shipping_label_data = base64.b64encode(
            pdf_response.content
        ).decode()
        order_ticket.save()
        return order_ticket
    else:
        logger.debug(response)
