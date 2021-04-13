"""Module contains all field types and special values"""
from abc import ABC, abstractmethod
from collections.abc import Callable
from random import randint
from typing import ClassVar, List, Type, Union
from multipledispatch import dispatch

import attr

from tests.utils.tools import random_string

# There is no circular import, because the import of the module is not yet completed at the moment,
# and this allows you to resolve the conflict.
from tests.utils import data_classes


@attr.dataclass
class PreparedFieldValue:
    """
    PreparedFieldValue is an object for body testing. Used for both positive and negative cases.

    An important object for generating test data, since it contains a description of what needs
    to be done with field value and what we expect as a result of sending it in body.


    value: Value to be set for field
    error_messages: Expected error message
    drop_key: If True, key in body request will be dropped
    f_type: Field type. Affects value generation

    generated_value: if True, value will be generated according to field type rules
                     when PreparedFieldValue value is requested via 'return_value' method
    """

    value: object = None
    generated_value: bool = False
    error_messages: Union[list, dict] = None
    f_type: "BaseType" = None

    drop_key: bool = False

    @dispatch(object)
    def return_value(self, pre_generated_value):
        """
        Return value in final view for fields in POST body tests
        :param pre_generated_value: Pre-generated valid value for set POSTable field value
        """
        if self.generated_value:
            if pre_generated_value is not None:
                return pre_generated_value
            return self.f_type.generate()

        return self.value

    @dispatch(object, object, object)
    def return_value(
        self, dbfiller, current_field_value, changed_field_value
    ):  # noqa: F811
        """
        Return value in final view for fields in PUT, PATCH body tests
        :param dbfiller: Object of class DbFiller. Required to create non-changeable fk fields
        :param current_field_value: Value with which creatable object was created
        :param changed_field_value: Valid value to which we can change original if possible
        """
        if self.generated_value:
            if changed_field_value is not None:
                return changed_field_value
            if isinstance(self.f_type, ForeignKey):
                return dbfiller.generate_new_value_for_unchangeable_fk_field(
                    f_type=self.f_type, current_field_value=current_field_value
                )
            return self.f_type.generate()

        return self.value

    def get_error_data(self):
        """Error data is a list by default but fk fields should be nested"""
        return self.error_messages


@attr.dataclass
class BaseType(ABC):
    """
    Base type of field
    Contains common methods and attributes for each types
    """

    _sp_vals_positive: list = None
    _sp_vals_negative: List[Union[object, Type["BaseType"], PreparedFieldValue]] = None

    error_message_required: ClassVar[str] = "The {name} field is required."
    error_message_invalid_data: ClassVar[str] = ""

    @abstractmethod
    def generate(self, **kwargs):
        """Should generate and return one value for the current child type"""

    def get_positive_values(self):
        """Positive values is:
        - boundary values
        - generated values
        - all enum values (if present)
        """
        if self._sp_vals_positive:
            return [
                PreparedFieldValue(value, f_type=self)
                for value in self._sp_vals_positive
            ]
        return [PreparedFieldValue(generated_value=True, f_type=self)]

    def get_negative_values(self):
        """Negative values is:
        - out of boundary values
        - invalid choice of enum values
        - invalid FK values
        - invalid type values (generated)
        """
        negative_values = (
            self._sp_vals_negative.copy() if self._sp_vals_negative else []
        )

        final_negative_values = []
        for negative_value in negative_values:
            if isinstance(negative_value, PreparedFieldValue):
                final_negative_values.append(negative_value)
            else:
                final_negative_values.append(
                    PreparedFieldValue(
                        negative_value,
                        f_type=self,
                        error_messages=[self.error_message_invalid_data],
                    )
                )
        return final_negative_values


class PositiveInt(BaseType):
    """Positive int field type"""

    _min_int32 = 0
    _max_int32 = (2 ** 31) - 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._sp_vals_positive = [self._min_int32, self._max_int32]
        self._sp_vals_negative = [
            3.14,
            random_string(),
            PreparedFieldValue(
                self._min_int32 - 1,
                f_type=self,
                error_messages=["The {name} must be at least 0."],
            ),
            PreparedFieldValue(
                self._max_int32 + 1,
                f_type=self,
                error_messages=[
                    f"The {{name}} may not be greater than {self._max_int32}."
                ],
            ),
        ]
        self.error_message_invalid_data = "The {name} must be an integer."

    def generate(self, **kwargs):
        return randint(self._min_int32, self._max_int32)


class String(BaseType):
    """String field type"""

    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self._sp_vals_positive = ["s", r"!@#$%^&*\/{}[]", random_string(max_length)]

        self._sp_vals_negative = [
            PreparedFieldValue(
                value=random_string(max_length + 1),
                f_type=self,
                error_messages=[
                    f"The {{name}} may not be greater than {self.max_length} characters."
                ],
            ),
        ]
        self.error_message_invalid_data = "Not a valid string."

    def generate(self, **kwargs):
        return random_string(randint(1, self.max_length))


class Text(BaseType):
    """Text field type"""

    is_huge = True

    def __init__(self, max_length=2000, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self._sp_vals_negative = [
            PreparedFieldValue(
                value=random_string(max_length + 1),
                f_type=self,
                error_messages=[
                    f"The {{name}} may not be greater than {self.max_length} characters."
                ],
            ),
        ]
        self.error_message_invalid_data = ""

    def generate(self, **kwargs):
        return random_string(randint(64, 200))


class ForeignKey(BaseType):
    """Foreign key field type"""

    fk_link: Type["data_classes.BaseClass"] = None

    def __init__(self, fk_link: Type["data_classes.BaseClass"], **kwargs):
        self.fk_link = fk_link
        super().__init__(**kwargs)
        self._sp_vals_negative = [
            PreparedFieldValue(
                100,
                f_type=self,
                error_messages=["The selected {name} is invalid."],
            ),
            PreparedFieldValue(
                2 ** 31,
                f_type=self,
                error_messages=["The selected {name} is invalid."],
            ),
        ]

    def generate(self, **kwargs):
        pass


@attr.dataclass
class Field:
    """Field class based on APP spec"""

    name: str
    f_type: BaseType = None
    required: bool = False


def get_fields(data_class: type, predicate: Callable = None) -> List[Field]:
    """Get fields by data class and filtered by predicate"""

    def dummy_predicate(_):
        return True

    if predicate is None:
        predicate = dummy_predicate
    return [
        value
        for (key, value) in data_class.__dict__.items()
        if isinstance(value, Field) and predicate(value)
    ]


def is_fk_field(field: Field) -> bool:
    """Predicate for fk fields selection"""
    return isinstance(field.f_type, ForeignKey)


def get_field_name_by_fk_dataclass(data_class: type, fk_data_class: type) -> str:
    """Get field name in data_class that is FK to another data_class"""
    for field in get_fields(data_class, predicate=is_fk_field):
        if field.f_type.fk_link == fk_data_class:
            return field.name
    raise AttributeError(f"No FK field pointing to {fk_data_class} found!")
