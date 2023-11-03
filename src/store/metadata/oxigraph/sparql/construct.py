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


def construct_edition_core(graph: Graph, edition_id: str) -> Graph:
    dataset_id = graph.identifier
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ons: <https://data.ons.gov.uk/ns#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
    			dcterms:identifier ?identifier ;
  				dcterms:title ?title ;
                dcterms:creator ?creator ;
                dcterms:abstract ?summary ;
                dcterms:description ?description ;
    			dcterms:publisher ?publisher ;
                dcterms:issued ?release_date ;
                ons:nextRelease ?next_release ;
                dcterms:license ?license ;
                dcterms:spatial ?spatial_coverage ;
                dcterms:temporal ?temporal_coverage .
        }}
        """.format(dataset_id=dataset_id,
        edition_id=edition_id
        )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result

# I do not know if these functions need to be separate from the core construct function, but I am taking guidance from the existing dataset functions.
def construct_edition_contact_point(graph: Graph, edition_id) -> Graph:
    dataset_id = graph.identifier
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcat:contactPoint ?contact_point .

            ?contact_point vcard:fn ?name ;
                vcard:hasEmail ?email .
        }}
    """.format(dataset_id=dataset_id,
        edition_id=edition_id
        )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_themes(graph: Graph, edition_id) -> Graph:
    dataset_id = graph.identifier
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcat:theme ?theme .
        }}
        """.format(dataset_id=dataset_id,
        edition_id=edition_id
        )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result


def construct_edition_keywords(graph: Graph, edition_id) -> Graph:
    dataset_id = graph.identifier
    query = """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {{
            <https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}> a dcat:Dataset ;
                dcat:keyword ?keyword .
        }}
        """.format(dataset_id=dataset_id,
        edition_id=edition_id
        )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result