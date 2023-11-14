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
            ons:spatialResolution ?spatial_resolution ;
            dcterms:spatial ?spatial_coverage ;
            dcterms:temporalResolution ?temporal_resolution ;
            hydra:Collection ?editions_url  .
        }}
        """.format(
        dataset_id=dataset_id
    )

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
        """.format(
        dataset_id=dataset_id
    )
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_topics(graph: Graph) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {
        <https://staging.idpd.uk/topics> a hydra:Collection ;
	        dcat:theme ?topic ;
            hydra:offset ?offset ;
            hydra:totalitems ?count .
        }
        """
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_topic_by_id(graph: Graph, topic_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/topics/{topic_id}> a dcat:theme ;
            dcterms:identifier ?identifier ;
            dcterms:title ?title ;
            dcterms:description ?description .
        }}
        """.format(
        topic_id=topic_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_subtopics_by_id(graph: Graph, topic_id: str) -> Graph:
    query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/topics/{topic_id}> skos:narrower ?sub_topics .
        }}
        """.format(
        topic_id=topic_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_parent_topics_by_id(graph: Graph, topic_id: str) -> Graph:
    query = """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/topics/{topic_id}> skos:broader ?parent_topics .
        }}
        """.format(
        topic_id=topic_id
    )

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
        """.format(
        dataset_id=dataset_id
    )
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_contact_point(graph: Graph, dataset_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}> a dcat:DatasetSeries ;
                dcat:contactPoint ?contact_point .

            ?contact_point vcard:fn ?name ;
                vcard:hasEmail ?email .
        }}
        """.format(
        dataset_id=dataset_id
    )
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
        """.format(
        dataset_id=dataset_id
    )
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
    """.format(
        dataset_id=dataset_id
    )
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()

    return result


def construct_publisher(graph: Graph, publisher_id: str) -> Graph:
    query = """
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX dcterms: <http://purl.org/dc/terms/>
            CONSTRUCT WHERE {{
                <https://staging.idpd.uk/publishers/{publisher_id}> a dcat:publisher;
      				dcterms:title ?title;
                    dcterms:description ?description;
    				dcat:landingPage ?landingpage .
        }}
        """.format(
        publisher_id=publisher_id
    )
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_editions(graph: Graph, dataset_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {{
        <https://staging.idpd.uk/datasets/{dataset_id}/editions> a hydra:Collection ;
	        dcterms:title ?title ;
            hydra:member ?editions .
        }}
        """.format(
        dataset_id=dataset_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_core(graph: Graph, dataset_id: str, edition_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ons: <https://data.ons.gov.uk/ns#>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcat:inSeries ?in_series ;
    			dcterms:identifier ?identifier ;
  				dcterms:title ?title ;
                dcterms:abstract ?summary ;
                dcterms:description ?description ;
    			dcterms:publisher ?publisher ;
                dcterms:creator ?creator ;
                dcterms:accrualPeriodicity ?frequency ;
                dcterms:license ?licence ;
                dcterms:issued ?issued ;
                dcterms:modified ?modified ;
                ons:spatialResolution ?spatial_resolution ;
                dcterms:spatial ?spatial_coverage ;
                dcterms:temporalResolution ?temporal_resolution ;
                ons:nextRelease ?next_release ;
                hydra:Collection ?versions_url ;
                hydra:member ?versions .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_table_schema(
    graph: Graph, dataset_id: str, edition_id: str
) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX csvw: <https://www.w3.org/ns/csvw#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                csvw:schema ?table_schema .
            ?table_schema csvw:column ?columns .
            ?columns csvw:name ?name ;
                csvw:datatype ?datatype ;
                dcterms:description ?description ;
                csvw:titles ?titles .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_versions(graph: Graph, dataset_id: str, edition_id: str) -> Graph:
    query = """
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> hydra:member ?versions .
            ?versions dcterms:issued ?issued ;
                dcterms:modified ?modified .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_contact_point(
    graph: Graph, dataset_id: str, edition_id: str
) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcat:contactPoint ?contact_point .
            ?contact_point vcard:fn ?name ;
                vcard:hasEmail ?email .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_topics(graph: Graph, dataset_id: str, edition_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcat:theme ?theme .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_keywords(graph: Graph, dataset_id: str, edition_id: str) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcat:keyword ?keyword .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_temporal_coverage(
    graph: Graph, dataset_id: str, edition_id: str
) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcterms:temporal ?temporal_coverage .
            ?temporal_coverage dcat:startDate ?start_date ;
                dcat:endDate ?end_date .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result
