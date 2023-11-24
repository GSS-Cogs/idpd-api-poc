sparql_queries = {
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
    "topics": """
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    CONSTRUCT WHERE {
        ?subject a ?type ;
            dcat:theme ?topics .
    }
    """,
    "versions": """
    PREFIX hydra: <http://www.w3.org/ns/hydra/core#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    CONSTRUCT WHERE {
        ?subject hydra:member ?versions .
        ?versions dcterms:issued ?issued ;
            dcterms:modified ?modified .
    }
    """,
}
