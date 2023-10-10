from unittest.mock import MagicMock

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from fastapi.exceptions import ResponseValidationError

from constants import JSONLD
from fixtures.datasets import dataset_data
from main import app, StubMetadataStore

# Devnotes:

# In this code, we want to test that certain MIME types
# result in certain store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.
# Mock data representing the expected response structure for /datasets/{id}

ENDPOINT = "/datasets/some-id"


# Fixture to load expected dataset data from a JSON file
@pytest.fixture
def expected_dataset_response_data():
    return dataset_data()


def test_dataset_valid_structure_200(expected_dataset_response_data):
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_dataset() is called exactly once.
    - And if store.get_datasets() returns not None
    - Status code 200 is returned.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_dataset = MagicMock(
        return_value=expected_dataset_response_data
    )
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_dataset.assert_called_once()


def test_dataset_invalid_structure_raises():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_dataset() is called exactly once.
    - And if store.get_dataset() returns data that does not
      match the response schema.
    - A ResponseValidationError is raised.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_dataset = MagicMock(
        return_value={"items": [{"invalid_field": "Invalid Dataset"}], "offset": 0}
    )
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)

    with pytest.raises(ResponseValidationError):
        client.get(ENDPOINT, headers={"Accept": JSONLD})


def test_dataset_404():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_dataset() is called exactly once.
    - And if store.get_datasets() returns None
    - Status code 404 is returned.

    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_dataset = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_dataset.assert_called_once()


def test_dataset_406():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_dataset() is not called.
    - Status code 406 is returned.
    """
    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_dataset = MagicMock(return_value=["foo"])
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_dataset.assert_not_called()
