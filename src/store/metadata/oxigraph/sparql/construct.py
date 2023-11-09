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
