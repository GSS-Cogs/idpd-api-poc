import pytest

from hello_app import app


def test_hello_world_handler_for_some_behaviour_or_other():
    """
    test the hello_world handler to conform its doing
    a specific thing given a specific request
    """

    # Create a test client
    client = app.test_client()

    # # any headers you want, as a key value dict
    headers = {"Accept":"application/ld+json"}

    # specify your end point
    response = client.get('/', headers=headers)

    # Assertions etc
    assert response.status_code == 200
    assert 'text/html' == response.mimetype