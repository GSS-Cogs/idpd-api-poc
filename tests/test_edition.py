from unittest.mock import MagicMock

from fastapi import status
from fastapi.exceptions import ResponseValidationError
from fastapi.testclient import TestClient
import pytest

from constants import CSV, JSONLD
from main import app, StubMetadataStore, StubCsvStore

from tests.fixtures.editions_oxigraph import edition_test_data


# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT = "/datasets/some-dataset-id/editions/some-edition-id"


def test_edition_valid_structure_200(edition_test_data):
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_edition() is called exactly once.
    - And if store.get_edition() returns not None
    - And the store provides valid data
    - Status code 200 is returned.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_edition = MagicMock(return_value=edition_test_data)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_edition.assert_called_once()


def test_edition_invalid_structure_raises():
    """
    Confirm that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_edition() is called exactly once.
    - And if store.get_edition() returns data that does not
      match the response schema.
    - A ResponseValidationError is raised.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_edition = MagicMock(
        return_value={"items": [{"invalid_field": "Invalid edition"}]}
    )
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    with pytest.raises(ResponseValidationError):
        response = client.get(ENDPOINT, headers={"Accept": JSONLD})


def test_edition_404():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_edition() is called exactly once.
    - And if store.get_edition() returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_edition() method
    mock_metadata_store = MagicMock()
    # Note: returning an empty list to simulate "id is not found"
    mock_metadata_store.get_edition = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_edition.assert_called_once()


def test_edition_406():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_edition() is not called.
    - Status code 406 is returned.
    """

    # Create a mock store with a callable mocked get_dataset() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_edition = MagicMock(return_value="irrelevant")
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_edition.assert_not_called()


def test_edition_csv_200(edition_test_data):
    """
    Confirms that:

    - Then store.get_edition() is called exactly once.
    - And if store.get_edition() returns not None
    - Status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_edition() method
    mock_csv_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_csv_store.get_edition = MagicMock(return_value=edition_test_data)
    app.dependency_overrides[StubCsvStore] = lambda: mock_csv_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": CSV})

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    mock_csv_store.get_edition.assert_called_once()


def test_edition_csv_404():
    """
    Confirms that:

    - Then store.get_edition() is called exactly once.
    - And if store.get_edition() returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_edition() method
    mock_csv_store = MagicMock()
    mock_csv_store.get_edition = MagicMock(return_value=None)
    app.dependency_overrides[StubCsvStore] = lambda: mock_csv_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": CSV})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_csv_store.get_edition.assert_called_once()