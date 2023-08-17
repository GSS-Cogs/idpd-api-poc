import pytest

from hello_app import app


def test_hello_world_handler_correct_header_input():
    """
    test the hello_world handler to conform its 
    returning the expected values based on specific input
    """

    # Create a test client
    client = app.test_client()

    # # any headers you want, as a key value dict
    headers = {"Accept":"application/ld+json"}

    # specify your end point
    response = client.get('/datasets', headers=headers)
    
    # Assertions etc
    assert response.status_code == 200


def test_hello_world_handler_for_some_behaviour_fail():
    """
    test the hello_world handler to conform it fails
    when a not specified data type is provided and returns the expected values
    """

    # Create a test client
    client = app.test_client()

    # # any headers you want, as a key value dict
    headers = {"Accept":"something"}

    # specify your end point
    response = client.get('/datasets', headers=headers)

    # Assertions etc
    assert response.status_code == 406