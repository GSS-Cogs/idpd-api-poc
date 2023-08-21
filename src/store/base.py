from abc import ABC, abstractmethod
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

    def __init__(self):
        self.query = ""

    # Do any setup this client requires
    def setup(self):
        # set the url for sparql
        self.url = "https://beta.gss-data.org.uk/sparql"

    
    def sparql_query(self) -> QueryResult:

    #this is where the url to get the data will be passed in
        sparql = SPARQLWrapper(self.url)

    #this is where the query will be passed in
        sparql.setQuery("""
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX gss: <http://gss-data.org.uk/catalog/>
        PREFIX pmd: <http://publishmydata.com/pmdcat#>
        SELECT DISTINCT * 
        WHERE { gss:datasets dcat:record ?record .
                ?record foaf:primaryTopic ?dataset .
            ?dataset    dcterms:issued ?issued ;
                dcterms:modified ?modified .
            optional {  ?dataset    rdfs:label      ?name} 
	        optional {  ?dataset    pmd:markdownDescription      ?description} 
	        optional {  ?dataset    rdfs:comment      ?comment} 
	        optional {  ?dataset    dcterms:license ?license .
				?license    rdfs:label      ?licenseName} 
            optional {  ?dataset    dcterms:creator ?creator .
                ?creator    rdfs:label      ?creatorName} 
            optional {  ?dataset    dcat:theme      ?theme .
                ?theme      rdfs:label      ?themeName} 
            }
            ORDER BY ASC (?name) 
            LIMIT 500""")

    #not sure if this is needed
        sparql.setReturnFormat(JSON)

        results = sparql.query()

        return results

    def get_datasets(self) -> QueryResult:
        # do stuff
        # use self.url or anything else you set in setup
        self.query = "this is where whe query will be passed in which will be the endpoint"

        result = self.sparql_query()

        return result 