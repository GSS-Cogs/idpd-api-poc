from store.base import BaseStore
import os
from SPARQLWrapper import SPARQLWrapper, JSON, QueryResult

class SparqlStore(BaseStore):

    #seting up the self.url
    def setup(self):

        # TODO - new endpoint
        url = os.environ.get("SPARQL_ENDPOINT_URL", "https://beta.gss-data.org.uk/sparql")
        self.sparql = SPARQLWrapper(url)

    def run_sparql(self, query) -> QueryResult:
        """ Runs and returns the results from a sparql query"""
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        return self.sparql.query()
    
    def get_datasets(self):
        """
        Get many datasets
        """

        # TODO - new query
        query = """
                """

        result = self.run_sparql(query).convert()
        return result