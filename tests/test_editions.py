from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from main import app


def test_editions_200():
    """
    Confirm that the metadat_store.get_editions() method is
    called exactly once and we get a 200 status code
    where it does not return None.
    """


    # Create a mock store with a callable mocked get_version() method
    mock_metadat_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadat_store.get_editions = MagicMock(return_value="")

    client = TestClient(app)
    app.state.stores["edition_metadata"] = mock_metadat_store
    response = client.get("/datasets/cpih/editions")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadat_store.get_version.assert_called_once()

def test_editions_404():
    """
    Confirm that the metadat_store.get_editions() method is
    called exactly once and we get a 404 status code
    where it returns None.
    """

    # Create a mock store with a callable mocked get_version() method
    mock_metadat_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadat_store.get_editions = MagicMock(return_value="")

    client = TestClient(app)
    app.state.stores["edition_metadata"] = mock_metadat_store
    response = client.get("/datasets/NAH/editions")

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadat_store.get_version.assert_called_once()
    