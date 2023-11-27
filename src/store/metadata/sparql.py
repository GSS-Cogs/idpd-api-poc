from typing import Dict, Optional

from rdflib import Graph
from rdflib.term import Identifier

from custom_logging import logger


def construct(
    query: str, graph: Graph, init_bindings: Optional[Dict[str, Identifier]] = None
) -> Graph:
    result = graph.query(query, initBindings=init_bindings).graph
    if len(result) == 0:
        logger.info(
            f"No results found for SPARQL query",
            data={"query": query, "init_bindings": init_bindings},
        )
    return result


SPARQL_QUERIES = {
    "contact_point": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcat:contactPoint ?contact_point .
            ?contact_point vcard:fn ?name ;
                vcard:hasEmail ?email .
        }
    """,
    "dataset": """
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ons: <https://data.ons.gov.uk/ns#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
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
                hydra:Collection ?editions_url .
        }
    """,
    "datasets": """
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {
            <https://staging.idpd.uk/datasets> a dcat:Catalog , hydra:Collection ; 
                dcat:DatasetSeries ?datasets ;
                hydra:offset ?offset ;
                hydra:totalitems ?count .
        }
    """,
    "edition": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX ons: <https://data.ons.gov.uk/ns#>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
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
        }
    """,
    "editions": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcterms:title ?title ;
                hydra:member ?editions .
            ?editions dcterms:issued ?issued ;
                dcterms:modified ?modified .
        }
    """,
    "keywords": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcat:keyword ?keywords .
        }
    """,
    "parent_topic": """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        CONSTRUCT WHERE {
            ?subject skos:broader ?parent_topic .
        }
    """,
    "publisher": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {
            ?subject a dcat:publisher;
                dcterms:title ?title;
                dcterms:description ?description;
                dcat:landingPage ?landingpage .
        }
    """,
    "publishers": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {
            <https://staging.idpd.uk/publishers> a hydra:Collection ;
                dcat:publisher ?publishers ;
                hydra:totalitems ?count ;
                hydra:offset ?offset .
        }
    """,
    "sub_topic": """
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        CONSTRUCT WHERE {
            ?subject skos:narrower ?sub_topic .
        }
    """,
    "table_schema": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX csvw: <https://www.w3.org/ns/csvw#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                csvw:schema ?table_schema .
            ?table_schema csvw:column ?columns .
            ?columns csvw:name ?name ;
                csvw:datatype ?datatype ;
                dcterms:description ?description ;
                csvw:titles ?titles .
        }
    """,
    "temporal_coverage": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcterms:temporal ?temporal_coverage .
            ?temporal_coverage dcat:startDate ?start_date ;
                dcat:endDate ?end_date .
        }
    """,
    "topic": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcterms:identifier ?identifier ;
                dcterms:title ?title ;
                dcterms:description ?description .
        }
    """,
    "topics": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcat:theme ?topics ;
                hydra:offset ?offset ;
                hydra:totalitems ?count .
        }
    """,
    "topic_uris": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcat:theme ?topics .
        }
    """,
    "summarised_version": """
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        CONSTRUCT WHERE {
            ?subject hydra:member ?versions .
            ?versions dcterms:issued ?issued ;
                dcterms:modified ?modified .
        }
    """,
    "version": """
        PREFIX dcat: <http://www.w3.org/ns/dcat#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX csvw: <https://www.w3.org/ns/csvw#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcterms:identifier ?identifier ;
                dcterms:title ?title ;
                dcterms:description ?description ;
                dcterms:abstract ?summary ;
                dcterms:issued ?release_date ;
                dcat:downloadUrl ?download_url ;
                dcterms:MediaType ?mediatype .
        }
    """,
    "versions": """
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
        CONSTRUCT WHERE {
            ?subject a ?type ;
                dcterms:title ?title ;
                hydra:member ?versions ;
                hydra:totalitems ?count ;
                hydra:offset ?offset .
        }
    """,
}
