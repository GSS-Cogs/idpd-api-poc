from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from main import app, StubCsvStore

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT = "/datasets/some-dataset-id/editions/some-edition-id/versions/some-version-id"

def test_version_csv_200():
    """
    Confirms that:
     
    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns not None
    - Status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_version() method
    mock_csv_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_csv_store.get_version = MagicMock(return_value="")
    app.dependency_overrides[StubCsvStore] = lambda: mock_csv_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT)

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_csv_store.get_version.assert_called_once()


def test_version_csv_404():
    """
    Confirms that:
     
    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_version() method
    mock_csv_store = MagicMock()
    mock_csv_store.get_version = MagicMock(return_value=None)
    app.dependency_overrides[StubCsvStore] = lambda: mock_csv_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT)

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_csv_store.get_version.assert_called_once()
