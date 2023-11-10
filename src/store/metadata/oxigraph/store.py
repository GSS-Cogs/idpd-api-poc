import json
import os
from typing import Dict, Optional

from pyld import jsonld
from rdflib import Dataset, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore

from .. import constants
from ..base import BaseMetadataStore
from .sparql.construct import (
    construct_dataset_contact_point,
    construct_dataset_core,
    construct_dataset_keywords,
    construct_dataset_parent_topics_by_id,
    construct_dataset_subtopics_by_id,
    construct_dataset_temporal_coverage,
    construct_dataset_topic_by_id,
    construct_dataset_topics,
    construct_publisher,
    construct_datasets,
)


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
        graph = self.db

        result: Graph = construct_datasets(graph)

        # Serialize the graph into jsonld
        data = json.loads(result.serialize(format="json-ld"))

        # Use a context file to shape our jsonld, removing long form references
        data = jsonld.flatten(
            data, {"@context": constants.CONTEXT, "@type": "hydra:Collection"}
        )

        for idx, topic in enumerate(data["@graph"][0]["topics"]):
            topic_id = topic["@id"].split("/")[-1]
            data["@graph"][0]["topics"][idx] = self.get_topic(topic_id)

        # TODO Update @context so it's not hardcoded
        data["@graph"][0]["@context"] = "https://staging.idpd.uk/#ns"
        result = data["@graph"][0]
        return result

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
            construct_dataset_core(graph)
            + construct_dataset_keywords(graph)
            + construct_dataset_topics(graph)
            + construct_dataset_contact_point(graph)
            + construct_dataset_temporal_coverage(graph)
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
        dataset_graph = next((x for x in data["@graph"] if "@type" in x.keys()), None)
        contact_point_graph = next(
            (x for x in data["@graph"] if "vcard:fn" in x.keys()), None
        )
        temporal_coverage_graph = next(
            (x for x in data["@graph"] if "dcat:endDate" in x.keys()), None
        )

        # Compact and embed anonymous nodes
        # TODO - we'll want to make sure these fields exist
        # to avoid key errors.
        dataset_graph["contact_point"] = {
            "name": contact_point_graph["vcard:fn"]["@value"],
            "email": contact_point_graph["vcard:hasEmail"],
        }
        dataset_graph["temporal_coverage"] = {
            "start": temporal_coverage_graph["dcat:endDate"]["@value"],
            "end": temporal_coverage_graph["dcat:startDate"]["@value"],
        }

        # Use a remote context
        dataset_graph["@context"] = "https://data.ons.gov.uk/ns#"

        return dataset_graph

    def get_editions(self, dataset_id: str) -> Optional[Dict]:  # pragma: no cover
        """
        Gets all editions of a specific dataset
        """
        raise NotImplementedError

    def get_edition(
        self, dataset_id: str, edition_id: str
    ) -> Optional[Dict]:  # pragma: no cover
        """
        Gets a specific edition of a specific dataset
        """
        raise NotImplementedError

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
        raise NotImplementedError

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

        for idx, topic in enumerate(data["@graph"][0]["topics"]):
            topic_id = topic["@id"].split("/")[-1]
            data["@graph"][0]["topics"][idx] = self.get_topic(topic_id)

        # TODO Update @context so it's not hardcoded
        data["@graph"][0]["@context"] = "https://staging.idpd.uk/#ns"
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

        # Workaround to replace `themes` with `dcat:theme` in `@type`
        data["@graph"][0]["@type"] = "dcat:theme"
        result = data["@graph"][0]
        return result

    def get_sub_topics(self, topic_id: str) -> Optional[Dict]:  # pragma: no cover
        """
        Get all sub-topics for a specific topic
        """
        raise NotImplementedError

    def get_sub_topic(
        self, topic_id: str, sub_topic_id: str
    ) -> Optional[Dict]:  # pragma: no cover
        """
        Get a specific sub-topic for a specific topic
        """
        raise NotImplementedError
