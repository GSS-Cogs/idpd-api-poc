from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from constants import JSONLD
from main import app, StubMetadataStore

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT = "/topics/some-topic-id"

def test_topic_200():
    """
    Confirm that the store.get_topic() method is
    called where an "accept: application/json+ld"
    header is provided and status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_topics() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_topic = MagicMock(return_value=["foo"])
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.json() == ["foo"]
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_topic.assert_called_once()


def test_topic_404():
    """
    Confirm that the store.get_topic() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """

    # Create a mock store with a callable mocked get_topics() method
    mock_metadata_store = MagicMock()
    # Note: returning an empty list to simulate "id is not found"
    mock_metadata_store.get_topic = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_topic.assert_called_once()


def test_topic_406():
    """
    Confirm that the store.get_topic() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """

    # Create a mock store with a callable mocked get_topics() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_topic = MagicMock(return_value="irrelevant")
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_topic.assert_not_called()
