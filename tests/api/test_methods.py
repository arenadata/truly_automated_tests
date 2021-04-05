"""APP API methods checks"""

from typing import List

import pytest
import allure

from tests.test_data.generators import TestData, get_data_for_methods_check
from tests.test_data.db_filler import DbFiller

pytestmark = [allure.suite("Allowed methods tests")]


@pytest.fixture(params=get_data_for_methods_check())
def prepare_data(request, app_fs):
    """
    Generate request body here since it depends on actual APP instance
    and can't be determined when generating
    """
    test_data_list: List[TestData] = request.param
    for test_data in test_data_list:
        request_data = DbFiller(app=app_fs).generate_valid_request_data(
            endpoint=test_data.request.endpoint, method=test_data.request.method
        )

        test_data.request.data = request_data["data"]
        test_data.request.object_id = request_data.get("object_id")

    return app_fs, test_data_list


def test_methods(prepare_data):
    """
    Test allowed methods
    Generate request and response pairs depending on allowed and not allowed methods
    for all api endpoints
    """
    app, test_data_list = prepare_data
    for test_data in test_data_list:
        app.exec_request(
            request=test_data.request, expected_response=test_data.response
        )
