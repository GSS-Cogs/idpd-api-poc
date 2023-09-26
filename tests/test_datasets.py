from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from main import app
from constants import JSONLD


# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

def test_datasets_200():
    """
    Confirm that the store.get_datasets() method is
    called where an "accept: application/json+ld"
    header is provided and status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(return_value={})
    
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["datasets_metadata"] = mock_metadata_store
    response = client.get("/datasets", headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_datasets.assert_called_once()


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
    response = client.get("/datasets", headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_datasets.assert_not_called()
