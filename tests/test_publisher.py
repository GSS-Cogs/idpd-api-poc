from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from constants import JSONLD
from main import app

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.


def test_publisher_200():
    """
    Confirm that the store.get_publisher() method is
    called where an "accept: application/json+ld"
    header is provided and status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_publishers_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_publisher = MagicMock(return_value="foo")

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["publisher_metadata"] = mock_metadata_store
    response = client.get("/publishers/some-id", headers={"Accept": JSONLD})

    # Assertions
    assert response.json() == "foo"
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_publisher.assert_called_once()


def test_publisher_404():
    """
    Confirm that the store.get_publisher() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """

    # Create a mock store with a callable mocked get_publishers_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning None to simulate "id is not found"
    mock_metadata_store.get_publisher = MagicMock(return_value=None)

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["publisher_metadata"] = mock_metadata_store
    response = client.get("/publishers/some-id", headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_publisher.assert_called_once()


def test_publisher_by_id_406():
    """
    Confirm that the store.get_publisher() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """

    # Create a mock store with a callable mocked get_publishers_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_publisher = MagicMock(return_value=["foo"])

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["publisher_metadata"] = mock_metadata_store
    response = client.get("/publishers/some-id", headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_publisher.assert_not_called()
