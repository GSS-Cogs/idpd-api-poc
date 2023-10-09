import json
import pathlib
import pytest

def dataset_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_dataset().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)["items"][0]


def datasets_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_datasets().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)


# Fixture to load expected edition data from a JSON file
@pytest.fixture
def expected_edition_response_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)["items"][0]
    
# Fixture to load expected editions data from a JSON file
@pytest.fixture
def expected_editions_response_data(): 
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)