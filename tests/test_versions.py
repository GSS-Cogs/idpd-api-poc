from unittest.mock import MagicMock

from fastapi import status
from fastapi.exceptions import ResponseValidationError
from fastapi.testclient import TestClient
import pytest

from constants import JSONLD
from main import app, StubMetadataStore
from fixtures.versions import versions_data

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT = "datasets/some-dataset-id/editions/some-edition-id/versions"


# TODO - reimplement once we've got a schema of the data model.

def test_versions_valid_structure_200(versions_data):
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_versions() is called exactly once.
    - And if store.get_versions() returns not None
    - Status code 200 is returned.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_versions = MagicMock(
        return_value=expected_versions_response_data
    )
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_versions.assert_called_once()


def test_versions_invalid_structure_raises():
    """
    Confirms that:

     - Where we have an "accept: application/json+ld" header.
     - Then store.get_versions() is called exactly once.
     - And if store.get_versions() returns data that does not
       match the response schema.
     - A ResponseValidationError is raised.
    """

    # Create a mock store with a callable mocked
    mock_metadata_store = MagicMock()
    invalid_response_data = {"items": [{"title": "Invalid version"}]}
    mock_metadata_store.get_versions = MagicMock(return_value=invalid_response_data)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)

    with pytest.raises(ResponseValidationError):
        client.get(ENDPOINT, headers={"Accept": JSONLD})


def test_versions_404():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_versions() is called exactly once.
    - And if store.get_versions() returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_versions() method
    mock_metadata_store = MagicMock()
    # Note: returning an empty list to simulate "id is not found"
    mock_metadata_store.get_versions = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_versions.assert_called_once()


def test_versions_406():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_versions() is not called.
    - Status code 406 is returned.
    """

    # Create a mock store with a callable mocked get_versions() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate id is found
    mock_metadata_store.get_versions = MagicMock(return_value="irrelevant")
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_versions.assert_not_called()
