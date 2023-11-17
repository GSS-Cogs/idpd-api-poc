from unittest.mock import MagicMock

from fastapi import status
from fastapi.exceptions import ResponseValidationError
from fastapi.testclient import TestClient
import pytest

from constants import CSV, JSONLD
from tests.fixtures.versions import version_test_data
from main import app, StubCsvStore, OxigraphMetadataStore


# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT = "/datasets/some-dataset-id/editions/some-edition-id/versions/some-version-id"


def test_version_valid_structure_200(version_test_data):
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns not None
    - And the store provides valid data
    - Status code 200 is returned.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_version = MagicMock(return_value=version_test_data)
    app.dependency_overrides[OxigraphMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_version.assert_called_once()


def test_version_invalid_structure_raises():
    """
    Confirm that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns data that does not
      match the response schema.
    - A ResponseValidationError is raised.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_version = MagicMock(
        return_value={"items": [{"invalid_field": "Invalid version"}]}
    )
    app.dependency_overrides[OxigraphMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    with pytest.raises(ResponseValidationError):
        response = client.get(ENDPOINT, headers={"Accept": JSONLD})


def test_version_404():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_edition() method
    mock_metadata_store = MagicMock()
    # Note: returning an empty list to simulate "id is not found"
    mock_metadata_store.get_version = MagicMock(return_value=None)
    app.dependency_overrides[OxigraphMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_version.assert_called_once()


def test_version_406():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_version() is not called.
    - Status code 406 is returned.
    """

    # Create a mock store with a callable mocked get_dataset() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_version = MagicMock(return_value="irrelevant")
    app.dependency_overrides[OxigraphMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_version.assert_not_called()


def test_version_csv_200(version_test_data):
    """
    Confirms that:

    - Then store.get_version() is called exactly once.
    - And if store.get_version() returns not None
    - Status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_version() method
    mock_csv_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_csv_store.get_version = MagicMock(return_value=version_test_data)
    app.dependency_overrides[StubCsvStore] = lambda: mock_csv_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": CSV})

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
    response = client.get(ENDPOINT, headers={"Accept": CSV})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_csv_store.get_version.assert_called_once()
