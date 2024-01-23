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
from main import combine_datasets
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

        # Check that the resource type is in the path
        # eg an id for a topic should have /topics in the url
        assert resource_type in resource["@id"], (
            f'''
            The @id for a resouce of type "{resource_type}" should contain
            /{resource_type} in the url, but does not.

            Got: {resource["@id"]}
            '''
        )

    # Schema validation
    schema(**resource_dict)

    # Parse the JSON-LD and add to the graph
    g += Graph().parse(data=json.dumps(set_context(resource_dict)), format="json-ld")
    assert len(g) > graph_length


def populate(oxigraph_url=None, write_to_db=True):
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
    # datasets_source_path = Path(metadata_stub_content_path / "datasets" / "*.json")
    editions_source_path = Path(metadata_stub_content_path / "datasets" / "*" / "editions")
    versions_source_path = Path(metadata_stub_content_path / "datasets" / "*" / "editions" / "*" / "versions")
    topics_source_path = Path(metadata_stub_content_path / "topics.json")
    publishers_source_path = Path(metadata_stub_content_path / "publishers.json")

    # ------------------
    # Datasets resources
    # ------------------

    # Load json file from disk
    # with open(datasets_source_path) as f:
    #     datasets_source_dict = json.load(f)
    datasets_source_dict = combine_datasets()
    _confirm_resource_count(datasets_source_dict, "datasets")

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

    # Extract creators from datasets.json for validation later
    dataset_creators = {
        dataset["creator"] for dataset in datasets_source_dict["datasets"]
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
        _confirm_resource_count(edition, "editions")
        assert (
            edition["@id"] in dataset_editions_urls
        ), f"Editions URL {edition['@id']} not found in {dataset_editions_urls}"
        for edn in edition["editions"]:
            versions_in_edition[edn["versions_url"]] = edn["versions"]
            topics_in_editions.update(edn["topics"])
            assert (
                edn["publisher"] in dataset_publishers
            ), f"{edn['publisher']} not in publisher list {dataset_publishers}"
        _assert_summarised_edition_in_dataset(datasets_source_dict["datasets"], edition)
        validate_and_parse_json(g, schemas.Editions, edition, "editions")

    # ------------------
    # Versions resources
    # ------------------

    # Load json files from disk
    versions = process_json_files(versions_source_path)

    # Validate data and add to graph
    for version in versions:
        _confirm_resource_count(version, "versions")
        assert (
            version["@id"] in versions_in_edition.keys()
        ), f"Versions URL {version['@id']} not found in {versions_in_edition.keys()}"
        _assert_summarised_version_in_edition(version, versions_in_edition)
        validate_and_parse_json(g, schemas.Versions, version, "versions")

    # ----------------
    # Topics resources
    # ----------------

    # Load json file from disk
    with open(topics_source_path) as f:
        topics_source_dict = json.load(f)
    _confirm_resource_count(topics_source_dict, "topics")

    # Validate data and add to graph
    topic_ids = [topic["@id"] for topic in topics_source_dict["topics"]]
    for dataset in datasets_source_dict["datasets"]:
        for topic in dataset["topics"]:
            assert (
                topic in topic_ids
            ), f"{topic} not in list of approved topics {topic_ids}"
    for topic in topics_in_editions:
        assert topic in topic_ids, (
            f'''
            We're defining a topic of {topic} within an edition but it is not (and must) de defined as a topic resource in topics.json.

            Defined topics from topics.json:
            {topic_ids}'''
            )
    validate_and_parse_json(g, schemas.Topics, topics_source_dict, "topics")

    # --------------------
    # Publishers resources
    # --------------------

    graph_length = len(g)
    with open(publishers_source_path) as f:
        publishers_source_dict = json.load(f)
    _confirm_resource_count(publishers_source_dict, "publishers")

    _confirm_in_use_publisher_resource(publishers_source_dict, dataset_publishers, dataset_creators)

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


def _confirm_resource_count(resource_dict: Dict, resource_name: str):
    """
    Check that the sub document of a json file has a length that
    matches the count field of that json file.
    """
    assert len(resource_dict[resource_name]) == int(resource_dict["count"]), (
        f'''
        The count field for {resource_name} is wrong.
        Got: {int(resource_dict["count"])}.
        Expected: {len(resource_dict[resource_name])}.
        '''
    )

def _confirm_in_use_publisher_resource(publishers: Dict, dataset_publishers: List[Dict], dataset_creators: List[Dict]):
    """
    Confirm that:

    - any publisher listed at the datasets level exists
    - any creator listed at the datasets level exists
    - all publisher resources appear in one or more of the above checks
    """
    publisher_ids_from_publishers_json = [x["@id"] for x in publishers["publishers"]]
    references_used = []

    for publisher in dataset_publishers:
        assert publisher in publisher_ids_from_publishers_json, (
            f'''
            The publisher: {publisher}
            is referenced in a datasets resource but does not exist in the definitions of publishers from publishers.json.
            '''
        )
        references_used.append(publisher)

    for publisher in dataset_creators:
        assert publisher in publisher_ids_from_publishers_json, (
            f'''
            The publisher: {publisher}
            is referenced in a datasets resource but does not exist in the definitions of publishers.
            '''
        )
        references_used.append(publisher)

    # At this point all publishers we've defined should have appeared at least once.
    unique_references_used = list(set(references_used))

    unique_references_used.sort()
    publisher_ids_from_publishers_json.sort()

    assert len(unique_references_used) == len(publisher_ids_from_publishers_json), (
        f'''
        Publishers are being created that do not appear to be utilised.

        Ids of publisher resources being created:
        {publisher_ids_from_publishers_json}

        Ids of publisher resources being used
        {unique_references_used}
        '''
    )

def _assert_summarised_edition_in_dataset(datasets: Dict, edition: Dict):
    """
    Editions sub documents are included in two places within our stubbed data
    content.

    1. A short form representation of an edition is included in a "editions" sub
       document within the dataset json file.
    2. The full edition documents is included in the edition json file.

    With this check we are making sure that the field values as included in the
    short form edition match the fields as included in the full edition document.
    """

    for id, issued, modified, in_series in [(x["@id"],x["issued"],x["modified"], x["in_series"]) for x in edition["editions"]]:

        # Confirm that the in_series reference is pointing to the
        # same series as is specified by the id
        assert id.startswith(in_series), f'''
        The in_series field should appear at the beginning of the @id but 
        does not. This is a data error.

        @id: {id}
        in_series: {in_series}
        '''

        # The in_series field identifies the parent dataset of a given edition, use this
        # to pull the correct dataset document from known datasets.
        parent_dataset = [x for x in datasets if x["@id"] == in_series]
        assert len(parent_dataset) == 1, f"Cannot find exactly one parent dataset with an @id of {in_series}"
        parent_dataset = parent_dataset[0]

        # Now get the short form editions from that dataset document
        short_form_editions = parent_dataset["editions"]

        # Using our list of short form editions docs, confirm there is exactly one short form
        # editional document (from those listed in the dataset) with the same @id as the long form
        # representation from the editions file.
        short_form_editions_with_correct_id = [x for x in short_form_editions if x["@id"] == id]

        assert len(short_form_editions_with_correct_id) == 1, (
            f'''
            Could not find exactly one edition listed at the dataset level that
            has the @id of:
            
            {id}
            
            Found {len(short_form_editions_with_correct_id)} matching editions in considered dataset:
            {parent_dataset["@id"]}.

            The truncated editions listed for this dataset are:
            {json.dumps(short_form_editions, indent=2)}
            '''
        )
        short_form_edition_with_correct_id = short_form_editions_with_correct_id[0]

        # Confirm the issued date matches
        assert issued == short_form_edition_with_correct_id["issued"], (
            f'''
            For the version {id}.

            The issued date in the full version document is {issued}.

            But in the truncated view at the dataset level it is {short_form_edition_with_correct_id["issued"]}.

            These fields should match.
            '''
        )

        # Confirm the issued date matches
        assert modified == short_form_edition_with_correct_id["modified"], (
            f'''
            For the version {id}.

            The issued date in the full version document is {modified}.

            But in the truncated view at the dataset level it is {short_form_edition_with_correct_id["modified"]}.

            These fields should match.
            '''
        )

        assert len(short_form_edition_with_correct_id) == 3, (
            f'''The version:

                {json.dumps(short_form_edition_with_correct_id, indent=2)}

            Should have three fields, "@id", "issued" and "mopdified" but has more.
            '''
        )


def _assert_summarised_version_in_edition(version: List[Dict], versions_in_edition: Dict[str, Dict]):
    """
    Versions sub documents are included in two places witin our stubbed data
    content.

    1. A short form representation of a version is included in a "versions" sub
       document within the edition json file for the relevant edition.
    2. The full version documents is included in the versions json file.

    With this check we are making sure that the field values as inlcuded in the
    short form version match the fields as included in the full version document.
    """

    for id, issued in [(x["@id"],x["issued"]) for x in version["versions"]]:

        # The version id includes the path to its edition so get all
        # the short form version information we processed at the edition level
        version_path = "/".join(id.split("/")[:-1])
        versions_for_this_edition = versions_in_edition.get(version_path, None)

        # Now we have a list of all relevant short form version docs, confirm there is
        # exactly one short form version document (from the editions file) with the
        # same @id as the long form representation from the versions file.
        short_form_versions_with_correct_id = [x for x in versions_for_this_edition if x["@id"] == id]
        assert len(short_form_versions_with_correct_id) == 1, (
            f'''
            Could not find exactly one version listed at the edition level that
            has the @id of {id}. Found {len(short_form_versions_with_correct_id)}.

            The truncated versions listed for this edition are:
            {versions_for_this_edition}
            '''
        )
        short_form_version_with_correct_id = short_form_versions_with_correct_id[0]

        # Confirm the issued date matches
        assert issued == short_form_version_with_correct_id["issued"], (
            f'''
            For the version {id}.

            The issued date in the full version document is {issued}.

            But in the truncated view at the editions level it is {short_form_version_with_correct_id["issued"]}.

            These fields should match.
            '''
        )

        assert len(short_form_version_with_correct_id) == 2, (
            f'''The version:

                {json.dumps(short_form_version_with_correct_id, indent=2)}

            Should only have two fields, "@id" and "issued" but has more.
            '''
        )


if __name__ == "__main__":
    oxigraph_url = os.getenv("GRAPH_DB_URL", None)
    populate(oxigraph_url=oxigraph_url)
