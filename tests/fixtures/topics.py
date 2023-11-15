import json
import pathlib
import pytest

from store.metadata.stub.store import StubMetadataStore


@pytest.fixture
def topic_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_topic().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/topics.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)["topics"][0]


@pytest.fixture
def topics_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_topics().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/topics.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)


@pytest.fixture
def sub_topic_test_data():
    """
    Returns a dictionary representing the dictionary
    we'd expect returned from store.get_sub_topics().
    """
    file_path = pathlib.Path("src/store/metadata/stub/content/subtopics.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)
