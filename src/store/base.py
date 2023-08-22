from abc import ABC, abstractmethod
import os
from SPARQLWrapper import SPARQLWrapper, JSON, QueryResult

class BaseStore(ABC):

    # Every client runs the setup method
    def __init__(self):
        self.setup()

    # Every client must have a setup method
    @abstractmethod
    def setup(self):
        ...

    @abstractmethod
    def get_datasets(self):
        ...


class SparqlStore(BaseStore):

    #seting up the self.url
    def setup(self):
        # set the url for sparql
        self.url = os.getenv("SPARQL_ENDPOINT_URL")

        #to make sure self.url is not none providin a default url
        if self.url == None:
            self.url = "https://beta.gss-data.org.uk/sparql"


    def get_datasets(self) -> QueryResult:

        #this is where the url to get the data will be passed in
        sparql = SPARQLWrapper(self.url)

        sparql.setQuery("""
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX gss: <http://gss-data.org.uk/catalog/>
        PREFIX pmd: <http://publishmydata.com/pmdcat#>

        SELECT * 
        WHERE { ?s ?p ?o . }
        
        LIMIT 10""")

        #formating the return value
        sparql.setReturnFormat(JSON)

        results = sparql.query()

        return results 