import json
import pathlib
import pytest
from data import populate
from store.metadata.context import ContextStore

@pytest.fixture
def dataset_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_dataset().
    """
    # loads the data
    file_path = pathlib.Path("tests/fixtures/content/datasets.json")
    
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        dataset = json.load(json_file)["datasets"][0]
        dataset["context"] = ContextStore().get_context()
    return dataset

@pytest.fixture
def datasets_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_datasets().
    """
    # loads the data
    file_path = pathlib.Path("tests/fixtures/content/datasets.json")
    
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        return json.load(json_file)