import json
import pytest
import pathlib

from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient
from fastapi.exceptions import ResponseValidationError

from constants import JSONLD
from main import app
from fixtures.data import get_datasets_json

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT_URL = "/datasets"


# Mock data representing the expected response structure for /datasets
@pytest.fixture
def expected_datasets_response_data():
    return get_datasets_json()


def test_datasets_jsonld_valid_structure_200(expected_datasets_response_data):
    """
    Confirm that where an "accept: application/json+ld"
    is provided and the response from the store is of
    the correct structure:

    - status code 200 is returned
    - the metadata store is called once.
    """

    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(
        return_value=expected_datasets_response_data
    )

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["datasets_metadata"] = mock_metadata_store
    response = client.get(ENDPOINT_URL, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_datasets.assert_called_once()


def test_datasets_invalid_structure_raises_returns_500():
    """
    Confirm that where an "accept: application/json+ld"
    is provided but the response from the store is of
    the incorrect structure then:

    - status code 500 is returned
    - the metadata store is called once
    - an appropriate server side error is raised
    """

    # Create a mock store with a callable mocked
    mock_metadata_store = MagicMock()
    invalid_response_data = {"items": [{"title": "Invalid Dataset"}], "offset": 0}
    mock_metadata_store.get_datasets = MagicMock(return_value=invalid_response_data)

    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["datasets_metadata"] = mock_metadata_store

    with pytest.raises(ResponseValidationError):
        response = client.get(ENDPOINT_URL, headers={"Accept": JSONLD})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    mock_metadata_store.get_datasets.assert_called_once()


def test_datasets_wrong_mimetype_406():
    """
    Confirm that where an "accept: application/json+ld"
    is not provided then the metadata store is not called
    and a 406 is returned.
    """

    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(return_value={})

    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["datasets_metadata"] = mock_metadata_store
    response = client.get(ENDPOINT_URL, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_datasets.assert_not_called()
