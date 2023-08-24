
from store.base import BaseStore
import os
from SPARQLWrapper import SPARQLWrapper, JSON, QueryResult

class SparqlStore(BaseStore):

    #seting up the self.url
    def setup(self):
        # set the url for sparql
        self.url = os.environ.get("SPARQL_ENDPOINT_URL", "https://beta.gss-data.org.uk/sparql")

        #to make sure self.url is not none providin a default url
        assert self.url is not None, "Then SPARQL_ENDPOINT_URL is a None value."

    def run_sparql(self, query):
        """ Runs and returns the results from a sparql query"""
        sparql = SPARQLWrapper(self.url)

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query()
    
    def get_datasets(self):
        """
        Get many datasets
        """
        query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX gss: <http://gss-data.org.uk/catalog/>
        PREFIX pmd: <http://publishmydata.com/pmdcat#>

        SELECT * 
        WHERE { ?s ?p ?o . }
        
        LIMIT 10"""
        result =  self.run_sparql(query)
