import json
import pathlib
import pytest


@pytest.fixture
def edition_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_edition().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)["items"][0]


@pytest.fixture
def editions_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_editions().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)
