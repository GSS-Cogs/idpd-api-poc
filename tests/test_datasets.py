from unittest.mock import MagicMock

from fastapi.exceptions import ResponseValidationError
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from constants import JSONLD
from main import app, StubMetadataStore
from fixtures.datasets import datasets_data

# Devnotes:

# In this code we just want to test that certain mimetypes
# result in certains store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.

ENDPOINT = "/datasets"


# Fixture to load expected dataset data from a JSON file
@pytest.fixture
def expected_datasets_response_data():
    return datasets_data()


def test_datasets_valid_structure_200(expected_datasets_response_data):
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_datasets() is called exactly once.
    - And if store.get_datasets() returns not None
    - Status code 200 is returned.
    """

    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(
        return_value=expected_datasets_response_data
    )
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_datasets.assert_called_once()


def test_datasets_invalid_structure_raises():
    """
    Confirms that:

     - Where we have an "accept: application/json+ld" header.
     - Then store.get_datasets() is called exactly once.
     - And if store.get_datasets() returns data that does not
       match the response schema.
     - A ResponseValidationError is raised.
    """

    # Create a mock store with a callable mocked
    mock_metadata_store = MagicMock()
    invalid_response_data = {"items": [{"title": "Invalid Dataset"}], "offset": 0}
    mock_metadata_store.get_datasets = MagicMock(return_value=invalid_response_data)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)

    with pytest.raises(ResponseValidationError):
        client.get(ENDPOINT, headers={"Accept": JSONLD})


def test_datasets_404():
    """
    Confirms that:

    - Where we have an "accept: application/json+ld" header.
    - Then store.get_datasets() is called exactly once.
    - And if store.get_datasets() method returns None
    - Status code 404 is returned.
    """

    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_datasets.assert_called_once()


def test_datasets_406():
    """
    Confirms that:

    - Where we do not have an "accept: application/json+ld" header.
    - Then store.get_datasets() is not called.
    - Status code 406 is returned.
    """

    # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_datasets = MagicMock(return_value="irrelevant")
    app.dependency_overrides[StubMetadataStore] = lambda: mock_metadata_store

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_datasets.assert_not_called()
