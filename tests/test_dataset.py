import json
from fastapi.exceptions import ResponseValidationError
from pydantic.error_wrappers import ValidationError
import pytest
import pathlib
from unittest.mock import MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from constants import JSONLD
from main import app

# Devnotes:

# In this code, we want to test that certain MIME types
# result in certain store methods being called and certain
# status codes being returned.
# We should NOT care what the stores actually do - that's
# what the /store tests are for, so we mock a store.
# Mock data representing the expected response structure for /datasets/{id}

endpoint_url = "/datasets/some-id"

# Fixture to load expected dataset data from a JSON file
@pytest.fixture
def expected_dataset_by_id_response_data():
    file_path = pathlib.Path("src/store/metadata/stub/content/datasets.json")
    with open(file_path, 'r') as json_file:
        return json.load(json_file)["items"][0]


def test_dataset_valid_structure_200(expected_dataset_by_id_response_data):
    """
    Confirm that the store.get_datasets() method is
    called where an "accept: application/json+ld"
    header is provided and the store provides valid
    data then status code 200 is returned.
    """

    # Create a mock store with a callable mocked get_dataset_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate ID is found
    mock_metadata_store.get_dataset = MagicMock(return_value=expected_dataset_by_id_response_data)

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_200_OK
    mock_metadata_store.get_dataset.assert_called_once()



def test_dataset_invalid_structure_raises(expected_dataset_by_id_response_data):
    """
    Confirm that the store.get_dataset(id) method is
    called where an "accept: application/json+ld"
    header is provided ....but... the store provides
    invalid data then a server-side exception is
    raised.
    """
    # Create a mock store with a callable mocked get_dataset_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning a populated list to simulate ID is found
    mock_metadata_store.get_dataset = MagicMock(return_value={"items": [{"invalid_field": "Invalid Dataset"}], "offset": 0})

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    
    with pytest.raises(ResponseValidationError):
        response = client.get(endpoint_url, headers={"Accept": JSONLD})
        print(response.status_code) 
        print(response.json())



    # response = client.get("/datasets/some-id", headers={"Accept": JSONLD})

    # # Assertions
    # assert response.json() != expected_dataset_by_id_response_data
    # assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    # mock_metadata_store.get_dataset_by_id.assert_called_once()


    # # Create a mock store with a callable mocked
    # mock_metadata_store = MagicMock()
    # invalid_response_data = {"invalid_field": "invalid Data"}
    # mock_metadata_store.get_dataset = MagicMock(return_value=invalid_response_data)

    # # Create a TestClient for your FastAPI app
    # client = TestClient(app)
    # app.state.stores["dataset_metadata"] = mock_metadata_store
    # response = client.get(endpoint_url, headers={"Accept": JSONLD})
    
    # with pytest.raises(ResponseValidationError):
    #     response = client.get(endpoint_url, headers={"Accept": JSONLD})
    #     print(response.status_code) 
    #     print(response.json())
   
   
   
   
    # Act and Assert
    # with pytest.raises(HTTPException) as exc_info:
    #     response = client.get(endpoint_url, headers={"Accept": JSONLD})
    #     print(response.status_code)  # Debug print the status code
    #     print(response.json())  # Debug print the response content

    # assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # assert "Validation Error" in str(exc_info.value)


def test_dataset_404():
    """
    Confirm that the store.get_dataset() method is
    called where an "accept: application/json+ld"
    header is not provided but status code 404 is returned
    where the id in question is not in the store.
    """
    
    # Create a mock store with a callable mocked get_dataset_by_id() method
    mock_metadata_store = MagicMock()
    # Note: returning None to simulate the id not being found in the store
    mock_metadata_store.get_dataset = MagicMock(return_value=None)

    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_metadata_store.get_dataset.assert_called_once()


def test_dataset_406():
    """
    Confirm that the store.get_datasets() method is not
    called where an "accept: application/json+ld"
    header is not provided. Status code 406 should be
    returned.
    """
        # Create a mock store with a callable mocked get_datasets() method
    mock_metadata_store = MagicMock()
    mock_metadata_store.get_dataset = MagicMock(return_value={})
    
    # Override the stub_store dependency with the mock_metadata_store
    # Create a TestClient for your FastAPI app
    client = TestClient(app)
    app.state.stores["dataset_metadata"] = mock_metadata_store
    response = client.get(endpoint_url, headers={"Accept": "foo"})

    # Assertions
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_metadata_store.get_dataset.assert_not_called()


