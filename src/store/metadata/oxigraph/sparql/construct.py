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

def construct_dataset_version(graph: Graph, dataset_id: str, edition_id: str, version_id: str) -> Graph:
    query = """
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        PREFIX csvw: <http://www.w3.org/ns/csvw#>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {{
        <http://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}> a hydra:member ;
        dcterms:identifier ?identifier ;
        dcterms:title ?title ;
        dcterms:description ?description ;
        dcterms:abstract ?summary ;
        dcterms:issued ?release_date ;
        dcat:download_url ?download_url ;
        csvw:schema ?table_schema .
        }}
        """.format(
        dataset_id=dataset_id,
        edition_id=edition_id,
        version_id=version_id
    )

    results_graph = graph.query(query).graph
    result = results_graph if results_graph else Graph()
    return result