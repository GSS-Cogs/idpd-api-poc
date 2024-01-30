import json
import pathlib
import pytest
from data import populate
from store.metadata.context import ContextStore

@pytest.fixture
def publisher_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_publisher().
    """
    file_path = pathlib.Path("tests/fixtures/content/publishers.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        publisher = json.load(json_file)["publishers"][0]
        publisher["@context"] = "https://staging.idpd.uk/ns#"
    return publisher


@pytest.fixture
def publishers_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_publishers().
    """
    file_path = pathlib.Path("tests/fixtures/content/publishers.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        return json.load(json_file)
