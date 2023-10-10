import os
import json
from typing import Dict, Optional

from pyld import jsonld
from rdflib import Dataset, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib import URIRef

from ..base import BaseMetadataStore
from .sparql.construct import (
    construct_dataset_core,
    construct_dataset_keywords,
    construct_dataset_themes,
    construct_dataset_contact_point,
    construct_dataset_temporal_coverage,
)
from .. import constants


class OxigraphMetadataStore(BaseMetadataStore):
    def setup(self):
        oxigraph_url = os.environ.get("GRAPH_DB_URL", None)
        assert oxigraph_url is not None, (
            "The env var 'GRAPH_DB_URL' must be set to use "
            "the OxigraphMetadataStore store."
        )

        configuration = (f"{oxigraph_url}/query", f"{oxigraph_url}/update")
        self.db = Dataset(
            store=SPARQLUpdateStore(*configuration)
        )

    def get_datasets(self) -> Optional[Dict]: # pragma: no cover
        """
        Gets all datasets
        """
        raise NotImplementedError

    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """
        Get a dataset by its ID and return its metadata as a JSON-LD dict.
        """

        # Specify the named graph from which we are fetching data
        graph = self.db.get_context(
            URIRef(f"https://data.ons.gov.uk/datasets/{dataset_id}/record")
        )

        # Use the construct wrappers to pull the raw RDF triples
        # (as one rdflib.Graph() for each function) and add them
        # together to create a sinlge Graph of the
        # data we need.
        result: Graph = (
            construct_dataset_core(graph)
            + construct_dataset_keywords(graph)
            + construct_dataset_themes(graph)
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
        contact_point_graph = next((x for x in data["@graph"] if "vcard:fn" in x.keys()), None)
        temporal_coverage_graph = next((x for x in data["@graph"] if "dcat:endDate" in x.keys()), None)
        
        # Compact and embed anonymous nodes
        # TODO - we'll want to make sure these fields exist
        # to avoid key errors.
        dataset_graph["contact_point"] = {
            "name": contact_point_graph["vcard:fn"]["@value"],
            "email": contact_point_graph["vcard:hasEmail"]["@id"]
        }
        dataset_graph["temporal_coverage"] = {
             "start": temporal_coverage_graph["dcat:endDate"]["@value"],
             "end": temporal_coverage_graph["dcat:startDate"]["@value"]
        }
        
        # Use a remote context
        dataset_graph["@context"] = "https://data.ons.gov.uk/ns#"

        return dataset_graph


    def get_editions(self, dataset_id: str) -> Optional[Dict]: # pragma: no cover
        """
        Gets all editions of a specific dataset
        """
        raise NotImplementedError

    def get_edition(self, dataset_id: str, edition_id: str) -> Optional[Dict]: # pragma: no cover
        """
        Gets a specific edition of a specific dataset
        """
        raise NotImplementedError

    def get_versions(self, dataset_id: str, edition_id: str) -> Optional[Dict]: # pragma: no cover
        """
        Gets all versions of a specific edition of a specific dataset
        """

    def get_version(
        self, dataset_id: str, edition_id: str, version_id: str
    ) -> Optional[Dict]: # pragma: no cover
        """
        Gets a specific version of a specific edition of a specific dataset
        """
        raise NotImplementedError

    def get_publishers(self) -> Optional[Dict]: # pragma: no cover
        """
        Gets all publishers
        """
        raise NotImplementedError

    def get_publisher(self, publisher_id: str) -> Optional[Dict]: # pragma: no cover
        """
        Get a specific publisher
        """
        raise NotImplementedError

    def get_topics(self) -> Optional[Dict]: # pragma: no cover
        """
        Get all topics
        """
        raise NotImplementedError

    def get_topic(self) -> Optional[Dict]: # pragma: no cover
        """
        Get a specific topic
        """
        raise NotImplementedError

    def get_sub_topics(self, topic_id: str) -> Optional[Dict]: # pragma: no cover
        """
        Get all sub-topics for a specific topic
        """
        raise NotImplementedError

    def get_sub_topic(self, topic_id: str, sub_topic_id: str) -> Optional[Dict]: # pragma: no cover
        """
        Get a specific sub-topic for a specific topic
        """
        raise NotImplementedError
