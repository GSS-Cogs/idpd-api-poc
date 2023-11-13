from unittest.mock import MagicMock

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from fastapi.exceptions import ResponseValidationError

from constants import JSONLD
from tests.fixtures.context import context_test_data
from main import app, StubMetadataStore

ENDPOINT = "/"


def test_context_valid_structure_200(context_test_data):
    mock_context = MagicMock()
    mock_context.get_context = MagicMock(return_value=context_test_data)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_context
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_200_OK
    mock_context.get_context.assert_called_once()


def test_context_404():
    mock_context = MagicMock()
    mock_context.get_context = MagicMock(return_value=None)
    app.dependency_overrides[StubMetadataStore] = lambda: mock_context
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": JSONLD})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_context.get_context.assert_called_once()


def test_context_406():
    mock_context = MagicMock()
    mock_context.get_context = MagicMock(return_value="irrelevant")
    app.dependency_overrides[StubMetadataStore] = lambda: mock_context
    client = TestClient(app)
    response = client.get(ENDPOINT, headers={"Accept": "foo"})

    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
    mock_context.get_context.assert_not_called()
