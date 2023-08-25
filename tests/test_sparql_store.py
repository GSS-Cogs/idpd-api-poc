from typing import Dict
import os
from SPARQLWrapper import QueryResult
import pytest

from store.sparql import SparqlStore


def test_get_datasets():
    """testing that the get_dataset will return access
    the url provided and run the SPRQL query, returns a Dictionary"""

    test_instance = SparqlStore()

    result = test_instance.get_datasets()

    assert isinstance(result, Dict)

def test_run_sparql():
    """testing that the run_sparql will return a QueryResult object"""
    
    test_instance = SparqlStore()

    query = "SELECT * WHERE { ?s ?p ?o . } LIMIT 10"

    result = test_instance.run_sparql(query)

    assert isinstance(result, QueryResult)


def test_sparql_store_setup_default():
    """
    testing the setup function having the correct url by default
    (when the env does not have a SPARQL_ENDPOINT_URL)
    """

    test_instance = SparqlStore()

    assert test_instance.sparql.endpoint == "https://beta.gss-data.org.uk/sparql"
    
def test_sparql_store_setup_custom():
    """
    testing the setup function having the correct 
    url when provided a custom env variable
    """
    temporary_storage= None
    #checking if user has already a SPARQL_ENDPOINT_URL 
    if os.environ.get("SPARQL_ENDPOINT_URL") is not None:
        #temporeraly saving the value
        temporary_storage = os.environ.get("SPARQL_ENDPOINT_URL")
        os.environ["SPARQL_ENDPOINT_URL"] = "https://beta.gss-data.org.uk/custom_endpoint"
    else:
        os.environ["SPARQL_ENDPOINT_URL"] = "https://beta.gss-data.org.uk/custom_endpoint"

    test_instance = SparqlStore()

    assert test_instance.sparql.endpoint == "https://beta.gss-data.org.uk/custom_endpoint"

    #re-setting the value back to what it was
    if temporary_storage is not None:
        os.environ["SPARQL_ENDPOINT_URL"] = temporary_storage
    