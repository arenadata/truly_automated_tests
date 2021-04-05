"""Endpoint data classes definition"""

from abc import ABC
from typing import List

from .types import (
    Field,
    PositiveInt,
    String,
    Text,
    ForeignKey,
)


class BaseClass(ABC):
    """Base data class"""

    implicitly_depends_on: List["BaseClass"] = []


class ClusterFields(BaseClass):
    """
    Data type class for /cluster
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)
    description = Field(name="description", f_type=Text(max_length=2000))


class FileSystemFields(BaseClass):
    """
    Data type class for /file-system
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)
    description = Field(name="description", f_type=Text(max_length=2000))


class ConnectionFields(BaseClass):
    """
    Data type class for /connection
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)
    cluster = Field(
        name="cluster_id", f_type=ForeignKey(fk_link=ClusterFields), required=True
    )
    filesystem = Field(
        name="filesystem_id", f_type=ForeignKey(fk_link=FileSystemFields), required=True
    )


class BackupFields(BaseClass):
    """
    Data type class for /backup
    """

    implicitly_depends_on = [ConnectionFields]

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)
    cluster = Field(
        name="cluster_id", f_type=ForeignKey(fk_link=ClusterFields), required=True
    )
    filesystem = Field(
        name="filesystem_id", f_type=ForeignKey(fk_link=FileSystemFields), required=True
    )
