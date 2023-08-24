
from store.base import BaseStore
import os
from SPARQLWrapper import SPARQLWrapper, JSON, QueryResult

class SparqlStore(BaseStore):

    #seting up the self.url
    def setup(self):
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
        query = """
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
                LIMIT 500"""

        result = self.run_sparql(query).convert()

        return result
