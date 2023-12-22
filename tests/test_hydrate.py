import re
import json
import pytest

from store.metadata.hydrate import _hydrate_graph_from_sub_graphs
from tests.fixtures.hydrate_data import hydrate_test_data

def test_hydrate_graph_from_subgraphs(hydrate_test_data):

    all_graphs = hydrate_test_data["@graph"]
    main_graph = hydrate_test_data["@graph"][2]

    hydrated_graph = _hydrate_graph_from_sub_graphs(main_graph, all_graphs)

    assert hydrated_graph
    assert hydrated_graph["temporal_coverage"]["dcat:startDate"]["@type"] == "xsd:dateTime"
    assert hydrated_graph["temporal_coverage"]["dcat:startDate"]["@value"] == "2005-01-01T00:00:00+00:00"

    assert hydrated_graph["temporal_coverage"]["dcat:endDate"]["@type"] == "xsd:dateTime"
    assert hydrated_graph["temporal_coverage"]["dcat:endDate"]["@value"] == "2019-03-01T00:00:00+00:00"
    
    assert hydrated_graph["contact_point"]["vcard:fn"]["@value"] == "Consumer Price Inflation Enquiries"
    assert hydrated_graph["contact_point"]["vcard:hasEmail"] == "mailto:cpih@ons.gov.uk"