import datetime
import os
from common.utils.request_utils import perform_request
from .market_details import MARKET_LIST


class PlentyMarketAPI:
    PLENTY_MARKET_BASE_URL = "https://www.toredo.de/rest"

    def __init__(self):
        self.base_url = self.PLENTY_MARKET_BASE_URL
        self.headers = {
            "Content-type": "application/json",
            "Accept": "application/json",
        }
        token = self.login()
        self.headers["Authorization"] = f"Bearer {token}"

    def login(self):
        url = f"{self.base_url}/login"
        response = perform_request(
            url,
            "post",
            self.headers,
            {
                "username": os.environ["PLENTYMARKET_USERNAME"],
                "password": os.environ["PLENTYMARKET_PASSWORD"],
            },
        )
        return response["access_token"]

    def get_address_data(self, address_id):
        url = f"{self.base_url}/accounts/addresses/{address_id}"
        response = perform_request(url, "get", self.headers)
        return response

    def get_order_details(self, order_id):
        url = f"{self.base_url}/orders/{order_id}"
        order_data = perform_request(
            url, "get", self.headers, {"with": "orderItems.serialNumbers"}
        )

        if not order_data:
            return None

        def get_utc_datetime_string(iso_datetime_string):
            return (
                datetime.datetime.fromisoformat(iso_datetime_string)
                .utcnow()
                .isoformat()
            )

        details = {
            "id": order_data["id"],
            "status": order_data["statusName"],
            "ext_created_at": get_utc_datetime_string(order_data["createdAt"]),
            "ext_updated_at": get_utc_datetime_string(order_data["updatedAt"]),
            "market_id": order_data["referrerId"],
            "ordered_items": [],
        }

        # get market name
        m_d = list(filter(lambda x: x["id"] == details["market_id"], MARKET_LIST))
        details["market_name"] = m_d[0]["name"] if len(m_d) else None

        # get external_order_id
        eid = list(filter(lambda x: x["typeId"] == 7, order_data["properties"]))
        details["external_order_id"] = eid[0]["value"] if len(eid) else None

        # get invoice number and date
        invoice_warranty = {'number': "", 'date': ""}
        # loop through all existing invoices
        for document in order_data.get('documents', []):
            if document['type'] == 'invoice':
                invoice_number = document['number']
                invoice_date = document['createdAt']

                # check if invoice warranty is already set
                if invoice_warranty['date'] == "":
                    invoice_warranty['number'] = invoice_number
                    invoice_warranty['date'] = get_utc_datetime_string(invoice_date)
                else:
                    # check which invoice number is smaller (older)
                    older_invoice = min(invoice_warranty['number'], invoice_number)
                    if older_invoice == invoice_number:
                        # re-define the invoice warranty
                        invoice_warranty['number'] = invoice_number
                        invoice_warranty['date'] = get_utc_datetime_string(invoice_date)
        details["invoice_number"] = invoice_warranty["number"] or "DUMMY"
        details["invoice_date"] = invoice_warranty["date"] or get_utc_datetime_string(
            order_data["createdAt"]
        )

        # get ordered items
        for oi in order_data["orderItems"]:
            if oi["itemVariationId"] == 0:
                continue
            od = {
                "name": oi["orderItemName"],
                "quantity": oi["quantity"],
                "ext_id": oi["id"],
                "variation_id": oi["itemVariationId"],
                "ext_created_at": get_utc_datetime_string(oi["createdAt"]),
                "ext_updated_at": get_utc_datetime_string(oi["updatedAt"]),
                "vat_rate": oi["vatRate"],
                "price_gross": oi["amounts"][0]["priceOriginalGross"],
                "price_net": oi["amounts"][0]["priceOriginalNet"],
                "discount": oi["amounts"][0]["discount"],
            }
            for sn in oi["serialNumbers"]:
                details["ordered_items"].append(
                    {**od, "serial_number": sn["serialNumber"]}
                )

        # get address data
        invoice_address_info = list(
            filter(lambda x: x["typeId"] == 1, order_data["addressRelations"])
        )
        shipping_address_info = list(
            filter(lambda x: x["typeId"] == 2, order_data["addressRelations"])
        )

        if invoice_address_info:
            invoice_address = self.get_address_data(
                invoice_address_info[0]["addressId"]
            )
            details["invoice_address"] = {
                "invoice_addr_company_name": invoice_address["name1"],
                "invoice_addr_first_name": invoice_address["name2"],
                "invoice_addr_last_name": invoice_address["name3"],
                "invoice_addr_line_1": invoice_address["address1"],
                "invoice_addr_line_2": invoice_address["address2"],
                "invoice_addr_line_3": invoice_address["address3"],
                "invoice_addr_zipcode": invoice_address["postalCode"],
                "invoice_addr_city": invoice_address["town"],
            }

            option_type_5 = list(
                filter(lambda x: x["typeId"] == 5, invoice_address["options"])
            )
            # customer email
            details["email"] = option_type_5[0]["value"] if len(option_type_5) else None
            option_type_4 = list(
                filter(lambda x: x["typeId"] == 4, invoice_address["options"])
            )
            # customer phone
            details["phone"] = option_type_4[0]["value"] if len(option_type_4) else None

        if shipping_address_info:
            shipping_address = self.get_address_data(
                shipping_address_info[0]["addressId"]
            )
            details["shipping_address"] = {
                "shipping_addr_company_name": shipping_address["name1"],
                "shipping_addr_first_name": shipping_address["name2"],
                "shipping_addr_last_name": shipping_address["name3"],
                "shipping_addr_line_1": shipping_address["address1"],
                "shipping_addr_line_2": shipping_address["address2"],
                "shipping_addr_line_3": shipping_address["address3"],
                "shipping_addr_zipcode": shipping_address["postalCode"],
                "shipping_addr_city": shipping_address["town"],
            }

        return details
