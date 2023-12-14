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
from typing import Dict, List

from rdflib import ConjunctiveGraph, Dataset, BNode, Graph
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql
import schemas


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


def validate_and_parse_json(g, schema, resource_dict, resource_type):
    """
    Validate resources, apply context, and add to an RDF graph.
    """
    graph_length = len(g)

    # Check that `@id` and `identifier` are consistent
    for resource in resource_dict[resource_type]:
        assert (
            resource["@id"].split("/")[-1] == resource["identifier"]
        ), f"Mismatch between '@id' and 'identifier' fields for {resource['@id']}"

    # Schema validation
    schema(**resource_dict)

    # Parse the JSON-LD and add to the graph
    g += Graph().parse(data=json.dumps(set_context(resource_dict)), format="json-ld")
    assert len(g) > graph_length

# def populate_all_files_in_directory(directory_path, oxigraph_url=None, write_to_db=True):
#     for filename in os.listdir(directory_path):
#         if filename.endswith(".jsonld"):  # or ".json", if your files are .json
#             file_path = os.path.join(directory_path, filename)
#             populate(jsonld_location=file_path, oxigraph_url=oxigraph_url, write_to_db=write_to_db)
            

def populate(jsonld_location=None, oxigraph_url=None, write_to_db=True):
    this_dir = Path(__file__).parent
    metadata_stub_content_path = Path("src/store/metadata/stub/content").absolute()

    # Clear up any previous
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

    # Load json ld from disk
    datasets_source_path = Path(
        Path(jsonld_location).absolute() / "datasets.json"
    )
    with open(datasets_source_path) as f:
        datasets_source_dict = json.load(f)

    # Validate data and add to graph
    validate_and_parse_json(g, schemas.Datasets, datasets_source_dict, "datasets")

    # Extract edition URLs from datasets.json for validation later
    dataset_editions_urls = [
        dataset["editions_url"] for dataset in datasets_source_dict["datasets"]
    ]

    # Extract publishers from datasets.json for validation later
    dataset_publishers = {
        dataset["publisher"] for dataset in datasets_source_dict["datasets"]
    }

    # ------------------
    # Editions resources
    # ------------------

    # Load json files from disk
    editions = process_json_files(editions_source_path)

    # Empty dict to hold version data from editions for validation later
    versions_in_edition = dict()
    # Empty set to hold topic data from editions for validation later
    topics_in_editions = set()

    # Validate data and add to graph
    for edition in editions:
        assert (
            edition["@id"] in dataset_editions_urls
        ), f"Editions URL {edition['@id']} not found in {dataset_editions_urls}"
        for edn in edition["editions"]:
            versions_in_edition[edn["versions_url"]] = edn["versions"]
            topics_in_editions.update(edn["topics"])
            assert (
                edn["publisher"] in dataset_publishers
            ), f"{edn['publisher']} not in publisher list {dataset_publishers}"
        for dataset in datasets_source_dict["datasets"]:
            _assert_dataset_edition_in_summarised_editions(dataset, edition)
        validate_and_parse_json(g, schemas.Editions, edition, "editions")

    # ------------------
    # Versions resources
    # ------------------

    # Load json files from disk
    versions = process_json_files(versions_source_path)

    # Validate data and add to graph
    for version in versions:
        assert (
            version["@id"] in versions_in_edition.keys()
        ), f"Versions URL {version['@id']} not found in {versions_in_edition.keys()}"
        _assert_summarised_version_in_edition(version, versions_in_edition)
        validate_and_parse_json(g, schemas.Versions, version, "versions")

    # ------------------
    # Topics resources
    # ------------------

    # Load json file from disk
    with open(topics_source_path) as f:
        topics_source_dict = json.load(f)

    # Validate data and add to graph
    topic_ids = [topic["@id"] for topic in topics_source_dict["topics"]]
    for dataset in datasets_source_dict["datasets"]:
        for topic in dataset["topics"]:
            assert (
                topic in topic_ids
            ), f"{topic} not in list of approved topics {topic_ids}"
    for topic in topics_in_editions:
        assert topic in topic_ids, f"{topic} not in {topic_ids}"
    validate_and_parse_json(g, schemas.Topics, topics_source_dict, "topics")

    # --------------------
    # Publishers resources
    # --------------------

    graph_length = len(g)
    with open(publishers_source_path) as f:
        publishers_source_dict = json.load(f)

    # TODO This currently fails as OFCOM is not listed as a publisher in any of the datasets (it's a creator for 4gc). Do we need a separate creators.json?
    # for publisher in publishers_source_dict["publishers"]:
    #     assert (
    #         publisher["@id"] in dataset_publishers
    #     ), f"{publisher['@id']} not in list of publishers {dataset_publishers}"

    # Validate then add to graph
    schemas.Publishers(**publishers_source_dict)
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


def _assert_dataset_edition_in_summarised_editions(dataset: Dict, edition: Dict):
    summarised_editions = [
        {
            "@id": edn["@id"],
            "issued": edn["issued"],
            "modified": edn["modified"],
        }
        for edn in edition["editions"]
    ]
    if dataset["editions_url"] == edition["@id"]:
        for edn in dataset["editions"]:
            assert (
                edn in summarised_editions
            ), f"Discrepancy between {edn} and {summarised_editions}"


def _assert_summarised_version_in_edition(version, versions_in_edition):
    summarised_versions = [
        {"@id": vsn["@id"], "issued": vsn["issued"]} for vsn in version["versions"]
    ]
    for summarised_version in summarised_versions:
        assert (
            summarised_version in versions_in_edition[version["@id"]]
        ), f"Discrepancy between {versions_in_edition} and {summarised_versions}"


if __name__ == "__main__":
    oxigraph_url = os.getenv("GRAPH_DB_URL", None)
    jsonld_location = os.getenv("JSONLD_LOCATION", None)
    populate(jsonld_location=jsonld_location, oxigraph_url=oxigraph_url)
