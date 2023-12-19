import json
import pathlib
import pytest
from data import populate

@pytest.fixture
def topic_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_topic().
    """
    file_path = pathlib.Path("tests/fixtures/content/topics.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        return json.load(json_file)["topics"][0]


@pytest.fixture
def topics_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_topics().
    """
    file_path = pathlib.Path("tests/fixtures/content/topics.json")
    # Use the data.py script to populate the graph
    populate(jsonld_location="tests/fixtures/content", write_to_db=False)
    with open(file_path, "r") as json_file:
        return json.load(json_file)
