from unittest.mock import MagicMock

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from fastapi.exceptions import ResponseValidationError

from store.metadata.stub.stub_store import StubMetadataStore

from constants import JSONLD
from tests.fixtures.publishers_oxigraph import publisher_test_data
from main import app, StubMetadataStore

# Devnotes:

# In this code, we want to test that certain MIME types
# result in certain store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.
# Mock data representing the expected response structure for /publishers/{id}

ENDPOINT = "/publishers/some-publisher-id"


def test_publisher_valid_structure_200(publisher_test_data):
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_publisher() is called exactly once.
    - And if store.get_publisher() returns not None
    - Status code 200 is returned.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_publisher = MagicMock(return_value=publisher_test_data)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_publisher.assert_called_once()


def test_publisher_invalid_structure_raises():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_publisher() is called exactly once.
    - And if store.get_publisher() returns data that does not
      match the response schema.
    - A ResponseValidationError is raised.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_publisher = MagicMock(
        return_value={
            "publishers": [{"invalid_field": "Invalid publisher"}],
            "offset": 0,
        }
    )
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)

    with pytest.raises(ResponseValidationError):
        client.get(ENDPOINT, headers={"Accept": JSONLD})


def test_publisher_404():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_publisher() is called exactly once.
    - And if store.get_publisher() returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_publisher() method
    mock_metadata_store = MagicMock()
    # Note: returning an empty list to simulate "id is not found"
    mock_metadata_store.get_publisher = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_publisher.assert_called_once()


def test_publisher_by_id_406():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_publisher() is not called.
    - Status code 406 is returned.
    """
    # Create a mock store with a callable mocked get_publisher() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_publisher = MagicMock(return_value={})
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_publisher.assert_not_called()
