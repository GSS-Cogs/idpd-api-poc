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
    assert len(json.loads(response)) != 0


def test_unsupported_accept_headers_return_406():
    """
    Confirm that a 406 status code is returned where
    an unsupported accept header is provided.
    """

    client = app.test_client()

    headers = {"Accept":"something"}

    response = client.get('/datasets', headers=headers)

    assert response.status_code == 406