"""Module contains api objects for executing and checking requests"""
from urllib.parse import urlencode

import allure
import attr

from .endpoints import Endpoints
from .methods import Methods
from .tools import attach_request_log
from ..steps.asserts import status_code_should_be, body_should_be


@attr.dataclass
class Request:
    """Request for a specific endpoint"""

    method: Methods
    endpoint: Endpoints
    object_id: int = None
    url_params: dict = {}
    headers: dict = {}
    data: dict = {}


@attr.dataclass
class ExpectedResponse:
    """Response to be expected. Checking the status code and body if present"""

    status_code: int
    body: dict = None


class APPApi:
    """APP api wrapper"""

    __slots__ = ("_url",)

    _api_prefix = ""

    def __init__(self, url="http://localhost:8000"):
        self._url = url

    @property
    def _base_url(self):
        return f"{self._url}{self._api_prefix}"

    def exec_request(self, request: Request, expected_response: ExpectedResponse):
        """
        Execute HTTP request based on "request" argument.
        Assert response params amd values based on "expected_response" argument.
        """
        url = self.get_url_for_endpoint(
            endpoint=request.endpoint,
            method=request.method,
            object_id=request.object_id,
        )
        url_params = request.url_params.copy()

        step_name = f"Send {request.method.name} {url.replace(self._base_url, '')}"
        if url_params:
            step_name += f"?{urlencode(url_params)}"
        with allure.step(step_name):
            response = request.method.function(
                url=url,
                params=url_params,
                json=request.data,
                headers=request.headers,
            )

            attach_request_log(response)

            status_code_should_be(
                response=response, status_code=expected_response.status_code
            )

            if expected_response.body is not None:
                body_should_be(response=response, expected_body=expected_response.body)

        return response

    def get_url_for_endpoint(
        self, endpoint: Endpoints, method: Methods, object_id: int
    ):
        """
        Return direct link for endpoint object
        """
        if "{id}" in method.url_template:
            if object_id is None:
                raise ValueError(
                    "Request template requires 'id', but 'request.object_id' is None"
                )
            url = method.url_template.format(name=endpoint.path, id=object_id)
        else:
            url = method.url_template.format(name=endpoint.path)

        return f"{self._base_url}{url}"
