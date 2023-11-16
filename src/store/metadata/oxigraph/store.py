import json
import os
import re
from typing import Dict, Optional
from custom_logging import logger

from pyld import jsonld
from rdflib import Dataset, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

from .. import constants
from ..base import BaseMetadataStore
from .sparql.construct import (
    construct_dataset_contact_point,
    construct_dataset_core,
    construct_dataset_keywords,
    construct_dataset_themes,
    construct_dataset_parent_topics_by_id,
    construct_dataset_subtopics_by_id,
    construct_dataset_temporal_coverage,
    construct_dataset_editions,
    construct_dataset_topic_by_id,
    construct_dataset_topics,
    construct_edition_contact_point,
    construct_edition_core,
    construct_edition_keywords,
    construct_edition_table_schema,
    construct_edition_temporal_coverage,
    construct_edition_topics,
    construct_edition_versions,
    construct_editions,
    construct_publisher,
    construct_dataset_version,
    construct_dataset_version_table_schema,
)
from custom_logging import logger


class OxigraphMetadataStore(BaseMetadataStore):
    def setup(self):
        oxigraph_url = os.environ.get("GRAPH_DB_URL", None)
        assert oxigraph_url is not None, (
            "The env var 'GRAPH_DB_URL' must be set to use "
            "the OxigraphMetadataStore store."
        )
        configuration = (f"{oxigraph_url}/query", f"{oxigraph_url}/update")
        self.db = Dataset(store=SPARQLUpdateStore(*configuration))

    def get_datasets(self) -> Optional[Dict]:  # pragma: no cover
        """
        Gets all datasets
        """
        raise NotImplementedError

    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """
        Get a dataset by its ID and return its metadata as a JSON-LD dict.
        """

        # Specify the named graph from which we are fetching data
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a sinlge Graph of the
        # data we need.
        result: Graph = (
            construct_dataset_core(graph, dataset_id)
            + construct_dataset_keywords(graph, dataset_id)
            + construct_dataset_themes(graph, dataset_id)
            + construct_dataset_contact_point(graph, dataset_id)
            + construct_dataset_temporal_coverage(graph, dataset_id)
            + construct_dataset_editions(graph, dataset_id)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:DatasetSeries"}
        )
        # At this point our jonsld has a "@graph" list field with three entries in it
        #
        # - the dataset graph in compact form
        # - an anonymous (blank root node) graph of contacts in long form
        # - an anonymous (blank root node) graph of temporal coverage in long form
        #
        # The user doesnt need to know about blank RDF nodes so we need
        # to flatten and embed the latter two graphs in the dataset graph.
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

        # Compact and embed anonymous nodes
        dataset_graph["contact_point"] = {
            "name": contact_point_graph["vcard:fn"]["@value"],
            "email": contact_point_graph["vcard:hasEmail"],
        }
        dataset_graph["temporal_coverage"] = {
            "start": temporal_coverage_graph["dcat:endDate"]["@value"],
            "end": temporal_coverage_graph["dcat:startDate"]["@value"],
        }
        return dataset_graph

    def get_editions(self, dataset_id: str) -> Optional[Dict]:  # pragma: no cover
        """
        Gets all editions of a specific dataset
        """
        # Populate the graph from the database
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = construct_editions(graph, dataset_id)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        editions_graph = _get_single_graph_for_field(data, "@type")
        if editions_graph is None:
            return None

        # TODO Fix context weirdness - at the moment, the flatten() method is changing @type to `versions_url` and `editions` to `versions`
        editions_graph["@type"] = "hydra:Collection"
        editions_graph["editions"] = editions_graph.pop("versions")

        editions_graph["editions"] = [
            self.get_edition(dataset_id, x.split("/")[-1])
            for x in editions_graph["editions"]
        ]
        editions_graph["@context"] = "https://staging.idpd.uk/ns#"
        return editions_graph

    def get_edition(
        self, dataset_id: str, edition_id: str
    ) -> Optional[Dict]:  # pragma: no cover
        """
        Gets a specific edition of a specific dataset
        """
        # Populate the graph from the database
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = (
            construct_edition_core(graph, dataset_id, edition_id)
            + construct_edition_contact_point(graph, dataset_id, edition_id)
            + construct_edition_topics(graph, dataset_id, edition_id)
            + construct_edition_keywords(graph, dataset_id, edition_id)
            + construct_edition_temporal_coverage(graph, dataset_id, edition_id)
            + construct_edition_table_schema(graph, dataset_id, edition_id)
            + construct_edition_versions(graph, dataset_id, edition_id)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:Dataset"}
        )

        edition_graph = _get_single_graph_for_field(data, "@type")
        contact_point_graph = _get_single_graph_for_field(data, "vcard:fn")
        temporal_coverage_graph = _get_single_graph_for_field(data, "dcat:endDate")
        columns_graph = [x for x in data["@graph"] if "datatype" in x.keys()]
        if None in [edition_graph, contact_point_graph, temporal_coverage_graph]:
            return None

        # Populate editions_graph.table_schema.columns with column definitions (without @id) and delete editions_graph.table_schema blank node @id
        for column in columns_graph:
            del column["@id"]
        edition_graph["table_schema"]["columns"] = columns_graph
        del edition_graph["table_schema"]["@id"]

        edition_graph["contact_point"] = {
            "name": contact_point_graph["vcard:fn"]["@value"],
            "email": contact_point_graph["vcard:hasEmail"],
        }
        edition_graph["temporal_coverage"] = {
            "start": temporal_coverage_graph["dcat:startDate"]["@value"],
            "end": temporal_coverage_graph["dcat:endDate"]["@value"],
        }

        version_graphs = [
            x
            for x in data["@graph"]
            if "@id" in x.keys() and re.search("/versions/", x["@id"])
        ]
        edition_graph["versions"] = version_graphs

        return edition_graph

    def get_versions(
        self, dataset_id: str, edition_id: str
    ) -> Optional[Dict]:  # pragma: no cover
        """
        Gets all versions of a specific edition of a specific dataset
        """

    def get_version(
        self, dataset_id: str, edition_id: str, version_id: str
    ) -> Optional[Dict]:  # pragma: no cover
        """
        Gets a specific version of a specific edition of a specific dataset
        """
        # Specify the named graph from which we are fetching data
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a sinlge Graph of the
        # data we need.
        result: Graph = construct_dataset_version(
            graph, dataset_id, edition_id, version_id
        ) + construct_dataset_version_table_schema(
            graph, dataset_id, edition_id, version_id
        )

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
        columns_graph = [x for x in data["@graph"] if "datatype" in x.keys()]
        for column in columns_graph:
            del column["@id"]
        version_graph["table_schema"]["columns"] = columns_graph
        del version_graph["table_schema"]["@id"]

        return version_graph

    def get_publishers(self) -> Optional[Dict]:  # pragma: no cover
        """
        Gets all publishers
        """
        raise NotImplementedError

    def get_publisher(self, publisher_id: str) -> Optional[Dict]:  # pragma: no cover
        """
        Get a specific publisher
        """
        # Specify the named graph from which we are fetching data
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a sinlge Graph of the
        # data we need.
        result: Graph = construct_publisher(graph, publisher_id)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:publisher"}
        )

        return data["@graph"][0]

    def get_topics(self) -> Optional[Dict]:  # pragma: no cover
        """
        Get all topics
        """
        graph = self.db

        result: Graph = construct_dataset_topics(graph)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )
        # TODO Fix context weirdness - at the moment, the flatten() method is changing @type to `versions_url`
        data["@graph"][0]["@type"] = "hydra:Collection"

        for idx, topic in enumerate(data["@graph"][0]["topics"]):
            topic_id = topic["@id"].split("/")[-1]
            data["@graph"][0]["topics"][idx] = self.get_topic(topic_id)

        # TODO Update @context so it's not hardcoded
        data["@graph"][0]["@context"] = "https://staging.idpd.uk/ns#"
        result = data["@graph"][0]
        return result

    def get_topic(self, topic_id: str) -> Optional[Dict]:
        """
        Get a specific topic by topic_id
        """
        # Populate the graph from the database
        graph = self.db

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a single Graph of the
        # data we need.
        result: Graph = (
            construct_dataset_topic_by_id(graph, topic_id)
            + construct_dataset_subtopics_by_id(graph, topic_id)
            + construct_dataset_parent_topics_by_id(graph, topic_id)
        )

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "dcat:theme"}
        )

        # TODO Fix context weirdness - at the moment, the flatten() method is changing @type to `themes`
        data["@graph"][0]["@type"] = "dcat:theme"
        result = data["@graph"][0]
        return result

    def get_sub_topics(self, topic_id: str) -> Optional[Dict]:  # pragma: no cover
        """
        Get all sub-topics for a specific topic
        """
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

    def get_sub_topic(
        self, topic_id: str, sub_topic_id: str
    ) -> Optional[Dict]:  # pragma: no cover
        """
        Get a specific sub-topic for a specific topic
        """
        raise NotImplementedError


def _get_single_graph_for_field(data: Dict, field: str) -> Optional[Dict]:
    """
    Utility function to get the dictionary corresponding to the `field` key provided. Only for SPARQL queries that should return one result.
    """
    node = [x for x in data["@graph"] if field in x.keys()]
    if len(node) == 1:
        return node[0]
    elif len(node) == 0:
        logger.error("No node for field defined", data={"field": field})
        return None
    else:
        logger.error("More than one node for field defined", data={"field": field})
        return None
