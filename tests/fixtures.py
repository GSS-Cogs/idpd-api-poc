import json
import pathlib

import pytest


# Fixture to load expected dataset data from a JSON file
@pytest.fixture
def expected_dataset_response_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)["items"][0]
    
@pytest.fixture
def expected_datasets_response_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)