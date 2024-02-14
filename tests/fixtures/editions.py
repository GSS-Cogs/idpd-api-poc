import json
import pathlib
import pytest


@pytest.fixture
def edition_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_edition().
    """
    file_path = pathlib.Path(
        "tests/fixtures/content/datasets/cpih/editions/2022-01.json"
    )
    with open(file_path, "r") as json_file:
        edition = json.load(json_file)["editions"][0]
    edition["@context"] = "https://staging.idpd.uk/ns#"
    return edition


@pytest.fixture
def editions_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_editions().
    """
    file_path = pathlib.Path(
        "tests/fixtures/content/datasets/cpih/editions/2022-01.json"
    )
    with open(file_path, "r") as json_file:
        return json.load(json_file)
