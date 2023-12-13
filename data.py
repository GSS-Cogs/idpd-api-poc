"""
Tool that uses jsonld files in /src/store/metadata/stub/content to:

- create ttl files per resource
- create a seed.trig file repredenting single load file of these
  resources as named graphs.
- loads this seed.trig into an oxigraph database running on
  http://localhost:7878

Please run this vai the Makefile if you want to finesses this behaviour.
"""

import json
import os
import shutil
import glob
from pathlib import Path

from rdflib import ConjunctiveGraph, Dataset, BNode, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql
from src import schemas


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


def process_json_files(g, dir_path, schema):
    """
    Process JSON files in a directory, apply context, and add to an RDF graph.
    """
    for json_file in glob.glob(os.path.join(dir_path, "*.json")):
        with open(json_file) as f:
            resource_dict = json.load(f)
            #  add schema validation
            schema(**resource_dict)

        # Parse the JSON-LD and add to the graph
        g += Graph().parse(
            data=json.dumps(set_context(resource_dict)), format="json-ld"
        )

# def populate_all_files_in_directory(directory_path, oxigraph_url=None, write_to_db=True):
#     for filename in os.listdir(directory_path):
#         if filename.endswith(".jsonld"):  # or ".json", if your files are .json
#             file_path = os.path.join(directory_path, filename)
#             populate(jsonld_location=file_path, oxigraph_url=oxigraph_url, write_to_db=write_to_db)
            

def populate(jsonld_location=None, oxigraph_url=None, write_to_db=True):
    this_dir = Path(__file__).parent
    subbed_metadata_store_content_path = Path(
        "src/store/metadata/stub/content"
    ).absolute()

    # Clear up any previous
    out = Path(this_dir / "out")
    if out.exists():
        shutil.rmtree(out.absolute())
    out.mkdir()

    # Conjuctive flavour of graph as in RDF terms each resource
    # is its own invidual named graph of a specific type.
    g = ConjunctiveGraph()

    # Remove then recreate any previous out folder
    out_dir = Path("out")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    # ------------------
    # Datasets resources
    # ------------------

    # Load from disk
    datasets_source_path = Path(
        Path(jsonld_location).absolute() / "datasets.json"
    )
    with open(datasets_source_path) as f:
        datasets_source_dict = json.load(f)
        # Validate then add to graph
        schemas.Datasets(**datasets_source_dict)
        g += Graph().parse(
            data=json.dumps(set_context(datasets_source_dict)),
            format="json-ld",
        )

    # ------------------
    # Editions resources
    # ------------------

    # Load from disk
    editions_source_path = Path(
        subbed_metadata_store_content_path / "editions"
    )
    # Validate then add to graph
    schema = schemas.Editions
    process_json_files(g, editions_source_path, schema)

    # ------------------
    # Versions resources
    # ------------------

    versions_source_path = Path(
        subbed_metadata_store_content_path / "editions/versions"
    )

    # Validate then add to graph
    schema = schemas.Versions
    process_json_files(g, versions_source_path, schema)

    # ------------------
    # Topics resources
    # ------------------

    topics_source_path = Path(
        subbed_metadata_store_content_path / "topics.json"
    )
    with open(topics_source_path) as f:
        topics_source_dict = json.load(f)
        # Validate then add to graph
        schemas.Topics(**topics_source_dict)
        g += Graph().parse(
            data=json.dumps(set_context(topics_source_dict)),
            format="json-ld",
        )

    # --------------------
    # Publishers resources
    # --------------------

    publishers_source_path = Path(
        subbed_metadata_store_content_path / "publishers.json"
    )
    with open(publishers_source_path) as f:
        publishers_source_dict = json.load(f)
        # Validate then add to graph
        schemas.Publishers(**publishers_source_dict)
        g += Graph().parse(
            data=json.dumps(set_context(publishers_source_dict)),
            format="json-ld",
        )

    out_path = Path("out/seed.ttl")
    g.serialize(out_path, format="ttl")

    if write_to_db:
        assert (
            oxigraph_url
        ), "You need to specfiy the oxigraph url via the OXIGRAPH_URL env var."

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
