import os
import re
from typing import Dict

from SPARQLWrapper import SPARQLWrapper, QueryResult, JSON

from store.base import BaseStore

def get_value_from_dict(item, name: str):
    """this function will aquire a value from a given list of dictionaries"""

    return item[name]["value"]

def get_dataset_ID(item, name: str):
    """This funciton will return the dataset ID"""

    full_id = get_value_from_dict(item, name)

    for s in re.finditer('/', full_id):
        index = s.start()

    id = full_id[(index + 1):len(full_id)]

    return id

class SparqlStore(BaseStore):

    #seting up the self.url
    def setup(self):
        url = os.environ.get("SPARQL_ENDPOINT_URL", "https://beta.gss-data.org.uk/sparql")
        self.sparql = SPARQLWrapper(url)
        self.host = "this will be the host adress"

    def run_sparql(self, query) -> QueryResult:
        """ Runs and returns the results from a sparql query"""
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat("json")
        return self.sparql.query()

    
    def map_query_response_to_json(self, list_of_data):
        nicer_list = []
        for item in list_of_data:
            n = {
                "title": get_value_from_dict(item, "name"),
                "description": get_value_from_dict(item, "description"),
                "summary": get_value_from_dict(item, "comment"),
                "last_updated": get_value_from_dict(item, "modified"),
                "links": {"self": {"url": self.host + "/datasets/" + get_dataset_ID(item, "dataset")},
                "publisher": {"url": get_value_from_dict(item, "creator"),
                              "id": get_value_from_dict(item, "creatorName")},
                "topic": {"url": get_value_from_dict(item, "theme"),
                          "id": get_value_from_dict(item, "themeName")},
                "latest_version": {"url": self.host + "/datasets/" + "ID of Dataset"},}
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
