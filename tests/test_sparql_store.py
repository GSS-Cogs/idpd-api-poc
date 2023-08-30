
from typing import Dict
import os
from SPARQLWrapper import QueryResult
import pytest

from store.sparql import SparqlStore

@pytest.fixture
def configure_environment():
    """
    This is test setup, it removes any existing custom 
    sparql endpoint specified by the user (an environment
    variable) for the length of each test before restoring it.

    To use, you just pass it into the test function.
    """

    # Keep track of the original value (if any)
    original_sparql_endpoint_env_var = os.environ.get("SPARQL_ENDPOINT_URL")

    # If there was an original value, delete it
    if original_sparql_endpoint_env_var is not None:
        del os.environ["SPARQL_ENDPOINT_URL"]

    # This yields (runs) the test
    yield 

    # Now the test has ran, if a custom env var was set - put it back
    if original_sparql_endpoint_env_var:
        os.environ["SPARQL_ENDPOINT_URL"] = original_sparql_endpoint_env_var

def test_get_datasets(configure_environment):
    """testing that the get_dataset will return access
    the url provided and run the SPRQL query, returns a Dictionary"""

    test_instance = SparqlStore()
    result = test_instance.get_datasets()
    assert isinstance(result, Dict)

def test_run_sparql(configure_environment):
    """testing that the run_sparql will return a QueryResult object"""
    
    test_instance = SparqlStore()
    query = "SELECT * WHERE { ?s ?p ?o . } LIMIT 10"
    result = test_instance.run_sparql(query)
    assert isinstance(result, QueryResult)

def test_sparql_store_setup_default(configure_environment):
    """
    testing the setup function having the correct url by default
    (when the env does not have a SPARQL_ENDPOINT_URL)
    """

    test_instance = SparqlStore()
    assert test_instance.sparql.endpoint == "https://beta.gss-data.org.uk/sparql"
    
def test_sparql_store_setup_custom(configure_environment):
    """
    testing the setup function having the correct 
    url when provided a custom env variable
    """

    os.environ["SPARQL_ENDPOINT_URL"] = "https://beta.gss-data.org.uk/custom_endpoint"
    test_instance = SparqlStore()
    assert test_instance.sparql.endpoint == "https://beta.gss-data.org.uk/custom_endpoint"
    
def test_dataset_return_values():
    """to test how to conver stuff with rdflib"""

    test_instance = SparqlStore()
    result = test_instance.get_datasets()

    assert isinstance(result, Dict)

