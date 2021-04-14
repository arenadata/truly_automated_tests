"""Methods for generate test data"""

from collections import ChainMap
from http import HTTPStatus
from typing import NamedTuple, List

import attr
import pytest
from _pytest.mark.structures import ParameterSet

from tests.utils.api_objects import Request, ExpectedResponse
from tests.utils.endpoints import Endpoints
from tests.utils.methods import Methods
from tests.utils.tools import fill_lists_by_longest
from tests.utils.types import (
    get_fields,
    BaseType,
    PreparedFieldValue,
)


class MaxRetriesError(BaseException):
    """Raise when limit of retries exceeded"""


@attr.dataclass(repr=False)
class TestData:
    """Pair of request and expected response for api tests"""

    request: Request
    response: ExpectedResponse
    description: str = None

    def __repr__(self):
        return (
            f"{self.request.method.name} {self.request.endpoint.path} "
            f"and expect {self.response.status_code} status code. at {hex(id(self))}"
        )


class TestDataWithPreparedBody(NamedTuple):
    """
    Class for separating request body and data needed to send and assert it
    """

    test_data: TestData
    test_body: dict


def _fill_pytest_param(
    value: List[TestDataWithPreparedBody] or List[TestData],
    endpoint: Endpoints,
    method: Methods,
    positive=True,
    addition=None,
) -> ParameterSet:
    """
    Create pytest.param for each test data set
    """
    marks = []
    if positive:
        marks.append(pytest.mark.positive)
        positive_str = "positive"
    else:
        marks.append(pytest.mark.negative)
        positive_str = "negative"
    param_id = f"{endpoint.path}_{method.name}_{positive_str}"
    if addition:
        param_id += f"_{addition}"
    return pytest.param(value, marks=marks, id=param_id)


def get_data_for_methods_check():
    """
    Get test data for allowed methods test
    """
    test_data = []
    for endpoint in Endpoints:
        for method in Methods:
            request = Request(
                method=method,
                endpoint=endpoint,
            )
            if method in endpoint.methods:
                response = ExpectedResponse(status_code=method.default_success_code)
            else:
                response = ExpectedResponse(status_code=HTTPStatus.METHOD_NOT_ALLOWED)

            test_data.append(
                _fill_pytest_param(
                    [TestData(request=request, response=response)],
                    endpoint=endpoint,
                    method=method,
                    positive=response.status_code != HTTPStatus.METHOD_NOT_ALLOWED,
                )
            )
    return test_data


def get_positive_data_for_post_body_check():
    """
    Generates positive datasets for POST method
    """
    test_sets = []
    for endpoint in Endpoints:
        if Methods.POST in endpoint.methods:
            test_sets.append(
                (
                    endpoint,
                    [
                        _get_special_body_datasets(
                            endpoint,
                            desc="All fields with special valid values",
                            method=Methods.POST,
                            positive_case=True,
                        ),
                        _get_datasets(
                            endpoint,
                            desc="All fields with valid values",
                            field_conditions=lambda x: True,
                            value_properties={"generated_value": True},
                        ),
                        _get_datasets(
                            endpoint,
                            desc="Only Required=True with valid values",
                            field_conditions=lambda x: not x.required,
                            value_properties={"drop_key": True},
                        ),
                        _get_datasets(
                            endpoint,
                            desc="Null values for Nullable=True fields",
                            field_conditions=lambda x: x.nullable,
                            value_properties={"value": None},
                        ),
                    ],
                )
            )
    return get_data_for_body_check(Methods.POST, test_sets, positive=True)


def get_negative_data_for_post_body_check():
    """
    Generates negative datasets for POST method
    """
    test_sets = []
    for endpoint in Endpoints:
        if Methods.POST in endpoint.methods:
            test_sets.append(
                (
                    endpoint,
                    [
                        _get_datasets(
                            endpoint,
                            desc="Drop fields with Required=True",
                            field_conditions=lambda x: x.required,
                            value_properties={
                                "error_message": BaseType.error_message_required,
                                "drop_key": True,
                            },
                        ),
                        _get_datasets(
                            endpoint,
                            desc="Null values for Nullable=False fields",
                            field_conditions=lambda x: not x.nullable and x.name != "id",
                            value_properties={
                                "error_message": BaseType.error_message_required,
                                "value": None,
                            },
                        ),
                        _get_special_body_datasets(
                            endpoint,
                            desc="Invalid field types and values",
                            method=Methods.POST,
                            positive_case=False,
                        ),
                    ],
                )
            )
    return get_data_for_body_check(Methods.POST, test_sets, positive=False)


def get_data_for_body_check(
    method: Methods, endpoints_with_test_sets: List[tuple], positive: bool
):
    """
    Collect test sets for body testing
    Each test set is set of data params where values are PreparedFieldValue instances
    :param method:
    :param endpoints_with_test_sets:
    :param positive: collect positive or negative datasets.
        Negative datasets additionally checks of response body for correct errors.
        In positive cases it doesn't make sense
    """
    test_data = []
    for endpoint, test_groups in endpoints_with_test_sets:
        for test_group, group_name in test_groups:
            values: List[TestDataWithPreparedBody] = []
            for test_set in test_group:
                status_code = (
                    method.default_success_code
                    if positive
                    else HTTPStatus.UNPROCESSABLE_ENTITY
                )
                # It makes no sense to check with all fields if test_set contains only one field
                if positive or len(test_set) > 1:
                    values.append(
                        _prepare_test_data_with_all_fields(
                            endpoint, method, status_code, test_set
                        )
                    )

                if not positive:
                    values.extend(
                        _prepare_test_data_with_one_by_one_fields(
                            endpoint, method, status_code, test_set
                        )
                    )
            if positive:
                for value in values:
                    test_data.append(
                        _fill_pytest_param(
                            [value],
                            endpoint=endpoint,
                            method=method,
                            positive=positive,
                            addition=group_name,
                        )
                    )
            elif values:
                test_data.append(
                    _fill_pytest_param(
                        values,
                        endpoint=endpoint,
                        method=method,
                        positive=positive,
                        addition=group_name,
                    )
                )
    return test_data


def _prepare_test_data_with_all_fields(
    endpoint: Endpoints, method: Methods, status_code: int, test_set: dict
) -> TestDataWithPreparedBody:
    request = Request(method=method, endpoint=endpoint)
    response = ExpectedResponse(status_code=status_code)

    return TestDataWithPreparedBody(
        test_data=TestData(
            request=request,
            response=response,
            description=f"All fields without body checks - {_step_description(test_set)}",
        ),
        test_body=test_set,
    )


def _step_description(test_set: dict):
    first_item = next(iter(test_set.values()))
    if first_item.generated_value is True:
        return "Generated value: " + ", ".join(test_set.keys())
    if first_item.drop_key is True:
        return "Missing in request: " + ", ".join(test_set.keys())
    return "Special values: " + ", ".join(test_set.keys())


def _prepare_test_data_with_one_by_one_fields(
    endpoint: Endpoints, method: Methods, status_code: int, test_set: dict
) -> List[TestDataWithPreparedBody]:
    test_data_list = []
    for param_name, param_value in test_set.items():
        request_data = {}
        if not param_value.error_messages:
            continue
        else:
            param_value.error_messages = list(
                map(
                    lambda x: x.format(name=param_name.replace("_", " ")),
                    param_value.error_messages,
                )
            )
        body = {param_name: param_value.get_error_data()}
        request_data[param_name] = param_value
        request = Request(method=method, endpoint=endpoint)
        response = ExpectedResponse(status_code=status_code, body=body)
        test_data_list.append(
            TestDataWithPreparedBody(
                test_data=TestData(
                    request=request,
                    response=response,
                    description=f"{param_name}: {param_value.error_messages}",
                ),
                test_body=request_data,
            )
        )
    return test_data_list


def _get_datasets(
    endpoint: Endpoints,
    desc,
    field_conditions,
    value_properties: dict,
) -> (list, str):
    """Generic dataset creator for editing request data later"""
    dataset = {}
    if "generated_value" in value_properties and "value" in value_properties:
        raise ValueError("'generated_value', 'value' properties are not compatible")
    for field in get_fields(endpoint.data_class):
        if field_conditions(field):
            dataset[field.name] = PreparedFieldValue(
                value=value_properties.get("value", None),
                generated_value=value_properties.get("generated_value", False),
                error_messages=[value_properties.get("error_message", None)],
                drop_key=value_properties.get("drop_key", False),
                f_type=field.f_type,
            )
    return [dataset] if dataset else [], desc


def _get_special_body_datasets(
    endpoint: Endpoints, desc, method: Methods, positive_case: bool
) -> (list, str):
    """Get datasets with based on special values for fields"""
    datasets = []
    special_values = {}
    for field in get_fields(endpoint.data_class, predicate=lambda x: x.name != "id"):
        if method == Methods.POST:
            if positive_case:
                special_values[field.name] = field.f_type.get_positive_values()
            else:
                negative_values = get_fields(
                    endpoint.data_class,
                    predicate=lambda x: x.f_type.get_negative_values(),
                )
                if negative_values:
                    special_values[field.name] = field.f_type.get_negative_values()
    if special_values:
        fill_lists_by_longest(special_values.values())
        for name, values in special_values.copy().items():
            special_values[name] = [{name: value} for value in values]
        for values in zip(*special_values.values()):
            datasets.append(dict(ChainMap(*values)))
    return datasets, desc
