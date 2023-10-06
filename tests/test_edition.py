import json
from fastapi.exceptions import ResponseValidationError
from pydantic.error_wrappers import ValidationError
import pytest
import pathlib
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from constants import JSONLD 
from main import app

# Devnotes:

# In this code, we want to test that certain MIME types
# result in certain store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.
# Mock data representing the expected response structure for /editions/{id}

endpoint_url = "/editions/some-id"

# Fixture to load expected edition data from a JSON file
@pytest.fixture
def expected_edition_by_id_response_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/editions.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


def test_edition_valid_structure_200(expected_edition_by_id_response_data):
    """
    Confirm that the store.get_editions() method is
    called where an "accept: application/json+ld"
    header is provided and the store provides valid
    data then status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_edition_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate ID is found
    mock_metadata_store.get_edition = MagicMock(return_value=expected_edition_by_id_response_data)

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["edition_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_edition.assert_called_once()



def test_edition_invalid_structure_raises():
    """
    Confirm that the store.get_edition(id) method is
    called where an "accept: application/json+ld"
    header is provided ....but... the store provides
    invalid data then a server-side exception is
    raised.
    """
    # Create a mock store with a callable mocked get_edition_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate ID is found
    mock_metadata_store.get_edition = MagicMock(return_value={"items": [{"invalid_field": "Invalid edition"}], "offset": 0})

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["edition_metadata"] = mock_metadata_store
    
    with pytest.raises(ResponseValidationError):
        response = client.get(endpoint_url, headers={"Accept": JSONLD})


def test_edition_404():
    """
    Confirm that the store.get_edition() method is
    called where an "accept: application/json+ld"
    header is not provided but status code 404 is returned
    where the id in question is not in the store.
    """
    
    # Create a mock store with a callable mocked get_edition_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning None to simulate the id not being found in the store
    mock_metadata_store.get_edition = MagicMock(return_value=None)

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["edition_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_edition.assert_called_once()


def test_edition_406():
    """
    Confirm that the store.get_editions() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """
        # Create a mock store with a callable mocked get_editions() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_edition = MagicMock(return_value={})
    
    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["edition_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_edition.assert_not_called()


