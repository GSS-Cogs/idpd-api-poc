import json
import pathlib
import pytest


@pytest.fixture
def dataset_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_dataset().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)["datasets"][0]


@pytest.fixture
def datasets_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_datasets().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)
