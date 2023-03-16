import json
import requests
import logging

logger = logging.getLogger(__name__)


def perform_request(url, method='get', headers={}, payload={}):
    # Check last request and sleep to respect rate limit of plenty market
    logger.info(
        f"Making API call. \n method: {method}\n url: {url} \n payload: {payload} \n"
    )

    http_params = {"url": url, "headers": headers}
    if method == "get":
        http_params["timeout"] = 60
    response_data = None
    if method in ['post', 'put', 'patch']:
        http_params['json'] = payload
    elif method == 'get':
        http_params['params'] = payload
    try:
        response = getattr(requests, method)(**http_params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.error(err)
    else:
        try:
            response_data = response.json()
        except json.decoder.JSONDecodeError:
            response_data = {}
    return response_data
