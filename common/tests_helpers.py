import datetime

from django.test.client import Client


def perform_api_call(url, method, data, token, is_json=True):
    headers = {}
    if token:
        headers["HTTP_AUTHORIZATION"] = f"Token {token}"

    api_method = getattr(Client(), method)

    if is_json:
        return api_method(
            url, data=data, format="json", content_type='application/json', **headers
        )
    return api_method(url, data=data, **headers)


def assert_dict_with_object(dict_data: dict, obj: object) -> None:
    for key in dict_data:
        val = dict_data[key]
        obj_val = getattr(obj, key)

        if type(val) == type(obj_val):
            assert val == obj_val

        elif isinstance(obj_val, datetime.datetime):
            assert obj_val == datetime.datetime.strptime(val, "%Y-%m-%d").date()
