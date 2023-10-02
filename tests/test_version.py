from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from main import app

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.


def test_version_csv_200():
    """
    Confirm that the csv_store.get_version() method is
    called exactly once and we get a 200 status code
    where it does not return None.
    """

    # Create a mock store with a callable mocked get_version() method
    mock_csv_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_csv_store.get_version = MagicMock(return_value="")

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["version_csv"] = mock_csv_store
    response = client.get("/datasets/foo/editions/bar/versions/baz")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_csv_store.get_version.assert_called_once()


def test_version_csv_404():
    """
    Confirm that the csv_store.get_version() method is
    called exactly once and we get a 404 status code
    where it returns None.
    """

    # Create a mock store with a callable mocked get_version() method
    mock_csv_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_csv_store.get_version = MagicMock(return_value=None)

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["version_csv"] = mock_csv_store
    response = client.get("/datasets/foo/editions/bar/versions/baz")

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_csv_store.get_version.assert_called_once()
