import pytest
import json
from main import app, jsonld

    
def test_jsonld_accept_header_returns_200():
    """
    Confirm that a 200 status code is returned where a
    "accept: application/json+ld" header is provided.
    """

    client = app.test_client()

    headers = {"Accept":"application/ld+json"}

    response = client.get('/datasets', headers=headers)
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == jsonld 
    data = json.loads(response.data.decode("utf-8"))
    assert len(data) > 0


def test_empty_dataset_returns_404(client):
    """
    Confirm that a 404 status code is returned when the dataset is empty.
    Assume storage.get_datasets() returns an empty dictionary for this test
    """
    headers = {"Accept": "application/ld+json"}
    response = client.get('/datasets', headers=headers)

    assert response.status_code == 404
    assert len(json.loads(response["items"])) == 0


def test_unsupported_accept_headers_return_406():
    """
    Confirm that a 406 status code is returned where
    an unsupported accept header is provided.
    """

    client = app.test_client()

    headers = {"Accept":"something"}

    response = client.get('/datasets', headers=headers)

    assert response.status_code == 406