"""Methods for get endpoints data"""

from tests.utils.endpoints import Endpoints
from tests.utils.methods import Methods
from tests.utils.api_objects import Request, ExpectedResponse, APPApi


def get_endpoint_data(app: APPApi, endpoint: Endpoints) -> list:
    """
    Fetch endpoint data with LIST method
    Data of LIST method excludes links to related objects and huge fields
    """
    if Methods.LIST not in endpoint.methods:
        raise AttributeError(
            f"Method {Methods.LIST.name} is not available for endpoint {endpoint.path}"
        )
    res = app.exec_request(
        request=Request(endpoint=endpoint, method=Methods.LIST),
        expected_response=ExpectedResponse(
            status_code=Methods.LIST.value.default_success_code
        ),
    )
    return res.json()


def get_object_data(app: APPApi, endpoint: Endpoints, object_id: int) -> dict:
    """
    Fetch full object data includes huge field and links to related objects
    """
    res = app.exec_request(
        request=Request(endpoint=endpoint, method=Methods.GET, object_id=object_id),
        expected_response=ExpectedResponse(
            status_code=Methods.GET.value.default_success_code
        ),
    )
    return res.json()
