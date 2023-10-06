from unittest.mock import MagicMock

from fastapi.exceptions import ResponseValidationError
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from main import app
from constants import JSONLD
from fixtures.datasets import datasets_data

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT_URL = "/datasets"


# Fixture to load expected dataset data from a JSON file
@pytest.fixture
def expected_datasets_response_data():
    return datasets_data()


def test_datasets_valid_structure_200(expected_datasets_response_data):
    """
    Confirm that the store.get_datasets() method is
    called where an "accept: application/json+ld"
    header is provided and the store provides valid
    data then status code 200 is returned.
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

    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_datasets.assert_called_once()


def test_datasets_invalid_structure_raises():
    """
    Confirm that the store.get_datasets() method is
    called where an "accept: application/json+ld"
    header is provided ....but... the store provides
    invalid data then a server side exception is
    raised.
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
        client.get(ENDPOINT_URL, headers={"Accept": JSONLD})


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
    response = client.get(ENDPOINT_URL, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_datasets.assert_not_called()
