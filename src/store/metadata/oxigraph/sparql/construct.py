from pyparsing import Literal
from rdflib import RDF, BNode, Graph, URIRef


def construct_dataset_core(graph: Graph, dataset_id: str) -> Graph:
    query = """ 
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ons: <https://data.ons.gov.uk/ns#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}> a dcat:DatasetSeries ;
            dcterms:identifier ?identifier ;
            dcterms:title ?title ;
            dcterms:abstract ?summary ;
            dcterms:description ?description ;
            dcterms:issued ?issued ;
            dcterms:modified ?modified ;
            ons:nextRelease ?next_release ;
            dcterms:publisher ?publisher ;
            dcterms:creator ?creator ;
            dcterms:accrualPeriodicity ?frequency ;
            dcterms:license ?license ;
            dcterms:spatial ?spatial_coverage ;
            hydra:collection ?editions_url  .
        }}
        """.format(dataset_id=dataset_id)

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_themes(graph: Graph, dataset_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}> a dcat:DatasetSeries ;
                dcat:theme ?theme .
        }}
        """.format(dataset_id=dataset_id)
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_keywords(graph: Graph, dataset_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}> a dcat:DatasetSeries ;
                dcat:keyword ?keyword .
        }}
        """.format(dataset_id=dataset_id)
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_contact_point(graph: Graph, dataset_id:  str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}> a dcat:DatasetSeries ;
                dcat:contactPoint ?contact_point .

            ?contact_point vcard:fn ?name ;
                vcard:hasEmail ?email .
        }}
        """.format(dataset_id=dataset_id)
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()

    return result


def construct_dataset_temporal_coverage(graph: Graph, dataset_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}> a dcat:DatasetSeries ;
                dcterms:temporal ?temporal_coverage .

            ?temporal_coverage dcat:startDate ?start_date ;
                dcat:endDate ?end_date .
        }}
        """.format(dataset_id=dataset_id)
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_editions(graph: Graph, dataset_id):
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}> a dcat:DatasetSeries ;
                hydra:member ?editions .
            ?editions dcterms:issued ?issued ;
                dcterms:modified ?modified .
        }}
    """.format(dataset_id=dataset_id)
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()

    return result