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

def test_dataset_200():
    """
    Confirm that the store.get_dataset() method is
    called where an "accept: application/json+ld"
    header is provided and status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_datasets_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_dataset = MagicMock(return_value=["foo"])

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    response = client.get("/datasets/some-id", headers={"Accept": JSONLD})

    # Assertions
    assert response.json() == "foo"
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_dataset.assert_called_once()


def test_dataset_by_id_404():
    """
    Confirm that the store.get_dataset() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """

    # Create a mock store with a callable mocked get_datasets_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning an empty list to simulate "id is not found"
    mock_metadata_store.get_dataset = MagicMock(return_value=[])
    
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    response = client.get("/datasets/some-id", headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_dataset.assert_called_once()


def test_dataset_by_id_406():
    """
    Confirm that the store.get_dataset() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """

    # Create a mock store with a callable mocked get_datasets_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_dataset = MagicMock(return_value=["foo"])
    
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    response = client.get("/datasets/some-id", headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_dataset.assert_not_called()
