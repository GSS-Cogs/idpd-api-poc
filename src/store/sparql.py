
from store.base import BaseStore
from typing import Dict
import os
from SPARQLWrapper import SPARQLWrapper, QueryResult

class SparqlStore(BaseStore):

    #seting up the self.url
    def setup(self):
        url = os.environ.get("SPARQL_ENDPOINT_URL", "https://beta.gss-data.org.uk/sparql")
        self.sparql = SPARQLWrapper(url)

    def run_sparql(self, query) -> QueryResult:
        """ Runs and returns the results from a sparql query"""
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat("json")
        return self.sparql.query()
    
    def map_query_response_to_json(self, list_of_data):
        nicer_list = []
        for item in list_of_data:
            n = {
                "title": item["name"]["value"],
                "description": item["description"]["value"],
                "summary": item["record"]["value"],
                "last_updated": item["issued"]["value"],
                "links": {"self": {"url": item["creator"]["value"]},
                "publisher": {"url":item["issued"]["value"],
                              "id": item["creatorName"]["value"]},
                "topic": {"url": item["theme"]["value"],
                          "id": item["description"]["value"]},
                "releases":{"url": item["comment"]["value"]},
                "latest_version": {"url": item["theme"]["value"],
                                "id": item["modified"]["value"]},}
            }
            nicer_list.append(n)

        return nicer_list

    def get_datasets(self) -> Dict:
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
                LIMIT 2"""

        result = self.run_sparql(query).convert()

        # directly after the result = query.convert() business 
        list_of_results = self.map_query_response_to_json(result['results']['bindings'])
        response = {
                    "items": list_of_results,
                    "offset": 0,
                    "count": len(list_of_results)
                    }

        return response
