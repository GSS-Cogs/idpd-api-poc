from unittest.mock import MagicMock

from fastapi import status
from fastapi.exceptions import ResponseValidationError
from fastapi.testclient import TestClient
import pytest

from constants import JSONLD
from tests.fixtures.topics_oxigraph import topic_test_data
from main import app, StubMetadataStore

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT = "/topics/some-topic-id"


def test_topic_valid_structure_200(topic_test_data):
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_topic() is called exactly once.
    - And if store.get_topic() returns returns data that does
      match the response schema.
    - Status code 200 is returned.
    """
    # Create a mock store with a callable mocked get_topic() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_topic = MagicMock(return_value=topic_test_data)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_topic.assert_called_once()


def test_topic_invalid_structure_raises():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_topic() is called exactly once.
    - And if store.get_topic() returns data that does not
      match the response schema.
    - A ResponseValidationError is raised.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_topic = MagicMock(
        return_value={"topics": [{"invalid_field": "Invalid topic"}], "offset": 0}
    )
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)

    with pytest.raises(ResponseValidationError):
        client.get(ENDPOINT, headers={"Accept": JSONLD})


def test_topic_404():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_topic() is called exactly once.
    - And if store.get_topic() returns None
    - Status code 404 is returned.

    """
    # Create a mock store with a callable mocked get_topic() method
    mock_metadata_store = MagicMock()
    # Note: returning an empty list to simulate "id is not found"
    mock_metadata_store.get_topic = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_topic.assert_called_once()


def test_topic_406():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_topic() is not called.
    - Status code 406 is returned.
    """
    # Create a mock store with a callable mocked get_topic() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_topic = MagicMock(return_value={})
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_topic.assert_not_called()
