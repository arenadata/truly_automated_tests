"""Possible Methods specification"""
from collections.abc import Callable
from enum import Enum
from http import HTTPStatus

import attr
import requests


@attr.dataclass
class Method:
    """Describe possible methods and how they are used in APP api"""

    function: Callable
    url_template: str
    default_success_code: int = HTTPStatus.OK


class Methods(Enum):
    """All possible methods"""

    def __init__(self, method: Method):
        self.method = method

    @property
    def function(self):
        """Getter for Method.function attribute"""
        return self.method.function

    @property
    def url_template(self):
        """Getter for Method.url_template attribute"""
        return self.method.url_template

    @property
    def default_success_code(self):
        """Getter for Method.default_success_code attribute"""
        return self.method.default_success_code

    GET = Method(function=requests.get, url_template="/{name}/{id}/")
    LIST = Method(function=requests.get, url_template="/{name}/")
    POST = Method(
        function=requests.post,
        url_template="/{name}/",
        default_success_code=HTTPStatus.CREATED,
    )
