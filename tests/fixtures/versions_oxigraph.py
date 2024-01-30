import json
import pathlib
import pytest
from data import populate
from store.metadata.context import ContextStore

@pytest.fixture
def version_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_versions().
    """
    file_path = pathlib.Path("tests/fixtures/content/editions/versions/cpih_2022-01.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        version = json.load(json_file)["versions"][0]
        version["@context"] = "https://staging.idpd.uk/ns#"
    return version


@pytest.fixture
def versions_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_versions().
    """
    file_path = pathlib.Path("tests/fixtures/content/editions/versions/cpih_2022-01.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        return json.load(json_file)
