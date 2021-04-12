"""Some useful methods"""
import random
import string
from itertools import repeat
from time import sleep

import requests
import allure
from requests_toolbelt.utils import dump


def wait_for_url(url: str, timeout=120) -> None:
    """Wait until url becomes available"""
    for _ in range(timeout):
        try:
            requests.get(url)
            return
        except requests.exceptions.ConnectionError:
            sleep(1)
    raise TimeoutError(f"No response from APP in {timeout} seconds")


def random_string(strlen=10):
    """Generating a random string of a certain length"""
    return "".join([random.choice(string.ascii_letters) for _ in range(strlen)])


def split_tag(image_name):
    """Split docker image by image name and tag"""
    image = image_name.split(":", maxsplit=1)
    if len(image) > 1:
        image_repo = image[0]
        image_tag = image[1]
    else:
        image_repo = image[0]
        image_tag = None
    return image_repo, image_tag


def fill_lists_by_longest(lists):
    """
    Fills each list by the longest one, thereby aligning them in length
    Last element is used as the fill value
    """
    max_len = len(max(lists, key=len))
    for current_list in lists:
        current_list.extend(repeat(current_list[-1], max_len - len(current_list)))


def nested_set(dictionary: dict, keys: list, value):
    """Set value to dict for list of nested keys

    >>> nested_set({'key': {'nested_key': None}}, keys=['key', 'nested_key'], value=123)
    {'key': {'nested_key': 123}}
    """
    nested_dict = dictionary
    for key in keys[:-1]:
        nested_dict = nested_dict[key]
    nested_dict[keys[-1]] = value
    return dictionary


def nested_get(dictionary: dict, keys: list):
    """Set value to dict for list of nested keys

    >>> nested_get({'key': {'nested_key': 123}}, keys=['key', 'nested_key'])
    123
    """
    nested_dict = dictionary
    for key in keys[:-1]:
        nested_dict = nested_dict[key]
    return nested_dict.get(keys[-1])


def create_dicts_by_chain(keys_chain: list):
    """
    Create nested dicts by keys chain
    >>> create_dicts_by_chain(['some', 'keys'])
    {'some': {'keys': {}}}
    """
    result = {}
    current_dict = result
    for key in keys_chain:
        current_dict[key] = {}
        current_dict = current_dict[key]
    return result


def attach_request_log(response):
    """Attach full HTTP request dump to Allure report"""
    allure.attach(
        dump.dump_all(response).decode("utf-8"),
        name="Full request log",
        extension="txt",
    )
