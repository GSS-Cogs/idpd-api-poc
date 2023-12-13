import json
import pathlib
import pytest
from data import populate

@pytest.fixture
def edition_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_edition().
    """
    file_path = pathlib.Path("tests/fixtures/content/editions/cpih_2022-01.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        return json.load(json_file)["editions"][0]


@pytest.fixture
def editions_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_editions().
    """
    file_path = pathlib.Path("tests/fixtures/content/editions/cpih_2022-01.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        return json.load(json_file)
