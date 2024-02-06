import json
import os
import re
from typing import Dict, Optional

from pyld import jsonld
from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

from custom_logging import configure_logger, logger
from store.metadata.sparql import SparqlQueries

from .. import constants
from ..base import BaseMetadataStore

configure_logger()


class OxigraphMetadataStore(BaseMetadataStore):
    def setup(self):
        oxigraph_url = os.environ.get("GRAPH_DB_URL", None)

        assert oxigraph_url is not None, (
            "The env var 'GRAPH_DB_URL' must be set to use "
            "the OxigraphMetadataStore store."
        )
        configuration = (f"{oxigraph_url}/query", f"{oxigraph_url}/update")
        self.db = Dataset(store=SPARQLUpdateStore(*configuration))
        self.sparql_queries = SparqlQueries(self.db)

    def get_datasets(self, request_id: Optional[str] = None) -> Optional[Dict]:
        """
        Gets all datasets
        """
        logger.info(
            "Constructing get_datasets() response from graph",
            request_id=request_id,
        )

        # Extract RDF triples from the database as one Graph
        result: Graph = self.sparql_queries.datasets()

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data,
            {
                "@context": constants.CONTEXT,
                "@type": ["dcat:Catalog", "hydra:Collection"],
            },
        )
        # Extract datasets graph from flattened json-ld data
        datasets_graph = _get_single_graph_for_field(data, "@type")
        if datasets_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url'
        datasets_graph["@type"] = ["dcat:Catalog", "hydra:Collection"]

        # Get dataset results for each dataset in `datasets`
        datasets_graph["datasets"] = [
            self.get_dataset(dataset["@id"].split("/")[-1])
            for dataset in datasets_graph["dcat:DatasetSeries"]
        ]
        # TODO Fix context weirdness - at the moment, the flatten() method is changing `datasets` to `dcat:DatasetSeries'
        del datasets_graph["dcat:DatasetSeries"]

        # TODO Update @context so it's not hardcoded
        datasets_graph = {"@context": "https://staging.idpd.uk/ns#", **datasets_graph}
        return datasets_graph

    def get_dataset(
        self, dataset_id: str, request_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get a dataset by its ID and return its metadata as a JSON-LD dict.
        """
        logger.info(
            "Constructing get_dataset() response from graph",
            data={"dataset_id": dataset_id},
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(f"https://staging.idpd.uk/datasets/{dataset_id}"),
            "type": URIRef("http://www.w3.org/ns/dcat#DatasetSeries"),
        }

        # Extract RDF triples from the database as one Graph
        # TODO: incorporate `keywords` and `topics` into the `sparql_queries.dataset` query?
        result: Graph = (
            self.sparql_queries.dataset(init_bindings)
            + self.sparql_queries.keywords(init_bindings)
            + self.sparql_queries.topic_uris(init_bindings)
            + self.sparql_queries.contact_point(init_bindings)
            + self.sparql_queries.temporal_coverage(init_bindings)
            + self.sparql_queries.editions(init_bindings)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:DatasetSeries"}
        )

        # Extract dataset graph and blank node graphs from flattened json-ld data
        dataset_graph = _get_single_graph_for_field(data, "@type")
        contact_point_graph = _get_single_graph_for_field(data, "vcard:fn")
        temporal_coverage_graph = _get_single_graph_for_field(data, "dcat:endDate")
        if None in [dataset_graph, contact_point_graph, temporal_coverage_graph]:
            return None

        # Add `issued` and `modified` fields to each edition in `editions`
        edition_graphs = [
            x
            for x in data["@graph"]
            if "@id" in x.keys() and re.search("/editions/", x["@id"])
        ]
        dataset_graph["editions"] = edition_graphs

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `editions` to `versions'
        del dataset_graph["versions"]

        # The user doesnt need to know about blank RDF nodes so we need
        # to flatten and embed these graphs into the dataset graph.
        dataset_graph["contact_point"] = {
            "name": contact_point_graph["vcard:fn"]["@value"],
            "email": contact_point_graph["vcard:hasEmail"],
        }
        dataset_graph["temporal_coverage"] = {
            "start": temporal_coverage_graph["dcat:endDate"]["@value"],
            "end": temporal_coverage_graph["dcat:startDate"]["@value"],
        }

        # TODO Update @context so it's not hardcoded
        dataset_graph = {"@context": "https://staging.idpd.uk/ns#", **dataset_graph}
        return dataset_graph

    def get_editions(
        self, dataset_id: str, request_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Gets all editions of a specific dataset with ID `dataset_id`
        """
        logger.info(
            "Constructing get_editions() response from graph",
            data={"dataset_id": dataset_id},
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(
                f"https://staging.idpd.uk/datasets/{dataset_id}/editions"
            ),
            "type": URIRef("http://www.w3.org/ns/hydra/core#Collection"),
        }

        # Extract RDF triples from the database as one Graph
        result: Graph = self.sparql_queries.editions(init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )

        # Extract editions graph from flattened json-ld data
        editions_graph = _get_single_graph_for_field(data, "@type")
        if editions_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url` and `editions` to `versions`
        editions_graph["@type"] = "hydra:Collection"
        editions_graph["editions"] = editions_graph.pop("versions")

        # Populate metadata for each edition in `editions`
        editions_graph["editions"] = [
            self.get_edition(dataset_id, x.split("/")[-1])
            for x in editions_graph["editions"]
        ]

        # TODO Update @context so it's not hardcoded
        editions_graph = {"@context": "https://staging.idpd.uk/ns#", **editions_graph}
        return editions_graph

    def get_edition(
        self, dataset_id: str, edition_id: str, request_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Gets a specific edition with ID `edition_id` of a specific dataset with ID `dataset_id`
        """
        logger.info(
            "Constructing get_edition() response from graph",
            data={"dataset_id": dataset_id, "edition_id": edition_id},
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(
                f"https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}"
            ),
            "type": URIRef("http://www.w3.org/ns/dcat#Dataset"),
        }

        # Extract RDF triples from the database as one Graph
        result: Graph = (
            self.sparql_queries.edition(init_bindings)
            + self.sparql_queries.contact_point(init_bindings)
            + self.sparql_queries.topic_uris(init_bindings)
            + self.sparql_queries.keywords(init_bindings)
            + self.sparql_queries.temporal_coverage(init_bindings)
            + self.sparql_queries.table_schema(init_bindings)
            + self.sparql_queries.summarised_version(init_bindings)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:Dataset"}
        )

        # Extract edition graph and blank node graphs from flattened json-ld data
        edition_graph = _get_single_graph_for_field(data, "@type")
        contact_point_graph = _get_single_graph_for_field(data, "vcard:fn")
        temporal_coverage_graph = _get_single_graph_for_field(data, "dcat:endDate")
        columns_graph = [x for x in data["@graph"] if "datatype" in x.keys()]
        if None in [edition_graph, contact_point_graph, temporal_coverage_graph]:
            return None

        # Populate editions_graph.table_schema.columns with column definitions (without `@id`) and delete editions_graph.table_schema blank node `@id`
        for column in columns_graph:
            del column["@id"]
        edition_graph["table_schema"]["columns"] = columns_graph
        del edition_graph["table_schema"]["@id"]

        # The user doesnt need to know about blank RDF nodes so we need
        # to flatten and embed these graphs into the primary graph.
        edition_graph["contact_point"] = {
            "name": contact_point_graph["vcard:fn"]["@value"],
            "email": contact_point_graph["vcard:hasEmail"],
        }
        edition_graph["temporal_coverage"] = {
            "start": temporal_coverage_graph["dcat:startDate"]["@value"],
            "end": temporal_coverage_graph["dcat:endDate"]["@value"],
        }

        # Add `issued` and `modified` fields to each version in `versions`
        version_graphs = [
            x
            for x in data["@graph"]
            if "@id" in x.keys() and re.search("/versions/", x["@id"])
        ]
        edition_graph["versions"] = version_graphs

        # TODO Update @context so it's not hardcoded
        edition_graph = {"@context": "https://staging.idpd.uk/ns#", **edition_graph}
        return edition_graph

    def get_versions(
        self, dataset_id: str, edition_id: str, request_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Gets all versions of a specific edition of a specific dataset
        """
        logger.info(
            "Constructing get_versions() response from graph",
            data={"dataset_id": dataset_id, "edition_id": edition_id},
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(
                f"https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions"
            ),
            "type": URIRef("http://www.w3.org/ns/hydra/core#Collection"),
        }

        # Extract RDF triples from the database as one Graph
        result: Graph = self.sparql_queries.versions(init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        # Extract versions graph from flattened json-ld data
        versions_graph = _get_single_graph_for_field(data, "@type")
        if versions_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url`
        versions_graph["@type"] = "hydra:Collection"

        # Populate metadata for each version in `versions`
        versions_graph["versions"] = [
            self.get_version(dataset_id, edition_id, x.split("/")[-1])
            for x in versions_graph["versions"]
        ]

        # TODO Update @context so it's not hardcoded
        versions_graph = {"@context": "https://staging.idpd.uk/ns#", **versions_graph}
        return versions_graph

    def get_version(
        self,
        dataset_id: str,
        edition_id: str,
        version_id: str,
        request_id: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Gets a specific version of a specific edition of a specific dataset
        """
        logger.info(
            "Constructing get_version() response from graph",
            data={
                "dataset_id": dataset_id,
                "edition_id": edition_id,
                "version_id": version_id,
            },
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        # TODO How to represent multiple objects for `type`?
        init_bindings = {
            "subject": URIRef(
                f"https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}"
            ),
            # "type": [
            #     URIRef("http://www.w3.org/ns/dcat#Distribution"),
            #     URIRef("https://www.w3.org/ns/csvw#Table"),
            # ],
        }

        # Extract RDF triples from the database as one Graph
        result: Graph = self.sparql_queries.version(
            init_bindings
        ) + self.sparql_queries.table_schema(init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data,
            {
                "@context": constants.CONTEXT,
                "@type": ["csvw:Table", "dcat:Distribution"],
            },
        )
        # Extract version graph from flattened json-ld data
        version_graph = _get_single_graph_for_field(data, "@type")
        if version_graph is None:
            return None

        # The user doesnt need to know about blank RDF nodes so we need
        # to flatten and embed these graphs into the version graph.
        columns_graph = [x for x in data["@graph"] if "datatype" in x.keys()]
        for column in columns_graph:
            del column["@id"]
        version_graph["table_schema"]["columns"] = columns_graph
        del version_graph["table_schema"]["@id"]

        # TODO Update @context so it's not hardcoded
        version_graph = {"@context": "https://staging.idpd.uk/ns#", **version_graph}
        return version_graph

    def get_publishers(self, request_id: Optional[str] = None) -> Optional[Dict]:
        """
        Gets all publishers
        """
        logger.info(
            "Constructing get_publishers() response from graph",
            request_id=request_id,
        )

        # Extract RDF triples from the database as one Graph
        result: Graph = self.sparql_queries.publishers()

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        # Extract publishers graph from flattened json-ld data
        publishers_graph = _get_single_graph_for_field(data, "@type")
        if publishers_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url`,
        publishers_graph["@type"] = "hydra:Collection"
        publishers_graph["publishers"] = publishers_graph.pop("dcat:publisher")

        # Populate metadata for each publisher in `publishers`
        publishers_graph["publishers"] = [
            self.get_publisher(x["@id"].split("/")[-1])
            for x in publishers_graph["publishers"]
        ]

        # TODO Update @context so it's not hardcoded
        publishers_graph = {
            "@context": "https://staging.idpd.uk/ns#",
            **publishers_graph,
        }
        return publishers_graph

    def get_publisher(
        self, publisher_id: str, request_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get a specific publisher
        """
        logger.info(
            "Constructing get_publisher() response from graph",
            data={"publisher_id": publisher_id},
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(f"https://staging.idpd.uk/publishers/{publisher_id}"),
        }

        # Extract RDF triples from the database as one Graph
        result: Graph = self.sparql_queries.publisher(init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:publisher"}
        )
        # Extract publisher graph from flattened json-ld data
        publisher_graph = _get_single_graph_for_field(data, "@type")
        if publisher_graph is None:
            return None

        # TODO Update @context so it's not hardcoded
        publisher_graph = {"@context": "https://staging.idpd.uk/ns#", **publisher_graph}
        return publisher_graph

    def get_topics(self, request_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get all topics
        """
        logger.info(
            "Constructing get_topics() response from graph",
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef("https://staging.idpd.uk/topics"),
            "type": URIRef("http://www.w3.org/ns/hydra/core#Collection"),
        }

        # Extract RDF triples from the database as one Graph
        result: Graph = self.sparql_queries.topics(init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        # Extract topics graph from flattened json-ld data
        topics_graph = _get_single_graph_for_field(data, "@type")
        if topics_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url`
        topics_graph["@type"] = "hydra:Collection"

        # Populate metadata for each topic in `topics`
        topics_graph["topics"] = [
            self.get_topic(topic["@id"].split("/")[-1])
            for topic in topics_graph["topics"]
        ]

        # TODO Update @context so it's not hardcoded
        topics_graph = {"@context": "https://staging.idpd.uk/ns#", **topics_graph}
        return topics_graph

    def get_topic(
        self, topic_id: str, request_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get a specific topic by topic_id
        """
        logger.info(
            "Constructing get_topic() response from graph",
            data={"topic_id": topic_id},
            request_id=request_id,
        )

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(f"https://staging.idpd.uk/topics/{topic_id}"),
            "type": URIRef("http://www.w3.org/ns/dcat#theme"),
        }

        # Extract RDF triples from the database as one Graph
        result: Graph = (
            self.sparql_queries.topic(init_bindings)
            + self.sparql_queries.sub_topic(init_bindings)
            + self.sparql_queries.parent_topic(init_bindings)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:theme"}
        )
        # Extract topic graph from flattened json-ld data
        topic_graph = _get_single_graph_for_field(data, "@type")
        if topic_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `themes`
        topic_graph["@type"] = "dcat:theme"

        # TODO Update @context so it's not hardcoded
        topic_graph = {"@context": "https://staging.idpd.uk/ns#", **topic_graph}
        return topic_graph

    def get_sub_topics(
        self, topic_id: str, request_id: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get all sub-topics for a specific topic
        """
        logger.info(
            "Constructing get_sub_topics() response from graph",
            data={"topic_id": topic_id},
            request_id=request_id,
        )

        # Get all topics
        all_topics = self.get_topics()

        # Extract topics which have a parent topic defined
        topics_with_parents = [
            topic
            for topic in all_topics["topics"]
            if topic.get("parent_topics", None) is not None
        ]

        # Get the subtopics associated with a parent topic with ID `topic_id`
        sub_topics = [
            topic
            for topic in topics_with_parents
            if any([x.endswith(topic_id) for x in topic["parent_topics"]])
        ]

        # If the topic with ID `topic_id` has no subtopics, return None
        if len(sub_topics) == 0:
            return None

        # Otherwise, return a dictionary matching the Topics schema
        return {
            "@context": "https://staging.idpd.uk/ns#",
            "@id": f"https://staging.idpd.uk/topics/{topic_id}/subtopics",
            "@type": "hydra:Collection",
            "topics": sub_topics,
            "count": len(sub_topics),
            "offset": 0,
        }


def _get_single_graph_for_field(data: Dict, field: str) -> Optional[Dict]:
    """
    Utility function to get the dictionary corresponding to the `field` key provided. Only for SPARQL queries that should return one result.
    """
    node = [x for x in data["@graph"] if field in x.keys()]
    if len(node) == 1:
        return node[0]
    elif len(node) == 0:
        logger.error("No node for field defined", data={"field": field, "jsonld": data})
        return None
    else:
        logger.error(
            "More than one node for field defined",
            data={"field": field, "jsonld": data},
        )
        return None
