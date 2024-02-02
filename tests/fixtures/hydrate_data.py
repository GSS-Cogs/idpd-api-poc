import json
import pathlib
import pytest


@pytest.fixture
def hydrate_test_data():
    """
    Returns a dictionary representing a graph to 
    be used as input for the hydrate() function tests.
    """
    file_path = pathlib.Path("tests/fixtures/content/hydrate.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)