"""Fill DB methods"""

import random
from collections import defaultdict

import allure

from tests.test_data.getters import get_endpoint_data, get_object_data
from tests.utils.api_objects import Request, ExpectedResponse, APPApi
from tests.utils.endpoints import Endpoints
from tests.utils.methods import Methods
from tests.utils.types import (
    get_fields,
    Field,
    is_fk_field,
    ForeignKey,
    get_field_name_by_fk_dataclass,
)


class DbFiller:
    """Utils to prepare data in DB before test"""

    __slots__ = ("app", "_available_fkeys", "_used_fkeys")

    def __init__(self, app: APPApi):
        self.app = app
        self._available_fkeys = defaultdict(set)
        self._used_fkeys = {}

    @allure.step("Generate valid request data")
    def generate_valid_request_data(self, endpoint: Endpoints, method: Methods) -> dict:
        """
        Return valid request body and url params for endpoint and method combination
        """
        # POST
        if method == Methods.POST:
            return {
                "data": self._get_or_create_data_for_endpoint(
                    endpoint=endpoint,
                    force=True,
                    prepare_data_only=True,
                )[0],
                "url_params": {},
            }
        # LIST
        if method == Methods.LIST:
            self._get_or_create_multiple_data_for_endpoint(endpoint=endpoint, count=3)
            return {"data": None, "url_params": {}}

        full_item = get_object_data(
            app=self.app,
            endpoint=endpoint,
            object_id=self._get_or_create_data_for_endpoint(endpoint=endpoint)[0]["id"],
        )
        # GET
        if method == Methods.GET:
            return {"data": None, "url_params": {}, "object_id": full_item["id"]}
        raise ValueError(f"No such method {method}")

    def _get_or_create_data_for_endpoint(
        self, endpoint: Endpoints, force=False, prepare_data_only=False
    ):
        """
        Get data for endpoint with data preparation
        """
        if force and not prepare_data_only and Methods.POST not in endpoint.methods:
            if current_ep_data := get_endpoint_data(app=self.app, endpoint=endpoint):
                return current_ep_data
            raise ValueError(
                f"Force data creation is not available for {endpoint.path}"
                "and there is no any existing data"
            )

        if not force:
            # try to fetch data from current endpoint
            if current_ep_data := get_endpoint_data(app=self.app, endpoint=endpoint):
                return current_ep_data

        data = self._prepare_data_for_object_creation(endpoint=endpoint, force=force)

        for data_class in endpoint.data_class.implicitly_depends_on:
            self._get_or_create_data_for_endpoint(
                endpoint=Endpoints.get_by_data_class(data_class), force=force
            )

        if not prepare_data_only:
            response = self.app.exec_request(
                request=Request(endpoint=endpoint, method=Methods.POST, data=data),
                expected_response=ExpectedResponse(
                    status_code=Methods.POST.value.default_success_code
                ),
            )
            return [response.json()]
        return [data]

    def _prepare_data_for_object_creation(self, endpoint: Endpoints, force=False):
        data = {}
        for field in get_fields(
            data_class=endpoint.data_class,
            predicate=lambda x: x.name != "id" and is_fk_field(x),
        ):
            fk_data = get_endpoint_data(
                app=self.app,
                endpoint=Endpoints.get_by_data_class(field.f_type.fk_link),
            )
            if not fk_data or force:
                fk_data = self._get_or_create_data_for_endpoint(
                    endpoint=Endpoints.get_by_data_class(field.f_type.fk_link),
                    force=force,
                )
            data[field.name] = self._choose_fk_field_value(field=field, fk_data=fk_data)
        for field in get_fields(
            data_class=endpoint.data_class,
            predicate=lambda x: x.name != "id" and not is_fk_field(x),
        ):
            data[field.name] = field.f_type.generate()

        return data

    def _get_or_create_multiple_data_for_endpoint(
        self, endpoint: Endpoints, count: int
    ):
        """
        Method for multiple data creation for given endpoint.
        For each object new object chain will be created.
        If endpoint does not allow data creation of any kind (POST, indirect creation, etc.)
        method will proceed without data creation or errors
        IMPORTANT: Class context _available_fkeys and _used_fkeys
                   will be relevant only for the last object in set
        """
        current_ep_data = get_endpoint_data(app=self.app, endpoint=endpoint)
        if len(current_ep_data) < count:
            for _ in range(count - len(current_ep_data)):
                # clean up context before generating new element
                self._available_fkeys = defaultdict(set)
                self._used_fkeys = {}
                self._get_or_create_data_for_endpoint(
                    endpoint=endpoint,
                    force=True,
                    prepare_data_only=False,
                )
                if len(get_endpoint_data(app=self.app, endpoint=endpoint)) > count:
                    break

    def _choose_fk_field_value(self, field: Field, fk_data: list):
        """Choose a random fk value for the specified field"""
        if isinstance(field.f_type, ForeignKey):
            fk_class_name = field.f_type.fk_link.__name__
            if fk_class_name in self._available_fkeys:
                new_fk = False
                fk_vals = self._available_fkeys[fk_class_name]
            else:
                new_fk = True
                fk_vals = {el["id"] for el in fk_data}

            key = random.choice(list(fk_vals))
            result = key
            self._used_fkeys[fk_class_name] = key
            self._available_fkeys[fk_class_name].add(key)
            if new_fk:
                self._add_child_fk_values_to_available_fkeys(
                    fk_ids=[key], fk_data_class=field.f_type.fk_link
                )
            return result
        # if field is not FK
        raise ValueError("Argument field is not FKey!")

    def _add_child_fk_values_to_available_fkeys(self, fk_ids: list, fk_data_class):
        """Add information about child FK values to metadata for further consistency"""
        for child_fk_field in get_fields(
            data_class=fk_data_class, predicate=is_fk_field
        ):
            fk_field_name = get_field_name_by_fk_dataclass(
                data_class=fk_data_class, fk_data_class=child_fk_field.f_type.fk_link
            )
            for fk_id in fk_ids:
                fk_data = get_object_data(
                    app=self.app,
                    endpoint=Endpoints.get_by_data_class(fk_data_class),
                    object_id=fk_id,
                )
                self._available_fkeys[child_fk_field.f_type.fk_link.__name__].add(
                    fk_data[fk_field_name]
                )
