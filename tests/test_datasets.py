import json
from fastapi.exceptions import ResponseValidationError
import pytest
import pathlib

from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from main import app
from constants import JSONLD


# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.


# Mock data representing the expected response structure for /datasets

endpoint_url = "/datasets"

@pytest.fixture
def expected_dataset_response_data(): 
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


def test_datasets_200(expected_datasets_response_data):
    """
    Confirm that the store.get_datasets() method is
    called where an "accept: application/json+ld"
    header is provided and status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(return_value=expected_datasets_response_data)
    
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["datasets_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": JSONLD})

    # Assertions
    with pytest.raises(ResponseValidationError):
        response = client.get(endpoint_url, headers={"Accept": JSONLD})


def test_datasets_406():
    """
    Confirm that the store.get_datasets() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """

    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(return_value={})
    
    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["datasets_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_datasets.assert_not_called()


def test_datasets_invalid_structure_returns_406(expected_datasets_response_data):
    """
Test that the store.get_dataset_by_id() method returns a 406 error
    when an "accept: application/json+ld" header is provided, and the data returned does not match the expected data.
    """

    # Create a mock store with a callable mocked 
    invalid_response_data = {"items": [{"title": "Invalid Dataset"}], "offset": 0}
    invalid_response_data.get_datasets = MagicMock(return_value=invalid_response_data)
    
    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["datasets_metadata"] = invalid_response_data
    response = client.get(endpoint_url, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    assert response.json() != expected_datasets_response_data  # The response structure is different
    invalid_response_data.get_datasets.assert_called_once()
