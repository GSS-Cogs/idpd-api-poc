import json
from fastapi.exceptions import ResponseValidationError
import pytest
import pathlib
from unittest.mock import MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from constants import JSONLD
from main import app

# Devnotes:

# In this code, we want to test that certain MIME types
# result in certain store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.
# Mock data representing the expected response structure for /datasets/{id}

endpoint_url = "/datasets/some-id"

# Fixture to load expected dataset data from a JSON file
@pytest.fixture
def expected_dataset_by_id_response_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)["items"][0]


def test_dataset_valid_structure_200(expected_dataset_by_id_response_data):
    """
    Confirm that the store.get_datasets() method is
    called where an "accept: application/json+ld"
    header is provided and the store provides valid
    data then status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_dataset_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate ID is found
    mock_metadata_store.get_dataset = MagicMock(return_value=expected_dataset_by_id_response_data)

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_dataset.assert_called_once()


def test_dataset_invalid_structure_raises():
    """
    Confirm that the store.get_dataset(id) method is
    called where an "accept: application/json+ld"
    header is provided ....but... the store provides
    invalid data then a server side exception is
    raised.
    """

    # Will be similar to test_datasets_invalid_structure_raises
    # in tests_datasets.py

    ...
    

def test_dataset_404():
    """
    Confirm that the store.get_dataset() method is
    called where an "accept: application/json+ld"
    header is not provided but status code 404 is returned
    where the id in question is not in the store.
    """
    
    # Note from mike - set your MagickMock(response_value=) as None
    # to simulate the id asked for not being in the store.

    ...


def test_dataset_406():
    """
    Confirm that the store.get_datasets() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """
    # Will be similar to test_datasets_406
    # in tests_datasets.py

    ...


