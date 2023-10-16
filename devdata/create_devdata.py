"""
Tool that uses jsonld files in /src/store/metadata/stub/content to:

- create ttl files per resource
- create a seed.trig file repredenting single load file of these
  resources as named graphs.
- loads this seed.trig into an oxigraph database running on
  http://localhost:7878

Please run this vai the Makefile if you want to finesses this behaviour.
"""

from datetime import datetime
import json
import os
from os import linesep
from pathlib import Path
import shutil

from pytz import timezone
from rdflib import ConjunctiveGraph, Dataset, BNode, Graph
from rdflib import Literal, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, XSD


# TODO - will need updating when the details are worked out.
def set_context(resource_item: dict) -> dict:
    """
    Set a specific context location to inform the RDF created
    from the jsonld samples.
    """
    repo_root = Path(__file__).parent.parent
    context_file = Path(repo_root / "src/store/metadata/context.json")

    with open(context_file) as f:
        context = json.load(f)

    resource_item["@context"] = context
    return resource_item


def populate(oxigraph_url=None, write_to_db=True):

    this_dir = Path(__file__).parent
    repo_root = this_dir.parent
    subbed_metadata_store_content_path = Path(
        repo_root / "src/store/metadata/stub/content"
    ).absolute()

    # Clear up any previous
    out = Path(this_dir / "out")
    if out.exists():
        shutil.rmtree(out.absolute())
    out.mkdir()

    # Conjuctive flavour of graph as in RDF terms each resource
    # is its own invidual named graph of a specific type.
    g = ConjunctiveGraph()

    # We're going to have to do some nasty wrangling to get
    # individual graphs in the trig format out of this
    prefixes = []
    wrangled_lines = []

    # -----------------
    # Dataset resources
    # -----------------
    datasets_source_jsonld = Path(subbed_metadata_store_content_path / "datasets.json")
    with open(datasets_source_jsonld) as f:
        resource_file = json.load(f)
    datasets_datasets_source_jsonl = set_context(resource_file)
    g = Graph().parse(data=json.dumps(datasets_datasets_source_jsonl), format="json-ld")

    # -----------------
    # Editions resources
    # -----------------
    # Write out our graph
    editions_source_jsonld = Path(subbed_metadata_store_content_path / "editions/cpih_2022-01.json")
    with open(editions_source_jsonld) as f:
        resource_file = json.load(f)
    editions_source_jsonl = set_context(resource_file)
    g += Graph().parse(data=json.dumps(editions_source_jsonl), format="json-ld")

    versions_source_jsonld = Path(subbed_metadata_store_content_path / "editions/versions/cpih_2022-01.json")
    with open(versions_source_jsonld) as f:
        resource_file = json.load(f)
    versions_source_jsonl = set_context(resource_file)
    g += Graph().parse(data=json.dumps(versions_source_jsonl), format="json-ld")

    topics_source_jsonld = Path(subbed_metadata_store_content_path / "topics.json")
    with open(topics_source_jsonld) as f:
        resource_file = json.load(f)
    topics_source_jsonl = set_context(resource_file)
    g += Graph().parse(data=json.dumps(topics_source_jsonl), format="json-ld")

    publisher_source_jsonld = Path(subbed_metadata_store_content_path / "publishers.json")
    with open(publisher_source_jsonld) as f:
        resource_file = json.load(f)
    publisher_source_jsonld = set_context(resource_file)
    g += Graph().parse(data=json.dumps(publisher_source_jsonld), format="json-ld")

    out_path = Path(repo_root / f"devdata/out/potential_seed.ttl")
    g.serialize(out_path, format="ttl")

    import sys
    sys.exit(1)
    

    for i, dataset_dict in enumerate(resource_file["items"]):
        dataset_id = dataset_dict["identifier"]

        # Create a named graph
        named_graph_uri = URIRef(
            f"https://data.ons.gov.uk/datasets/{dataset_id}/record"
        )

        # Populate with database side structural triples
        current_datetime = datetime.now(timezone("UTC")).isoformat(timespec="seconds")
        g.add((named_graph_uri, RDF.type, DCAT.CatalogRecord))
        g.add(
            (
                named_graph_uri,
                FOAF.primaryTopic,
                URIRef(f"https://data.ons.gov.uk/datasets/{dataset_id}"),
            )
        )
        g.add(
            (
                named_graph_uri,
                DCTERMS.created,
                Literal(current_datetime, datatype=XSD.dateTime),
            )
        )

        # Add an appropriate context to our jsonld to allow converstion to RDF
        dataset_dict = set_context(dataset_dict)

        # Add the graph of jsonld sourced triples to the named graph
        # alongside our structural triples
        jsonld_as_graph = Graph()
        jsonld_as_graph.parse(data=json.dumps(dataset_dict), format="json-ld")
        g += jsonld_as_graph

        # Write out our graph
        out_path = Path(repo_root / f"devdata/out/dataset{i}.ttl")
        g.serialize(out_path, format="ttl")

        # Now do some (uber primitive) wrangling to get the ttl
        # into the trig format with the individual named graphs
        # explicitly shown.
        with open(out_path) as f:
            started_graph = False
            for i, line in enumerate(f.readlines()):
                if line.startswith("@prefix"):
                    if line not in prefixes:
                        prefixes.append(line)
                else:
                    if not started_graph:
                        wrangled_lines.append("")
                        wrangled_lines.append(f"<{named_graph_uri}>" + " {" + linesep)
                        started_graph = True
                    if line.strip() == "":
                        wrangled_lines.append(line)
                    else:
                        wrangled_lines.append("\t" + line)
            wrangled_lines.append("}" + linesep + linesep)

    # ------------------
    # Editions resources
    # ------------------
    # TODO

    # ------------------
    # Versions resources
    # ------------------
    # TODO

    # etc etc...

    if write_to_db:

        assert (
            oxigraph_url
        ), "You need to specfiy the oxigraph url via the OXIGRAPH_URL env var."

        seed = Path(repo_root / "devdata/out/seed.trig")
        with open(seed, "w") as f:
            for prefix in prefixes:
                f.write(prefix)
            f.write(linesep)

            for line in wrangled_lines:
                f.write(line)

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
        db.parse(seed)


if __name__ == "__main__":
    oxigraph_url = os.getenv("GRAPH_DB_URL", None)
    populate(oxigraph_url=oxigraph_url)
