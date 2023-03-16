import os
import json
import logging
from requests import Session, post
from zeep import Client, xsd
from zeep.transports import Transport
from base64 import b64encode
from requests import Session
from requests.auth import HTTPBasicAuth
from datetime import date


logger = logging.getLogger(__name__)


class DHLAdapter:
    """
    doc: https://entwickler.dhl.de/group/ep/home
    """

    def __init__(self):
        self.base_url = "https://cig.dhl.de/services/production/rest/"
        project_user_pass = b64encode(os.environ["DHL_B64_CREDENTIAL"]).decode("ascii")
        acccount_user_pass = b64encode(b"toredo-api:DaLnL$#bU3EH9uG").decode("ascii")
        self.headers = {
            'Authorization': 'Basic %s' % project_user_pass,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'DPDHL-User-Authentication-Token': acccount_user_pass,
        }
        logger.info("Successful: Request Handler for DHL has been prepared")

    def get_return_label(
        self,
        receiver_id: str,
        customer_reference: str,
        shipping_reference: str,
        sender_address: dict,
        customer_email: str,
        customer_phone: str,
        weight_in_grams: int,
    ):

        url = f"{self.base_url}returns/"

        payload = {
            "receiverId": receiver_id,
            "customerReference": customer_reference,
            "shipmentReference": shipping_reference,
            "senderAddress": sender_address,
            "email": customer_email,
            "telephoneNumber": customer_phone,
            "weightInGrams": weight_in_grams,
            # "value": 60,
            "returnDocumentType": "SHIPMENT_LABEL",
        }

        response = post(url, headers=self.headers, data=json.dumps(payload))
        return_label = {}
        try:
            return_label["shiptment_number"] = response.json()["shipmentNumber"]
            return_label["label_data"] = response.json()['labelData']
            return return_label
        except:
            return response

    def get_shipping_label_for_address(
        self,
        customer_reference: str,
        weight_in_kg: int,
        name_1: str,
        street_with_number: str,
        zip_code: str,
        city: str,
        name_2: str = "",
        name_3: str = "",
        customer_email: str = "",
    ):

        user = "after_sales_management_1"
        password = "79xD7EJvBzXUyl388H5z0ub6ui5Arp"
        USER = os.environ["DHL_USERNAME"]
        PASSWORD = os.environ["DHL_PASSWORD"]

        base_url = "https://cig.dhl.de/services/production/soap"

        wsdl = "common/connectors/dhl_files/geschaeftskundenversand-api-3.4.0/geschaeftskundenversand-api-3.4.0.wsdl"  # downloaded and stored local

        session = Session()

        # Authenticate  with gateway
        session.auth = HTTPBasicAuth(user, password)
        client = Client(wsdl, transport=Transport(session=session))

        # Build Authentification header for API-Endpoint using zeep xsd
        header = xsd.Element(
            '{http://test.python-zeep.org}Authentification',
            xsd.ComplexType(
                [
                    xsd.Element('{http://test.python-zeep.org}user', xsd.String()),
                    xsd.Element('{http://test.python-zeep.org}signature', xsd.String()),
                ]
            ),
        )
        header_value = header(user=USER, signature=PASSWORD)

        product = "V01PAK"  # V01PAK: DHL PAKET; V53WPAK: DHL PAKET International; V54EPAK: DHL Europaket; V62WP: Warenpost; V66WPI: Warenpost International
        account_number = "63134046530101"
        shipmentDate = date.today().strftime(
            "%Y-%m-%d"
        )  # Iso format required: yyyy-mm-dd.

        dict = {
            'Version': {'majorRelease': '3', 'minorRelease': '4'},
            'ShipmentOrder': {
                'sequenceNumber': "",
                'Shipment': {
                    'ShipmentDetails': {
                        'product': product,
                        'accountNumber': account_number,
                        'customerReference': customer_reference,
                        'shipmentDate': shipmentDate,
                        'ShipmentItem': {
                            'weightInKG': weight_in_kg,
                        },
                    },
                    'Shipper': {
                        'Name': {'name1': 'HS Sales GmbH', 'name2': 'Toredo Shop'},
                        'Address': {
                            'streetName': 'Drygalski-Allee 33B',
                            'zip': '81477',
                            'city': 'München',
                            'Origin': {'countryISOCode': 'DE'},
                        },
                    },
                    'Receiver': {
                        'name1': name_1,
                        'Address': {
                            'name2': name_2,
                            'name3': name_3,
                            'streetName': street_with_number,
                            'zip': zip_code,
                            'city': city,
                            'Origin': {'countryISOCode': 'DE'},
                        },
                        'Communication': {
                            'contactPerson': name_1,
                            'email': customer_email,
                        },
                    },
                },
            },
            'labelFormat': "910-300-600",
        }
        response = client.service.createShipmentOrder(
            _soapheaders=[header_value], **dict
        )
        if response["Status"]["statusText"] == "ok":
            logger.info("Successful: Shipping label could be created successfully.")
            shipment_number = response["CreationState"][0]["shipmentNumber"]
            logger.info(f"Tracking number: {shipment_number}")
            label_url = response["CreationState"][0]["LabelData"]["labelUrl"]
            return [shipment_number, label_url]
        elif response["Status"]["statusText"] == "Weak validation error occured.":
            logger.info("Successful: Shipping label could be created successfully.")
            error_message = response["CreationState"][0]["LabelData"]["Status"][
                "warningMessage"
            ][0]
            logger.error("Weak validation error occurded")
            logger.error(error_message)
        else:
            logger.error(
                "Error: Shipping label could not be generated. Check Response for details."
            )
            return response
