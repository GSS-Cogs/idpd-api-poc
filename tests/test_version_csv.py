from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient
import pytest

from constants import CSV
from store.csv.googlecloudstorage.store import CloudStorageCsvStore
from main import app

ENDPOINT = "/datasets/some-dataset-id/editions/some-edition-id/versions/some-version-id"

@pytest.mark.asyncio
def test_version_csv_200():
    """
    Confirms that:

    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns not None
    - Status code 200 is returned.
    - The response is a streamable download.
    """

    # note: based on path parameters in ENDPOINT
    expected_filename = "some-dataset-id_some-edition-id_some-version-id.csv"

    # Mock the HTTP response
    mock_csv_store = MagicMock()
    mock_csv_store.get_version = MagicMock(return_value=(expected_filename, iter([b"1", b"2", b"3"])))
    app.dependency_overrides[CloudStorageCsvStore] = lambda: mock_csv_store

    test_client = TestClient(app)
    response = test_client.get(ENDPOINT, headers={"accept": CSV})

    assert response.status_code == 200
    assert "Content-Disposition" in response.headers
    assert response.headers["Content-Disposition"] == f'attachment; filename="{expected_filename}"'
    assert response.content == b"123"
    mock_csv_store.get_version.assert_called_once()


def test_version_csv_404_from_not_found():
    """
    Confirms that:

    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_version() method
    mock_csv_store = MagicMock()
    mock_csv_store.get_version = MagicMock(return_value=(None, None))
    app.dependency_overrides[CloudStorageCsvStore] = lambda: mock_csv_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": CSV})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_csv_store.get_version.assert_called_once()