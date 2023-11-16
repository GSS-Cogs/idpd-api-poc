import json
import pathlib
import pytest


@pytest.fixture
def context_test_data():
    file_path = pathlib.Path("src/store/metadata/context.json")
    with open(file_path, "r") as json_file:
        return json.load(json_file)
