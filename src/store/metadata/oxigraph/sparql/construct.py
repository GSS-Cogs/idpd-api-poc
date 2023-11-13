from rdflib import Graph


def construct_dataset_core(graph: Graph) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ons: <https://data.ons.gov.uk/ns#>
        CONSTRUCT WHERE {
            ?ds a dcat:DatasetSeries ;
                dcterms:identifier ?identifier ;
                dcterms:title ?title ;
                dcterms:creator ?creator ;
                dcterms:description ?description ;
                dcterms:accrualPeriodicity ?frquency ;
                dcterms:abstract ?summary ;
                dcterms:issued ?release_date ;
                ons:nextRelease ?next_release ;
                dcterms:publisher ?publisher ;
                dcterms:license ?license ;
                dcterms:spatial ?spatial_coverage ;
                dcterms:temporal ?temporal_coverage .
        }
        """
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_themes(graph: Graph) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {
            ?ds a dcat:DatasetSeries ;
                dcat:theme ?theme .
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


def construct_dataset_keywords(graph: Graph) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {
            ?ds a dcat:DatasetSeries ;
                dcat:keyword ?keyword .
        }
        """
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_contact_point(graph: Graph) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        CONSTRUCT WHERE {
            ?ds a dcat:DatasetSeries ;
                dcat:contactPoint ?contact_point .

            ?contact_point vcard:fn ?name ;
                vcard:hasEmail ?email .
        }
        """
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()

    return result


def construct_dataset_temporal_coverage(graph: Graph) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {
            ?ds a dcat:DatasetSeries ;
                dcterms:temporal ?temporal_coverage .

            ?temporal_coverage dcat:startDate ?start_date ;
                dcat:endDate ?end_date .
        }
        """
    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_dataset_version(
    graph: Graph, dataset_id: str, edition_id: str, version_id: str
) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        PREFIX csvw: <https://www.w3.org/ns/csvw#>
        CONSTRUCT WHERE {{
        <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}> a ?type ;
        dcterms:identifier ?identifier ;
        dcterms:title ?title ;
        dcterms:description ?description ;
        dcterms:abstract ?summary ;
        dcterms:issued ?release_date ;
        dcat:downloadUrl ?download_url ;
        csvw:schema ?table_schema .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id, version_id=version_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result

def construct_dataset_version(
    graph: Graph, dataset_id: str, edition_id: str, version_id: str
) -> Graph:
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX csvw: <https://www.w3.org/ns/csvw#>
        CONSTRUCT WHERE {{
        <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}> a ?type ;
        dcterms:identifier ?identifier ;
        dcterms:title ?title ;
        dcterms:description ?description ;
        dcterms:abstract ?summary ;
        dcterms:issued ?release_date ;
        dcat:downloadUrl ?download_url ;
        dcterms:MediaType ?mediatype .
        }}
        """.format(dataset_id=dataset_id, edition_id=edition_id, version_id=version_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result

def construct_dataset_version_table_schema(
    graph: Graph, dataset_id: str, edition_id: str, version_id: str
) -> Graph:
    query = """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX csvw: <https://www.w3.org/ns/csvw#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}> a ?type  ;
        csvw:schema ?table_schema .
            ?table_schema csvw:column ?columns .
            ?columns csvw:name ?name ;
                    csvw:datatype ?datatype ;
                    dcterms:description ?description ;
                    csvw:titles ?titles .
        }}
        """.format(
        dataset_id=dataset_id, edition_id=edition_id, version_id=version_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result