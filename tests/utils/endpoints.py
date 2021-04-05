"""APP Endpoints classes and methods"""

from enum import Enum
from typing import List, Type, Optional

import attr

from .data_classes import (
    ClusterFields,
    FileSystemFields,
    BackupFields,
    ConnectionFields,
    BaseClass,
)
from .methods import Methods
from .types import get_fields


@attr.dataclass
class Endpoint:
    """
    Endpoint class
    :attribute path: endpoint name
    :attribute methods: list of allowed methods for endpoint
    :attribute data_class: endpoint fields specification
    """

    path: str
    methods: List[Methods]
    data_class: Type[BaseClass]


class Endpoints(Enum):
    """All current endpoints"""

    def __init__(self, endpoint: Endpoint):
        self.endpoint = endpoint

    @property
    def path(self):
        """Getter for Endpoint.path attribute"""
        return self.endpoint.path

    @property
    def methods(self):
        """Getter for Endpoint.methods attribute"""
        return self.endpoint.methods

    @property
    def data_class(self):
        """Getter for Endpoint.data_class attribute"""
        return self.endpoint.data_class

    @classmethod
    def get_by_data_class(cls, data_class: Type[BaseClass]) -> Optional["Endpoints"]:
        """Get endpoint instance by data class"""
        for endpoint in cls:
            if endpoint.data_class == data_class:
                return endpoint
        return None

    def get_child_endpoint_by_fk_name(self, field_name: str) -> Optional["Endpoints"]:
        """Get endpoint instance by data class"""
        for field in get_fields(self.value.data_class):
            if field.name == field_name:
                try:
                    return self.get_by_data_class(field.f_type.fk_link)
                except AttributeError:
                    raise ValueError(
                        f"Field {field_name} must be a Foreign Key field type"
                    ) from AttributeError
        return None

    Cluster = Endpoint(
        path="cluster",
        methods=[
            Methods.GET,
            Methods.LIST,
            Methods.POST,
        ],
        data_class=ClusterFields,
    )

    FileSystem = Endpoint(
        path="file-system",
        methods=[
            Methods.GET,
            Methods.LIST,
            Methods.POST,
        ],
        data_class=FileSystemFields,
    )

    Connection = Endpoint(
        path="connection",
        methods=[
            Methods.GET,
            Methods.LIST,
            Methods.POST,
        ],
        data_class=ConnectionFields,
    )

    Backup = Endpoint(
        path="backup",
        methods=[
            Methods.GET,
            Methods.LIST,
            Methods.POST,
        ],
        data_class=BackupFields,
    )
