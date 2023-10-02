# import json
# from pydantic import ValidationError
# import pytest
# import pathlib

# from unittest.mock import MagicMock

# from fastapi import status
# from fastapi.testclient import TestClient
# from fastapi.exceptions import ResponseValidationError

# from constants import JSONLD
# from main import app

# # Devnotes:

# # In this code we just want to test that certain mimetypes
# # result in certains store methods being called and certain
# # status codes being returned.
# # We should NOT care what the stores actually do - that's
# # what the /store tests are for, so we mock a store.
# # Mock data representing the expected response structure for /datasets/{id}

# endpoint_url = "/datasets/{id}"


# # Fixture to load expected dataset data from a JSON file
# @pytest.fixture
# def expected_dataset_by_id_response_data():
#     file_path = pathlib.Path("src/store/stub/content/datasets.json")
#     with open(file_path, 'r') as json_file:
#         return json.load(json_file)


# def test_dataset_valid_structure_200(expected_dataset_by_id_response_data):
#     """
#     Test that the store.get_dataset_by_id() method is called
#     when an "accept: application/json+ld" header is provided,
#     and it returns status code 200 with the expected response data.
#     """

#     # Create a mock store with a callable mocked get_dataset_by_id() method
#     mock_metadata_store = MagicMock()
#     # Note: returning a populated list to simulate ID is found
#     mock_metadata_store.get_dataset_by_id = MagicMock(return_value=expected_dataset_by_id_response_data)

#     # Create a TestClient for your FastAPI app
#     client = TestClient(app)
#     app.state.stores["dataset_metadata"] = mock_metadata_store
#     response = client.get(endpoint_url, headers={"Accept": JSONLD})

#     with pytest.raises(ResponseValidationError):
#         response = client.get(endpoint_url, headers={"Accept": JSONLD})


# def test_dataset_404():
#     """
#     Confirm that the store.get_dataset() method is not
#     called where an "accept: application/json+ld"
#     header is not provided. Status code 406 should be
#     returned.
#     """

#     # Create a mock store with a callable mocked get_dataset() method
#     mock_metadata_store = MagicMock()
#     # Note: returning an empty list to simulate "id is not found"
#     mock_metadata_store.get_dataset = MagicMock(return_value=[])

#     # Create a TestClient for your FastAPI app
#     client = TestClient(app)
#     app.state.stores["dataset_metadata"] = mock_metadata_store
#     response = client.get("/datasets/some-id")

#     # Assertions
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     mock_metadata_store.get_dataset.assert_called_once()


# def test_dataset_invalid_structure_406(expected_dataset_by_id_response_data):
#     """
#     Confirm that the store.get_dataset_by_id() method is not
#     called when an "accept: application/json+ld" header is not provided.
#     Status code 500 should be returned.
#     """

#     # Create a mock store with a callable mocked get_dataset_by_id() method
#     mock_metadata_store = MagicMock()
#     # Note: returning a populated list to simulate ID is found
#     mock_metadata_store.get_dataset_by_id = MagicMock(return_value={"items": [{"title": "Invalid Dataset"}], "offset": 0})

#     # Create a TestClient for your FastAPI app
#     client = TestClient(app)
#     app.state.stores["dataset_metadata"] = mock_metadata_store
#     response = client.get("/datasets/some-id", headers={"Accept": JSONLD})

#     # Assertions
#     assert response.status_code == status.HTTP_406_INTERNAL_SERVER_ERROR
#     assert response.json() != expected_dataset_by_id_response_data
#     mock_metadata_store.get_dataset_by_id.assert_called_once()


# def test_dataset_500_error():
#     """
#     Test that the store.get_dataset_by_id() method returns a 500 error
#     when an "accept: application/json+ld" header is provided, and there's an error.
#     """

#     # Define the endpoint URL
#     endpoint_url = "/datasets/some-id"

#     # Create a mock store with a callable mocked get_dataset_by_id() method
#     mock_metadata_store = MagicMock()

#     # Simulate an error by raising an exception
#     mock_metadata_store.get_dataset_by_id = MagicMock(side_effect=Exception("Simulated error"))

#     # Create a TestClient for your FastAPI app
#     client = TestClient(app)
#     app.state.stores["dataset_metadata"] = mock_metadata_store

#     # Make the GET request with the defined endpoint_url
#     response = client.get(endpoint_url, headers={"Accept": JSONLD})

#     # Assertions
#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
