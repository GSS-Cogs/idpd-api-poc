import json
import pathlib
import pytest

@pytest.fixture
def expected_edition_response_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)["items"][0]
    
@pytest.fixture
def expected_editions_response_data(): 
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)