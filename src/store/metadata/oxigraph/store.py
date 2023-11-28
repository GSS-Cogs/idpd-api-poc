import json
import os
import re
from typing import Dict, Optional

from pyld import jsonld
from rdflib import Dataset, Graph, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

from custom_logging import logger
from store.metadata.sparql import construct, SPARQL_QUERIES

from .. import constants
from ..base import BaseMetadataStore


class OxigraphMetadataStore(BaseMetadataStore):
    def setup(self):
        oxigraph_url = os.environ.get("GRAPH_DB_URL", None)
        assert oxigraph_url is not None, (
            "The env var 'GRAPH_DB_URL' must be set to use "
            "the OxigraphMetadataStore store."
        )
        configuration = (f"{oxigraph_url}/query", f"{oxigraph_url}/update")
        self.db = Dataset(store=SPARQLUpdateStore(*configuration))

    def get_datasets(self) -> Optional[Dict]:
        """
        Gets all datasets
        """
        logger.info("Constructing get_datasets() response from graph")

        # Populate the graph from the database
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = construct(SPARQL_QUERIES["datasets"], graph)

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

    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """
        Get a dataset by its ID and return its metadata as a JSON-LD dict.
        """
        logger.info(
            "Constructing get_dataset() response from graph",
            data={"dataset_id": dataset_id},
        )

        # Populate the graph from the database
        graph = self.db

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(f"https://staging.idpd.uk/datasets/{dataset_id}"),
            "type": URIRef("http://www.w3.org/ns/dcat#DatasetSeries"),
        }

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        # TODO: incorporate `keywords` and `topics` into the `sparql_queries["dataset"]` query?
        result: Graph = (
            construct(SPARQL_QUERIES["dataset"], graph, init_bindings)
            + construct(SPARQL_QUERIES["keywords"], graph, init_bindings)
            + construct(SPARQL_QUERIES["topic_uris"], graph, init_bindings)
            + construct(SPARQL_QUERIES["contact_point"], graph, init_bindings)
            + construct(SPARQL_QUERIES["temporal_coverage"], graph, init_bindings)
            + construct(SPARQL_QUERIES["editions"], graph, init_bindings)
        )
        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:DatasetSeries"}
        )

        # Extract default graph and blank node graphs from flattened json-ld data
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

    def get_editions(self, dataset_id: str) -> Optional[Dict]:
        """
        Gets all editions of a specific dataset with ID `dataset_id`
        """
        logger.info(
            "Constructing get_editions() response from graph",
            data={"dataset_id": dataset_id},
        )

        # Populate the graph from the database
        graph = self.db

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(
                f"https://staging.idpd.uk/datasets/{dataset_id}/editions"
            ),
            "type": URIRef("http://www.w3.org/ns/hydra/core#Collection"),
        }

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = construct(SPARQL_QUERIES["editions"], graph, init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        editions_graph = _get_single_graph_for_field(data, "@type")
        if editions_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url` and `editions` to `versions`
        editions_graph["@type"] = "hydra:Collection"
        editions_graph["editions"] = editions_graph.pop("versions")

        editions_graph["editions"] = [
            self.get_edition(dataset_id, x.split("/")[-1])
            for x in editions_graph["editions"]
        ]

        # TODO Update @context so it's not hardcoded
        editions_graph = {"@context": "https://staging.idpd.uk/ns#", **editions_graph}
        return editions_graph

    def get_edition(self, dataset_id: str, edition_id: str) -> Optional[Dict]:
        """
        Gets a specific edition with ID `edition_id` of a specific dataset with ID `dataset_id`
        """
        logger.info(
            "Constructing get_edition() response from graph",
            data={"dataset_id": dataset_id, "edition_id": edition_id},
        )

        # Populate the graph from the database
        graph = self.db

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(
                f"https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}"
            ),
            "type": URIRef("http://www.w3.org/ns/dcat#Dataset"),
        }

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = (
            construct(SPARQL_QUERIES["edition"], graph, init_bindings)
            + construct(SPARQL_QUERIES["contact_point"], graph, init_bindings)
            + construct(SPARQL_QUERIES["topic_uris"], graph, init_bindings)
            + construct(SPARQL_QUERIES["keywords"], graph, init_bindings)
            + construct(SPARQL_QUERIES["temporal_coverage"], graph, init_bindings)
            + construct(SPARQL_QUERIES["table_schema"], graph, init_bindings)
            + construct(SPARQL_QUERIES["summarised_version"], graph, init_bindings)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:Dataset"}
        )

        # Extract default graph and blank node graphs from flattened json-ld data
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

    def get_versions(self, dataset_id: str, edition_id: str) -> Optional[Dict]:
        """
        Gets all versions of a specific edition of a specific dataset
        """
        logger.info(
            "Constructing get_versions() response from graph",
            data={"dataset_id": dataset_id, "edition_id": edition_id},
        )
        # Populate the graph from the database
        graph = self.db

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(
                f"https://staging.idpd.uk/datasets/{dataset_id}/editions/{edition_id}/versions"
            ),
            "type": URIRef("http://www.w3.org/ns/hydra/core#Collection"),
        }

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = construct(SPARQL_QUERIES["versions"], graph, init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        versions_graph = _get_single_graph_for_field(data, "@type")
        if versions_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url`
        versions_graph["@type"] = "hydra:Collection"

        versions_graph["versions"] = [
            self.get_version(dataset_id, edition_id, x.split("/")[-1])
            for x in versions_graph["versions"]
        ]

        # TODO Update @context so it's not hardcoded
        versions_graph = {"@context": "https://staging.idpd.uk/ns#", **versions_graph}
        return versions_graph

    def get_version(
        self, dataset_id: str, edition_id: str, version_id: str
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
        )

        # Specify the named graph from which we are fetching data
        graph = self.db

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

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a sinlge Graph of the
        # data we need.
        result: Graph = construct(
            SPARQL_QUERIES["version"], graph, init_bindings
        ) + construct(SPARQL_QUERIES["table_schema"], graph, init_bindings)

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

    def get_publishers(self) -> Optional[Dict]:
        """
        Gets all publishers
        """
        logger.info("Constructing get_publishers() response from graph")

        # Specify the named graph from which we are fetching data
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = construct(SPARQL_QUERIES["publishers"], graph)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )

        publishers_graph = _get_single_graph_for_field(data, "@type")
        if publishers_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url`,
        publishers_graph["@type"] = "hydra:Collection"
        publishers_graph["publishers"] = publishers_graph.pop("dcat:publisher")

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

    def get_publisher(self, publisher_id: str) -> Optional[Dict]:
        """
        Get a specific publisher
        """
        logger.info(
            "Constructing get_publisher() response from graph",
            data={"publisher_id": publisher_id},
        )

        # Specify the named graph from which we are fetching data
        graph = self.db

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(f"https://staging.idpd.uk/publishers/{publisher_id}"),
        }

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = construct(SPARQL_QUERIES["publisher"], graph, init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:publisher"}
        )
        publisher_graph = _get_single_graph_for_field(data, "@type")
        if publisher_graph is None:
            return None

        # TODO Update @context so it's not hardcoded
        publisher_graph = {"@context": "https://staging.idpd.uk/ns#", **publisher_graph}
        return publisher_graph

    def get_topics(self) -> Optional[Dict]:
        """
        Get all topics
        """
        logger.info("Constructing get_topics() response from graph")

        # Populate the graph from the database
        graph = self.db

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(f"https://staging.idpd.uk/topics"),
            "type": URIRef("http://www.w3.org/ns/hydra/core#Collection"),
        }

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = construct(SPARQL_QUERIES["topics"], graph, init_bindings)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        topics_graph = _get_single_graph_for_field(data, "@type")
        if topics_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `versions_url`
        topics_graph["@type"] = "hydra:Collection"

        topics_graph["topics"] = [
            self.get_topic(topic["@id"].split("/")[-1])
            for topic in topics_graph["topics"]
        ]

        # TODO Update @context so it's not hardcoded
        topics_graph = {"@context": "https://staging.idpd.uk/ns#", **topics_graph}
        return topics_graph

    def get_topic(self, topic_id: str) -> Optional[Dict]:
        """
        Get a specific topic by topic_id
        """
        logger.info(
            "Constructing get_topic() response from graph", data={"topic_id": topic_id}
        )

        # Populate the graph from the database
        graph = self.db

        # Define initBindings for SPARQL query
        init_bindings = {
            "subject": URIRef(f"https://staging.idpd.uk/topics/{topic_id}"),
            "type": URIRef("http://www.w3.org/ns/dcat#theme"),
        }

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = (
            construct(SPARQL_QUERIES["topic"], graph, init_bindings)
            + construct(SPARQL_QUERIES["sub_topic"], graph, init_bindings)
            + construct(SPARQL_QUERIES["parent_topic"], graph, init_bindings)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:theme"}
        )
        topic_graph = _get_single_graph_for_field(data, "@type")
        if topic_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing `@type` to `themes`
        topic_graph["@type"] = "dcat:theme"

        # TODO Update @context so it's not hardcoded
        topic_graph = {"@context": "https://staging.idpd.uk/ns#", **topic_graph}
        return topic_graph

    def get_sub_topics(self, topic_id: str) -> Optional[Dict]:
        """
        Get all sub-topics for a specific topic
        """
        logger.info(
            "Constructing get_sub_topics() response from graph",
            data={"topic_id": topic_id},
        )

        all_topics = self.get_topics()
        topics_with_parents = [
            topic
            for topic in all_topics["topics"]
            if topic.get("parent_topics", None) is not None
        ]
        sub_topics = [
            topic
            for topic in topics_with_parents
            if any([x.endswith(topic_id) for x in topic["parent_topics"]])
        ]

        if len(sub_topics) == 0:
            return None

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
