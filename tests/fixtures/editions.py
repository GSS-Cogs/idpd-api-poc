import json
import pathlib
import pytest

@pytest.fixture
def edition_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)["items"][0]
    
@pytest.fixture
def editions_data(): 
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)