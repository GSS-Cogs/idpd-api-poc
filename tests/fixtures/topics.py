import json
import pathlib
import pytest


@pytest.fixture
def topic_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_topic().
    """
    file_path = pathlib.Path("tests/fixtures/content/topics.json")
    with open(file_path, "r") as json_file:
        topic = json.load(json_file)["topics"][0]
        topic["@context"] = "https://staging.idpd.uk/ns#"
    return topic

@pytest.fixture
def topics_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_topics().
    """
    file_path = pathlib.Path("tests/fixtures/content/topics.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)
