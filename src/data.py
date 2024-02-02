"""
Tool that uses jsonld files in /src/store/metadata/stub/content to:

- create ttl files per resource
- create a seed.trig file repredenting single load file of these
  resources as named graphs.
- loads this seed.trig into an oxigraph database running on
  http://localhost:7879

Please run this via the Makefile if you want to finesse this behaviour.
"""

import glob
import json
import os
import shutil
from pathlib import Path

from rdflib import BNode, ConjunctiveGraph, Dataset, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql

from store.metadata.stub.stub_store import StubMetadataStore

# Load the context file
with open(Path("src/store/metadata/context.json")) as f:
    context = json.load(f)


def set_context(resource_item):
    """
    Set a specific context location to inform the RDF created
    from the jsonld samples.
    """
    resource_item["@context"] = context
    return resource_item


def process_json_files(dir_path):
    """
    Process all JSON files in a given directory
    """
    json_files = glob.glob(os.path.join(dir_path, "*.json"))
    assert len(json_files) > 0
    resource_dicts = []
    for json_file in json_files:
        with open(json_file) as f:
            resource_dicts.append(json.load(f))
    return resource_dicts


def populate(jsonld_location=None, oxigraph_url=None, write_to_db=True):
    this_dir = Path(__file__).parent
    store = StubMetadataStore(content_path=jsonld_location)
    metadata_stub_content_path = store.content_dir

    # Clear up any previous out files
    out = Path(this_dir / "out")
    if out.exists():
        shutil.rmtree(out.absolute())
    out.mkdir()

    # Create an empty conjunctive graph, as in RDF terms each resource
    # is its own individual named graph of a specific type.
    g = ConjunctiveGraph()

    # Remove then recreate any previous out folder
    out_dir = Path("out")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    # Specify locations of JSON files
    datasets_source_path = Path(metadata_stub_content_path / "datasets.json")
    editions_source_path = Path(metadata_stub_content_path / "editions")
    versions_source_path = Path(metadata_stub_content_path / "editions" / "versions")
    topics_source_path = Path(metadata_stub_content_path / "topics.json")
    publishers_source_path = Path(metadata_stub_content_path / "publishers.json")

    # ------------------
    # Datasets resources
    # ------------------

    # Load json file from disk
    with open(datasets_source_path) as f:
        datasets_source_dict = json.load(f)

    # Add datasets to graph
    graph_length = len(g)
    g += Graph().parse(
        data=json.dumps(set_context(datasets_source_dict)), format="json-ld"
    )
    assert len(g) > graph_length
    # ------------------
    # Editions resources
    # ------------------

    # Load json files from disk
    editions = process_json_files(editions_source_path)

    # Add editions to graph
    graph_length = len(g)
    for edition in editions:
        g += Graph().parse(data=json.dumps(set_context(edition)), format="json-ld")
        # _assert_editions_ordered_by_issued(edition, "editions", "versions")
    assert len(g) > graph_length
    # ------------------
    # Versions resources
    # ------------------

    # Load json files from disk
    versions = process_json_files(versions_source_path)

    # Add versions to graph
    graph_length = len(g)
    for version in versions:
        g += Graph().parse(data=json.dumps(set_context(version)), format="json-ld")
    assert len(g) > graph_length

    # ------------------
    # Topics resources
    # ------------------

    # Load json file from disk
    with open(topics_source_path) as f:
        topics_source_dict = json.load(f)

    # Add topics to graph
    graph_length = len(g)
    g += Graph().parse(
        data=json.dumps(set_context(topics_source_dict)), format="json-ld"
    )
    assert len(g) > graph_length

    # --------------------
    # Publishers resources
    # --------------------

    with open(publishers_source_path) as f:
        publishers_source_dict = json.load(f)

    # Add publishers to graph
    graph_length = len(g)
    g += Graph().parse(
        data=json.dumps(set_context(publishers_source_dict)),
        format="json-ld",
    )
    assert len(g) > graph_length

    out_path = Path("out/seed.ttl")
    g.serialize(out_path, format="ttl")

    if write_to_db:
        assert (
            oxigraph_url
        ), "You need to specify the Oxigraph URL via the OXIGRAPH_URL env var."

        # Now get this seed data into the database
        # adapted from:
        # - https://github.com/rossbowen/poc-api/blob/main/api/src/poc_api/database.py
        # - https://github.com/rossbowen/poc-api/blob/main/api/src/poc_api/seed/seed.py

        def skolemise(node):
            if isinstance(node, BNode):
                return "<bnode:b%s>" % node
            return _node_to_sparql(node)

        configuration = (f"{oxigraph_url}/query", f"{oxigraph_url}/update")
        db = Dataset(store=SPARQLUpdateStore(*configuration, node_to_sparql=skolemise))
        db.parse(out_path)


if __name__ == "__main__":
    oxigraph_url = os.getenv("GRAPH_DB_URL", None)
    jsonld_location = os.getenv("JSONLD_LOCATION", None)
    populate(jsonld_location=jsonld_location, oxigraph_url=oxigraph_url)
