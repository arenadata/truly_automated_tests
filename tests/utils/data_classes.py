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


class ClusterTypeFields(BaseClass):
    """
    Data type class for /cluster-type
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)


class ClusterFields(BaseClass):
    """
    Data type class for /cluster
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)
    description = Field(name="description", f_type=Text(max_length=2000), nullable=True)
    cluster_type_id = Field(
        name="cluster_type_id",
        f_type=ForeignKey(fk_link=ClusterTypeFields),
        required=True,
    )


class FileSystemTypeFields(BaseClass):
    """
    Data type class for /fs-type
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)


class FileSystemFields(BaseClass):
    """
    Data type class for /file-system
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)
    description = Field(name="description", f_type=Text(max_length=2000), nullable=True)
    fs_type_id = Field(
        name="fs_type_id",
        f_type=ForeignKey(fk_link=FileSystemTypeFields),
        required=True,
    )


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


class RestoreFields(BaseClass):
    """
    Data type class for /restore
    """

    id = Field(name="id", f_type=PositiveInt())
    name = Field(name="name", f_type=String(max_length=255), required=True)
    timeout = Field(name="timeout", f_type=PositiveInt(), required=True, nullable=True)
    backup_id = Field(
        name="backup_id", f_type=ForeignKey(fk_link=BackupFields), required=True
    )
