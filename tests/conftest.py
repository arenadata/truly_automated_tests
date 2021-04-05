"""APP fixtures"""

import time

import allure
import docker
import pytest
import requests

from docker.errors import NotFound
from retry.api import retry_call

from .utils.docker import (
    APP,
    DockerWrapper,
    get_initialized_app_image,
    gather_app_data_from_container,
)
from .utils.api_objects import APPApi
from .utils.tools import split_tag


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    There is no default info about test stages execution available in pytest
    This hook is meant to store such info in metadata
    """
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"

    setattr(item, "rep_" + rep.when, rep)


def pytest_addoption(parser):
    """
    Additional options for APP testing
    """
    # Do not stop APP container after test execution
    # It is really useful for debugging
    parser.addoption("--dontstop", action="store_true", default=False)

    parser.addoption(
        "--app-image",
        action="store",
        default=None,
        help="Ex: app:latest",
    )


@pytest.fixture(scope="session")
def cmd_opts(request):
    """Returns pytest request options object"""
    return request.config.option


def _image(request, cmd_opts):
    """This fixture creates APP container, waits until
    database becomes initialised and store that as images
    with random tag and name local/app

    That can be useful to use that fixture to make APP
    container startup time shorter.

    Fixture returns list:
    repo, tag
    """

    dc = docker.from_env()
    params = dict()

    if cmd_opts.app_image:
        params["app_repo"], params["app_tag"] = split_tag(
            image_name=cmd_opts.app_image
        )

    init_image = get_initialized_app_image(dc=dc, **params)

    if not cmd_opts.dontstop:

        def fin():
            image_name = "{}:{}".format(*init_image.values())
            for container in dc.containers.list(filters=dict(ancestor=image_name)):
                try:
                    container.wait(condition="removed", timeout=30)
                except ConnectionError:
                    # https://github.com/docker/docker-py/issues/1966 workaround
                    pass
            dc.images.remove(image_name, force=True)
            containers = dc.containers.list(filters=dict(ancestor=image_name))
            if len(containers) > 0:
                raise RuntimeWarning(f"There are containers left! {containers}")

        request.addfinalizer(fin)

    return init_image["repo"], init_image["tag"]


def _app(image, request) -> APP:
    repo, tag = image
    dw = DockerWrapper()
    app = dw.run_app(image=repo, tag=tag)

    def fin():
        if not request.config.option.dontstop:
            gather = True
            try:
                if not request.node.rep_call.failed:
                    gather = False
            except AttributeError:
                # There is no rep_call attribute. Presumably test setup failed,
                # or fixture scope is not function. Will collect /adcm/data anyway
                pass
            if gather:
                with allure.step(
                    f"Gather /var/www/html/storage/app/ from APP container: {app.container.id}"
                ):
                    file_name = f"{request.node.name}_{time.time()}"
                    try:
                        with gather_app_data_from_container(app) as data:
                            allure.attach(
                                data, name="{}.tgz".format(file_name), extension="tgz"
                            )
                    except NotFound:
                        pass

            try:
                retry_call(
                    app.container.kill,
                    exceptions=requests.exceptions.ConnectionError,
                    tries=5,
                    delay=5,
                )
            except NotFound:
                pass

    request.addfinalizer(fin)

    return app


@pytest.fixture(scope="session")
def image(request, cmd_opts):
    """
    Image fixture (session scope)
    """
    return _image(request, cmd_opts)


@pytest.fixture()
def app_fs(image, request) -> APPApi:
    """Runs APP container with a previously initialized image.
    Returns authorized instance of APPApi object
    """
    return _app(image, request).api
