"""Module helps to run APP in docker"""
import io
import random
import socket
from contextlib import contextmanager
from gzip import compress

import allure
import docker
from docker.errors import APIError, ImageNotFound

from .api_objects import APPApi
from .tools import wait_for_url, random_string

MIN_DOCKER_PORT = 8000
MAX_DOCKER_PORT = 9000
DEFAULT_IP = "127.0.0.1"
CONTAINER_START_RETRY_COUNT = 20
DEFAULT_IMAGE = "app"
DEFAULT_TAG = "latest"


class UnableToBind(Exception):
    """Raise when it is impossible to get a free port"""


class RetryCountExceeded(Exception):
    """Raise when container was not started"""


def _port_is_free(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((ip, port))
    if result == 0:
        return False
    return True


def _find_random_port(ip):
    for _ in range(0, 20):
        port = random.randint(MIN_DOCKER_PORT, MAX_DOCKER_PORT)
        if _port_is_free(ip, port):
            return port
    raise UnableToBind("There is no free port for Docker after 20 tries.")


class APP:
    """
    Class that wraps APP Api operation over self.api
    and wraps docker over self.container (see docker module for info)
    """

    def __init__(self, container, ip, port):
        self.container = container
        self.ip = ip
        self.port = port
        self.url = "http://{}:{}".format(self.ip, self.port)
        self.api = APPApi(self.url)

    def stop(self):
        """Stops container"""
        self.container.stop()


class DockerWrapper:
    """Allow connecting to local docker daemon and spawn APP instances."""

    __slots__ = ("client",)

    def __init__(self):
        self.client = docker.from_env()

    def run_app(
        self, image=None, remove=True, name=None, tag=None, ip=None, volumes=None
    ):
        """
        Run APP in docker image.
        Return APP instance.
        """
        if image is None:
            image = DEFAULT_IMAGE
        if tag is None:
            tag = DEFAULT_TAG
        if not ip:
            ip = DEFAULT_IP

        container, port = self.app_container(
            image=image, remove=remove, name=name, tag=tag, ip=ip, volumes=volumes
        )

        wait_for_url("http://{}:{}/api/v1/".format(ip, port), 60)
        return APP(container, ip, port)

    def app_container(
        self, image=None, remove=True, name=None, tag=None, ip=None, volumes=None
    ):
        """
        Run APP in docker image.
        Return APP container and bind port.
        """
        for _ in range(0, CONTAINER_START_RETRY_COUNT):
            port = _find_random_port(ip)
            try:
                with allure.step(f"Run container: {image}:{tag}"):
                    container = self.client.containers.run(
                        "{}:{}".format(image, tag),
                        ports={"80": (ip, port)},
                        volumes=volumes,
                        remove=remove,
                        detach=True,
                        name=name,
                    )
                break
            except APIError as err:
                if (
                    "failed: port is already allocated" in err.explanation
                    or "bind: address already in use" in err.explanation  # noqa: W503
                ):
                    # such error excepting leaves created container and there is
                    # no way to clean it other than from docker library
                    pass
                else:
                    raise err
        else:
            raise RetryCountExceeded(
                f"Unable to start container after {CONTAINER_START_RETRY_COUNT} retries"
            )
        return container, port


@contextmanager
def gather_app_data_from_container(app):
    """Get archived data from APP container and return it compressed"""
    bits, _ = app.container.get_archive("/var/www/html/storage/")

    with io.BytesIO() as stream:
        for chunk in bits:
            stream.write(chunk)
        stream.seek(0)
        yield compress(stream.getvalue())


def get_initialized_app_image(
    repo="local/app", tag=None, app_repo=None, app_tag=None, dc=None
) -> dict:
    """
    If we don't know tag image must be initialized, tag will be randomly generated.
    """
    if not dc:
        dc = docker.from_env()

    if tag and image_exists(repo, tag, dc):
        return {"repo": repo, "tag": tag}
    else:
        if not tag:
            tag = random_string()
        return init_app(repo, tag, app_repo, app_tag)


def init_app(repo, tag, app_repo, app_tag):
    """Run APP and commit container as a new image"""
    dw = DockerWrapper()
    app = dw.run_app(image=app_repo, tag=app_tag, remove=False)
    # Create a snapshot from initialized container
    app.container.stop()
    app.container.commit(repository=repo, tag=tag)
    app.container.remove()
    return {"repo": repo, "tag": tag}


def image_exists(repo, tag, dc=None):
    """Check that image with repo and tag exists"""
    if dc is None:
        dc = docker.from_env()
    try:
        dc.images.get(name="{}:{}".format(repo, tag))
    except ImageNotFound:
        return False
    return True
